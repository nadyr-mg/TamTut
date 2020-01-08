import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView

from core.enums import FeedSorting
from core.forms import UserRegistrationForm, HobbyList, EditProfileForm, MessageForm, CreatePostForm
from core.models import Profile, Message, Post, Hobby

from TamTut.settings import POSTS_ON_PROFILE_PAGE, POSTS_ON_HOME_PAGE, DAYS_HOT_POSTS, FOLLOWERS_ON_FOLLOWS_PAGE


def paginate(request, objects, num_of_elements):
    objects = Paginator(objects, num_of_elements)
    page = request.GET.get('page')
    objects = objects.get_page(page)
    return objects


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'GET':
        form = UserRegistrationForm()
    else:
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(
                username=username, password=raw_password,
            )
            login(request, authenticated_user)
            return redirect('home')

    context = {'form': form}
    return render(request, 'core/register.html', context)


@login_required(login_url='login')
def home(request, *args, **kwargs):
    is_global_feed = False
    if 'sorting' in request.GET:
        # if we have 'sorting' argument then we switch to global feed type
        try:
            arg = request.GET['sorting'].lower()
            feed_sorting = FeedSorting(arg)
            is_global_feed = True
        except ValueError:
            feed_sorting = None
    else:
        feed_sorting = None

    all_posts = Post.objects.all()
    if feed_sorting is None:
        # means we return follower feed
        following_profiles = request.user.profile.follows.all()
        feed = get_followers_feed(request, following_profiles)
    elif feed_sorting == FeedSorting.NEW:
        feed = all_posts.order_by('-date_posted')
    elif feed_sorting == FeedSorting.HOT:
        date_from = datetime.datetime.now() - datetime.timedelta(days=DAYS_HOT_POSTS)
        hot_feed = all_posts.filter(date_posted__gte=date_from)
        feed = sorted(hot_feed, key=lambda x: x.likes_amount, reverse=True)
    else:
        feed = sorted(all_posts, key=lambda x: x.likes_amount, reverse=True)

    feed = paginate(request, feed, POSTS_ON_HOME_PAGE)
    context = {
        'feed': feed,
        'is_global_feed': is_global_feed,
    }
    return render(request, 'core/home.html', context)


def get_followers_feed(request, following_profiles):
    followers_feed = Post.objects.filter(author__in=following_profiles)
    if followers_feed.exists():
        followers_feed = followers_feed.order_by('-date_posted')
        followers_feed = paginate(request, followers_feed, POSTS_ON_HOME_PAGE)
    return followers_feed


class ProfileFollowersView(ListView):
    template_name = 'core/profile_followers_page.html'
    paginate_by = FOLLOWERS_ON_FOLLOWS_PAGE

    def get_queryset(self):
        try:
            target_profile_followers = Profile.objects.get(pk=self.kwargs['pk']).followed_by.all()
            return target_profile_followers
        except Profile.DoesNotExist:
            raise Http404("User doesn't exist")


class ProfileFollowingView(ListView):
    template_name = 'core/profile_following_page.html'
    paginate_by = FOLLOWERS_ON_FOLLOWS_PAGE

    def get_queryset(self):
        try:
            target_profile_follows = Profile.objects.get(pk=self.kwargs['pk']).follows.all()
            return target_profile_follows
        except Profile.DoesNotExist:
            raise Http404("User doesn't exist")


def profile(request, pk):
    try:
        profile_user = User.objects.get(id=pk)
    except User.DoesNotExist:
        raise Http404("Page doesn't exist")
    target_profile = Profile.objects.get(user=profile_user)

    if request.method == 'GET':
        create_post_form = CreatePostForm()

        hobbies = target_profile.hobby.all()
        followed_by = target_profile.followed_by.all()

        posts = target_profile.posts.all()
        posts = paginate(request, posts, POSTS_ON_PROFILE_PAGE)
        context = {
            'hobbies': hobbies,
            'prof': target_profile,
            'create_post_form': create_post_form,
            'posts': posts,
            'followed_by': followed_by
        }
        return render(request, 'core/profile.html', context)
    else:
        create_post(request, target_profile)

        return redirect('profile', pk=target_profile.pk)


def create_post(request, target_profile):
    create_post_form = CreatePostForm(request.POST or None)
    if create_post_form.is_valid():
        post_text = create_post_form.cleaned_data['text']
        Post.objects.create(author=request.user.profile, text=post_text)
        return redirect('profile', pk=target_profile.pk)


@login_required(login_url='login')
def follow_target_profile(request, pk):
    try:
        target_user = User.objects.get(id=pk)
        target_profile = Profile.objects.get(user=target_user)
        cur_profile = request.user.profile
        if target_profile in cur_profile.follows.all():
            cur_profile.follows.remove(target_profile)
        else:
            cur_profile.follows.add(target_profile)

        return redirect('profile', pk=target_profile.pk)
    except User.DoesNotExist:
        raise Http404("Page doesn't exist")


@login_required(login_url='login')
def edit_profile(request):
    target_user = User.objects.get(id=request.user.id)
    target_profile = target_user.profile

    if request.method == 'POST':
        edit_profile_form = EditProfileForm(request.POST, request.FILES)
        edit_profile_form.set_hobbies_choices(Hobby.objects.all())

        if edit_profile_form.is_valid():
            data = edit_profile_form.cleaned_data

            parameters = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'email': data.get('email')
            }
            save_cur_user_info(target_user, parameters)

            coors = data.get('coors')
            hobby = data.get('hobby')
            image = data.get('image')
            save_cur_prof_info(target_profile, hobby, image, coors)
            return redirect(reverse('profile', args=[request.user.id]))
        else:
            return redirect(reverse('profile', args=[request.user.id]))

    else:
        edit_profile_form = EditProfileForm({
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_user.email,
            'hobby': [hobby for hobby in target_profile.hobby.all().values_list('name', flat=True)],
            'coors': f'{target_profile.latitude}, {target_profile.longitude}'
        })
        edit_profile_form.set_hobbies_choices(Hobby.objects.all())
        context = {
            'edit_profile_form': edit_profile_form,
        }
        return render(request, 'core/edit_profile.html', context)


def save_cur_user_info(target_user, parameters):
    for field, value in parameters.items():
        setattr(target_user, field, value)
    target_user.save()


def save_cur_prof_info(target_profile, hobby, image, coors):
    hobbies = Hobby.objects.filter(name__in=hobby)
    target_profile.hobby.set(hobbies)

    if image:
        target_profile.image = image

    if coors:
        lat, long = float(coors.split(', ')[0]), float(coors.split(', ')[1])
        target_profile.latitude, target_profile.longitude = lat, long

    target_profile.save()


@login_required(login_url='login')
def map_view(request, *args, **kwargs):
    hobbies_form = HobbyList()
    all_profiles = Profile.objects.all()
    if request.method == 'GET':
        cur_user_hobbies = request.user.profile.hobby.all()
        matched_profiles = all_profiles.filter(hobby__in=cur_user_hobbies).distinct().exclude(
            user=request.user)

        context = {
            'matched_profiles': matched_profiles,
            'hobbies_form': hobbies_form,
        }
        return render(request, 'core/map.html', context)
    else:
        hobbies_form = HobbyList(request.POST or None)
        if hobbies_form.is_valid():
            hobbies = hobbies_form.cleaned_data['hobby']
            matched_profiles = request.user.profile.filter_by_hobbies(hobbies).exclude(user=request.user)
            any_match_profiles = Profile.objects.filter(hobby__in=hobbies).distinct()

            context = {
                'matched_profiles': matched_profiles,
                'hobbies_form': hobbies_form,
                'any_match_profiles': any_match_profiles
            }
            return render(request, 'core/map.html', context)


@login_required(login_url='login')
def chat(request):
    cur_user_msgs = Message.user_msgs(request.user)
    interlocutors = []
    for msg in cur_user_msgs:
        if msg.sender == request.user:
            interlocutor = msg.receiver
        else:
            interlocutor = msg.sender

        if interlocutor not in interlocutors:
            interlocutors.append(interlocutor)

    context = {'interlocutors': interlocutors}
    return render(request, 'core/chat.html', context)


@login_required(login_url='login')
def chat_by_user(request, chat_username):
    if chat_username == request.user.username:
        return redirect(reverse('chat'))

    try:
        chat_user = User.objects.get(username=chat_username)
    except ObjectDoesNotExist:
        raise Http404("User doesn't exist")

    if request.method == 'POST':
        msg_form = MessageForm(request.POST)
        if msg_form.is_valid():
            msg_text = msg_form.cleaned_data['msg_text']
            Message.objects.create(receiver=chat_user, sender=request.user, msg_text=msg_text)
            return redirect(reverse('chat_by_user', args=[chat_username]))
    else:
        msg_form = MessageForm()

    cur_user_msgs = Message.user_msgs(request.user)
    interlocutors = []
    for msg in cur_user_msgs:
        if msg.sender == request.user:
            interlocutor = msg.receiver
        else:
            interlocutor = msg.sender

        if interlocutor not in interlocutors:
            interlocutors.append(interlocutor)

    msgs_by_user = cur_user_msgs.filter(Q(sender=chat_user) | Q(receiver=chat_user)).order_by('date_sent')
    context = {'msg_form': msg_form, 'new_all_msgs': msgs_by_user, 'chat_user': chat_user,
               'chat_username': chat_username, 'interlocutors': interlocutors}
    return render(request, 'core/chat.html', context)


@login_required(login_url='login')
def like_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        post.liked_by.add(request.user.profile)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Post.DoesNotExist:
        raise Http404("User doesn't exist")


@login_required(login_url='login')
def dislike_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        post.liked_by.remove(request.user.profile)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Post.DoesNotExist:
        raise Http404("User doesn't exist")

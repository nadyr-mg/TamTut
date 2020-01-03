import datetime
from itertools import chain

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

from core.forms import UserRegistrationForm, EditUserInfo, EditProfileInfo, HobbyList, CoorsForm, MessageForm, \
    FollowButtonForm, CreatePostForm, FeedTypeForm, SortGlobalFeedForm
from core.models import Profile, Message, Post

POSTS_ON_PROFILE_PAGE = 10


def paginate(request, objects, num_of_elements):
    objects = Paginator(objects, num_of_elements)
    page = request.GET.get('page')
    objects = objects.get_page(page)
    return objects


@login_required(login_url='login')
def home(request):
    feed_type = FeedTypeForm()
    following_profiles = request.user.profile.follows.all()

    if request.method == 'GET':
        feed = get_followers_feed(request, following_profiles)
        context = {
            'feed': feed,
            'feed_type': feed_type
        }
        return render(request, 'core/home.html', context)
    else:
        # TODO: get rid of forms, use GET arguments in urls to switch between different feed types
        feed_type_post = FeedTypeForm(request.POST or None)
        if feed_type_post.is_valid():
            followers_feed_true = feed_type_post.cleaned_data['followers_feed']
            if followers_feed_true:
                posts = get_followers_feed(request, following_profiles)
                context = {
                    'feed': posts,
                    'feed_type': feed_type
                }
                return render(request, 'core/home.html', context)

            global_feed_true = feed_type_post.cleaned_data['global_feed']
            if global_feed_true:
                sort_global_feed_form = SortGlobalFeedForm(request.POST or None)
                all_posts = Post.objects.all()
                if sort_global_feed_form.is_valid():
                    global_feed = sort_global_feed(sort_global_feed_form, all_posts)
                else:
                    global_feed = sorted(all_posts, key=lambda x: x.date_posted, reverse=True)

                global_feed = paginate(request, global_feed, 15)
                context = {
                    'feed': global_feed,
                    'feed_type': feed_type,
                    
                    'global_feed': True,
                    'sort_global_feed': SortGlobalFeedForm()
                }
                return render(request, 'core/home.html', context)

        return redirect('home')


def get_followers_feed(request, following_profiles):
    followers_feed = Post.objects.filter(author__in=following_profiles)
    if followers_feed.exists():
        followers_feed = followers_feed.order_by('-date_posted')
        # TODO: constant for page size
        followers_feed = paginate(request, followers_feed, 20)
    return followers_feed


def sort_global_feed(_sort_global_feed, all_posts):
    sort_global_feed_best = _sort_global_feed.cleaned_data['best']
    sort_global_feed_hot = _sort_global_feed.cleaned_data['hot']

    global_feed = all_posts.order_by('-date_posted')
    if sort_global_feed_best:
        global_feed = sorted(all_posts, key=lambda x: x.likes_amount, reverse=True)
    if sort_global_feed_hot:
        # TODO: constant for hot days
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        hot_feed = all_posts.filter(date_posted__gte=date_from)
        global_feed = sorted(hot_feed, key=lambda x: x.likes_amount, reverse=True)

    # TODO: move pagination here, create a constant var to define page size for feed
    return global_feed


def register(request):
    if request.method != 'POST':
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


class ProfileFollowersView(ListView):
    template_name = 'core/profile_followers_page.html'
    # TODO: create a contant var
    paginate_by = 50

    def get_queryset(self):
        # FIXME: check if profile doesn't exist
        return Profile.objects.get(pk=self.kwargs['pk']).followed_by.all()


class ProfileFollowingView(ListView):
    template_name = 'core/profile_following_page.html'
    # TODO: create a contant var
    paginate_by = 50

    def get_queryset(self):
        # FIXME: check if profile doesn't exist
        return Profile.objects.get(pk=self.kwargs['pk']).follows.all()


def profile(request, pk):
    try:
        profile_user = User.objects.get(id=pk)
    except User.DoesNotExist:
        raise Http404("Page doesn't exist")
    # 1
    target_profile = Profile.objects.get(user=profile_user)

    if request.method == 'GET':
        # 2
        create_post_form = CreatePostForm()
        # 3
        follow_button_form = FollowButtonForm()

        # 1
        hobbies = target_profile.hobby.all()
        followed_by = target_profile.followed_by.all()

        # 1
        posts = target_profile.posts.all()
        posts = paginate(request, posts, POSTS_ON_PROFILE_PAGE)
        context = {
            'hobbies': hobbies,
            'prof': target_profile,
            'create_post_form': create_post_form,
            'follow_button_form': follow_button_form,
            'posts': posts,
            'followed_by': followed_by
        }
        return render(request, 'core/profile.html', context)
    else:
        # 2
        create_post_form = CreatePostForm(request.POST or None)

        # 3
        # TODO: Move to a different view  and url (instead of using a separate form)
        follow_button_form = FollowButtonForm(request.POST or None)
        if follow_button_form.is_valid():
            following = follow_button_form.cleaned_data['follow']
            if following is True:
                cur_profile = request.user.profile
                if target_profile in cur_profile.follows.all():
                    cur_profile.follows.remove(target_profile)
                else:
                    cur_profile.follows.add(target_profile)

                return redirect('profile', pk=target_profile.pk)

        # 2
        # TODO: Move to a different view and url
        if create_post_form.is_valid():
            post_text = create_post_form.cleaned_data['text']
            Post.objects.create(author=request.user.profile, text=post_text)
            return redirect('profile', pk=target_profile.pk)

        return redirect('profile', pk=target_profile.pk)


@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        # TODO: merge 3 forms (EditUserInfo, EditProfileInfo, CoorsForm) into one
        u_form = EditUserInfo(request.POST, instance=request.user)
        p_form = EditProfileInfo(request.POST,
                                 request.FILES,
                                 instance=request.user.profile)
        coors_form = CoorsForm(request.POST or None)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

        if coors_form.is_valid():
            coors = coors_form.cleaned_data.get('coors')
            if coors:
                lat, long = float(coors.split(', ')[0]), float(coors.split(', ')[1])

                cur_profile = Profile.objects.get(user=request.user)
                cur_profile.latitude, cur_profile.longitude = lat, long
                cur_profile.save()

                return redirect(reverse('profile', args=[request.user.id]))
    else:
        u_form = EditUserInfo(instance=request.user)
        p_form = EditProfileInfo(instance=request.user.profile)
        coors_form = CoorsForm()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'coors_form': coors_form,
    }
    return render(request, 'core/edit_profile.html', context)


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


def like_post(request, pk):
    # TODO: check if post doesn't exist
    post = Post.objects.get(pk=pk)
    post.liked_by.add(request.user.profile)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def dislike_post(request, pk):
    # TODO: check if post doesn't exist
    post = Post.objects.get(pk=pk)
    post.liked_by.remove(request.user.profile)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

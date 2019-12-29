from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponseRedirect

from itertools import chain

from core.forms import UserRegistrationForm, EditUserInfo, EditProfileInfo, HobbyList, CoorsForm, MessageForm, \
    FollowButtonForm, CreatePostForm
from core.models import Profile, Hobby, Message, UserFeed


@login_required(login_url='login')
def home(request):
    if request.method == 'GET':
        following_profiles = request.user.profile.following.all()
        all_posts = UserFeed.objects.all()
        followers_feed = None
        like_post = FollowButtonForm()
        for profile in following_profiles:
            if followers_feed is not None:
                followers_feed = list(chain(followers_feed, all_posts.filter(user_profile_posted=profile.user.profile)))
            else:
                followers_feed = all_posts.filter(user_profile_posted=profile.user.profile)
        if followers_feed:
            followers_feed = sorted(followers_feed, key=lambda x: x.date_posted, reverse=True)
            followers_feed = Paginator(followers_feed, 20)
            page = request.GET.get('page')
            followers_feed = followers_feed.get_page(page)
        context = {
            'followers_feed': followers_feed,
            'like_post': like_post
        }
        return render(request, 'core/home.html', context)


def like_post(request, pk):
    post = UserFeed.objects.get(pk=pk)
    post.liked_by.add(request.user.profile)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def dislike_post(request, pk):
    post = UserFeed.objects.get(pk=pk)
    post.liked_by.remove(request.user.profile)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
    paginate_by = 50

    def get_queryset(self):
        return Profile.objects.filter(following__user=Profile.objects.get(pk=self.kwargs['pk']).user)


class ProfileFollowingView(ListView):
    template_name = 'core/profile_following_page.html'
    paginate_by = 50

    def get_queryset(self):
        return Profile.objects.get(pk=self.kwargs['pk']).following.all()


def profile(request, pk):
    try:
        profile_user = User.objects.get(id=pk)
    except User.DoesNotExist:
        raise Http404("Page doesn't exist")
    prof = Profile.objects.get(user=profile_user)

    if request.method == 'GET':
        create_post_form = CreatePostForm()
        hobbies = prof.hobby.all()

        followed_by = Profile.objects.filter(following__user=prof.user)

        follow_button_form = FollowButtonForm()

        user_feed = prof.userfeed_set.all()
        user_feed = Paginator(user_feed, 8)
        page = request.GET.get('page')
        user_feed = user_feed.get_page(page)
        context = {
            'hobbies': hobbies,
            'prof': prof,
            'create_post_form': create_post_form,
            'user_feed': user_feed,
            'follow_button_form': follow_button_form,
            'followed_by': followed_by
        }
        return render(request, 'core/profile.html', context)
    else:
        create_post_form = CreatePostForm(request.POST or None)
        follow_button_form = FollowButtonForm(request.POST or None)
        if follow_button_form.is_valid():
            following = follow_button_form.cleaned_data['follow']
            if following is True:
                cur_profile = request.user.profile
                prof_followed = prof.followed
                if prof.followed not in cur_profile.following.all():
                    cur_profile.following.add(prof_followed)
                else:
                    cur_profile.following.remove(prof_followed)
                return redirect('profile', pk=prof.pk)

        if create_post_form.is_valid():
            post_text = create_post_form.cleaned_data['text']
            UserFeed.objects.create(user_profile_posted=request.user.profile, text=post_text)
            return redirect('profile', pk=prof.pk)
        return redirect('profile', pk=prof.pk)


def edit_profile(request):
    if request.method == 'POST':
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
                logged_user_profile = Profile.objects.get(user=request.user)
                logged_user_profile.latitude = lat
                logged_user_profile.longitude = long
                logged_user_profile.save()
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
    all_msgs = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('date_sent')
    interlocutors = []
    for msg in all_msgs:
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

    all_msgs = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('date_sent')
    interlocutors = []
    for msg in all_msgs:
        if msg.sender == request.user:
            interlocutor = msg.receiver
        else:
            interlocutor = msg.sender

        if interlocutor not in interlocutors:
            interlocutors.append(interlocutor)

    msgs_by_user = all_msgs.filter(Q(sender=chat_user) | Q(receiver=chat_user)).order_by('date_sent')
    context = {'msg_form': msg_form, 'new_all_msgs': msgs_by_user, 'chat_user': chat_user,
               'chat_username': chat_username, 'interlocutors': interlocutors}
    return render(request, 'core/chat.html', context)

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from itertools import chain

from core.forms import UserRegistrationForm, EditUserInfo, EditProfileInfo, HobbyList, CoorsForm, CreatePostForm, \
    FollowButtonForm
from core.models import Profile, UserFeed, Followers


def home(request):
    if request.user.is_anonymous:
        return redirect('login')
    else:
        return render(request, 'core/home.html')


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


def profile(request, pk):
    prof = Profile.objects.get(id=pk)
    if request.method == 'GET':
        create_post_form = CreatePostForm()
        hobbies = prof.hobby.all()

        follow_button_form = FollowButtonForm()

        user_feed = prof.userfeed_set.all()
        user_feed = Paginator(user_feed, 6)
        page = request.GET.get('page')
        user_feed = user_feed.get_page(page)
        context = {
            'hobbies': hobbies,
            'prof': prof,
            'create_post_form': create_post_form,
            'user_feed': user_feed,
            'follow_button_form': follow_button_form
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
                    cur_profile.following.set(list(chain(cur_profile.following.all(), Followers.objects.filter(
                        user=prof.followed.user))))
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
                return redirect(reverse('edit_profile'))
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

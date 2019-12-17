from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from core.forms import UserRegistrationForm, EditUserInfo, EditProfileInfo, HobbyList, MessageForm
from core.models import Profile, Message
from django.http import Http404


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
    try:
        prof = Profile.objects.get(id=pk)
        hobbies = prof.hobby.all()
        context = {'hobbies': hobbies, 'prof': prof}
    except Profile.DoesNotExist:
        raise Http404("Page doesn't exist")

    return render(request, 'core/profile.html', context)


def edit_profile(request):
    if request.method == 'POST':
        u_form = EditUserInfo(request.POST, instance=request.user)
        p_form = EditProfileInfo(request.POST,
                                 request.FILES,
                                 instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect(reverse('home'))
    else:
        u_form = EditUserInfo(instance=request.user)
        p_form = EditProfileInfo(instance=request.user.profile)
    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'core/edit_profile.html', context)


def hobby_page(request):
    profiles = []
    if request.method == 'POST':
        hobbies_form = HobbyList(request.POST)
        if hobbies_form.is_valid():
            # return list of users with common hobbies
            hobbies = hobbies_form.cleaned_data['hobby']
            profiles = Profile.objects.all()
            for hobby in hobbies:
                profiles = profiles.filter(hobby__hobby=hobby)

            profiles2 = Profile.objects.filter(hobby__in=hobbies).distinct()

            context = {'hobbies_form': hobbies_form, 'profiles': profiles, 'profiles2': profiles2, }
            return render(request, 'core/hobby_page.html', context)
    else:
        hobbies_form = HobbyList()
    context = {'hobbies_form': hobbies_form, 'profiles': profiles}
    return render(request, 'core/hobby_page.html', context)


def message(request):
    if request.method == 'POST':
        msg_form = MessageForm(request.POST)
        if msg_form.is_valid():
            receiver = msg_form.cleaned_data['receiver']
            msg_text = msg_form.cleaned_data['msg_text']
            Message.objects.create(receiver=receiver, sender=request.user, msg_text=msg_text)
    else:
        msg_form = MessageForm()

    context = {'msg_form': msg_form}
    return render(request, 'core/message.html', context)

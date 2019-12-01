from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import UserRegistrationForm


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


def profile(request):
    # acc = User.objects.get(id=pk)
    # form = acc.all
    # form = UserRegistrationForm(request.GET)

    # context = {acc:'acc', form:'form'}
    return render(request, 'core/profile.html')
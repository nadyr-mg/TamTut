from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.models import Profile, Message, UserFeed


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=250, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


class EditProfileInfo(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image', 'hobby')


class EditUserInfo(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class HobbyList(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('hobby',)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('msg_text',)
        labels = {
            'msg_text': ''
        }
        widgets = {
            'msg_text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Напишите сообщение...', }),
        }


class CoorsForm(forms.Form):
    coors = forms.CharField(max_length=300, required=False, label='Координаты')


class FollowButtonForm(forms.Form):
    follow = forms.BooleanField(initial=True)


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = UserFeed
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

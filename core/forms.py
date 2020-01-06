from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.models import Profile, Message, Post, Hobby


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=250, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


def get_hobby_choices():
    choices = []
    for hobby in Hobby.objects.all():
        choices.append((hobby, hobby))
    choices = tuple(choices)
    return choices


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=300, required=False, label='Имя')
    last_name = forms.CharField(max_length=300, required=False, label='Фамилия')
    email = forms.EmailField(required=False, label='Email')
    image = forms.ImageField(allow_empty_file=True, required=False)
    hobby = forms.MultipleChoiceField(choices=[], required=False)
    coors = forms.CharField(max_length=300, required=False, label='Координаты')

    def set_hobbies_choices(self, hobbies):
        self.fields['hobby'].choices = [(hobby, hobby) for hobby in hobbies]


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


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

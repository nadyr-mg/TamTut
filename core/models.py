from PIL import Image
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import reverse


class Hobby(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hobby = models.ManyToManyField(Hobby)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    latitude = models.FloatField(null=True, default=None, blank=True)
    longitude = models.FloatField(null=True, default=None, blank=True)

    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    @staticmethod
    def filter_by_hobbies(hobbies):
        hobbies = hobbies
        matched_profiles = Profile.objects.all()
        for hobby in hobbies:
            matched_profiles = matched_profiles.filter(hobby__name=hobby)
        return matched_profiles

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Post(models.Model):
    author = models.ForeignKey(Profile, default=None, null=True, related_name='posts', on_delete=models.SET_NULL,
                               verbose_name="author's profile")
    text = models.CharField(max_length=500)
    date_posted = models.DateTimeField(auto_now_add=True)

    liked_by = models.ManyToManyField(Profile, related_name="liked")

    def like_post(self):
        return reverse('like_post', kwargs={
            'pk': self.pk
        })

    def dislike_post(self):
        return reverse('dislike_post', kwargs={
            'pk': self.pk
        })

    def get_authors_name(self):
        return self.author.user.username

    @property
    def likes_amount(self):
        return self.liked_by.count()

    def __str__(self):
        return f'By {self.author.user.username} - {self.text[:10]}'


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_by", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_by", on_delete=models.CASCADE)
    msg_text = models.TextField(max_length=500, blank=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def user_msgs(user):
        return Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('date_sent')

    def __str__(self):
        return self.msg_text

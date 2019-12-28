from PIL import Image
from django.db import models
from django.contrib.auth.models import User


class Hobby(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Followers(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hobby = models.ManyToManyField(Hobby)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    latitude = models.FloatField(null=True, default=None, blank=True)
    longitude = models.FloatField(null=True, default=None, blank=True)

    following = models.ManyToManyField(Followers, related_name="following")
    followed = models.OneToOneField(Followers, related_name="followed", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} Profile'

    @staticmethod
    def filter_by_hobbies(hobbies):
        hobbies = hobbies
        matched_profiles = Profile.objects.all()
        for hobby in hobbies:
            matched_profiles = matched_profiles.filter(hobby__hobby=hobby)
        return matched_profiles

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class UserFeed(models.Model):
    user_profile_posted = models.ForeignKey(Profile, default=None, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'By {self.user_profile_posted.user.username} - {self.text[:10]}'


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.CASCADE)
    msg_text = models.TextField(max_length=500, blank=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.msg_text

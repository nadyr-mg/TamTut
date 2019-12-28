from PIL import Image
from django.db import models
from django.contrib.auth.models import User


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


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.CASCADE)
    msg_text = models.TextField(max_length=500, blank=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.msg_text

from PIL import Image
from django.db import models
from django.contrib.auth.models import User


class Hobby(models.Model):
    hobby = models.CharField(max_length=100)

    def __str__(self):
        return self.hobby


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

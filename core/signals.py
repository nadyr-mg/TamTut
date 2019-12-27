from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Followers


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        followed = Followers.objects.create(user=instance)
        Profile.objects.create(user=instance, followed=followed)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

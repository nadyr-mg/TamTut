from django.contrib import admin
from core.models import Profile, Hobby, Message, Post, GroupChat

admin.site.register(Profile)
admin.site.register(Hobby)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(GroupChat)

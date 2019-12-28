from django.contrib import admin
from core.models import Profile, Hobby, Message, UserFeed, Followers

admin.site.register(Profile)
admin.site.register(Hobby)
admin.site.register(UserFeed)
admin.site.register(Followers)
admin.site.register(Message)

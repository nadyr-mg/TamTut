from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='core/logout.html'), name='logout'),

    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile/<int:pk>/followers/', views.ProfileFollowersView.as_view(), name='profile_followers'),
    path('profile/<int:pk>/following/', views.ProfileFollowingView.as_view(), name='profile_following'),

    path('profile/<int:pk>/follow/', views.follow_target_profile, name='follow'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('chat/', views.chat, name='chat'),
    path('chat/<str:chat_username>/', views.chat_by_user, name='chat_by_user'),

    path('map/', views.map_view, name='map_page'),

    path('likepost/<int:pk>/', views.like_post, name='like_post'),
    path('dislikepost/<int:pk>/', views.dislike_post, name='dislike_post'),
]


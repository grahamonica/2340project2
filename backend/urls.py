from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home Pages
    path('', views.spotify_presentation, name='home'),  # Main home page with user data
    path('spotify-social/', views.spotify_social, name='spotify_social'),  # Social page for public Wrapped
    path('post/', views.post_spotify_presentation, name='post_spotify_presentation'),


    # Contact and Misc
    path('contact/', views.contact, name='contact'),
    path('thank-you/', views.thank_you, name='thank_you'),

    # Account Management
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('account_info/', views.account_info, name='account_info'),
    path('delete_account/', views.delete_account, name='delete_account'),

    # Spotify Authentication
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('spotify/check-auth/', views.check_spotify_auth, name='check_spotify_auth'),


    # Liking and Viewing Posts
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('liked-posts/', views.liked_posts, name='liked_posts'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),

    path('duo_wrapped/<int:post_id>/', views.duo_wrapped, name='duo_wrapped'),
    path('my-duo-wraps/', views.my_duo_wraps, name='my_duo_wraps'),
]

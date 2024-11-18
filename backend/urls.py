#urls.py
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views  # <-- Add this line

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.spotify_presentation, name='home'),  # New home page
    path('spotify-social/', views.spotify_social, name='spotify_social'),  # Old home page renamed
    path('contact/', views.contact, name='contact'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),  # Use custom_logout
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
]
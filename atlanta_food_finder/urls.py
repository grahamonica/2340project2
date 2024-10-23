from django.contrib import admin
from django.urls import path

from food_finder import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("search/", views.search_restaurants, name="search_restaurants"),
]

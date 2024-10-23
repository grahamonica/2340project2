from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from food_finder import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("check-user/", views.check_user_exists, name="check_user_exists"),
    path("register-or-login/", views.register_or_login, name="register_or_login"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.logout, name="logout"),
    path("search_restaurants/", views.search_restaurants, name="search_restaurants"),
    path("get_location/", views.get_location, name="get_location"),
    path("toggle_favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.fetch_favorites, name="fetch_favorites"),
    path("user_reviews/", views.fetch_user_reviews, name="fetch_user_reviews"),
    path("add_review/", views.add_review, name="add_review"),
    path("remove_review/<int:review_id>/", views.remove_review, name="remove_review"),
]

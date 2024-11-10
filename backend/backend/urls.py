from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", views.register_user, name="register"),
    path('api/login/', views.login_user, name='login'),
    path("api/logout/", views.logout_user, name="logout"),
    # Spotify Wrapped endpoints
    path("api/wrapped/", views.get_wrapped_posts, name="get_wrapped_posts"),
    path("api/wrapped/create/", views.create_wrapped_post, name="create_wrapped_post"),
    path(
        "api/wrapped/toggle-public/<int:post_id>/",
        views.toggle_public,
        name="toggle_public",
    ),
    # Spotify OAuth endpoints
    path("api/spotify/login/", views.spotify_login, name="spotify_login"),
    path("api/spotify/callback/", views.spotify_callback, name="spotify_callback"),
]

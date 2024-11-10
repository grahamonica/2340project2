from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from .models import SpotifyWrapped
from .serializers import SpotifyWrappedSerializer, UserSerializer

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(
    client_id=settings.SPOTIPY_CLIENT_ID,
    client_secret=settings.SPOTIPY_CLIENT_SECRET,
    redirect_uri=settings.SPOTIPY_REDIRECT_URI,
    scope="user-top-read",
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User created successfully",
                "username": user.username,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "username": user.username,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
        )

    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out"})
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_wrapped_posts(request):
    posts = SpotifyWrapped.objects.filter(is_public=True)
    serializer = SpotifyWrappedSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_wrapped_post(request):
    serializer = SpotifyWrappedSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_public(request, post_id):
    try:
        post = SpotifyWrapped.objects.get(id=post_id, user=request.user)
        post.is_public = not post.is_public
        post.save()
        return Response({"is_public": post.is_public})
    except SpotifyWrapped.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spotify_login(request):
    auth_url = sp_oauth.get_authorize_url()
    return Response({"auth_url": auth_url})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return Response(
            {"error": "No authorization code provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token_info = sp_oauth.get_access_token(code)
        sp = Spotify(auth=token_info["access_token"])

        # Fetch user's top tracks and artists
        top_tracks = sp.current_user_top_tracks(limit=5)["items"]
        top_artists = sp.current_user_top_artists(limit=5)["items"]

        # Format the data
        top_tracks_data = [
            {"name": track["name"], "artist": track["artists"][0]["name"]}
            for track in top_tracks
        ]
        top_artists_data = [{"name": artist["name"]} for artist in top_artists]

        # Save or update the user's Spotify Wrapped data
        wrapped, _ = SpotifyWrapped.objects.update_or_create(
            user=request.user,
            defaults={
                "top_tracks": top_tracks_data,
                "top_artists": top_artists_data,
                "is_public": True,
            },
        )

        serializer = SpotifyWrappedSerializer(wrapped)
        return Response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

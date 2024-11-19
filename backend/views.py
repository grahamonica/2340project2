import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from .models import SpotifyWrapped
from .forms import CustomUserCreationForm
from django.contrib.auth import logout as django_logout
from spotipy import SpotifyException
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse

@login_required
def toggle_like(request, post_id):
    """
    Toggle the like status of a post for the current user.
    """
    post = get_object_or_404(SpotifyWrapped, id=post_id, is_public=True)
    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        liked = False
    else:
        post.liked_by.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.liked_by.count()})


@login_required
def liked_posts(request):
    """
    Display posts liked by the current user.
    """
    posts = SpotifyWrapped.objects.filter(liked_by=request.user, is_public=True)
    return render(request, 'spotify_social.html', {'public_wrapped_posts': posts, 'filter': 'liked'})


@login_required
def spotify_presentation(request):
    """
    View for the new home page. Presents the user's Spotify data, including top tracks and top artists.
    """
    user_taste = None
    try:
        # Fetch the user's latest Spotify Wrapped data
        wrapped = SpotifyWrapped.objects.filter(user=request.user).latest('id')
        user_taste = {
            'top_tracks': wrapped.top_tracks,
            'top_artists': wrapped.top_artists
        }
    except SpotifyWrapped.DoesNotExist:
        # If no data exists for the user, set user_taste to None
        user_taste = None

    return render(request, 'home.html', {'user_taste': user_taste})

@login_required
def spotify_social(request):
    """
    View for the "Spotify Social" page. Displays all public Spotify Wrapped posts.
    """
    # Fetch all public Spotify Wrapped posts
    public_wrapped_posts = SpotifyWrapped.objects.filter(is_public=True)
    return render(request, 'spotify_social.html', {'public_wrapped_posts': public_wrapped_posts})

@login_required
def spotify_login(request):
    """
    Initiates Spotify login and authentication process.
    """
    # Create a unique cache path for each user
    cache_path = f".cache-{request.user.id}"
    
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",
        cache_path=cache_path,
        show_dialog=True
    )
    
    # Clear any existing token
    if os.path.exists(cache_path):
        os.remove(cache_path)
    
    # Generate authorization URL
    auth_url = sp_oauth.get_authorize_url()
    request.session['cache_path'] = cache_path
    
    return redirect(auth_url)

@login_required
def spotify_callback(request):
    """
    Handles Spotify's OAuth callback and fetches the user's data.
    """
    code = request.GET.get('code')
    cache_path = request.session.get('cache_path')
    
    if not code:
        messages.error(request, "Authorization code not found.")
        return redirect('home')
    
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",
        cache_path=cache_path
    )
    
    try:
        # Get token info
        token_info = sp_oauth.get_access_token(code)
        if not token_info:
            raise Exception("Failed to get access token")
            
        sp = Spotify(auth=token_info['access_token'])
        
        # Fetch user data
        user_profile = sp.current_user()
        print(f"User Profile: {user_profile}")
        
        # Fetch top tracks and artists
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term').get('items', [])
        top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term').get('items', [])
        
        # Format data
        formatted_tracks = [
            {'name': track['name'], 'artist': track['artists'][0]['name']}
            for track in top_tracks
        ] or "No recently listened to tracks."
        
        formatted_artists = [
            {'name': artist['name']}
            for artist in top_artists
        ] or "No top artists found."

        # Save data
        SpotifyWrapped.objects.create(
            user=request.user,
            top_tracks=formatted_tracks,
            top_artists=formatted_artists,
            is_public=True
        )
        
        messages.success(request, "Your Spotify Wrapped has been posted successfully!")
    except Exception as e:
        print(f"Error in spotify_callback: {e}")
        messages.error(request, f"There was an error accessing your Spotify data: {str(e)}")
    
    # Clean up cache
    if cache_path and os.path.exists(cache_path):
        os.remove(cache_path)
    
    return redirect('home')

def signup(request):
    """
    Handles user sign-up process.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})

def custom_logout(request):
    """
    Logs the user out and clears Spotify token info.
    """
    django_logout(request)
    request.session.pop('token_info', None)
    return redirect("https://accounts.spotify.com/en/logout")

def contact(request):
    """
    Handles contact form submissions.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"New message from {name} ({email}): {message}")
        return render(request, 'thank_you.html')
    
    return render(request, 'contact.html')

def thank_you(request):
    """
    Displays a thank-you page after form submissions.
    """
    return render(request, 'thank_you.html')
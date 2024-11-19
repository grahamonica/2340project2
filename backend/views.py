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
    Toggle between showing liked posts and all public posts.
    """
    filter_liked = request.GET.get('filter_liked', 'true').lower() == 'true'

    if filter_liked:
        posts = SpotifyWrapped.objects.filter(liked_by=request.user, is_public=True)
    else:
        posts = SpotifyWrapped.objects.filter(is_public=True)

    return render(
        request,
        'spotify_social.html',
        {
            'public_wrapped_posts': posts,
            'filter_liked': filter_liked,  # Pass the current filter status
        },
    )

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
    Handles Spotify's OAuth callback and posts the home page slideshow presentation.
    """
    code = request.GET.get('code')
    cache_path = request.session.get('cache_path', None)

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",
        cache_path=cache_path
    )

    try:
        # Get access token
        token_info = sp_oauth.get_access_token(code)
        sp = Spotify(auth=token_info['access_token'])

        # Fetch top tracks, artists, and genres
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')['items']
        top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')['items']
        top_genres = {genre for artist in top_artists for genre in artist.get('genres', [])}

        # Construct the slideshow HTML (reuse the home page format)
        slideshow_html = f"""
        <div class="slideshow-container">
            <div class="slide">
                <h2>Your Spotify Wrapped</h2>
            </div>
            <div class="slide">
                <h3>Top Tracks:</h3>
                <ul>
                    {''.join(f'<li>{track["name"]} by {track["artists"][0]["name"]}</li>' for track in top_tracks)}
                </ul>
            </div>
            <div class="slide">
                <h3>Top Artists:</h3>
                <ul>
                    {''.join(f'<li>{artist["name"]}</li>' for artist in top_artists)}
                </ul>
            </div>
            <div class="slide">
                <h3>Top Genres:</h3>
                <ul>
                    {''.join(f'<li>{genre}</li>' for genre in top_genres)}
                </ul>
            </div>
        </div>
        <div class="controls">
            <button class="prev" onclick="changeSlide(-1)">&#10094;</button>
            <button class="next" onclick="changeSlide(1)">&#10095;</button>
        </div>
        """

        # Save the slideshow as the presentation
        SpotifyWrapped.objects.create(
            user=request.user,
            presentation=slideshow_html,
            is_public=True
        )

        messages.success(request, "Your Spotify Wrapped slideshow has been posted!")
    except Exception as e:
        print(f"Error during Spotify callback: {e}")
        messages.error(request, "Failed to post your Spotify Wrapped slideshow.")

    # Redirect to Spotify Social page
    return redirect('spotify_social')


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
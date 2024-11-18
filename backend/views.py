# views.py
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from .models import SpotifyWrapped
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from spotipy import SpotifyException


@login_required
def spotify_login(request):
    # Create a unique cache path for each user
    cache_path = f".cache-{request.user.id}"
    
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",  # Added user-read-email scope
        cache_path=cache_path,
        show_dialog=True  # Force showing the Spotify auth dialog
    )
    
    # Clear any existing token
    if os.path.exists(cache_path):
        os.remove(cache_path)
    
    # Generate authorization URL with explicit scope parameter
    auth_url = sp_oauth.get_authorize_url("user-top-read user-read-private user-read-email")
    
    # Store the cache path in session for callback
    request.session['cache_path'] = cache_path
    
    return redirect(auth_url)

@login_required
def spotify_callback(request):
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
            
        # Create Spotify client
        sp = Spotify(auth=token_info['access_token'])
        
        # First test with a basic profile request
        user_profile = sp.current_user()
        print("Successfully retrieved user profile:", user_profile['id'])
        
        # Then try to get top tracks
        try:
            top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')
            print("Successfully retrieved top tracks")
        except Exception as e:
            print(f"Error getting top tracks: {e}")
            raise
            
        try:
            top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')
            print("Successfully retrieved top artists")
        except Exception as e:
            print(f"Error getting top artists: {e}")
            raise
        
        # Format the data
        formatted_tracks = [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'spotify_id': track['id']
            }
            for track in top_tracks['items']
        ]
        
        formatted_artists = [
            {'name': artist['name']}
            for artist in top_artists['items']
        ]
        
        # Save or update the user's Spotify Wrapped
        wrapped, created = SpotifyWrapped.objects.update_or_create(
            user=request.user,
            defaults={
                'top_tracks': formatted_tracks,
                'top_artists': formatted_artists,
                'is_public': True
            }
        )
        
        messages.success(request, "Your Spotify Wrapped has been posted successfully!")
        
    except Exception as e:
        print(f"Error in spotify_callback: {e}")
        messages.error(request, f"There was an error accessing your Spotify data: {str(e)}")
    
    # Clean up cache file
    if cache_path and os.path.exists(cache_path):
        os.remove(cache_path)
    
    return redirect('home')

@login_required
def home(request):
    # Fetch all public Spotify Wrapped posts
    public_wrapped_posts = SpotifyWrapped.objects.filter(is_public=True)
    return render(request, 'home.html', {'public_wrapped_posts': public_wrapped_posts})

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create the new user
            login(request, user)  # Log the user in automatically after signup
            messages.success(request, "Account created successfully!")
            return redirect("home")  # Redirect to the home page
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


from django.contrib.auth import logout as django_logout

def custom_logout(request):
    logout(request)  # Logs out from Django
    request.session.pop('token_info', None)  # Clears Spotify token info if stored
    return redirect("https://accounts.spotify.com/en/logout")  # Optionally redirect to Spotify logout page


# Contact view for contacting developers
def contact(request):
    if request.method == 'POST':
        # Print contact form data to the terminal
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"New message from {name} ({email}): {message}")

        return render(request, 'thank_you.html')
    
    return render(request, 'contact.html')

def thank_you(request):
    return render(request, 'thank_you.html')

def custom_logout(request):
    logout(request)  # Logs out from Django
    request.session.pop('token_info', None)  # Clears Spotify token info if stored
    return redirect("http://127.0.0.1:8000/accounts/login/?next=/")  # Optionally redirect to Spotify logout page

def slideshow_view(request):
    return render(request, 'my_app/slideshow.html')
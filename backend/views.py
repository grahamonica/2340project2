# views.py

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


# Set up Spotify OAuth with the necessary scopes
sp_oauth = SpotifyOAuth(
    client_id=settings.SPOTIPY_CLIENT_ID,
    client_secret=settings.SPOTIPY_CLIENT_SECRET,
    redirect_uri=settings.SPOTIPY_REDIRECT_URI,
    scope="user-top-read",
    cache_path=None  # This forces Spotify to ask for login every time
)

def spotify_login(request):
    # Clear any existing token data
    request.session.pop("token_info", None)

    # Redirect to Spotify's authorization page
    auth_url = sp_oauth.get_authorize_url()
    print("Spotify Authorization URL:", auth_url)  # Debugging
    return redirect(auth_url)


def spotify_callback(request):
    code = request.GET.get('code')
    
    if code:
        try:
            # Get the access token
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
            sp = Spotify(auth=access_token)

            # Fetch top tracks and artists
            top_tracks_response = sp.current_user_top_tracks(limit=5)
            top_artists_response = sp.current_user_top_artists(limit=5)

            # Debug: Print raw API responses
            print("Raw Top Tracks Response:", top_tracks_response)
            print("Raw Top Artists Response:", top_artists_response)

            # Extract and format data
            top_tracks = top_tracks_response.get('items', [])
            top_artists = top_artists_response.get('items', [])

            top_tracks_data = [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks]
            top_artists_data = [{'name': artist['name']} for artist in top_artists]

            # Debug: Log formatted data
            print("Formatted Top Tracks:", top_tracks_data)
            print("Formatted Top Artists:", top_artists_data)

            # Save data to database
            SpotifyWrapped.objects.update_or_create(
                user=request.user,
                defaults={'top_tracks': top_tracks_data, 'top_artists': top_artists_data, 'is_public': True}
            )

            messages.success(request, "Your Spotify Wrapped has been posted successfully!")
            return redirect('home')
        except Exception as e:
            print("Error during Spotify callback:", e)
            messages.error(request, "There was an issue connecting to Spotify.")
            return redirect('home')
    else:
        messages.error(request, "No authorization code provided.")
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

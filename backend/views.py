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
    scope="user-top-read"
)

def spotify_login(request):
    # Redirect to Spotify's authorization page
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    # Retrieve the authorization code from the callback URL
    code = request.GET.get('code')
    
    if code:
        try:
            # Get the access token using the code
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
            
            # Initialize Spotify client with the access token
            sp = Spotify(auth=access_token)

            # Fetch user's top tracks and artists
            top_tracks = sp.current_user_top_tracks(limit=5)['items']
            top_artists = sp.current_user_top_artists(limit=5)['items']

            # Format the track and artist data for storage
            top_tracks_data = [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks]
            top_artists_data = [{'name': artist['name']} for artist in top_artists]

            # Save data in the SpotifyWrapped model associated with the logged-in user
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

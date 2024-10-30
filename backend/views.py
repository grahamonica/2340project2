# views.py
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect, render
from .models import SpotifyWrapped
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm  # Import the custom form


sp_oauth = SpotifyOAuth(
    client_id=settings.SPOTIPY_CLIENT_ID,
    client_secret=settings.SPOTIPY_CLIENT_SECRET,
    redirect_uri=settings.SPOTIPY_REDIRECT_URI,
    scope="user-top-read"
)

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

    
def spotify_login(request):
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        return render(request, 'error.html', {'message': 'Authentication failed.'})

    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Fetch user's top tracks and artists
    top_tracks = sp.current_user_top_tracks(limit=10)['items']
    top_artists = sp.current_user_top_artists(limit=10)['items']

    # Format data to store in JSONField
    top_tracks_data = [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks]
    top_artists_data = [{'name': artist['name']} for artist in top_artists]

    # Save data in the SpotifyWrapped model
    wrapped, created = SpotifyWrapped.objects.update_or_create(
        user=request.user,
        defaults={'top_tracks': top_tracks_data, 'top_artists': top_artists_data, 'is_public': False}
    )

    # Redirect to home page
    return redirect('home')

@login_required
def home(request):
    # Fetch all public Spotify Wrapped posts
    public_wrapped_posts = SpotifyWrapped.objects.filter(is_public=True)
    return render(request, 'home.html', {'public_wrapped_posts': public_wrapped_posts})
# backend/views.py

from django.shortcuts import render
from django.http import HttpResponse

def contact(request):
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Print the message to the terminal
        print(f"New message from {name} ({email}): {message}")

        return render(request, 'thank_you.html')  # Redirect to a thank you page after submission
    
    return render(request, 'contact.html')

def thank_you(request):
    return render(request, 'thank_you.html')  # Render a thank you page
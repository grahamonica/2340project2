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
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from decouple import config
from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def check_spotify_auth(request):
    """
    Checks if the user's Spotify tokens are valid.
    """
    try:
        # Attempt to fetch a valid access token
        get_valid_spotify_token(request.user)
        return JsonResponse({'status': 'ok'})  # Spotify tokens are valid
    except ValueError:
        return JsonResponse({'status': 'unauthorized'}, status=401)  # Spotify tokens are missing or invalid



def send_email(name, email, message):
    try:
        sg_message = Mail(
            from_email='monicagraham40@gmail.com',  # Your verified sender email
            to_emails='monicagraham40@gmail.com',  # Replace with recipient email
            subject='Contact Form Submission',
            html_content=f"""
                <h1>New Contact Form Submission</h1>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong><br>{message}</p>
            """
        )
        sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
        response = sg.send(sg_message)
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Log form data to the terminal
        print(f"New Contact Form Submission:\nName: {name}\nEmail: {email}\nMessage: {message}")

        # Send email using SendGrid
        send_email(name, email, message)

        # Redirect to thank you page
        return HttpResponseRedirect(reverse('thank_you'))
    
    return render(request, 'contact.html')

def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # Delete user and related data
        return redirect('home')  # Redirect to the home page

from django.contrib import messages

@login_required
def account_info(request):
    """
    Displays the user's past posts and provides an option to delete them.
    """
    # Fetch all posts by the logged-in user
    user_posts = SpotifyWrapped.objects.filter(user=request.user)

    return render(request, 'account_info.html', {'user_posts': user_posts})

@login_required
def delete_post(request, post_id):
    """
    Deletes a specific post made by the user.
    """
    post = get_object_or_404(SpotifyWrapped, id=post_id, user=request.user)
    post.delete()
    messages.success(request, "Post deleted successfully!")
    return redirect('account_info')

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
    Fetches and displays the user's Spotify data.
    Saves the presentation in the SpotifyWrapped model.
    """
    try:
        access_token = get_valid_spotify_token(request.user)
        sp = Spotify(auth=access_token)

        # Fetch top tracks and artists
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')['items']
        top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')['items']

        # Generate user taste dictionary
        user_taste = {
            'top_tracks': [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks],
            'top_artists': [{'name': artist['name']} for artist in top_artists],
        }

        # Use `home.html` for generating the presentation
        presentation_html = render_to_string(
            'home.html',  # Assuming this template exists and is suitable
            {'user_taste': user_taste}
        )

        # Save or update the SpotifyWrapped instance for the user
        SpotifyWrapped.objects.update_or_create(
            user=request.user,
            defaults={
                'top_tracks': user_taste['top_tracks'],
                'top_artists': user_taste['top_artists'],
                'presentation': presentation_html,
                'is_public': False,  # Default to private until explicitly posted
            },
        )
    except Exception as e:
        print(f"Error fetching Spotify data: {e}")
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
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",
        show_dialog=True,
    )

    # Generate authorization URL
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from spotipy.oauth2 import SpotifyOAuth

@login_required
def spotify_callback(request):
    """
    Handles Spotify's OAuth callback and saves the user's Spotify tokens.
    """
    code = request.GET.get('code')

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",
    )

    try:
        # Get access and refresh tokens
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        # Make expires_at timezone-aware
        expires_at = make_aware(datetime.now() + timedelta(seconds=token_info['expires_in']))

        # Save tokens in the database
        SpotifyAuth.objects.update_or_create(
            user=request.user,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at,
                'scope': token_info.get('scope', ''),
            },
        )

        messages.success(request, "Spotify account linked successfully!")
    except Exception as e:
        print(f"Error during Spotify callback: {e}")
        messages.error(request, "Failed to connect Spotify account.")

    # Redirect to the home page or desired location
    return redirect('home')

def signup(request):
    """
    Handles user sign-up process and redirects to Spotify login.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately

            # Redirect to Spotify login after account creation
            messages.success(request, "Account created successfully! Please link your Spotify account.")
            return redirect("spotify_login")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})

def custom_logout(request):
    """
    Logs the user out and clears Spotify token info.
    """
    # Clear Spotify tokens from the database
    try:
        SpotifyAuth.objects.filter(user=request.user).delete()
    except Exception as e:
        print(f"Error clearing Spotify tokens: {e}")

    # Log out from Django session
    django_logout(request)

    # Redirect to the site's login page
    return redirect("login")

def thank_you(request):
    """
    Displays a thank-you page after form submissions.
    """
    return render(request, 'thank_you.html')


from spotipy.oauth2 import SpotifyOAuth
from django.utils.timezone import now
from .models import SpotifyAuth

def get_valid_spotify_token(user):
    """
    Returns a valid Spotify access token, refreshing if necessary.
    """
    try:
        spotify_auth = SpotifyAuth.objects.get(user=user)
        if now() >= spotify_auth.expires_at:
            # Token expired, refresh it
            sp_oauth = SpotifyOAuth(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIPY_REDIRECT_URI,
            )
            token_info = sp_oauth.refresh_access_token(spotify_auth.refresh_token)
            spotify_auth.access_token = token_info['access_token']
            spotify_auth.expires_at = now() + timedelta(seconds=token_info['expires_in'])
            spotify_auth.save()
        return spotify_auth.access_token
    except SpotifyAuth.DoesNotExist:
        raise ValueError("Spotify tokens not found. User needs to log in.")

@login_required
def post_spotify_presentation(request):
    """
    Posts the user's Spotify Wrapped presentation to Spotify Social.
    """
    try:
        # Attempt to get a valid token without reauthorizing
        try:
            access_token = get_valid_spotify_token(request.user)
            sp = Spotify(auth=access_token)

            # Fetch top tracks and artists
            top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')['items']
            top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')['items']

            user_taste = {
                'top_tracks': [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks],
                'top_artists': [{'name': artist['name']} for artist in top_artists],
            }

            # Convert the presentation into HTML format for storage
            presentation_html = render_to_string(
                'home.html',
                {'user_taste': user_taste, 'is_posting': True},
                request=request
            )

            # Save the presentation to the database
            SpotifyWrapped.objects.create(user=request.user, presentation=presentation_html, is_public=True)
            messages.success(request, "Your Spotify Wrapped presentation has been posted!")
        except ValueError:
            # If no valid token is available, show an error
            messages.error(request, "Your Spotify session has expired. Please reconnect your account.")
            return redirect('spotify_login')

    except Exception as e:
        print(f"Error posting Spotify Wrapped: {e}")
        messages.error(request, "Failed to post Spotify Wrapped.")

    return redirect('spotify_social')

@login_required
def delete_post(request, post_id):
    """
    Deletes a specific post created by the logged-in user.
    """
    try:
        # Get the post associated with the logged-in user
        post = get_object_or_404(SpotifyWrapped, id=post_id, user=request.user)

        # Delete the post
        post.delete()

        # Display a success message and redirect
        messages.success(request, "Your post has been deleted successfully!")
    except Exception as e:
        print(f"Error deleting post: {e}")
        messages.error(request, "An error occurred while trying to delete the post.")

    return redirect('account_info')

from collections import Counter

@login_required
def duo_wrapped(request, post_id):
    """
    Generates a Duo Wrapped comparison between the logged-in user and another user's post.
    """
    try:
        # Get the logged-in user's Wrapped
        user_wrapped = SpotifyWrapped.objects.get(user=request.user)
        if not user_wrapped.top_artists or not user_wrapped.top_tracks:
            messages.error(request, "Your Spotify Wrapped data is incomplete. Please regenerate your Wrapped.")
            return redirect('spotify_social')

        # Get the selected user's Wrapped post
        other_wrapped = get_object_or_404(SpotifyWrapped, id=post_id)
        if not other_wrapped.top_artists or not other_wrapped.top_tracks:
            messages.error(request, "The selected user's Spotify Wrapped data is incomplete.")
            return redirect('spotify_social')

        # Extract data safely
        user_artists = [artist.get('name') for artist in user_wrapped.top_artists]
        other_artists = [artist.get('name') for artist in other_wrapped.top_artists]

        user_tracks = [track.get('name') for track in user_wrapped.top_tracks]
        other_tracks = [track.get('name') for track in other_wrapped.top_tracks]

        # Compare overlaps
        shared_artists = set(user_artists) & set(other_artists)
        shared_tracks = set(user_tracks) & set(other_tracks)

        # Prepare data for the template
        context = {
            'user_wrapped': user_wrapped,
            'other_wrapped': other_wrapped,
            'shared_artists': shared_artists,
            'shared_tracks': shared_tracks,
            'unique_user_artists': set(user_artists) - shared_artists,
            'unique_other_artists': set(other_artists) - shared_artists,
            'unique_user_tracks': set(user_tracks) - shared_tracks,
            'unique_other_tracks': set(other_tracks) - shared_tracks,
        }

        return render(request, 'duo_wrapped.html', context)

    except SpotifyWrapped.DoesNotExist:
        messages.error(request, "You must have a Spotify Wrapped to view a Duo Wrapped.")
        return redirect('spotify_social')
    except Exception as e:
        print(f"Error in Duo Wrapped: {e}")
        messages.error(request, "An error occurred while generating Duo Wrapped.")
        return redirect('spotify_social')

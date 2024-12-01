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
from .models import DuoWrap

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
    """
    print(f"Accessing spotify_presentation for user: {request.user.username}")  # Debug print
    
    try:
        # Check if user has any wrapped presentations
        wrapped = SpotifyWrapped.objects.filter(user=request.user).order_by('-created_at').first()
        print(f"Found existing wrapped: {bool(wrapped)}")  # Debug print
        if wrapped:
            print(f"Wrapped data - tracks: {bool(wrapped.top_tracks)}, artists: {bool(wrapped.top_artists)}")  # Debug print

        user_taste = None
        if wrapped and wrapped.top_tracks and wrapped.top_artists:
            user_taste = {
                'top_tracks': wrapped.top_tracks,
                'top_artists': wrapped.top_artists
            }
            print("Using existing wrapped data")  # Debug print
        else:
            print("Attempting to fetch new data from Spotify")  # Debug print
            access_token = get_valid_spotify_token(request.user)
            sp = Spotify(auth=access_token)

            top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')['items']
            top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')['items']

            user_taste = {
                'top_tracks': [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks],
                'top_artists': [{'name': artist['name']} for artist in top_artists],
            }
            print("Successfully fetched new data")  # Debug print

        return render(request, 'home.html', {'user_taste': user_taste})

    except Exception as e:
        print(f"Error in spotify_presentation: {e}")  # Debug print
        return render(request, 'home.html', {'user_taste': None})


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
    try:
        print("Starting spotify_callback")  # Debug print
        code = request.GET.get('code')
        print(f"Got authorization code: {bool(code)}")  # Debug print

        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIPY_REDIRECT_URI,
            scope="user-top-read user-read-private user-read-email",
        )

        try:
            # Get access and refresh tokens
            print("Getting access token")  # Debug print
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
            print("Successfully got access token")  # Debug print

            # Save tokens in database
            print("Saving tokens to database")  # Debug print
            auth_obj, created = SpotifyAuth.objects.update_or_create(
                user=request.user,
                defaults={
                    'access_token': access_token,
                    'refresh_token': token_info['refresh_token'],
                    'expires_at': make_aware(datetime.now() + timedelta(seconds=token_info['expires_in'])),
                    'scope': token_info.get('scope', ''),
                }
            )
            print(f"Tokens saved, auth object created: {created}")  # Debug print

            # Initialize Spotify client
            print("Initializing Spotify client")  # Debug print
            sp = Spotify(auth=access_token)

            # Fetch data
            print("Fetching top tracks and artists")  # Debug print
            top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')['items']
            top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')['items']
            print(f"Fetched {len(top_tracks)} tracks and {len(top_artists)} artists")  # Debug print

            # Process data
            user_taste = {
                'top_tracks': [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks],
                'top_artists': [{'name': artist['name']} for artist in top_artists],
            }
            print("Processed user taste data")  # Debug print

            # Create presentation
            print("Creating presentation HTML")  # Debug print
            presentation_html = render_to_string(
                'home.html',
                {'user_taste': user_taste},
                request=request
            )

            # Save wrapped
            print("Saving Wrapped presentation")  # Debug print
            wrapped = SpotifyWrapped.objects.create(
                user=request.user,
                top_tracks=user_taste['top_tracks'],
                top_artists=user_taste['top_artists'],
                presentation=presentation_html,
                is_public=False
            )
            print(f"Successfully created Wrapped with ID: {wrapped.id}")  # Debug print

            messages.success(request, "Spotify account linked successfully! Your Wrapped has been generated.")
        except Exception as e:
            print(f"Error during token exchange and data fetching: {e}")
            raise

    except Exception as e:
        print(f"Error during Spotify callback: {e}")
        messages.error(request, "Failed to connect Spotify account.")

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
    try:
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

            # Create the slideshow HTML structure explicitly
            slideshow_html = render_to_string(
                'presentation_snippet.html',  # Create this new template
                {
                    'user_taste': user_taste,
                    'user': request.user
                },
                request=request
            )

            # Save to database
            SpotifyWrapped.objects.create(
                user=request.user,
                presentation=slideshow_html,
                is_public=True,
                top_tracks=user_taste['top_tracks'],
                top_artists=user_taste['top_artists']
            )
            messages.success(request, "Your Spotify Wrapped presentation has been posted!")
            
        except ValueError:
            messages.error(request, "Your Spotify session has expired. Please reconnect your account.")
            return redirect('spotify_login')

    except Exception as e:
        print(f"Error posting Spotify Wrapped: {e}")
        messages.error(request, "Failed to post Spotify Wrapped.")

    return redirect('spotify_social')

@login_required
def duo_wrapped(request, post_id):
    try:
        # Get both users' wrapped data
        user_wrapped = SpotifyWrapped.objects.filter(user=request.user).latest('created_at')
        other_wrapped = get_object_or_404(SpotifyWrapped, id=post_id)
        
        # Create or update DuoWrap with both users' data
        duo_wrap, created = DuoWrap.objects.update_or_create(
            user=request.user,
            compared_user=other_wrapped.user,
            defaults={
                'user_artists': user_wrapped.top_artists,
                'user_tracks': user_wrapped.top_tracks,
                'compared_artists': other_wrapped.top_artists,
                'compared_tracks': other_wrapped.top_tracks
            }
        )

        return redirect('my_duo_wraps')

    except Exception as e:
        print(f"Error in Duo Wrapped: {e}")
        messages.error(request, "An error occurred while generating Duo Wrapped.")
        return redirect('spotify_social')
@login_required
def my_duo_wraps(request):
    print(f"Accessing my_duo_wraps for user: {request.user.username}")  # Debug print
    duo_wraps = DuoWrap.objects.filter(user=request.user)
    
    # Update debug prints to use new field names
    for wrap in duo_wraps:
        print(f"Duo Wrap ID: {wrap.id}")
        print(f"User artists: {wrap.user_artists}")
        print(f"Compared artists: {wrap.compared_artists}")
        print(f"User tracks: {wrap.user_tracks}")
        print(f"Compared tracks: {wrap.compared_tracks}")
        print("---")

    return render(request, 'my_duo_wraps.html', {'duo_wraps': duo_wraps})
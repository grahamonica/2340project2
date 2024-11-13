from django.db import models
from django.contrib.auth.models import User

class SpotifyWrapped(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    top_tracks = models.JSONField()  # Store as JSON
    top_artists = models.JSONField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on save

    def __str__(self):
        return f"{self.user.username}'s Spotify Wrapped"

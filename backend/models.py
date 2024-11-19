from django.db import models
from django.contrib.auth.models import User

class SpotifyWrapped(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    top_tracks = models.JSONField(null=True, blank=True)
    top_artists = models.JSONField(null=True, blank=True)
    top_genres = models.JSONField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # Track likes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    presentation = models.TextField(null=True, blank=True)  # Store formatted presentation

    def __str__(self):
        return f"{self.user.username}'s Spotify Wrapped"

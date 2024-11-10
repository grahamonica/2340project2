from django.contrib.auth.models import User
from rest_framework import serializers

from .models import SpotifyWrapped


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )
        return user


class SpotifyWrappedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = SpotifyWrapped
        fields = ["id", "username", "top_tracks", "top_artists", "is_public"]
        read_only_fields = ["user"]

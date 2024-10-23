from rest_framework import serializers

from .models import FoodLocation, UserProfile


class FoodLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodLocation
        fields = [
            "id",
            "name",
            "address",
            "latitude",
            "longitude",
            "category",
            "rating",
            "top_k_reviews",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodLocation
        fields = [
            "id",
            "author",
            "title",
            "content",
            "rating",
            "created_at",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "user",
            "bio",
            "location",
            "birth_date",
            "favorite_locations",
        ]

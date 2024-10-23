from rest_framework import serializers

from .models import FoodLocation, Review, UserProfile


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "title",
            "content",
            "rating",
            "created_at",
            "is_google_review",
        ]


class FoodLocationSerializer(serializers.ModelSerializer):
    top_k_reviews = ReviewSerializer(many=True, read_only=True)

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
            "photo_url",
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

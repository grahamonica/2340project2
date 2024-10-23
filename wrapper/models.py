from django.contrib.auth.models import User
from django.db import models


class Review(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_google_review = models.BooleanField(default=False)

    def __str__(self):
        return f"Review '{self.title}' by {self.author}"


class FoodLocation(models.Model):
    id = models.CharField(
        max_length=255, primary_key=True
    )  # Use place_id as primary key
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    category = models.CharField(max_length=100)
    rating = models.FloatField(null=True, blank=True)
    top_k_reviews = models.ManyToManyField(Review, related_name="top_k_reviews")
    photo_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    favorite_locations = models.ManyToManyField(
        FoodLocation, related_name="favorited_by", blank=True
    )

    def __str__(self):
        return self.user.username


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=100)
    is_superadmin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"

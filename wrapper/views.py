from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from geopy.geocoders import Nominatim
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from food_finder.utils import create_gmaps_client, get_restaurants_in_atlanta

from .models import FoodLocation, Review, UserProfile
from .serializers import FoodLocationSerializer, ReviewSerializer

gmaps_client = create_gmaps_client(settings.GOOGLE_MAPS_API_KEY)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id, author=request.user.username)
        review.delete()
        return Response(
            {"message": "Review removed successfully"}, status=status.HTTP_200_OK
        )
    except Review.DoesNotExist:
        return Response(
            {"error": "Review not found or you don't have permission to remove it"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_user_reviews(request):
    user_reviews = Review.objects.filter(
        author=request.user.username, is_google_review=False
    )
    serializer = ReviewSerializer(user_reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_review(request):
    restaurant_id = request.data.get("restaurant_id")
    rating = request.data.get("rating")
    content = request.data.get("content")

    print(request.data)

    if not all([restaurant_id, rating, content]):
        return Response(
            {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        restaurant = FoodLocation.objects.get(id=restaurant_id)
    except FoodLocation.DoesNotExist:
        return Response(
            {"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND
        )

    review = Review.objects.create(
        author=request.user.username,
        title=f"Review for {restaurant.name}",
        content=content,
        rating=rating,
        is_google_review=False,
    )

    restaurant.top_k_reviews.add(review)

    return Response(
        {"message": "Review added successfully"}, status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_favorites(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    favorite_locations = user_profile.favorite_locations.all()
    serializer = FoodLocationSerializer(favorite_locations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    restaurant_id = request.data.get("restaurant_id")

    if not restaurant_id:
        return Response(
            {"error": "Restaurant ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        restaurant = FoodLocation.objects.get(id=restaurant_id)
    except FoodLocation.DoesNotExist:
        return Response(
            {"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if restaurant in user_profile.favorite_locations.all():
        user_profile.favorite_locations.remove(restaurant)
        message = "Restaurant removed from favorites"
    else:
        user_profile.favorite_locations.add(restaurant)
        message = "Restaurant added to favorites"

    return Response({"message": message}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_restaurants(request):
    name = request.GET.get("name")
    cuisine_type = request.GET.get("cuisine_type")
    limit = int(request.GET.get("limit", 20))
    min_rating = float(request.GET.get("min_rating", 0))

    try:
        results = get_restaurants_in_atlanta(
            gmaps_client,
            name=name,
            cuisine_type=cuisine_type,
            limit=limit,
            min_rating=min_rating,
        )

        restaurants = []
        for result in results:
            place_details = gmaps_client.place(result.id, fields=["photo", "review"])

            photo_reference = None
            if place_details["result"].get("photos"):
                photo_reference = place_details["result"]["photos"][0][
                    "photo_reference"
                ]

            # Construct the photo URL
            photo_url = None
            if photo_reference:
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={settings.GOOGLE_MAPS_API_KEY}"

            food_location, created = FoodLocation.objects.update_or_create(
                id=result.id,
                defaults={
                    "name": result.name,
                    "address": result.address,
                    "latitude": result.latitude,
                    "longitude": result.longitude,
                    "category": result.types[0] if result.types else "",
                    "rating": result.rating,
                    "photo_url": photo_url,
                },
            )

            # Add reviews
            if place_details["result"].get("reviews"):
                top_k_reviews = place_details["result"]["reviews"][
                    :5
                ]  # Limit to top 5 reviews
                for review_data in top_k_reviews:
                    review, created = Review.objects.update_or_create(
                        author=review_data["author_name"],
                        content=review_data["text"],
                        defaults={
                            "title": f"Review for {food_location.name}",
                            "rating": review_data["rating"],
                            "is_google_review": True,
                        },
                    )
                    food_location.top_k_reviews.add(review)

            restaurants.append(food_location)

        serializer = FoodLocationSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ValueError as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(
            {"error": "An unexpected error occurred: " + str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_location(request):
    query = request.GET.get("query")
    if not query:
        return Response(
            {"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    geolocator = Nominatim(user_agent="myapp")
    location = geolocator.geocode(query + ", Atlanta, GA")

    if location:
        return Response(
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address,
            }
        )
    else:
        return Response(
            {"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def check_user_exists(request):
    username = request.data.get("username")
    email = request.data.get("email")

    user_exists = User.objects.filter(Q(username=username) | Q(email=email)).exists()

    return Response({"exists": user_exists}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_or_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    user = User.objects.filter(Q(username=username) | Q(email=email)).first()

    if user:
        # User exists, attempt login
        user = authenticate(request, username=user.username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            refresh["username"] = user.username  # Add this line
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "message": "Registration successful",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        # User doesn't exist, create new user
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        refresh = RefreshToken.for_user(user)
        refresh["username"] = user.username
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "Registration successful",
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

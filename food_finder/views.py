from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from food_finder.utils import create_gmaps_client, get_restaurants_in_atlanta

gmaps_client = create_gmaps_client(settings.GOOGLE_MAPS_API_KEY)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_restaurants(request):
    # Get parameters from the request
    base_location = request.GET.get("base_location", "Georgia Tech")
    name = request.GET.get("name")
    cuisine_type = request.GET.get("cuisine_type")
    max_distance = float(request.GET.get("max_distance", 10))
    limit = int(request.GET.get("limit", 20))
    min_rating = float(request.GET.get("min_rating", 0))

    try:
        # Get restaurants using the utility function
        results = get_restaurants_in_atlanta(
            gmaps_client,
            base_location=base_location,
            name=name,
            cuisine_type=cuisine_type,
            max_distance=max_distance,
            limit=limit,
            min_rating=min_rating,
        )

        # Convert results to a list of dictionaries
        restaurants = [result.model_dump() for result in results]

        return Response(restaurants, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred: " + str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(username=username, password=password, email=email)
    token = Token.objects.get_or_create(user=user)
    return Response({"token": token[0].key}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        token = Token.objects.get_or_create(user=user)
        return Response({"token": token[0].key}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
    else:
        return Response({"error": "Not logged in"}, status=status.HTTP_400_BAD_REQUEST)

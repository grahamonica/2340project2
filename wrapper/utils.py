from datetime import datetime
from typing import List, Optional
from django.conf import settings
import googlemaps
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from pydantic import BaseModel, Field
from shapely.geometry import Point, Polygon


def get_atlanta_polygon():
    # Approximate polygon for Atlanta city limits
    # These coordinates form a rough boundary of Atlanta
    return Polygon(settings.ATLANTA_COORDS)


def is_in_atlanta(lat, lng):
    point = Point(lng, lat)
    atlanta_polygon = get_atlanta_polygon()
    return atlanta_polygon.contains(point)


class Review(BaseModel):
    author: str
    rating: float
    text: str
    time: str


class PlaceDetails(BaseModel):
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    price_level: Optional[int] = None
    reviews: List[Review] = []
    opening_hours: Optional[List[str]] = None
    is_restaurant: bool = Field(
        default=False, description="Indicates if the place is a restaurant"
    )
    is_in_atlanta: bool = Field(
        default=False, description="Indicates if the place is in Atlanta"
    )
    distance_from_base: float = Field(
        default=0.0, description="Distance from base location in kilometers"
    )
    types: List[str] = Field(default_factory=list, description="Types of the place")
    website: Optional[str] = None
    phone_number: Optional[str] = None
    photo_url: Optional[str] = None


def create_gmaps_client(api_key):
    return googlemaps.Client(key=api_key)


def get_restaurants_in_atlanta(
    gmaps,
    name: str = None,
    cuisine_type: str = None,
    max_distance: float = 10,
    limit: int = 20,
    min_rating: float = 0,  # New parameter for minimum rating
) -> List[PlaceDetails]:
    geolocator = Nominatim(user_agent="myapp")
    base_coords = geolocator.geocode("Atlanta, GA")
    base_point = (base_coords.latitude, base_coords.longitude)

    query = "restaurant"
    if name:
        query += f" {name}"
    if cuisine_type:
        query += f" {cuisine_type}"

    places_result = gmaps.places(
        query=query, location=base_point, radius=max_distance * 1000
    )

    results = []
    for place in places_result.get("results", []):
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]

        if not is_in_atlanta(lat, lng):
            continue

        place_point = (lat, lng)
        distance = geodesic(base_point, place_point).miles

        if distance > max_distance:
            continue

        place_id = place["place_id"]

        place_details = gmaps.place(
            place_id=place_id,
            fields=[
                "name",
                "formatted_address",
                "type",
                "rating",
                "reviews",
                "price_level",
                "opening_hours",
                "website",
                "formatted_phone_number",
                "photo",
            ],
        )

        result = place_details["result"]

        # Skip this place if its rating is below the minimum
        if result.get("rating", 0) < min_rating:
            continue

        details = PlaceDetails(
            id=place_id,
            name=result.get("name", ""),
            address=result.get("formatted_address", ""),
            latitude=lat,
            longitude=lng,
            rating=result.get("rating"),
            price_level=result.get("price_level"),
            opening_hours=result.get("opening_hours", {}).get("weekday_text"),
            is_restaurant=True,
            is_in_atlanta=True,
            distance_from_base=round(distance, 2),
            types=place.get("types", []),
            website=result.get("website"),
            phone_number=result.get("formatted_phone_number"),
            photo_url=result.get("photos", [{}])[0].get("html_attributions", [""])[0]
            if result.get("photos")
            else None,
        )

        if "reviews" in result:
            details.reviews = [
                Review(
                    author=review.get("author_name", ""),
                    rating=review.get("rating", 0),
                    text=review.get("text", ""),
                    time=datetime.fromtimestamp(review.get("time", 0)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
                for review in result["reviews"]
            ]

        results.append(details)

        if len(results) >= limit:
            break

    return results

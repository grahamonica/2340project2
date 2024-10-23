import axios from "axios";
import { Restaurant } from "./schema";

export const API_URL = "http://localhost:8000"; // Replace with your Django backend URL

export const fetchUserReviews = async () => {
  try {
    const response = await axios.get(`${API_URL}/user_reviews/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching user reviews:", error);
    throw error;
  }
};

export const removeReview = async (reviewId: number) => {
  try {
    const response = await axios.delete(`${API_URL}/remove_review/${reviewId}/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error removing review:", error);
    throw error;
  }
};

export const addReview = async (
  restaurantId: string,
  review: { rating: number; content: string }
) => {
  try {
    console.log("Sending review data:", { restaurantId, review });
    const response = await axios.post(
      `${API_URL}/add_review/`,
      {
        restaurant_id: restaurantId,
        rating: Number(review.rating),
        content: review.content,
      },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        "Error adding review:",
        error.response?.data || error.message
      );
      throw new Error(error.response?.data?.error || error.message);
    } else {
      console.error("Unexpected error:", error);
      throw error;
    }
  }
};

export const fetchFavorites = async () => {
  try {
    const response = await axios.get(`${API_URL}/favorites/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching favorites:", error);
  }
};

export const toggleFavorite = async (restaurantId: string) => {
  try {
    const response = await axios.post(
      `${API_URL}/toggle_favorite/`,
      {
        restaurant_id: restaurantId,
      },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error toggling favorite:", error);
    throw error;
  }
};

export const searchRestaurants = async (
  name?: string,
  cuisineType?: string,
  limit: number = 100,
  minRating: number = 0
): Promise<Restaurant[]> => {
  try {
    const response = await axios.get(`${API_URL}/search_restaurants/`, {
      params: {
        name,
        cuisine_type: cuisineType,
        limit,
        min_rating: minRating,
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    });

    // Fetch favorites to compare with search results
    const favorites = await fetchFavorites();
    const favoriteIds = new Set(favorites.map((fav: Restaurant) => fav.id));

    return response.data.map((restaurant: any) => ({
      ...restaurant,
      distance_from_base: restaurant.distance_from_base || 0,
      isFavorite: favoriteIds.has(restaurant.id),
    }));
  } catch (error) {
    console.error("Error searching restaurants:", error);
    throw error;
  }
};

export const getLocation = async (
  query: string
): Promise<{ latitude: number; longitude: number }> => {
  try {
    const response = await axios.get(`${API_URL}/get_location/`, {
      params: { query },
    });
    return response.data;
  } catch (error) {
    console.error("Error getting location:", error);
    throw error;
  }
};

export const checkUserExists = async (username: string, email: string) => {
  const response = await fetch(`${API_URL}/check-user/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email }),
  });
  return response.json();
};

export const registerOrLogin = async (
  username: string,
  password: string,
  email: string
) => {
  const response = await fetch(`${API_URL}/register-or-login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, email }),
  });
  return response.json();
};

const getHeaders = () => {
  const token = localStorage.getItem("accessToken");
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
};

export const logout = async () => {
  const refreshToken = localStorage.getItem("refreshToken");
  if (!refreshToken) {
    throw new Error("No refresh token found");
  }

  const response = await fetch(`${API_URL}/logout/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!response.ok) {
    throw new Error("Logout failed");
  }

  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");

  return response.json();
};

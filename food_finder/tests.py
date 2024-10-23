from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_register(self):
        data = {
            "username": "newuser",
            "password": "newpass123",
            "email": "new@example.com",
        }
        response = self.client.post("/register/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login(self):
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post("/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_logout(self):
        token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post("/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully logged out")
        self.assertFalse(Token.objects.filter(user=self.test_user).exists())

    def test_logout_unauthenticated(self):
        response = self.client.post("/logout/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchRestaurantsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_search_restaurants(self):
        # Make a GET request to the search_restaurants endpoint
        response = self.client.get(
            "/search/?base_location=Georgia Tech&name=Pizza&max_distance=5&limit=5"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response is a list
        self.assertIsInstance(response.data, list)

        # Check if we got any results (this may vary based on actual data)
        self.assertTrue(len(response.data) > 0)

        # Check the structure of the first restaurant in the results
        if len(response.data) > 0:
            restaurant = response.data[0]
            self.assertIn("name", restaurant)
            self.assertIn("address", restaurant)
            self.assertIn("rating", restaurant)
            self.assertIn("distance_from_base", restaurant)

        # Check if the number of results is less than or equal to the limit
        self.assertLessEqual(len(response.data), 5)

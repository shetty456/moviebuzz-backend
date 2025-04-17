# movies/tests.py

from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase
from datetime import timedelta, time, datetime
from django.utils import timezone  # Import timezone
from movies.models import Movie, Language
from reservations.models import Auditorium, Showtime, Seat
from user.models import UserAccount  # adjust if your user model import is different

from django.contrib.auth import get_user_model
from rest_framework import status

from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken


user = get_user_model()


class GetAvailableSeatsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user
        self.admin_user = UserAccount.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="adminpass",
            role="admin",
        )

        # Generate JWT token for the admin user
        self.refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(self.refresh.access_token)

        self.client.force_authenticate(user=self.admin_user)

        # Create a movie
        self.movie = Movie.objects.create(
            title="Interstellar",
            description="A space adventure.",
            duration=timedelta(hours=2, minutes=49),
            language=None,  # Add if required
            user=self.admin_user,
            rate=8.6,
            price=12.99,
            image_url="",
        )

        # Create auditorium
        self.auditorium = Auditorium.objects.create(
            name="Auditorium 1",
            total_seats=100,
            total_shows=8,  # Add other fields if needed
        )

        # Create showtime (fix for naive datetime)
        self.show_time = time(18, 30)  # 6:30 PM
        naive_datetime = datetime.combine(datetime.today(), self.show_time)

        # Convert naive datetime to aware datetime
        aware_datetime = timezone.make_aware(naive_datetime)

        self.showtime = Showtime.objects.create(
            movie=self.movie, auditorium=self.auditorium, start_time=aware_datetime
        )

        # Create a few seats
        self.seat1 = Seat.objects.create(
            seat_number="A1", is_booked=False, showtime=self.showtime
        )
        self.seat2 = Seat.objects.create(
            seat_number="A2", is_booked=True, showtime=self.showtime
        )

    def test_get_available_seats(self):
        # Correct reverse URL
        url = reverse(
            "reservations:avilableseats"
        )  # 🔁 Corrected URL name with namespace

        # Prepare the query parameters
        response = self.client.get(
            url,
            {
                "movie_name": self.movie.title,
                "auditorium_name": self.auditorium.name,
                "show_time": self.show_time.strftime("%H:%M:%S"),
            },
        )

        # Check for correct response and available seats
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            any(seat["seat_number"] == "A1" for seat in response.data)
        )  # A1 should be available
        self.assertTrue(
            any(seat["seat_number"] == "A2" for seat in response.data)
        )  # A2 should be in the response


class MovieViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create the admin user
        self.admin_user = UserAccount.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="adminpass",
            role="Admin",
        )

        # Create non-admin user (optional)
        self.non_admin_user = UserAccount.objects.create_user(
            email="user@example.com",
            name="User",
            password="userpass",
            role="user",
        )

        # Create a language
        self.language = Language.objects.create(name="English")

        # Generate JWT token for the admin user
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)

        # Set JWT auth header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create a movie object
        self.movie = Movie.objects.create(
            title="Interstellar",
            description="A space adventure.",
            duration=timedelta(hours=2, minutes=49),
            language=self.language,
            user=self.admin_user,
            rate=8.6,
            price=12.99,
            image_url="",
        )

    def test_admin_user_can_access_movies_list(self):
        response = self.client.get("/api/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_user_can_create_movie(self):
        new_movie_data = {
            "title": "The Dark Knight",
            "description": "A superhero movie.",
            "duration": "02:32:00",  # duration must be passed as string
            "rate": 9.0,
            "price": 12.00,
            "language": self.language.id,
            "user": self.admin_user.id,
        }
        response = self.client.post("/api/movies/", new_movie_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "The Dark Knight")

    def test_admin_user_can_update_movie(self):
        updated_data = {
            "title": "Inception Updated",
            "description": "A mind-bending thriller with a twist.",
            "duration": "02:30:00",
            "rate": 9.0,
            "price": 12.00,
            "language": self.language.id,
            "user": self.admin_user.id,
        }
        response = self.client.put(
            f"/api/movies/{self.movie.id}/", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Inception Updated")

    def test_admin_user_can_delete_movie(self):
        response = self.client.delete(f"/api/movies/{self.movie.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ShowtimeViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an admin user
        self.admin_user = UserAccount.objects.create_user(
            email="admin@example.com",
            name="Admin",
            password="adminpass",
            role="Admin",
        )

        # JWT Auth
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create a language and movie
        self.language = Language.objects.create(name="English")
        self.movie = Movie.objects.create(
            title="Inception",
            description="Sci-fi thriller.",
            duration=timedelta(hours=2, minutes=28),
            language=self.language,
            user=self.admin_user,
            rate=8.8,
            price=10.99,
        )

        # Create auditorium
        self.auditorium = Auditorium.objects.create(
            name="Main Hall", total_seats=100, total_shows=5
        )

        # Create a showtime
        self.start_time = timezone.make_aware(
            datetime.combine(datetime.today(), time(18, 30))
        )
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            auditorium=self.auditorium,
            start_time=self.start_time,
        )

    def test_admin_can_list_showtimes(self):
        response = self.client.get("/api/showtimes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_create_showtime(self):
        new_start_time = timezone.make_aware(
            datetime.combine(datetime.today(), time(21, 0))
        )
        data = {
            "movie": self.movie.id,
            "auditorium": self.auditorium.id,
            "start_time": new_start_time.isoformat(),
            "status": "scheduled",
        }
        response = self.client.post("/api/showtimes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["movie"], self.movie.id)

    def test_admin_can_update_showtime(self):
        updated_time = timezone.make_aware(
            datetime.combine(datetime.today(), time(20, 0))
        )

        # Normalize actual time in the response to use '+00:00' instead of 'Z'
        # updated_time_iso = updated_time.isoformat().replace("Z", "+00:00")

        data = {
            "movie": self.movie.id,
            "auditorium": self.auditorium.id,
            "start_time": updated_time.isoformat(),
            "status": "scheduled",
        }
        response = self.client.put(
            f"/api/showtimes/{self.showtime.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["start_time"], updated_time.isoformat().replace("+00:00", "Z")
        )

    def test_admin_can_delete_showtime(self):
        response = self.client.delete(f"/api/showtimes/{self.showtime.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

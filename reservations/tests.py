# movies/tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from datetime import datetime, timedelta

from movies.models import Movie
from reservations.models import Auditorium, Showtime

from django.contrib.auth import get_user_model


from rest_framework.test import APIClient
from rest_framework import status

from movies.models import Movie, Language
from reservations.models import BookingHistory, Showtime, Auditorium, Seat

from django.utils import timezone



User = get_user_model()


class ListMoviesOnParticularDateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", name="Test User", password="password"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            language_id=None,
            duration=timedelta(minutes=120),
            user_id=self.user,
            rate=4.5,
            price=300.00,
        )
        self.auditorium = Auditorium.objects.create(
            name="Test Auditorium",
            total_seats=100,
            movie=self.movie,
            total_shows="3",
            place="Test City",
        )
        self.showtime = Showtime.objects.create(
            movie_id=self.movie,
            auditorium_id=self.auditorium,
            status="completed",
            start_time=make_aware(datetime(2025, 4, 16, 4, 6, 40)),
        )

    def test_get_showtimes_by_date(self):
        url = reverse("user:showsbydate")  # use your actual url name here
        response = self.client.get(url, {"date": "2025-04-16"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["movie_id"], self.movie.id)


class ReservationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123", name="Admin User"
        )

        # Create a regular user
        self.user = User.objects.create_user(
            email="user@example.com", password="userpass123", name="Test User"
        )

        # Create a language and a movie
        self.language = Language.objects.create(name="English")
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test Description",
            duration=timedelta(minutes=120),
            language=self.language,
            rate=4.5,
            price=10.00,
            user=self.user,
        )

        # Create an auditorium
        self.auditorium = Auditorium.objects.create(
            name="Main Hall",
            total_seats=100,
            movie=self.movie,
            total_shows=3,
            place="City Center",
            admin=self.admin_user,
        )

        # Create a showtime
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            auditorium=self.auditorium,
            start_time=timezone.make_aware(datetime(2030, 4, 13, 18, 0)),
        )

        # Create a seat
        self.seat = Seat.objects.create(
            seat_number="A1", is_booked=False, showtime=self.showtime
        )

    def test_admin_can_view_all_user_reservations(self):
        """Admin can retrieve all reservations"""
        BookingHistory.objects.create(
            user=self.user, movie=self.movie, showtime=self.showtime, tickets=2
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("reservations:view_all_reservations"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_cannot_book_any_ticket(self):
        """Admin should receive 403 when trying to book a seat"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse("reservations:reserve_seat"),
            {"seat_id": self.seat.id, "showtime_id": self.showtime.id, "tickets": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("not allowed", response.data["error"].lower())

    def test_user_can_cancel_future_booking(self):
        """User can cancel a reservation for a future showtime"""
        booking = BookingHistory.objects.create(
            user=self.user, movie=self.movie, showtime=self.showtime, tickets=1
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("reservations:cancel_reservation"),
            {"booking_id": booking.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data["message"].lower())

    def test_user_can_view_their_own_reservations(self):
        """User can see their own booking history"""
        booking = BookingHistory.objects.create(
            user=self.user, movie=self.movie, showtime=self.showtime, tickets=1
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("reservations:view_user_reservations"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], booking.id)

    def test_user_can_view_seat_details_of_their_booking(self):
        """User can see seat details for their reservation"""
        BookingHistory.objects.create(
            user=self.user,
            movie=self.movie,
            showtime=self.showtime,
            seat=self.seat,
            tickets=1,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("reservations:reservation_details"),
            {"seat_id": self.seat.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["seat"]["seat_number"], self.seat.seat_number)

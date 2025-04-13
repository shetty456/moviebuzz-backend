from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from user.models import UserAccount
from movies.models import Movie, Language
from reservations.models import BookingHistory, Showtime, Auditorium, Seat
from datetime import timedelta
from django.utils import timezone
from datetime import datetime


class AdminReservationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create admin user
        self.admin_user = UserAccount.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            name="Admin User",
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user
        self.user = UserAccount.objects.create_user(
            email="user@example.com", password="userpass123", name="Test User"
        )

        # Create a Language instance
        self.language = Language.objects.create(name="English")

        # Create a Movie instance
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test Description",
            duration=timedelta(minutes=120),
            language=self.language,
            rate=4.5,
            price=10.00,
            user=self.user,
        )

        # Create Auditorium
        self.auditorium = Auditorium.objects.create(
            name="Main Hall",
            total_seats=100,
            movie=self.movie,
            total_shows=3,
            place="City Center",
            admin=self.admin_user,
        )

        # Create Showtime
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            auditorium=self.auditorium,
            start_time=timezone.make_aware(datetime(2030, 4, 13, 18, 0)),
        )

        # Create Seat (correct field names: seat_number and is_booked)
        self.seat = Seat.objects.create(
            seat_number="A1",  
            is_booked=False, 
            showtime=self.showtime,  # Link to the showtime
        )

        # Create Booking with explicit tickets field
        self.booking = BookingHistory.objects.create(
            user=self.admin_user,
            movie=self.movie,
            showtime=self.showtime,
            tickets=2,  
        )

    def test_admin_can_view_all_reservations(self):
        response = self.client.get(reverse("reservations:view_all_reservations"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_cancel_future_reservation(self):
        # Create a new booking to cancel, ensure 'tickets' field is set
        booking = BookingHistory.objects.create(
            user=self.admin_user,
            movie=self.movie,
            showtime=self.showtime,
            tickets=1,  
        )

        # Use the correct format to send data as JSON
        response = self.client.post(
            reverse("reservations:cancel_reservation"),
            {"booking_id": booking.id},
            format="json",  
        )

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response message contains "success"
        self.assertIn("success", response.data["message"].lower())

    def test_view_user_reservations(self):
        # Create a booking for the user
        booking = BookingHistory.objects.create(
            user=self.user,
            movie=self.movie,
            showtime=self.showtime,
            tickets=1, 
        )

        # API endpoint to view user reservations
        url = reverse("reservations:view_user_reservations")

        # Request the user reservations (authenticated as the user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        # Assert that the response is OK (200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the reservation is returned in the response
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], booking.id)

    def test_user_can_see_seat_details(self):
        # Ensure the 'tickets' field is provided when creating a booking
        booking = BookingHistory.objects.create(
            user=self.user,
            movie=self.movie,
            showtime=self.showtime,
            tickets=1,  # Ensure tickets are set
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("reservations:reservation_details"),
            {"seat_id": self.seat.id},
            format="json",
        )

        # Check if the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# movies/tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from datetime import datetime, timedelta

from movies.models import Movie
from reservations.models import Auditorium, Showtime
from user.models import UserAccount
from django.contrib.auth import get_user_model

User = get_user_model()

class ListMoviesOnParticularDateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='Test User', password='password')
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            language_id=None,
            duration=timedelta(minutes=120),
            user_id=self.user,
            rate=4.5,
            price=300.00
        )
        self.auditorium = Auditorium.objects.create(
            name="Test Auditorium",
            total_seats=100,
            movie=self.movie,
            total_shows="3",
            place="Test City"
        )
        self.showtime = Showtime.objects.create(
            movie_id=self.movie,
            auditorium_id=self.auditorium,
            status="completed",
            start_time=make_aware(datetime(2025, 4, 16, 4, 6, 40))
        )

    def test_get_showtimes_by_date(self):
        url = reverse('user:showsbydate') # use your actual url name here
        response = self.client.get(url, {'date': '2025-04-16'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie_id'], self.movie.id)

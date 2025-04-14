from django.db import models
from user.models import UserAccount
from movies.models import Movie
from django.contrib.auth import get_user_model

User = get_user_model()


class Auditorium(models.Model):
    name = models.CharField(max_length=100)
    total_seats = models.PositiveIntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True)
    total_shows = models.CharField(max_length=100)
    place = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.place}"


class Showtime(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    auditorium_id = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    start_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie_id.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')} in {self.auditorium_id.name}"

    @property
    def get_date_of_show(self):
        return self.start_time.strftime("%Y-%m-%d")


class Seat(models.Model):
    showtime_id = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Seat {self.seat_number} - {'Booked' if self.is_booked else 'Available'}"
        )


class Review(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.movie.title} - {self.rating}★"


class BookingHistory(models.Model):
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    showtime_id = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    tickets = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.username} booked {self.tickets} ticket(s) for {self.showtime}"
        )

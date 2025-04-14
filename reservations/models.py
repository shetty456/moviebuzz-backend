from django.db import models
from user.models import UserAccount
from movies.models import Movie
from django.utils import timezone


class Auditorium(models.Model):
    name = models.CharField(max_length=100)
    total_seats = models.PositiveIntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True)
    total_shows = models.PositiveIntegerField()
    place = models.CharField(max_length=255)
    admin = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditoriums",
    )

    def __str__(self):
        return f"{self.name} - {self.place}"

    @property
    def upcoming_showtimes(self):
        return self.showtime_set.filter(start_time__gte=timezone.now()).order_by(
            "start_time"
        )


class Showtime(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    start_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')} in {self.auditorium.name}"

    @property
    def available_seats(self):
        return self.seat_set.filter(is_booked=False)

    @property
    def total_booked(self):
        return self.seat_set.filter(is_booked=True).count()

    def cancel_show(self):
        self.status = "cancelled"
        self.save()


class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("showtime", "seat_number")

    def __str__(self):
        return (
            f"Seat {self.seat_number} - {'Booked' if self.is_booked else 'Available'}"
        )

    def book(self):
        if not self.is_booked:
            self.is_booked = True
            self.save()

    def cancel_booking(self):
        if self.is_booked:
            self.is_booked = False
            self.save()


class Review(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.movie.title} - {self.rating}★"

    class Meta:
        ordering = ["-reviewed_at"]


class BookingHistory(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    tickets = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)
    seat = models.ForeignKey(Seat, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return (
            f"{self.user.username} booked {self.tickets} ticket(s) for {self.showtime}"
        )

    @property
    def show_time_str(self):
        return self.showtime.start_time.strftime("%Y-%m-%d %H:%M")

    class Meta:
        ordering = ["-booked_at"]

from rest_framework import serializers
from reservations.models import Auditorium, Seat, Showtime, Review, BookingHistory


# Auditorium Serializer
class AuditoriumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditorium
        fields = ("name", "total_seats", "total_shows", "movie", "place", "admin")


# Seat Serializer
class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ("seat_number", "is_booked")


# Showtime Serializer
class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ("movie", "auditorium", "status", "start_time")


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("user", "movie", "rating", "comment", "reviewed_at")


# BookingHistory Serializer
class BookingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingHistory
        fields = ("user", "movie", "showtime_id", "tickets", "booked_at")

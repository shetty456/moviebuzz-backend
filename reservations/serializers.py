from rest_framework import serializers
from movies.models import Movie
from reservations.models import Auditorium, Seat, Showtime, Review, BookingHistory
from movies.serilizers import MovieSerializer


# Seat Serializer
class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ("seat_number", "is_booked", "showtime")


# Showtime Serializer
class ShowtimeDetailerializer(serializers.ModelSerializer):
    movie = MovieSerializer()

    class Meta:
        model = Showtime
        fields = ("movie", "auditorium", "status", "start_time")


class ShowtimeSerializer(serializers.ModelSerializer):
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all()
    )  # Only the movie ID (primary key)

    class Meta:
        model = Showtime
        fields = ("movie", "auditorium", "status", "start_time")


# Auditorium Serializer
class AuditoriumSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    upcoming_showtimes = ShowtimeSerializer(
        many=True, read_only=True, source="upcoming_showtimes"
    )

    class Meta:
        model = Auditorium
        fields = (
            "name",
            "total_seats",
            "total_shows",
            "movie",
            "place",
            "admin",
            "upcoming_showtimes",
        )


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("user", "movie", "rating", "comment", "reviewed_at")


# BookingHistory Serializer
class BookingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingHistory
        fields = "__all__"
        depth = 1


class SeatQuerySerializer(serializers.Serializer):
    movie_name = serializers.CharField()
    auditorium_name = serializers.CharField()
    show_time = serializers.CharField()

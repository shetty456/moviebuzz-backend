
from rest_framework import serializers
from reservations.models import Auditorium, Seat, Showtime, Review, BookingHistory

# Auditorium Serializer
class AuditoriumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditorium
        fields = ('name','total_seats','total_shows','movie_id','place') 

# Seat Serializer
class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ('showtime_id','seat_number','is_booked') 

# Showtime Serializer
class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ('movie_id','auditorium_id','status','start_time')  

# Review Serializer 
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('user_id','movie_id','rating','comment','reviewed_at')

# BookingHistory Serializer
class BookingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingHistory
        fields = ('user_id', 'movie_id', 'showtime_id', 'tickets', 'booked_at') 

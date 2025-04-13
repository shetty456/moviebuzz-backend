from rest_framework.decorators import api_view, permission_classes
from reservations.models import BookingHistory, Seat
from reservations.serializers import BookingHistorySerializer, SeatSerializer
from rest_framework.response import Response
from user.permissions import IsAdminorReadonly
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone


# View all reservations – Admin only
@api_view(["GET"])
@permission_classes([IsAdminorReadonly])
def view_all_reservation(request):
    """
    Admin view to list all reservations.
    """
    reservation = BookingHistory.objects.all()
    serializers = BookingHistorySerializer(reservation, many=True)
    return Response(serializers.data)


# View reservations for the currently authenticated user
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_of_user_reservation(request):
    """
    View reservations of the currently authenticated user.
    """
    user = request.user
    reservation = BookingHistory.objects.filter(user=user)
    serializers = BookingHistorySerializer(reservation, many=True)
    return Response(serializers.data)


# Cancel future reservation (user only)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_future_reservation(request):
    """
    Allows a user to cancel future reservations.
    """
    booking_id = request.data.get("booking_id")

    try:
        reservation = BookingHistory.objects.get(id=booking_id, user=request.user)
    except BookingHistory.DoesNotExist:
        return Response(
            {"error": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if the showtime has already started
    if reservation.showtime.start_time <= timezone.now():
        return Response(
            {"error": "Cannot cancel past or ongoing showtime reservations."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Cancel the reservation
    reservation.delete()

    return Response(
        {"message": "Reservation cancelled successfully."}, status=status.HTTP_200_OK
    )


# User reservation with seat number and time
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_reservation_details(request):
    """
    Retrieve seat details for a user's reservation.
    """
    seat_id = request.data.get("seat_id")

    if not seat_id:
        return Response(
            {"error": "Seat ID is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        seat = Seat.objects.get(id=seat_id)
    except Seat.DoesNotExist:
        return Response({"error": "Seat not found."}, status=status.HTTP_404_NOT_FOUND)

    booking = BookingHistory.objects.filter(
        user=request.user, showtime=seat.showtime
    ).first()

    if not booking:
        return Response(
            {"error": "This seat does not belong to any of your bookings."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Check if the showtime has already started
    if seat.showtime.start_time <= timezone.now():
        return Response(
            {"error": "Cannot access past or ongoing showtime reservations."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    seat_data = SeatSerializer(seat).data

    return Response(
        {
            "message": "Seat details retrieved successfully.",
            "seat": seat_data,
            "showtime": seat.showtime.start_time,
            "movie": seat.showtime.movie.title,
        },
        status=status.HTTP_200_OK,
    )


# Reserve seats for a show booking (prevent double booking)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reserve_seat(request):
    """
    Reserve a seat for a showtime, preventing double booking.
    """
    seat_id = request.data.get("seat_id")
    showtime_id = request.data.get("showtime_id")
    tickets = request.data.get("tickets", 1)
    if not seat_id or not showtime_id:
        return Response(
            {"error": "Seat ID and Showtime ID are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        seat = Seat.objects.select_related("showtime").get(
            id=seat_id, showtime_id=showtime_id
        )
    except Seat.DoesNotExist:
        return Response(
            {"error": "Seat or Showtime not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if the seat is already booked
    if BookingHistory.objects.filter(seat=seat).exists():
        return Response(
            {"error": "Seat is already booked."}, status=status.HTTP_409_CONFLICT
        )

    # Check if the showtime has already started
    if seat.showtime.start_time <= timezone.now():
        return Response(
            {"error": "Cannot book a seat for a past or ongoing showtime."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create the booking
    booking = BookingHistory.objects.create(
        user=request.user, seat=seat, showtime=seat.showtime,tickets=tickets,
    )

    return Response(
        {"message": "Seat reserved successfully.", "booking_id": booking.id},
        status=status.HTTP_201_CREATED,
    )

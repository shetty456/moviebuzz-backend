from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone

from reservations.models import BookingHistory, Seat
from reservations.serializers import BookingHistorySerializer, SeatSerializer
from user.permissions import IsAdminOrReadOnly


class ViewAllReservations(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        reservation = BookingHistory.objects.all()
        serializer = BookingHistorySerializer(reservation, many=True)
        return Response(serializer.data)


class ViewUserReservations(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservation = BookingHistory.objects.filter(user=request.user)
        serializer = BookingHistorySerializer(reservation, many=True)
        return Response(serializer.data)


class CancelFutureMovieReservation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get("booking_id")

        try:
            reservation = BookingHistory.objects.get(id=booking_id, user=request.user)
        except BookingHistory.DoesNotExist:
            return Response(
                {"error": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if reservation.showtime.start_time <= timezone.now():
            return Response(
                {"error": "Cannot cancel past or ongoing showtime reservations."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.delete()
        return Response(
            {"message": "Reservation cancelled successfully."},
            status=status.HTTP_200_OK,
        )


class UserReservationDetails(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        seat_id = request.data.get("seat_id")

        if not seat_id:
            return Response(
                {"error": "Seat ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            seat = Seat.objects.select_related("showtime", "showtime__movie").get(
                id=seat_id
            )
        except Seat.DoesNotExist:
            return Response(
                {"error": "Seat not found."}, status=status.HTTP_404_NOT_FOUND
            )

        booking = BookingHistory.objects.filter(
            user=request.user, showtime=seat.showtime
        ).first()

        if not booking:
            return Response(
                {"error": "This seat does not belong to any of your bookings."},
                status=status.HTTP_403_FORBIDDEN,
            )

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


class ReserveSeat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        seat_id = request.data.get("seat_id")
        showtime_id = request.data.get("showtime_id")
        tickets = request.data.get("tickets", 1)
        if request.user.role == "admin":
            return Response(
                {"error": "Admin users are not allowed to book tickets."},
                status=status.HTTP_403_FORBIDDEN,
            )

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
                {"error": "Seat or Showtime not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if BookingHistory.objects.filter(seat=seat).exists():
            return Response(
                {"error": "Seat is already booked."},
                status=status.HTTP_409_CONFLICT,
            )

        if seat.showtime.start_time <= timezone.now():
            return Response(
                {"error": "Cannot book a seat for a past or ongoing showtime."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = BookingHistory.objects.create(
            user=request.user,
            seat=seat,
            showtime=seat.showtime,
            tickets=tickets,
        )

        return Response(
            {"message": "Seat reserved successfully.", "booking_id": booking.id},
            status=status.HTTP_201_CREATED,
        )

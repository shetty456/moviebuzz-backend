from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from reservations.models import BookingHistory, Seat, Showtime, Auditorium
from movies.models import Movie
from movies.serilizers import MovieSerializer
from reservations.serializers import (
    BookingHistorySerializer,
    SeatSerializer,
    ShowtimeSerializer,
    ShowtimeDetailerializer,
)
from user.permissions import IsAdminOrReadOnly
import datetime
from user.permissions import IsAdminOrReadOnly, IsUser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


class ViewAllReservations(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        reservation = BookingHistory.objects.all()
        serializer = BookingHistorySerializer(reservation, many=True)
        return Response(serializer.data)


class ViewUserReservations(APIView):
    permission_classes = [IsUser]

    def get(self, request):
        reservation = BookingHistory.objects.filter(user=request.user)
        serializer = BookingHistorySerializer(reservation, many=True)
        return Response(serializer.data)


class CancelFutureMovieReservation(APIView):
    permission_classes = [IsUser]

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        examples=[OpenApiExample("Cancel Booking", value={"booking_id": "1"})],
        responses={
            200: OpenApiResponse(
                description="Success",
                examples=[
                    OpenApiExample(
                        "OK", value={"message": "Reservation cancelled successfully."}
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Missing", value={"error": "Booking ID is required."}
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "Not Found", value={"error": "Reservation not found."}
                    )
                ],
            ),
        },
    )
    def post(self, request):
        booking_id = request.data.get("booking_id")
        if not booking_id:
            return Response(
                {"error": "Booking ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reservation = BookingHistory.objects.get(id=booking_id, user=request.user)
        except BookingHistory.DoesNotExist:
            return Response(
                {"error": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if reservation.showtime.start_time <= timezone.now():
            return Response(
                {"error": "Cannot cancel past or ongoing reservations."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.delete()
        return Response(
            {"message": "Reservation cancelled successfully."},
            status=status.HTTP_200_OK,
        )


class UserReservationDetails(APIView):
    permission_classes = [IsUser]

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        examples=[OpenApiExample("Seat Info", value={"seat_id": "5"})],
        responses={
            200: OpenApiResponse(
                description="Details Found",
                examples=[
                    OpenApiExample(
                        "Info",
                        value={
                            "message": "Seat details retrieved successfully.",
                            "seat": {"id": 5, "number": "A3", "status": "booked"},
                            "showtime": "2025-04-25T18:00:00Z",
                            "movie": "Inception",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Missing",
                examples=[
                    OpenApiExample(
                        "Missing Seat ID", value={"error": "Seat ID is required."}
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[
                    OpenApiExample("Seat Missing", value={"error": "Seat not found."})
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "Invalid",
                        value={
                            "error": "This seat does not belong to any of your bookings."
                        },
                    )
                ],
            ),
        },
    )
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
                {"error": "Cannot access past or ongoing reservations."},
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
    permission_classes = [IsUser]

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Reserve", value={"seat_id": "10", "showtime_id": "2", "tickets": 1}
            )
        ],
        responses={
            201: OpenApiResponse(
                description="Created",
                examples=[
                    OpenApiExample(
                        "Booked",
                        value={
                            "message": "Seat reserved successfully.",
                            "booking_id": 101,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Missing",
                        value={"error": "Seat ID and Showtime ID are required."},
                    )
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "Admin Block",
                        value={"error": "Admin users are not allowed to book tickets."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "Missing", value={"error": "Seat or Showtime not found."}
                    )
                ],
            ),
            409: OpenApiResponse(
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "Already Booked", value={"error": "Seat is already booked."}
                    )
                ],
            ),
        },
    )
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
                {"error": "Seat is already booked."}, status=status.HTTP_409_CONFLICT
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


class GetavilableSeats(generics.GenericAPIView):

    serializer_class = SeatSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "movie_name",
                # OpenApiParameter.IN_QUERY,
                description="The name of the movie",
                type=str,
                required=True,
            ),
            OpenApiParameter(
                "auditorium_name",
                # OpenApiParameter.IN_QUERY,
                description="The name of the auditorium",
                type=str,
                required=True,
            ),
            OpenApiParameter(
                "show_time",
                # OpenApiParameter.IN_QUERY,
                description="The show time for the movie",
                type=str,
                required=True,
            ),
        ]
    )
    def get(self, request):
        movie_name = request.GET.get("movie_name")
        auditorium_name = request.GET.get("auditorium_name")
        show = request.GET.get("show_time")

        moviedata = Movie.objects.get(title=movie_name)
        auditoriumdata = Auditorium.objects.get(name=auditorium_name)

        if not all([movie_name, auditorium_name, show]):
            return Response({"Error:parameters required"})

        else:
            try:

                show_time = datetime.datetime.strptime(show, "%H:%M:%S").time()

                show = Showtime.objects.filter(
                    movie=moviedata,
                    auditorium=auditoriumdata,
                    start_time__time=show_time,
                ).first()
            except Showtime.DoesNotExist:
                return Response({"Error:show not found"}, status=404)
        seats = Seat.objects.filter(showtime=show)
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)


class MovieViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class ShowtimeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Showtime.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:
            return ShowtimeDetailerializer
        return ShowtimeSerializer

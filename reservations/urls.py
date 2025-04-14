from django.urls import path
from reservations.views import (
    ViewUserReservations,
    ViewAllReservations,
    ReserveSeat,
    UserReservationDetails,
    CancelFutureMovieReservation,
)

app_name = "reservations"

urlpatterns = [
    path(
        "reservations/admin/",
        ViewAllReservations.as_view(),
        name="view_all_reservations",
    ),
    path(
        "reservations/user/",
        ViewUserReservations.as_view(),
        name="view_user_reservations",
    ),
    path(
        "reservations/cancel/",
        CancelFutureMovieReservation.as_view(),
        name="cancel_reservation",
    ),
    path(
        "reservations/details/",
        UserReservationDetails.as_view(),
        name="reservation_details",
    ),
    path("reservations/book/", ReserveSeat.as_view(), name="reserve_seat"),
]

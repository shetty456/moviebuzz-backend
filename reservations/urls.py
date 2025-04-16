from django.urls import path,include
from reservations.views import (
    ViewUserReservations,
    ViewAllReservations,
    ReserveSeat,
    UserReservationDetails,
    CancelFutureMovieReservation,
    GetavilableSeats,
    ShowtimeViewSet
   
)

from rest_framework.routers import DefaultRouter



app_name = "reservations"

router = DefaultRouter()
router.register(r'showtimes', ShowtimeViewSet)

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
    path("getavailableseat/",GetavilableSeats.as_view(),name="avilableseats"),
    path('', include(router.urls)),
]

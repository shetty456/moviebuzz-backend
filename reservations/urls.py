from django.urls import path
from reservations.views import (
    view_of_user_reservation,
    view_all_reservation,
    reserve_seat,
    user_reservation_details,
    cancel_future_reservation,
)

app_name = "reservations"

urlpatterns = [
    path("reservations/admin/", view_all_reservation, name="view_all_reservations"),
    path("reservations/user/", view_of_user_reservation, name="view_user_reservations"),
    path("reservations/cancel/", cancel_future_reservation, name="cancel_reservation"),
    path("reservations/details/", user_reservation_details, name="reservation_details"),
    path("reservations/book/", reserve_seat, name="reserve_seat"),
]

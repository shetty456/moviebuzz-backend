from django.contrib import admin
from reservations.models import Showtime,Auditorium, Seat, Review, BookingHistory

# Register your models here.
admin.site.register(Showtime),
admin.site.register(Auditorium),
admin.site.register(Seat),
admin.site.register(Review),
admin.site.register(BookingHistory),
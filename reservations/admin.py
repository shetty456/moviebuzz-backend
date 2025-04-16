from django.contrib import admin
from reservations.models import Showtime,Auditorium

# Register your models here.
admin.site.register(Showtime),
admin.site.register(Auditorium)

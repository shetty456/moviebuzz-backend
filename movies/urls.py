from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reservations.views import MovieViewSet

app_name = "movies"

router = DefaultRouter()
router.register(r'movies', MovieViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.db import models
from user.models import UserAccount


class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    language_id = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    duration = models.DurationField()
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=3, decimal_places=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title


class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "genre")

    def __str__(self):
        return f"{self.movie.title} - {self.genre.name}"

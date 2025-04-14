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
    language= models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    duration = models.DurationField()
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=3, decimal_places=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-rate", "title"]

    @property
    def short_description(self):
        return (
            self.description[:100] + "..."
            if len(self.description) > 100
            else self.description
        )

    @property
    def genre_names(self):
        return [genre.name for genre in self.genres.all()]

    def add_genres(self, genre_list):
        """
        Utility method to add genres to the movie.
        :param genre_list: List of Genre instances
        """

        for genre in genre_list:
            MovieGenre.objects.get_or_create(movie=self, genre=genre)

    def remove_genres(self, genre_list):
        """
        Utility method to remove specific genres from the movie.
         :param genre_list: List of Genre instances
        """
        MovieGenre.objects.filter(movie=self, genre__in=genre_list).delete()

    def clear_genres(self):
        """
        Remove all genres associated with this movie.
        """
        self.moviegenre_set.all().delete()

    @property
    def duration_minutes(self):
        return int(self.duration.total_seconds() // 60)


class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "genre")
        verbose_name = "Movie Genre"
        verbose_name_plural = "Movie Genres"

    def __str__(self):
        return f"{self.movie.title} - {self.genre.name}"

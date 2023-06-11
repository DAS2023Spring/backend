from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Movie(models.Model):
    name = models.CharField(max_length=64)
    director = models.CharField(max_length=128)
    created_year = models.IntegerField()
    length_minutes = models.IntegerField()
    logo = models.ImageField()


class MovieRating(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    movie = models.ForeignKey(to="movie.Movie", on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = [("user", "movie")]


class MovieList(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    movies = models.ManyToManyField(to="movie.Movie")

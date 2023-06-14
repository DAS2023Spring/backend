from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class MovieQuerySet(models.QuerySet):
    def annotate_overall_rating(self):
        return self.annotate(
            overall_rating=models.Subquery(
                MovieRating.objects.filter(movie_id=models.OuterRef("id")).values("movie_id").annotate(
                    average_rating=models.Avg("rating", output_field=models.FloatField()),
                ).values("average_rating")[:1],
                output_field=models.FloatField(),
            ),
        )


class Movie(models.Model):
    objects = models.Manager.from_queryset(MovieQuerySet)()
    name = models.CharField(max_length=64)
    director = models.CharField(max_length=128)
    created_year = models.IntegerField()
    length_minutes = models.IntegerField()
    imdb_rating = models.FloatField()
    logo = models.ImageField()
    header_image = models.ImageField()
    story = models.TextField()


class MovieRating(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    movie = models.ForeignKey(to="movie.Movie", on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "movie")]
        ordering = ["-id"]


class MovieList(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    movies = models.ManyToManyField(to="movie.Movie")

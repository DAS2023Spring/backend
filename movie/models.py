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

    def annotate_is_in_watchlist(self, watchlist):
        if watchlist is None:
            return self.annotate(is_in_watchlist=models.Value(False, models.BooleanField()))
        return self.annotate(
            is_in_watchlist=models.Exists(
                MovieList.movies.through.objects.filter(movie_id=models.OuterRef("id"), movielist_id=watchlist.id),
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

    def __str__(self):
        return f"{self.name} ({self.created_year})"


class MovieRating(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    movie = models.ForeignKey(to="movie.Movie", on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.movie}"

    class Meta:
        unique_together = [("user", "movie")]
        ordering = ["-id"]


class MovieList(models.Model):
    WATCH_LIST_NAME = "watch-list"

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    movies = models.ManyToManyField(to="movie.Movie")

    @classmethod
    def get_watchlist(cls, user):
        return cls.objects.get_or_create(user=user)

    class Meta:
        unique_together = [("user", "name")]

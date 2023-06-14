from rest_framework import serializers, status
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from movie.models import Movie, MovieRating, MovieList
from utility.serializers import ContextDefault


class ListMovieAPIView(ListAPIView):
    class ListMovieSerializer(serializers.ModelSerializer):
        overall_rating = serializers.FloatField()
        is_in_watchlist = serializers.BooleanField()

        class Meta:
            model = Movie
            fields = [
                "id",
                "name",
                "director",
                "created_year",
                "length_minutes",
                "logo",
                "overall_rating",
                "imdb_rating",
                "is_in_watchlist",
            ]

    serializer_class = ListMovieSerializer

    def get_queryset(self):
        queryset = Movie.objects.annotate_overall_rating()
        if self.request.user.is_authenticated:
            movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        else:
            movie_list = None
        return queryset.annotate_is_in_watchlist(movie_list)


class MovieRatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = MovieRating
        fields = [
            "username",
            "rating",
            "comment",
        ]


class RetrieveMovieAPIView(RetrieveAPIView):
    class RetrieveMovieSerializer(serializers.ModelSerializer):
        ratings = MovieRatingSerializer(source="movierating_set", many=True)
        overall_rating = serializers.FloatField()
        can_rate = serializers.SerializerMethodField()
        is_in_watchlist = serializers.BooleanField()

        class Meta:
            model = Movie
            fields = [
                "id",
                "name",
                "director",
                "created_year",
                "length_minutes",
                "logo",
                "overall_rating",
                "ratings",
                "imdb_rating",
                "header_image",
                "story",
                "can_rate",
                "is_in_watchlist",
            ]

        def get_can_rate(self, movie: Movie):
            user = self.context["request"].user
            if not user.is_authenticated:
                return False
            return not movie.movierating_set.filter(user=user).exists()

    serializer_class = RetrieveMovieSerializer

    def get_queryset(self):
        queryset = Movie.objects.annotate_overall_rating()
        if self.request.user.is_authenticated:
            movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        else:
            movie_list = None
        return queryset.annotate_is_in_watchlist(movie_list)


class CreateMovieRatingAPIView(CreateAPIView):
    class CreateMovieRatingSerializer(serializers.ModelSerializer):
        user = serializers.HiddenField(default=CurrentUserDefault())
        movie = serializers.HiddenField(default=ContextDefault("movie"))

        class Meta:
            model = MovieRating
            fields = [
                "user",
                "movie",
                "rating",
                "comment",
            ]

    permission_classes = [IsAuthenticated]
    serializer_class = CreateMovieRatingSerializer
    queryset = Movie.objects.all()

    def get_serializer_context(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_serializer_context()
        return {
            **super().get_serializer_context(),
            "movie": self.get_object(),
        }


class RetrieveWatchList(ListAPIView):
    class WatchlistMovieSerializer(serializers.ModelSerializer):
        overall_rating = serializers.FloatField()

        class Meta:
            model = Movie
            fields = [
                "id",
                "name",
                "director",
                "created_year",
                "length_minutes",
                "logo",
                "overall_rating",
                "imdb_rating",
            ]

    permission_classes = [IsAuthenticated]
    serializer_class = WatchlistMovieSerializer

    def get_queryset(self):
        movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        return movie_list.movies.all().annotate_overall_rating()


class AddRemoveMovieToWatchList(GenericAPIView):
    queryset = Movie.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        movie = self.get_object()
        movie_list.movies.add(movie)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        movie = self.get_object()
        movie_list.movies.remove(movie)
        return Response(status=status.HTTP_204_NO_CONTENT)

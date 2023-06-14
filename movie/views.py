from rest_framework import serializers, status
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from movie.models import Movie, MovieRating, MovieList
from utility.serializers import ContextDefault


class ListMovieSerializer(serializers.ModelSerializer):
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


class ListMovieAPIView(ListAPIView):
    queryset = Movie.objects.annotate_overall_rating()
    serializer_class = ListMovieSerializer


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
            ]

        def get_can_rate(self, movie: Movie):
            user = self.context["request"].user
            if not user.is_authenticated:
                return False
            return not movie.movierating_set.filter(user=user).exists()

    queryset = Movie.objects.annotate_overall_rating()
    serializer_class = RetrieveMovieSerializer


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

    permission_classes = [IsAuthenticated]
    serializer_class = ListMovieSerializer

    def get_queryset(self):
        movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        return movie_list.movies.all().annotate_overall_rating()


class AddMovieToWatchList(GenericAPIView):
    queryset = Movie.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        movie_list, _ = MovieList.objects.get_or_create(user=self.request.user, name=MovieList.WATCH_LIST_NAME)
        movie = self.get_object()
        movie_list.movies.add(movie)
        return Response(status=status.HTTP_201_CREATED)

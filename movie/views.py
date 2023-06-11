from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from movie.models import Movie, MovieRating
from utility.serializers import ContextDefault


class ListMovieAPIView(ListAPIView):
    class ListMovieSerializer(serializers.ModelSerializer):
        overall_rating = serializers.IntegerField()

        class Meta:
            model = Movie
            fields = [
                "name",
                "director",
                "created_year",
                "length_minutes",
                "logo",
                "overall_rating",
            ]

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
        overall_rating = serializers.IntegerField()

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
            ]

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

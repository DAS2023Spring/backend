from django.urls import path

from . import views

app_name = "movie"

urlpatterns = [
    path('', views.ListMovieAPIView.as_view(), name="list"),
    path('<int:pk>/', views.RetrieveMovieAPIView.as_view(), name="retrieve"),
    path('<int:pk>/rating/', views.CreateMovieRatingAPIView.as_view(), name="create_rating"),
]

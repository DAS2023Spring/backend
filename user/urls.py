import rest_framework.authtoken.views
from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', rest_framework.authtoken.views.obtain_auth_token, name='login'),
    path('reset-password/<str:username>/', views.ResetPasswordAPIView.as_view(), name='reset-password'),
]

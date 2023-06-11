from django.contrib.auth.models import User
from django.db import models


class SecurityQuestion(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='security_question')
    question = models.TextField()
    answer = models.TextField()

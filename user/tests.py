import random
import string

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import SecurityQuestion


def make_strong_password():
    return "".join(random.choices(string.ascii_letters, k=8))

class RegisterAPITest(APITestCase):
    def make_request(self, username, password, security_question, security_answer):
        return self.client.post(
            reverse("user:register"),
            data={
                "username": username,
                "password": password,
                "security_question": {
                    "question": security_question,
                    "answer": security_answer,
                }
            }
        )

    def test_register(self):
        password = make_strong_password()
        response = self.make_request("username", password, "salam", "bye")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get()
        self.assertEqual(user.username, "username")
        self.assertTrue(user.check_password(password))

        self.assertEqual(user.security_question.question, "salam")
        self.assertEqual(user.security_question.answer, "bye")

    def test_common_password(self):
        response = self.make_request("username", "password", "salam", "bye")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        result = response.json()
        self.assertIn("password", result)
        self.assertIn("common", result["password"][0])


class LoginAPITest(APITestCase):

    def setUp(self):
        self.user = baker.make(User)
        self.password = "something"
        self.user.set_password(self.password)
        self.user.save()

    def make_request(self, username, password):
        return self.client.post(
            reverse("user:login"),
            data={
                "username": username,
                "password": password,
            }
        )

    def test_login(self):
        response = self.make_request(self.user.username, self.password)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn("token", result)


class ChangePasswordAPITest(APITestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.password = "something"
        self.user.set_password(self.password)
        self.user.save()
        self.security_question = baker.make(SecurityQuestion, user=self.user)

    def make_get_request(self, username):
        return self.client.get(
            reverse("user:reset-password", args=[username]),
        )

    def make_post_request(self, username, answer, password):
        return self.client.post(
            reverse("user:reset-password", args=[username]),
            data={
                "answer": answer,
                "password": password,
            }
        )

    def test_get(self):
        response = self.make_get_request(self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertEqual(result["question"], self.security_question.question)

    def test_post(self):
        password = make_strong_password()
        response = self.make_post_request(self.user.username, self.security_question.answer, password)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(password))

    def test_post_bad_password(self):
        response = self.make_post_request(self.user.username, self.security_question.answer, "password")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        result = response.json()
        self.assertIn("password", result)

    def test_post_no_question(self):
        user = baker.make(User)
        response = self.make_post_request(user.username, "answer", "password")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_no_question(self):
        user = baker.make(User)
        response = self.make_get_request(user.username)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_no_user(self):
        response = self.make_get_request("something")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

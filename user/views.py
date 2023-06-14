from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_error_detail
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response

from user.models import SecurityQuestion


class SecurityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityQuestion
        fields = [
            'question',
            'answer',
        ]
        extra_kwargs = {
            'answer': {'write_only': True},
        }


class RegisterSerializer(serializers.ModelSerializer):
    security_question = SecurityQuestionSerializer(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'security_question'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as ve:
            raise ValidationError(get_error_detail(ve))
        return password

    @transaction.atomic
    def create(self, validated_data):
        security_question_data = validated_data.pop('security_question')
        user = User.objects.create_user(username=validated_data["username"], password=validated_data["password"])
        security_question_data['user'] = user
        self.fields['security_question'].create(security_question_data)
        return user


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    answer = serializers.CharField()

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as ve:
            raise ValidationError(get_error_detail(ve))
        return password

    def validate_answer(self, answer):
        if self.context['security_question'].answer.strip() != answer.strip():
            raise ValidationError("پاسخ داده‌شده با پاسخ زمان ثبت‌نام مطابقت ندارد.")
        return answer

    class Meta:
        fields = ['password', 'answer']


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer


class ResetPasswordAPIView(GenericAPIView):
    queryset = User.objects.all()
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SecurityQuestionSerializer
        else:
            return ResetPasswordSerializer

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        security_question = get_object_or_404(SecurityQuestion, user=user)
        return Response(self.get_serializer(instance=security_question).data)

    def post(self, request, *args, **kwargs):
        user: User = self.get_object()
        security_question = get_object_or_404(SecurityQuestion, user=user)
        serializer = self.get_serializer(
            data=request.data,
            context={**self.get_serializer_context(), 'security_question': security_question}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response()

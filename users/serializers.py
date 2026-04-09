import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="이미 사용 중인 이메일입니다.",
            )
        ]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "phone"]

    def validate_phone(self, value):
        if not value:
            return value
        if not re.fullmatch(r"\d{2,3}-?\d{3,4}-?\d{4}", value):
            raise serializers.ValidationError(
                "전화번호 형식이 올바르지 않습니다. (예: 010-1234-5678)"
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "비밀번호가 일치하지 않습니다."}
            )
        return attrs

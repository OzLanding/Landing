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

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def validate_phone(self, value):
        if not value:
            return None

        cleaned_phone = value.replace("-", "")

        if not cleaned_phone.isdigit():
            raise serializers.ValidationError("전화번호는 숫자로만 입력해주세요.")

        if not re.match(r"^01[016789]\d{7,8}$", cleaned_phone):
            raise serializers.ValidationError(
                "올바른 휴대폰 번호 형식이 아닙니다. (예: 01012345678)"
            )

        return cleaned_phone

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "phone"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

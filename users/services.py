from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.core import signing
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class UserService:
    EMAIL_VERIFY_SALT = "email-verify"
    EMAIL_VERIFY_MAX_AGE = 60 * 60 * 3

    @staticmethod
    def signup(serializer) -> User:
        validated_data = dict(serializer.validated_data)

        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        UserService.send_verification_email(user)

        return user

    @staticmethod
    def get_tokens_for_user(user) -> dict:
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def generate_email_token(user) -> str:
        return signing.dumps(user.email, salt=UserService.EMAIL_VERIFY_SALT)

    @staticmethod
    def verify_email_token(token) -> User:
        email = signing.loads(
            token,
            salt=UserService.EMAIL_VERIFY_SALT,
            max_age=UserService.EMAIL_VERIFY_MAX_AGE,
        )

        user = User.objects.get(email=email)
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        return user

    @staticmethod
    def send_verification_email(user):
        token = UserService.generate_email_token(user)
        verify_url = f"{settings.SITE_URL}/api/users/verify-email/?token={token}"

        send_mail(
            subject="Landing 이메일 인증",
            message=f"아래 링크를 클릭해 이메일 인증을 완료하세요.:\n{verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    @staticmethod
    def login(serializer) -> dict:
        data = serializer.validated_data

        user = authenticate(email=data["email"], password=data["password"])

        if not user:
            raise ValidationError("확인되지 않는 이메일 또는 비밀번호 입니다.")

        if not user.is_email_verified:
            raise ValidationError("이메일 인증이 완료되지 않은 회원입니다.")

        return UserService.get_tokens_for_user(user)

    @staticmethod
    def logout(refresh):
        token = RefreshToken(refresh)
        token.blacklist()

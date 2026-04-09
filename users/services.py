from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserService:
    @staticmethod
    def signup(serializer) -> User:
        validated_data = dict(serializer.validated_data)
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)
        serializer.instance = user
        return user

    @staticmethod
    def logout(refresh_token: str) -> None:
        if not refresh_token:
            raise ValidationError("refresh 토큰이 필요합니다.")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as exc:
            raise ValidationError("유효하지 않은 토큰입니다.") from exc

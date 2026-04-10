from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserService:
    @staticmethod
    def signup(serializer) -> User:
        validated_data = dict(serializer.validated_data)

        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

        return user

    @staticmethod
    def get_tokens_for_user(user) -> dict:
        refresh = RefreshToken.for_user(user)

        return {"access": str(refresh.access_token), "refresh_token": str(refresh)}

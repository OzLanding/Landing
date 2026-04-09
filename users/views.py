from rest_framework import generics, permissions, status
from rest_framework.response import Response

from users.serializers import SignupSerializer
from users.services import UserService


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        UserService.signup(serializer)


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        UserService.logout(request.data.get("refresh"))
        return Response(status=status.HTTP_204_NO_CONTENT)

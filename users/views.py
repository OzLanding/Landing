from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import SignupSerializer
from users.services import UserService


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.signup(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        UserService.logout(request.data.get("refresh"))
        return Response(status=status.HTTP_204_NO_CONTENT)

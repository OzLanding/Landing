from django.core import signing
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import SignupSerializer, LoginSerializer
from .services import UserService


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        request=SignupSerializer,
        examples=[
            OpenApiExample(
                "회원가입 예시",
                value={
                    "email": "user@example.com",
                    "username": "string",
                    "password": "string",
                    "password2": "string",
                    "phone": "",
                },
                request_only=True,
            ),
        ],
        responses={
            201: {
                "example": {
                    "message": "인증 이메일이 발송되었습니다. 인증완료 후 로그인할 수 있습니다."
                }
            }
        },
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.signup(serializer)

        response = Response(
            {
                "message": "인증 이메일이 발송되었습니다. 인증완료 후 로그인할 수 있습니다."
            },
            status=status.HTTP_201_CREATED,
        )

        return response


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이메일 인증",
        parameters=[
            {"name": "token", "in": "query", "required": True, "type": "string"}
        ],
        responses={200: {"example": {"message": "이메일 인증이 완료되었습니다."}}},
    )
    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "이메일 인증이 완료되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            UserService.verify_email_token(token)
            return Response({"message": "이메일 인증이 완료되었습니다."})
        except signing.BadSignature:
            return Response(
                {"error": "유효하지 않거나 만료된 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="로그인",
        request=LoginSerializer,
        responses={200: {"example": {"message": "로그인 완료", "access": "eyJ..."}}},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = UserService.login(serializer)

        response = Response(
            {
                "message": "로그인 완료",
                "access": tokens["access"],
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="refresh",
            value=tokens["refresh"],
            httponly=True,
            samesite="Lax",
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="로그아웃",
        request=None,
        responses={200: {"example": {"message": "로그아웃 되었습니다."}}},
    )
    def post(self, request):
        refresh = request.COOKIES.get("refresh")

        if not refresh:
            return Response(
                {"error": "refresh 토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            UserService.logout(refresh)
            return Response({"message": "로그아웃 되었습니다."})
        except Exception:
            return Response(
                {"error": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

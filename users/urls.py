from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, EmailVerifyView, LoginView, LogoutView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-email/", EmailVerifyView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
]

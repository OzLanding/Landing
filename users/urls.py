from django.urls import path
from .views import SignupView, EmailVerifyView, LoginView, LogoutView, TokenRefreshView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-email/", EmailVerifyView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
]

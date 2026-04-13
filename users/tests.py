from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from .services import UserService

User = get_user_model()


class SomeTest(APITestCase):
    def setUp(self):
        self.url = "/api/users/signup/"
        self.valid_data = {
            "email": "new@test.com",
            "username": "newuser",
            "password": "Testpass123!",
            "password2": "Testpass123!",
            "phone": "01012345678",
        }

    def test_signup_success(self):
        res = self.client.post(self.url, self.valid_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_signup_user_not_emailverivied(self):
        self.client.post(self.url, self.valid_data)
        user = User.objects.get(email="new@test.com")
        self.assertFalse(user.is_email_verified)

    def test_signup_password_mismatch(self):
        data = {**self.valid_data, "password2": "different123!"}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_email(self):
        self.client.post(self.url, self.valid_data)
        res = self.client.post(self.url, self.valid_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_phone(self):
        data = {**self.valid_data, "phone": "123456"}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_without_phone(self):
        data = {**self.valid_data, "phone": ""}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class EmailVerifyTest(APITestCase):
    def setUp(self):
        self.url = "/api/users/verify-email/"
        self.user = User.objects.create_user(
            email="verify@test.com",
            username="verifyuser",
            password="Testpass123!",
        )

    def test_verify_email_success(self):
        token = UserService.generate_email_token(self.user)
        res = self.client.get(self.url, {"token": token})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_email_no_token(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_invalid_token(self):
        res = self.client.get(self.url, {"token": "invalid_token"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(APITestCase):
    def setUp(self):
        self.url = "/api/users/login/"
        self.user = User.objects.create_user(
            email="login@test.com",
            username="loginuser",
            password="Testpass123!",
        )
        self.user.is_email_verified = True
        self.user.save(update_fields=["is_email_verified"])

    def test_login_success(self):
        res = self.client.post(
            self.url,
            {
                "email": "login@test.com",
                "password": "Testpass123!",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_sets_cookies(self):
        res = self.client.post(
            self.url,
            {
                "email": "login@test.com",
                "password": "Testpass123!",
            },
        )
        self.assertIn("access", res.cookies)
        self.assertIn("refresh", res.cookies)

    def test_login_wrong_password(self):
        res = self.client.post(
            self.url,
            {
                "email": "login@test.com",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_email(self):
        self.user.is_email_verified = False
        self.user.save(update_fields=["is_email_verified"])
        res = self.client.post(
            self.url,
            {
                "email": "login@test.com",
                "password": "Testpass123!",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_email(self):
        res = self.client.post(
            self.url,
            {
                "email": "nobody@test.com",
                "password": "Testpass123!",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTest(APITestCase):
    def setUp(self):
        self.url = "/api/users/logout/"
        self.user = User.objects.create_user(
            email="logout@test.com",
            username="logoutuser",
            password="Testpass123!",
        )
        self.user.is_email_verified = True
        self.user.save(update_fields=["is_email_verified"])

    def _login(self):
        self.client.post(
            "/api/users/login/",
            {
                "email": "logout@test.com",
                "password": "Testpass123!",
            },
        )

    def test_logout_success(self):
        self._login()
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_without_refresh_token(self):
        self._login()
        self.client.cookies.pop("refresh")
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTest(APITestCase):
    def setUp(self):
        self.url = "/api/users/token/refresh/"
        self.user = User.objects.create_user(
            email="refresh@test.com",
            username="refreshuser",
            password="Testpass123!",
        )
        self.user.is_email_verified = True
        self.user.save(update_fields=["is_email_verified"])

    def _login(self):
        self.client.post(
            "/api/users/login/",
            {
                "email": "refresh@test.com",
                "password": "Testpass123!",
            },
        )

    def test_token_refresh_success(self):
        self._login()
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.cookies)

    def test_token_refresh_without_cookie(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

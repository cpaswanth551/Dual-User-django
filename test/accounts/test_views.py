import random
from unittest.mock import patch
from django.urls import reverse
import pytest
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.core import mail

from ..utils import *


@pytest.mark.django_db
class TestRegisteration:

    def test_successfull_registeration(self, api_client):
        url = reverse("auth-register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "confirm_password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "user_type": "peer",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["username"] == "newuser"

    def test_registeration_password_mismatch(self, api_client):
        url = reverse("auth-register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "confirm_password": "wrong_password",
            "first_name": "New",
            "last_name": "User",
            "user_type": "peer",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthentication:
    url = "/api/v1/accounts/auth/token/"

    def test_successful_login(self, api_client, user, test_password):

        data = {
            "email": user.email,
            "password": test_password,
        }
        response = api_client.post(self.url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK, "Login failed"

    def test_login_invalid_credentials(self, api_client, user):
        data = {"email": user.email, "password": "wrongpassword"}
        response = api_client.post(self.url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, api_client, create_user, test_password):
        inactive_user = create_user(is_active=False)
        data = {"email": inactive_user.email, "password": test_password}
        response = api_client.post(self.url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "disabled" in str(response.data["error"]).lower()


@pytest.mark.django_db
class TestPasswordReset:
    forget_url = "/api/v1/accounts/user-password/forget/"
    reset_url = "/api/v1/accounts/user-password/reset/"

    def test_forgot_password_success(self, api_client, user):

        response = api_client.post(self.forget_url, {"email": user.email})
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["message"]
            == "Password reset instructions have been sent to your email."
        )

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Password Reset Request"
        assert user.email in mail.outbox[0].to

    def test_forgot_password_invalid_email(self, api_client):

        response = api_client.post(
            self.forget_url, {"email": "nonexistent@example.com"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_forgot_password_empty_email(self, api_client):

        response = api_client.post(self.forget_url, {"email": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_reset_password_success(self, api_client, user):

        reset_response = api_client.post(self.forget_url, {"email": user.email})

        token = mail.outbox[0].body.split("reset-password/")[-1].split("\n")[0].strip()

        new_password = "NewStrongPassword123!"
        reset_response = api_client.post(
            self.reset_url,
            {
                "token": token,
                "password": new_password,
                "confirm_password": new_password,
            },
        )

        print("Reset response status:", reset_response.status_code)
        print("Reset response data:", reset_response.data)

        assert (
            reset_response.status_code == status.HTTP_200_OK
        ), f"Unexpected response: {reset_response.data}"
        assert reset_response.data["message"] == "Password has been reset successfully."

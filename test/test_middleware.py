import json
from rest_framework import status
from .utils import *


class TestAccessMiddleware:

    def test_public_paths(self, api_rf, middleware):
        public_paths = [
            "/api/v1/accounts/auth/token/",
            "/api/v1/admin/auth/token/",
            "/api/v1/accounts/auth/register/",
            "/api/schema/",
        ]

        for path in public_paths:
            request = api_rf.get(path)
            response = middleware.process_request(request)
            assert response is None

    def test_missing_authorization_header(self, api_rf, middleware):
        request = api_rf.get("/api/v1/accounts/users/")
        response = middleware.process_request(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.content.decode("utf-8"))
        assert (
            response_data["message"] == "Authentication credentials were not provided."
        )

    def test_invalid_auth_header_format(self, api_rf, middleware):

        request = api_rf.get("/api/v1/accounts/users/")
        request.META["HTTP_AUTHORIZATION"] = "InValid Token"
        response = middleware.process_request(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.content.decode("utf-8"))
        assert (
            response_data["message"] == "Authentication credentials were not provided."
        )

    def test_expired_token(self, api_rf, middleware, user, generate_token):
        token = generate_token(user.username, expired=True)
        request = api_rf.get("/api/v1/accounts/users/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer{token}"
        response = middleware.process_request(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.content.decode("utf-8"))
        assert (
            response_data["message"] == "Authentication credentials were not provided."
        )

    def test_invalid_token_signature(self, api_rf, middleware):
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRlc3QifQ.invalid-signature"
        request = api_rf.get("/api/v1/accounts/users/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer{token}"
        response = middleware.process_request(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response_data = json.loads(response.content.decode("utf-8"))
        assert (
            response_data["message"] == "Authentication credentials were not provided."
        )

from typing import Optional, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from rest_framework import status
import jwt

from accounts.models import WebUser
from medwb_admins.models import AdminUser


def get_user_by_id(username):
    user = WebUser.objects.filter(username=username).first()
    if user:
        return user
    return AdminUser.objects.filter(username=username).first()


class UserAccessMiddleware:
    PUBLIC_PATHS = {
        # Authentication routes
        "/api/v1/accounts/auth/token/",
        "/api/v1/admin/auth/token/",
        "/api/v1/accounts/auth/register/",
        "/api/v1/admin/auth/register/",
        # Password management
        "/api/v1/accounts/user-password/forget/",
        "/api/v1/accounts/user-password/reset/",
        "/api/v1/admin/admin-password/reset/",
        "/api/v1/admin/admin-password/forget/",
        # API documentation
        "/api/schema/",
        "/api/schema/swagger-ui/",
        "/api/schema/redoc/",
    }

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        if self._is_public_path(request.path):
            return None

        try:
            token = self._extract_token(request)
            if not token:
                return self._create_error_response(
                    "Authentication credentials were not provided.",
                    status.HTTP_401_UNAUTHORIZED,
                )

            payload = self._decode_token(token)
            if not payload:
                return self._create_error_response(
                    "Invalid or expired token.", status.HTTP_401_UNAUTHORIZED
                )

            user = self._get_user(payload)
            if not user:
                return self._create_error_response(
                    "User not found.", status.HTTP_401_UNAUTHORIZED
                )

            request.user = user

            if not self._check_permissions(request, user):
                return self._create_error_response(
                    "You don't have permission to access this resource.",
                    status.HTTP_403_FORBIDDEN,
                )

            return None

        except Exception as e:
            return self._create_error_response(
                str(e), status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _is_public_path(self, path: str) -> bool:
        return any(path.startswith(public_path) for public_path in self.PUBLIC_PATHS)

    def _extract_token(self, request: HttpRequest) -> Optional[str]:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    def _decode_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                },
            )
        except jwt.PyJWTError:
            return None

    def _get_user(self, payload: dict) -> Optional[object]:
        try:
            return get_user_by_id(payload.get("username"))
        except Exception:
            return None

    def _check_permissions(self, request: HttpRequest, user: object) -> bool:
        is_admin = isinstance(user, AdminUser)
        is_web_user = isinstance(user, WebUser)

        if request.path.startswith("/api/v1/admin/"):
            return is_admin

        if request.path.startswith("/api/v1/accounts/") and not request.path.startswith(
            "/api/v1/accounts/auth/"
        ):
            return is_web_user

        return True

    def _create_error_response(self, message: str, status_code: int) -> JsonResponse:
        return JsonResponse(
            {"error": True, "message": message, "status_code": status_code},
            status=status_code,
        )

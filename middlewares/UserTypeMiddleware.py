from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import jwt

from accounts.models import WebUser
from medwb_admins.models import AdminUser


def get_user_by_id(username):
    user = WebUser.objects.filter(username=username).first()
    if user:
        return user
    else:

        return AdminUser.objects.filter(username=username).first()


class UserAccessMiddleware(MiddlewareMixin):

    def process_request(self, request):
        auth_paths = [
            "/api/v1/accounts/auth/token/",
            "/api/v1/admin/auth/token/",
            "/api/v1/accounts/auth/register/",
            "/api/v1/admin/auth/register/",
            "/api/v1/accounts/user-password/forget/",
            "/api/v1/accounts/user-password/reset/",
            "/api/v1/admin/admin-password/reset/",
            "/api/v1/admin/admin-password/forget/",
            "/api/schema/",
            "/api/schema/swagger-ui/",
            "/api/schema/redoc/",
        ]

        if any(request.path.startswith(path) for path in auth_paths):
            return None

        auth_details = request.META.get("HTTP_AUTHORIZATION")
        token = auth_details.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            user = get_user_by_id(payload["username"])

            is_admin = isinstance(user, AdminUser)
            is_web_user = isinstance(user, WebUser)

            if request.path.startswith("/api/v1/admin/"):
                if not is_admin:
                    return HttpResponseForbidden(
                        "Access denied. Admin access required."
                    )

            if request.path.startswith(
                "/api/v1/accounts/"
            ) and not request.path.startswith("/api/v1/accounts/auth/"):
                if not is_web_user:
                    return HttpResponseForbidden(
                        "Access denied. Web user access required."
                    )

            return None
        except jwt.PyJWTError:
            pass

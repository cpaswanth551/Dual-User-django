from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt

from accounts.models import WebUser
from medwb_admins.models import AdminUser


User = get_user_model()


def get_user(username: str):
    user = WebUser.objects.filter(username=username).first()
    if user:
        return user
    else:
        return AdminUser.objects.filter(username=username).first()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user(payload["username"])
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")

        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        except Exception as e:
            raise AuthenticationFailed(str(e))

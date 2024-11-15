from datetime import datetime, timedelta

from django.conf import settings
import jwt


def generate_tokens(user_request):
    access_token_payload = {
        "id": user_request.id,
        "username": user_request.username,
        "exp": datetime.now() + timedelta(hours=1),
        "iat": datetime.now(),
        "token_type": "access",
    }

    refresh_token_payload = {
        "id": user_request.id,
        "exp": datetime.now() + timedelta(days=7),
        "iat": datetime.now(),
        "token_type": "refresh",
    }

    access_token = jwt.encode(
        access_token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return access_token, refresh_token

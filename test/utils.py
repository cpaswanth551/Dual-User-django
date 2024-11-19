import datetime
from django.http import HttpResponse
from django.urls import reverse
import jwt
import pytest
from rest_framework.test import APIClient
from django.test import RequestFactory
from django.contrib.auth.hashers import make_password
import factory
from faker import Faker
from pytest_factoryboy import register

from accounts.models import WebUser
from core import settings
from middlewares.UserTypeMiddleware import UserAccessMiddleware

fake = Faker()


class WebUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WebUser
        django_get_or_create = ("email",)

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    password = "testpass123"
    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)
    user_type = factory.Iterator(["peer", "admin", "moderator"])
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the _create method to properly set the password"""
        password = kwargs.pop("password", None)
        obj = super()._create(model_class, *args, **kwargs)
        if password:
            obj.set_password(password)
            obj.save()
        return obj


register(WebUserFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_rf():
    return RequestFactory()


@pytest.fixture
def test_password():
    return "testpass123"


@pytest.fixture
def test_user_data(test_password):
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": test_password,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "user_type": "peer",
    }


@pytest.fixture
def create_user(db, test_password):
    def make_user(**kwargs):
        kwargs["password"] = test_password
        return WebUserFactory(**kwargs)

    return make_user


@pytest.fixture
def user(create_user):
    return create_user()


@pytest.fixture
def authenticated_client(db, api_client, user, test_password):
    url = reverse("auth-token")
    response = api_client.post(url, {"email": user.email, "password": test_password})

    token = response.data.get("access_token")
    if token:
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def get_response():
    def _get_response(request):
        return HttpResponse()

    return _get_response


@pytest.fixture
def middleware(get_response):
    return UserAccessMiddleware(get_response=get_response)


@pytest.fixture
def generate_token():
    def _generate_token(username, expired):
        payload = {
            "username": username,
            "exp": datetime.datetime.now()
            + datetime.timedelta(days=-1 if expired else 1),
            "iat": datetime.datetime.now(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return _generate_token

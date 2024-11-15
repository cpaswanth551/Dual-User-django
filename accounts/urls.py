from django.urls import include, path
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet, AuthViewSet, AccountPasswordViewSet


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"user-password", AccountPasswordViewSet, basename="password")

urlpatterns = [
    path("", include(router.urls)),
]

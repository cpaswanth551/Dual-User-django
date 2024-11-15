from django.urls import include, path
from rest_framework.routers import DefaultRouter
from medwb_admins.views import AdminAuthViewset, AdminPasswordViewSet


router = DefaultRouter()
router.register(r"auth", AdminAuthViewset, basename="auth")
router.register(r"admin-password", AdminPasswordViewSet, basename="admin_password")


urlpatterns = [path("", include(router.urls))]

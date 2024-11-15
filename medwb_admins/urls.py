from django.urls import include, path
from rest_framework.routers import DefaultRouter
from medwb_admins.views import AdminAuthViewset


router = DefaultRouter()
router.register(r"auth", AdminAuthViewset, basename="auth")


urlpatterns = [path("", include(router.urls))]

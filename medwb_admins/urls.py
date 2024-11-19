from django.urls import include, path
from rest_framework.routers import DefaultRouter
from medwb_admins.views import (
    AdminAuthViewset,
    AdminPasswordViewSet,
    AdminRoleViewset,
    AdminUserViewset,
    RolehasPermissionViewset,
    WebUserModelViewset,
)


router = DefaultRouter()
router.register(r"role", AdminRoleViewset, basename="role")
router.register(
    r"role-haspermissions", RolehasPermissionViewset, basename="role_haspermissions"
)
router.register(r"admin-user", AdminUserViewset, basename="admin_user")
router.register(r"auth", AdminAuthViewset, basename="auth")
router.register(r"admin-password", AdminPasswordViewSet, basename="admin_password")
router.register(r"web-user", WebUserModelViewset, basename="web_user")


urlpatterns = [path("", include(router.urls))]

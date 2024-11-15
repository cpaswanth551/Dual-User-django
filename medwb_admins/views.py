from django.conf import settings
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from accounts.serializers import (
    LoginSerializer,
)
from core.utils import generate_tokens
from medwb_admins.models import AdminUser, AdminRole, RoleHasPermission
from medwb_admins.serializers import (
    AdminRoleSerializer,
    AdminUserRegistrationSerializer,
    AdminUserSerializer,
    RolehasPermissionerializer,
)
from utils.PasswordSerializers import (
    AdminUserForgotPasswordSerializer,
    AdminUserResetPasswordSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["role"]),
    retrieve=extend_schema(tags=["role"]),
    create=extend_schema(tags=["role"]),
    update=extend_schema(tags=["role"]),
    partial_update=extend_schema(tags=["role"]),
    destroy=extend_schema(tags=["role"]),
)
class AdminRoleViewset(viewsets.ModelViewSet):
    queryset = AdminRole.objects.all()
    serializer_class = AdminRoleSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["RolehasPermission"]),
    retrieve=extend_schema(tags=["RolehasPermission"]),
    create=extend_schema(tags=["RolehasPermission"]),
    update=extend_schema(tags=["RolehasPermission"]),
    partial_update=extend_schema(tags=["RolehasPermission"]),
    destroy=extend_schema(tags=["RolehasPermission"]),
)
class RolehasPermissionViewset(viewsets.ModelViewSet):
    queryset = RoleHasPermission.objects.all()
    serializer_class = RolehasPermissionerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Admin"]),
    retrieve=extend_schema(tags=["Admin"]),
    create=extend_schema(tags=["Admin"]),
    update=extend_schema(tags=["Admin"]),
    partial_update=extend_schema(tags=["Admin"]),
    destroy=extend_schema(tags=["Admin"]),
)
class AdminUserViewset(viewsets.ModelViewSet):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    token=extend_schema(tags=["Admin"]),
    register=extend_schema(tags=["Admin"]),
)
class AdminAuthViewset(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def token(self, request):
        """
        Authenticates a user and provides access and refresh tokens upon success.
        """

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        try:
            authenticated_user = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, authenticated_user.password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        access_token, refresh_token = generate_tokens(authenticated_user)
        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": authenticated_user.id,
                    "username": authenticated_user.email,
                    "email": authenticated_user.email,
                },
            }
        )

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = AdminUserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            admin_user = serializer.save()
            superadmin = AdminUser.objects.filter(admin_role__name="Superadmin").first()
            if superadmin:
                send_mail(
                    "New Admin Registration",
                    f"New admin registration request from {admin_user.email}. Please review and approve.",
                    settings.DEFAULT_FROM_EMAIL,
                    [superadmin.email],
                    fail_silently=False,
                )

            return Response(
                {
                    "message": "Registration successful. Waiting for superadmin approval.",
                    "user": {
                        "email": admin_user.email,
                        "username": admin_user.username,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def approve_admin(self, request, pk=None):

        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can approve new admins"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            admin_user = AdminUser.objects.get(id=pk)

            admin_user.is_active = True
            admin_user.save()

            return Response(
                {
                    "message": "Admin User has been approved!",
                    "user": {"id": admin_user.id, "username": admin_user.username},
                },
                status=status.HTTP_200_OK,
            )
        except AdminUser.DoesNotExist:
            return Response(
                {"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AdminPasswordViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def forget(self, request):
        serializer = AdminUserForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Password reset instructions have been sent to your email."
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def reset(self, request):
        serializer = AdminUserResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

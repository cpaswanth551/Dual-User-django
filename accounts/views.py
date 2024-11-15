from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from django.contrib.auth.hashers import check_password
from accounts.models import WebUser
from accounts.serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterationSeriailizer,
    UserSerializers,
    ResetPasswordSerializer,
)
from core.utils import generate_tokens


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializers
    queryset = WebUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class AuthViewSet(viewsets.ViewSet):
    """
    API Endpont manages authentication actions, including user login and token refresh.
    """

    permission_classes = [permissions.AllowAny]

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
            user = WebUser.objects.get(email=email)
        except WebUser.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, user.password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "User account is disabled"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token, refresh_token = generate_tokens(user)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = RegisterationSeriailizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "user Registeration completed !.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "user_type": user.user_type,
                },
            }
        )


class AccountPasswordViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def forget(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
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
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
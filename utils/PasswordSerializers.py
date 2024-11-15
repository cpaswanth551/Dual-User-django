from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
import random
import os

from accounts.models import PasswordResetToken, WebUser
from medwb_admins.models import AdminPasswordResetToken, AdminUser


class BaseForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = self.get_user_model().objects.get(email=value)
        except self.get_user_model().DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def get_user_model(self):
        raise NotImplementedError("Subclasses must implement get_user_model()")

    def get_token_model(self):
        raise NotImplementedError("Subclasses must implement get_token_model()")

    def save(self):
        user = self.user
        token = str(format(random.randint(0, 999999), "06d"))

        self.get_token_model().objects.create(user=self.user, token=token)
        reset_url = (
            f"{os.environ.get('PASSWORD_RESET_BASE_URL')}/reset-password/{token}"
        )

        send_mail(
            subject="Password Reset Request",
            message=f"""
            Hello {user.username},
            You requested to reset your password. Use the following url to reset your password:
            URL : {reset_url}
            This token will expire in 24 hours.
            If you didn't request this, please ignore this email.
            Thanks,
            MedWB Team :)
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True


class WebUserForgotPasswordSerializer(BaseForgotPasswordSerializer):
    def get_user_model(self):
        return WebUser

    def get_token_model(self):
        return PasswordResetToken


class AdminUserForgotPasswordSerializer(BaseForgotPasswordSerializer):
    def get_user_model(self):
        return AdminUser

    def get_token_model(self):
        return AdminPasswordResetToken


class BaseResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def get_user_model(self):
        raise NotImplementedError("Subclasses must implement get_user_model()")

    def get_token_model(self):
        raise NotImplementedError("Subclasses must implement get_token_model()")

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        try:
            token_obj = self.get_token_model().objects.get(token=attrs["token"])
            if not token_obj.is_valid():
                raise serializers.ValidationError(
                    {"token": "Token has expired or already been used"}
                )

            if not isinstance(token_obj.user, self.get_user_model()):
                raise serializers.ValidationError(
                    {"token": "Invalid token for this user type"}
                )

            self.token_obj = token_obj
            self.user = token_obj.user
        except self.get_token_model().DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid reset token"})

        return attrs

    def save(self):
        self.user.set_password(self.validated_data["password"])
        self.user.save()
        self.token_obj.is_used = True
        self.token_obj.save()
        return self.user


class WebUserResetPasswordSerializer(BaseResetPasswordSerializer):
    def get_user_model(self):
        return WebUser

    def get_token_model(self):
        return PasswordResetToken


class AdminUserResetPasswordSerializer(BaseResetPasswordSerializer):
    def get_user_model(self):
        return AdminUser

    def get_token_model(self):
        return AdminPasswordResetToken

import os
import random
import uuid
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import PasswordResetToken, WebUser
from django.core.mail import send_mail


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = WebUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
        ]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class RegisterationSeriailizer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = WebUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        attrs.pop("confirm_password", None)
        attrs["password"] = make_password(attrs["password"])
        return attrs

    def validate_email(self, value):
        if WebUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if WebUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value


# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         try:
#             self.user = WebUser.objects.get(email=value)
#         except WebUser.DoesNotExist:
#             raise serializers.ValidationError("No user found with this email address.")
#         return value

#     def save(self):
#         user = self.user

#         token = str(format(random.randint(0, 999999), "06d"))

#         PasswordResetToken.objects.create(user=user, token=token)
#         reset_url = (
#             f"{os.environ.get('PASSWORD_RESET_BASE_URL')}/reset-password/{token}"
#         )

#         send_mail(
#             subject="Password Reset Request",
#             message=f"""
#             Hello {user.username},
            
#             You requested to reset your password. Use the following url to reset your password:
            
#             URL : {reset_url}
            
#             This token will expire in 24 hours.
            
#             If you didn't request this, please ignore this email.
            
#             Thanks,
#             MedWB Team :)
#             """,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )
#         return True


# class ResetPasswordSerializer(serializers.Serializer):
#     token = serializers.CharField()
#     password = serializers.CharField(min_length=8, write_only=True)
#     confirm_password = serializers.CharField(min_length=8, write_only=True)

#     def validate(self, attrs):
#         if attrs["password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError(
#                 {"password": "Password fields didn't match."}
#             )

#         try:
#             token_obj = PasswordResetToken.objects.get(token=attrs["token"])
#             if not token_obj.is_valid():
#                 raise serializers.ValidationError(
#                     {"token": "Token has expired or already been used"}
#                 )
#             self.token_obj = token_obj
#             self.user = token_obj.user
#         except PasswordResetToken.DoesNotExist:
#             raise serializers.ValidationError({"token": "Invalid reset token"})

#         return attrs

#     def save(self):

#         self.user.set_password(self.validated_data["password"])
#         self.user.save()

#         self.token_obj.is_used = True
#         self.token_obj.save()

#         return self.user

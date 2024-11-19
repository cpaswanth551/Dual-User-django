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
        normalized_email = value.lower().strip()
        if WebUser.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if WebUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

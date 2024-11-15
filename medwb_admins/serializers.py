from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from medwb_admins.models import AdminRole, AdminUser


class AdminUserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = AdminUser
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        admin_role, created = AdminRole.objects.get_or_create(name="RegularAdmin")
        attrs["admin_role"] = admin_role

        attrs.pop("confirm_password", None)
        attrs["password"] = make_password(attrs["password"])
        attrs["is_staff"] = True
        attrs["is_superuser"] = False
        attrs["is_active"] = False
        return attrs


class AdminRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminRole
        fields = ["name"]


class RoleDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminRole
        fields = ["id", "name"]


class AdminUserSerializer(serializers.ModelSerializer):
    admin_role = RoleDisplaySerializer(read_only=True)

    class Meta:
        model = AdminUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "admin_role",
            "password",
        ]

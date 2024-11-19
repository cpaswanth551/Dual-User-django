from rest_framework.permissions import BasePermission

from medwb_admins.models import AdminUser


class AuthPermission(BasePermission):
    ACTION_PERMISSIONS = {
        "list": "list",
        "retrieve": "view",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        role = user.role.name

        if role.lower() == "superuser":
            return True

        action = self.ACTION_PERMISSIONS.get(view.action)
        if not action:
            return False

        model_name = view.queryset.model.__name__.lower()
        permission_codename = f"{action}_{model_name}"

        if user.role.permissions.filter(codename=permission_codename).exists():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        role = user.role.name

        if role.lower() == "superuser":
            return True

        if isinstance(obj, AdminUser) and obj.id == user.id:
            return True

        action = self.ACTION_PERMISSIONS.get(view.action)
        if not action:
            return False

        model_name = obj.__class__.__name__.lower()
        permission_codename = f"{action}_{model_name}"

        if user.role.permissions.filter(codename=permission_codename).exists():
            return True
        return False

from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, AbstractBaseUser
from django.contrib.auth.models import BaseUserManager


class UserBase(AbstractBaseUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        abstract = True


class AdminRole(models.Model):
    name = models.CharField(max_length=250, null=False, blank=False, unique=True)


class AdminHasPermission(models.Model):
    permissions = models.ManyToManyField(Permission, related_name="permission")
    role_id = models.ForeignKey(
        AdminRole, related_name="adminrole", on_delete=models.CASCADE
    )


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("admin_role", self.get_or_create_superuser_role())
        return self.create_user(username, email, password, **extra_fields)

    def get_or_create_superuser_role(self):
        superuser_role, created = AdminRole.objects.get_or_create(name="Superadmin")
        if created:

            permissions = Permission.objects.all()
            print(permissions)
            for permission in permissions:
                AdminHasPermission.objects.create(
                    role_id=superuser_role, permissions=permission
                )
        return superuser_role


class AdminUser(UserBase):
    admin_role = models.ForeignKey(
        AdminRole, related_name="has_permission", on_delete=models.CASCADE
    )
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    objects = UserManager()

    class Meta:
        db_table = "admin_user"
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"

    @property
    def is_superadmin(self):
        return self.admin_role.name == "Superadmin"

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_superuser = self.is_superadmin
        super().save(*args, **kwargs)


class AdminPasswordResetToken(models.Model):
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=150, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and self.created_at >= timezone.now() - timedelta(
            hours=24
        )

    class Meta:
        db_table = "admin_password_reset_tokens"

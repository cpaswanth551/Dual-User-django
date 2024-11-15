from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission, AbstractBaseUser


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
    email = models.EmailField(_("email address"), blank=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
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
    REQUIRED_FIELDS = ["email", "password"]

    class Meta:
        abstract = True


class WebUser(UserBase):

    USER_TYPE = [
        ("supervisor", "Supervisor"),
        ("undersigned", "Undersigned"),
        ("peer", "Peer"),
    ]
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default="peer")

    def save(self, *args, **kwargs):
        if self.user_type == "supervisor":
            self.is_staff = True
        self.is_superuser = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = "web_user"
        verbose_name = "Web User"
        verbose_name_plural = "Web Users"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(WebUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=150, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and self.created_at >= timezone.now() - timedelta(
            hours=24
        )

    class Meta:
        db_table = "password_reset_tokens"

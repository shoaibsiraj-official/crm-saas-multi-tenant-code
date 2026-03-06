"""
accounts/models.py
Multi-tenant custom user model
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class RoleChoices(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", _("Super Admin")
    ORG_ADMIN   = "ORG_ADMIN",   _("Organization Admin")
    MANAGER     = "MANAGER",     _("Manager")
    MEMBER      = "MEMBER",      _("Member")


class User(AbstractBaseUser, PermissionsMixin):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email      = models.EmailField(_("email address"), unique=True, db_index=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name  = models.CharField(_("last name"), max_length=150, blank=True)

    role = models.CharField(
        _("role"),
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBER,
        db_index=True,
    )

    # Multi-tenancy (FK — Django automatically provides organization_id column)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        db_index=True,
        verbose_name=_("organization"),
    )

    is_active   = models.BooleanField(_("active"), default=True, db_index=True)
    is_staff    = models.BooleanField(_("staff status"), default=False)
    is_verified = models.BooleanField(_("email verified"), default=False, db_index=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name        = _("user")
        verbose_name_plural = _("users")
        ordering            = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["role", "organization"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["organization", "role", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def has_role(self, *roles) -> bool:
        return self.role in roles


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------

class AuditLog(models.Model):
    class EventType(models.TextChoices):
        LOGIN           = "LOGIN", _("Login")
        LOGOUT          = "LOGOUT", _("Logout")
        REGISTER        = "REGISTER", _("Register")
        PASSWORD_RESET  = "PASSWORD_RESET", _("Password Reset")
        PASSWORD_CHANGE = "PASSWORD_CHANGE", _("Password Change")
        TOKEN_REFRESH   = "TOKEN_REFRESH", _("Token Refresh")
        FAILED_LOGIN    = "FAILED_LOGIN", _("Failed Login")

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    email      = models.EmailField(blank=True)
    event_type = models.CharField(max_length=30, choices=EventType.choices, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata   = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["user", "event_type"]),
            models.Index(fields=["email", "event_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} - {self.email} at {self.created_at}"


class EmailVerificationToken(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="verification_token"
    )
    token      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"Verification token for {self.user.email}"


class PasswordResetToken(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Password reset token for {self.user.email}"
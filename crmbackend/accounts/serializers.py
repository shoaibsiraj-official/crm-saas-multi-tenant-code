"""
accounts/serializers.py  (updated — adds org_name to RegisterSerializer)
"""

import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import User


def validate_strong_password(value: str) -> str:
    try:
        validate_password(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(list(exc.messages))

    if not re.search(r"[A-Z]", value):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"\d", value):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise serializers.ValidationError("Password must contain at least one special character.")
    return value


class RegisterSerializer(serializers.Serializer):
    email            = serializers.EmailField(max_length=254)
    password         = serializers.CharField(
        write_only=True, min_length=8, validators=[validate_strong_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    first_name       = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name        = serializers.CharField(max_length=150, required=False, allow_blank=True)
    # NEW: optional org name; auto-derived from email domain if omitted
    org_name         = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_email(self, value):
        return value.lower().strip()

    def validate(self, data):
        if data["password"] != data.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return data


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token                = serializers.UUIDField()
    new_password         = serializers.CharField(
        write_only=True, min_length=8, validators=[validate_strong_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if str(data["new_password"]) != str(data.pop("new_password_confirm")):
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name         = serializers.ReadOnlyField()
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, allow_null=True
    )
    organization_slug = serializers.CharField(
        source="organization.slug", read_only=True, allow_null=True
    )

    class Meta:
        model  = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "organization",
            "organization_name",
            "organization_slug",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "email", "role", "organization", "organization_name",
            "organization_slug", "is_active", "is_verified", "created_at", "updated_at",
        ]
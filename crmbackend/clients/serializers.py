"""
clients/serializers.py

Four-serializer pattern for the Client resource:

  ClientListSerializer     — lean, for paginated list responses
  ClientDetailSerializer   — full record + nested org/user context
  ClientCreateSerializer   — validated create payload
  ClientUpdateSerializer   — all-optional PATCH payload with "at least one field" rule

No business logic lives here — just shape + field-level validation.
Organization is NEVER accepted from the client payload; it is always
injected from request.user in the service / view layer.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Client, ClientStatus

User = get_user_model()


# ---------------------------------------------------------------------------
# Shared micro-serializer
# ---------------------------------------------------------------------------

class CreatedBySerializer(serializers.ModelSerializer):
    """Minimal user snippet embedded in detail responses."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model        = User
        fields       = ["id", "email", "full_name"]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# 1. ClientListSerializer  — lean, list-view optimised
# ---------------------------------------------------------------------------

class ClientListSerializer(serializers.ModelSerializer):
    """
    Used for GET /clients/ responses.
    Intentionally omits heavy text fields (address, notes) to keep
    list payloads small — callers fetch the detail view when needed.
    """

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model  = Client
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "company_name",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# 2. ClientDetailSerializer  — full record + nested context
# ---------------------------------------------------------------------------

class ClientDetailSerializer(serializers.ModelSerializer):
    """
    Used for GET /clients/<id>/ responses.
    Embeds organization name and creator info without exposing sensitive data.
    """

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )
    created_by    = CreatedBySerializer(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model  = Client
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "company_name",
            "address",
            "notes",
            "status",
            "status_display",
            "organization",        # FK id
            "organization_name",   # denormalized name
            "created_by",          # nested snippet
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# 3. ClientCreateSerializer  — validated create payload
# ---------------------------------------------------------------------------

class ClientCreateSerializer(serializers.Serializer):
    """
    Validates POST /clients/ payload.
    `organization` is NEVER accepted here — always injected from request.user.
    """

    name         = serializers.CharField(max_length=255)
    email        = serializers.EmailField()
    phone        = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    address      = serializers.CharField(required=False, allow_blank=True, default="")
    notes        = serializers.CharField(required=False, allow_blank=True, default="")
    status       = serializers.ChoiceField(
        choices=ClientStatus.choices,
        default=ClientStatus.ACTIVE,
        required=False,
    )

    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def validate_email(self, value: str) -> str:
        return value.lower().strip()


# ---------------------------------------------------------------------------
# 4. ClientUpdateSerializer  — all-optional PATCH payload
# ---------------------------------------------------------------------------

class ClientUpdateSerializer(serializers.Serializer):
    """
    Validates PATCH /clients/<id>/ payload.
    All fields are optional; at least one must be provided.
    Email uniqueness within the org is checked in the view after
    this serializer passes (needs the org context the serializer doesn't have).
    """

    name         = serializers.CharField(max_length=255, required=False)
    email        = serializers.EmailField(required=False)
    phone        = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    address      = serializers.CharField(required=False, allow_blank=True)
    notes        = serializers.CharField(required=False, allow_blank=True)
    status       = serializers.ChoiceField(choices=ClientStatus.choices, required=False)

    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def validate_email(self, value: str) -> str:
        return value.lower().strip()

    def validate(self, data: dict) -> dict:
        if not data:
            raise serializers.ValidationError(
                "At least one field must be provided for an update."
            )
        return data
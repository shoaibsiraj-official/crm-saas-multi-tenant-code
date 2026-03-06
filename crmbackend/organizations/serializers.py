"""
organizations/serializers.py

Serializers handle input validation only.  No business logic lives here
— that belongs in services.py.

Conventions:
  • Read serializers (output)  → ModelSerializer with explicit fields
  • Write serializers (input)  → Serializer with explicit validation
  • Nested reads use a slimmer serializer to avoid over-fetching
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Organization, OrganizationInvite, SubscriptionPlan,Contact

User = get_user_model()


# ---------------------------------------------------------------------------
# Shared / nested
# ---------------------------------------------------------------------------

class OrganizationMemberSerializer(serializers.ModelSerializer):
    """
    Lightweight user representation used inside organization responses.
    Deliberately omits sensitive fields (password hash, tokens, etc.).
    """

    full_name = serializers.ReadOnlyField()

    class Meta:
        model  = User
        fields = [
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_verified",
            "created_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class OrganizationSerializer(serializers.ModelSerializer):
    """Full organization read representation (returned to org admins)."""

    member_count    = serializers.IntegerField(read_only=True)
    seats_remaining = serializers.SerializerMethodField()
    plan_display    = serializers.CharField(
        source="get_subscription_plan_display", read_only=True
    )

    class Meta:
        model  = Organization
        fields = [
            "id",
            "name",
            "slug",
            "subscription_plan",
            "plan_display",
            "seat_limit",
            "member_count",
            "seats_remaining",
            "is_active",
            "billing_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "subscription_plan",   # changed via billing flow, not this API
            "seat_limit",          # set by billing flow
            "member_count",
            "seats_remaining",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_seats_remaining(self, obj) -> int | str:
        return obj.seats_remaining()


class OrganizationPublicSerializer(serializers.ModelSerializer):
    """Slim read-only view exposed to regular members (no billing details)."""

    plan_display = serializers.CharField(
        source="get_subscription_plan_display", read_only=True
    )

    class Meta:
        model  = Organization
        fields = ["id", "name", "slug", "subscription_plan", "plan_display", "created_at"]
        read_only_fields = fields


class OrganizationUpdateSerializer(serializers.Serializer):
    """
    Validates PATCH /api/organizations/update/ payload.
    Only exposes fields an ORG_ADMIN is permitted to change.
    """

    name          = serializers.CharField(max_length=255, required=False)
    billing_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_name(self, value: str) -> str:
        return value.strip()


# ---------------------------------------------------------------------------
# Invite
# ---------------------------------------------------------------------------

INVITABLE_ROLES = {"ORG_ADMIN", "MANAGER", "MEMBER"}


class OrganizationInviteSerializer(serializers.ModelSerializer):
    """Read representation of a pending/historical invite."""

    invited_by_email = serializers.EmailField(
        source="invited_by.email", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model  = OrganizationInvite
        fields = [
            "id",
            "email",
            "role",
            "status",
            "invited_by_email",
            "organization_name",
            "expires_at",
            "accepted_at",
            "created_at",
        ]
        read_only_fields = fields


class InviteCreateSerializer(serializers.Serializer):
    """
    Validates POST /api/organizations/invite/ payload.

    Business rules enforced here (structural); seat limits etc. are
    enforced in the service layer where the DB state is checked atomically.
    """

    email = serializers.EmailField()
    role  = serializers.ChoiceField(choices=list(INVITABLE_ROLES), default="MEMBER")

    def validate_email(self, value: str) -> str:
        return value.lower().strip()

    def validate_role(self, value: str) -> str:
        if value not in INVITABLE_ROLES:
            raise serializers.ValidationError(
                f"Role must be one of: {', '.join(sorted(INVITABLE_ROLES))}"
            )
        return value


class InviteAcceptSerializer(serializers.Serializer):
    """Validates POST /api/organizations/invite/accept/ payload."""

    token = serializers.UUIDField()


class MemberRoleUpdateSerializer(serializers.Serializer):
    """
    Validates PATCH /api/organizations/members/<id>/role/ payload.
    ORG_ADMIN cannot elevate a member above their own role.
    """

    role = serializers.ChoiceField(choices=list(INVITABLE_ROLES))

    def validate_role(self, value: str) -> str:
        request = self.context.get("request")
        if not request:
            return value
        requester_role = request.user.role
        from .permissions import ROLE_HIERARCHY
        if ROLE_HIERARCHY.get(value, 0) > ROLE_HIERARCHY.get(requester_role, 0):
            raise serializers.ValidationError(
                "You cannot assign a role higher than your own."
            )
        return value


class MemberRemoveSerializer(serializers.Serializer):
    """Validates DELETE /api/organizations/members/<id>/ payload (target user id)."""

    user_id = serializers.UUIDField()


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by"]
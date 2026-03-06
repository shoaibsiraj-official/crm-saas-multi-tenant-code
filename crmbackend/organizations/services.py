"""
organizations/services.py
"""

import logging
import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import InviteStatus, Organization, OrganizationInvite
from .tasks import send_invite_email

logger = logging.getLogger(__name__)

# -----------------------------
# TYPE SAFE USER IMPORT
# -----------------------------
if TYPE_CHECKING:
    from accounts.models import User

INVITE_EXPIRY_HOURS = getattr(settings, "INVITE_EXPIRY_HOURS", 72)

PLAN_SEAT_LIMITS = getattr(
    settings,
    "PLAN_SEAT_LIMITS",
    {
        "FREE": 5,
        "PRO": 50,
        "ENTERPRISE": -1,
    },
)

# -----------------------------
# Custom Exceptions
# -----------------------------
class OrganizationError(Exception):
    pass


class SeatLimitExceeded(OrganizationError):
    pass


class InviteError(OrganizationError):
    pass


class PermissionError(OrganizationError):
    pass


class NotFoundError(OrganizationError):
    pass


# -----------------------------
# Organization Lifecycle
# -----------------------------
@transaction.atomic
def create_organization_for_user(user, org_name: str = "") -> Organization:
    if not org_name:
        domain = user.email.split("@")[-1].split(".")[0]
        org_name = f"{domain.capitalize()}'s Organization"

    org = Organization.objects.create(
        name=org_name,
        billing_email=user.email,
        seat_limit=PLAN_SEAT_LIMITS["FREE"],
    )

    user.organization = org
    user.role = "ORG_ADMIN"
    user.save(update_fields=["organization", "role", "updated_at"])

    logger.info(
        "org_created org_id=%s org_name=%r user_id=%s",
        org.id, org.name, user.id,
    )
    return org


@transaction.atomic
def update_organization(org: Organization, validated_data: dict) -> Organization:
    allowed = {"name", "billing_email"}

    for field, value in validated_data.items():
        if field in allowed:
            setattr(org, field, value)

    if "name" in validated_data:
        org.slug = org._unique_slug()

    org.save(update_fields=list(validated_data.keys()) + ["updated_at"])

    logger.info("org_updated org_id=%s", org.id)
    return org


# -----------------------------
# Member Management
# -----------------------------
def get_org_members(org: Organization):
    UserModel = get_user_model()
    return (
        UserModel.objects.filter(organization=org, is_active=True)
        .order_by("created_at")
        .select_related("organization")
    )


@transaction.atomic
def change_member_role(
    org: Organization,
    target_user_id: str,
    new_role: str,
    requesting_user,
) -> "User":

    from .permissions import ROLE_HIERARCHY
    UserModel = get_user_model()

    try:
        target = UserModel.objects.select_for_update().get(
            id=target_user_id,
            organization=org,
            is_active=True,
        )
    except UserModel.DoesNotExist:
        raise NotFoundError("Member not found.")

    if target.id == requesting_user.id:
        raise PermissionError("You cannot change your own role.")

    requester_level = ROLE_HIERARCHY.get(requesting_user.role, 0)
    target_level = ROLE_HIERARCHY.get(target.role, 0)
    new_level = ROLE_HIERARCHY.get(new_role, 0)

    if target_level >= requester_level and requesting_user.role != "SUPER_ADMIN":
        raise PermissionError("Cannot modify equal/higher role.")

    if new_level > requester_level:
        raise PermissionError("Cannot assign higher role.")

    old_role = target.role
    target.role = new_role
    target.save(update_fields=["role", "updated_at"])

    logger.info(
        "member_role_changed org_id=%s user_id=%s old=%s new=%s by=%s",
        org.id, target.id, old_role, new_role, requesting_user.id,
    )

    return target


@transaction.atomic
def remove_member(
    org: Organization,
    target_user_id: str,
    requesting_user,
) -> None:

    from .permissions import ROLE_HIERARCHY
    UserModel = get_user_model()

    try:
        target = UserModel.objects.select_for_update().get(
            id=target_user_id,
            organization=org,
            is_active=True,
        )
    except UserModel.DoesNotExist:
        raise NotFoundError("Member not found.")

    # ❌ Prevent self removal
    if target.id == requesting_user.id:
        raise PermissionError("Cannot remove yourself.")

    requester_level = ROLE_HIERARCHY.get(requesting_user.role, 0)
    target_level = ROLE_HIERARCHY.get(target.role, 0)

    # ❌ Cannot remove equal or higher role
    if target_level >= requester_level and requesting_user.role != "SUPER_ADMIN":
        raise PermissionError("Cannot remove equal/higher role.")

    # 🔥 Prevent removing last admin
    if target.role == "ORG_ADMIN":
        active_admins = (
            UserModel.objects.filter(
                organization=org,
                role="ORG_ADMIN",
                is_active=True,
            )
            .select_for_update()
            .count()
        )

        if active_admins <= 1:
            raise PermissionError("You cannot remove the last admin.")

    # Soft delete member
    target.is_active = False
    target.organization = None
    target.save(update_fields=["is_active", "organization", "updated_at"])

    logger.info(
        "member_removed org_id=%s user_id=%s by=%s",
        org.id, target.id, requesting_user.id,
    )


# -----------------------------
# Invite Flow
# -----------------------------
@transaction.atomic
def invite_member(
    org: Organization,
    email: str,
    role: str,
    invited_by,
) -> OrganizationInvite:

    UserModel = get_user_model()
    org = Organization.objects.select_for_update().get(pk=org.pk)

    if UserModel.objects.filter(
        email=email,
        organization=org,
        is_active=True,
    ).exists():
        raise InviteError("User already member.")

    if org.seat_limit != -1:
        active_members = org.members.filter(is_active=True).count()
        pending_invites = org.invites.filter(
            status=InviteStatus.PENDING,
            expires_at__gt=timezone.now(),
        ).count()

        if active_members + pending_invites >= org.seat_limit:
            raise SeatLimitExceeded("Seat limit reached.")

    existing = OrganizationInvite.objects.filter(
        organization=org,
        email=email,
        status=InviteStatus.PENDING,
    ).first()

    if existing:
        existing.token = uuid.uuid4()
        existing.role = role
        existing.invited_by = invited_by
        existing.expires_at = timezone.now() + timedelta(
            hours=INVITE_EXPIRY_HOURS
        )
        existing.save()
        invite = existing
    else:
        invite = OrganizationInvite.objects.create(
            organization=org,
            invited_by=invited_by,
            email=email,
            role=role,
            expires_at=timezone.now() + timedelta(
                hours=INVITE_EXPIRY_HOURS
            ),
        )

    send_invite_email.delay(str(invite.id))
    return invite

@transaction.atomic
def accept_invite(token: uuid.UUID, user) -> Organization:
    UserModel = get_user_model()

    try:
        invite = OrganizationInvite.objects.select_for_update().select_related(
            "organization"
        ).get(
            token=token,
            status=InviteStatus.PENDING
        )
    except OrganizationInvite.DoesNotExist:
        raise InviteError("Invalid or already-used invite token.")

    if invite.expires_at <= timezone.now():
        invite.status = InviteStatus.EXPIRED
        invite.save(update_fields=["status"])
        raise InviteError("This invite has expired.")

    if invite.email.lower() != user.email.lower():
        raise InviteError("Invite email does not match your account.")

    org = invite.organization

    # Seat limit check
    if org.seat_limit != -1:
        if org.members.filter(is_active=True).count() >= org.seat_limit:
            raise SeatLimitExceeded("Seat limit reached.")

    # Assign user
    user.organization = org
    user.role = invite.role
    user.save(update_fields=["organization", "role", "updated_at"])

    invite.status = InviteStatus.ACCEPTED
    invite.accepted_at = timezone.now()
    invite.save(update_fields=["status", "accepted_at", "updated_at"])


    logger.info(
        "invite_accepted org_id=%s user_id=%s role=%s",
        org.id, user.id, invite.role,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
    f"org_{org.id}",
    {
        "type": "member_joined",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
        },
    },
)
    return org

@transaction.atomic
def revoke_invite(invite_id: str, org: Organization, requesting_user) -> None:
    try:
        invite = OrganizationInvite.objects.select_for_update().get(
            id=invite_id,
            organization=org,
            status=InviteStatus.PENDING
        )
    except OrganizationInvite.DoesNotExist:
        raise NotFoundError("Pending invite not found.")

    invite.status = InviteStatus.REVOKED
    invite.save(update_fields=["status", "updated_at"])

    logger.info(
        "invite_revoked invite_id=%s org_id=%s by=%s",
        invite.id, org.id, requesting_user.id,
    )
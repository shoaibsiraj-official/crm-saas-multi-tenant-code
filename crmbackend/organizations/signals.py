"""
organizations/signals.py — Hooks for organization lifecycle events.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OrganizationInvite, InviteStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrganizationInvite)
def on_invite_status_change(sender, instance: OrganizationInvite, created: bool, **kwargs):
    """Log invite lifecycle transitions for audit trail."""
    if created:
        logger.info(
            "invite_created invite_id=%s org=%s email=%s role=%s",
            instance.id, instance.organization_id, instance.email, instance.role,
        )
    elif instance.status == InviteStatus.ACCEPTED:
        logger.info(
            "invite_accepted invite_id=%s org=%s email=%s",
            instance.id, instance.organization_id, instance.email,
        )
    elif instance.status == InviteStatus.REVOKED:
        logger.info(
            "invite_revoked invite_id=%s org=%s email=%s",
            instance.id, instance.organization_id, instance.email,
        )
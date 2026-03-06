"""
organizations/tasks.py — Async Celery tasks for organization emails.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="organizations.send_invite_email",
)
def send_invite_email(self, invite_id: str):
    """Send organization invitation email asynchronously."""
    from .models import OrganizationInvite  # avoid circular at module level

    try:
        invite = OrganizationInvite.objects.select_related(
            "organization", "invited_by"
        ).get(id=invite_id)
    except OrganizationInvite.DoesNotExist:
        logger.error("send_invite_email: invite %s not found", invite_id)
        return

    accept_url = f"{settings.FRONTEND_URL}/accept-invite/{invite.token}"

    inviter_name = (
        invite.invited_by.full_name if invite.invited_by else "Your organization"
    )

    subject = f"You've been invited to join {invite.organization.name}"

    html_message = render_to_string(
        "emails/organization_invite.html",
        {
            "invite":       invite,
            "inviter_name": inviter_name,
            "accept_url":   accept_url,
            "expiry_hours": settings.INVITE_EXPIRY_HOURS if hasattr(settings, "INVITE_EXPIRY_HOURS") else 72,
        },
    )
    plain_message = (
        f"Hi,\n\n"
        f"{inviter_name} has invited you to join {invite.organization.name} "
        f"as {invite.role}.\n\n"
        f"Accept your invitation here:\n{accept_url}\n\n"
        f"This link expires in 72 hours."
    )

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invite.email],
            fail_silently=False,
        )
        logger.info("invite_email_sent invite_id=%s to=%s", invite_id, invite.email)
    except Exception as exc:
        logger.exception(
            "invite_email_failed invite_id=%s to=%s err=%s", invite_id, invite.email, exc
        )
        raise self.retry(exc=exc)
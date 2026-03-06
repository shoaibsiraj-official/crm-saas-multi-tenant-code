"""
Celery tasks for asynchronous email delivery.
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
    name="accounts.send_verification_email",
)
def send_verification_email(self, user_id: str, token: str):
    """Send an email verification link to the newly registered user."""
    from .models import User  # avoid circular imports at module level

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("send_verification_email: User %s not found", user_id)
        return

    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email?token={token}"
    )

    subject = "Verify your email address"
    html_message = render_to_string(
        "emails/verify_email.html",
        {"user": user, "verification_url": verification_url},
    )
    plain_message = (
        f"Hi {user.full_name},\n\n"
        f"Please verify your email by visiting:\n{verification_url}\n\n"
        f"This link expires in {settings.EMAIL_VERIFICATION_EXPIRY_HOURS} hours."
    )

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Verification email sent to %s", user.email)
    except Exception as exc:
        logger.exception("Failed to send verification email to %s: %s", user.email, exc)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="accounts.send_password_reset_email",
)
def send_password_reset_email(self, user_id: str, token: str):
    """Send a password reset link."""
    from .models import User

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("send_password_reset_email: User %s not found", user_id)
        return

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    subject = "Reset your password"
    html_message = render_to_string(
        "emails/password_reset.html",
        {"user": user, "reset_url": reset_url},
    )
    plain_message = (
        f"Hi {user.full_name},\n\n"
        f"Reset your password by visiting:\n{reset_url}\n\n"
        f"This link expires in {settings.PASSWORD_RESET_EXPIRY_HOURS} hours.\n"
        f"If you didn't request this, please ignore this email."
    )

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Password reset email sent to %s", user.email)
    except Exception as exc:
        logger.exception("Failed to send reset email to %s: %s", user.email, exc)
        raise self.retry(exc=exc)
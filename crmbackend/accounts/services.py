"""
accounts/services.py  (updated for multi-tenant organization support)

Key change: register_user() now calls organizations.services.create_organization_for_user()
inside the same atomic transaction so user + org are always consistent.
"""

import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuditLog, EmailVerificationToken, PasswordResetToken, User
from .tokens import generate_tokens_for_user
from .tasks import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)

PASSWORD_RESET_EXPIRY_HOURS    = getattr(settings, "PASSWORD_RESET_EXPIRY_HOURS",    24)
EMAIL_VERIFICATION_EXPIRY_HOURS = getattr(settings, "EMAIL_VERIFICATION_EXPIRY_HOURS", 48)


# ---------------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------------

def _log_audit(
    event_type: str, request, user=None, email: str = "", metadata: dict = None
):
    AuditLog.objects.create(
        user=user,
        email=email or (user.email if user else ""),
        event_type=event_type,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        metadata=metadata or {},
    )


def _get_client_ip(request) -> str:
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


# ---------------------------------------------------------------------------
# Registration — creates user + organization atomically
# ---------------------------------------------------------------------------

class RegistrationError(Exception):
    pass


@transaction.atomic
def register_user(validated_data: dict, request) -> dict:
    """
    Full registration flow (single atomic transaction):
      1. Validate email uniqueness
      2. Create User (role=MEMBER initially)
      3. Create Organization (derived from email domain or provided name)
      4. Elevate user to ORG_ADMIN and link to org
      5. Create email verification token
      6. Dispatch async verification email
      7. Return JWT token pair

    The organization name can be supplied as `org_name` in validated_data,
    or is derived automatically from the email domain.
    """
    email = validated_data["email"].lower()

    if User.objects.filter(email=email).exists():
        raise RegistrationError("A user with this email already exists.")

    # Step 1: create bare user (no org yet — FK is nullable)
    user = User.objects.create_user(
        email=email,
        password=validated_data["password"],
        first_name=validated_data.get("first_name", ""),
        last_name=validated_data.get("last_name", ""),
        role="MEMBER",  # promoted to ORG_ADMIN inside create_organization_for_user
    )

    # Step 2: create org + promote user — all in the same transaction
    from organizations.services import create_organization_for_user
    org_name = validated_data.get("org_name", "")
    create_organization_for_user(user, org_name=org_name)

    # Step 3: email verification
    verification_token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=EMAIL_VERIFICATION_EXPIRY_HOURS),
    )
    send_verification_email.delay(str(user.id), str(verification_token.token))

    _log_audit(AuditLog.EventType.REGISTER, request, user=user)
    logger.info("user_registered email=%s org_id=%s", email, user.organization_id)

    # Refresh from DB so JWT claims include the newly assigned organization
    user.refresh_from_db()
    return generate_tokens_for_user(user)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class AuthenticationError(Exception):
    pass


def login_user(email: str, password: str, request) -> dict:
    user = authenticate(request=request, username=email.lower(), password=password)

    if user is None:
        _log_audit(
            AuditLog.EventType.FAILED_LOGIN,
            request,
            email=email,
            metadata={"reason": "invalid_credentials"},
        )
        logger.warning("failed_login email=%s", email)
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    _log_audit(AuditLog.EventType.LOGIN, request, user=user)
    logger.info("user_login email=%s", email)
    return {"user": user, "tokens": generate_tokens_for_user(user)}


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class LogoutError(Exception):
    pass


def logout_user(refresh_token_str: str, request, user) -> None:
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
    except TokenError as exc:
        raise LogoutError(str(exc))

    _log_audit(AuditLog.EventType.LOGOUT, request, user=user)
    logger.info("user_logout email=%s", user.email)


# ---------------------------------------------------------------------------
# Token Refresh
# ---------------------------------------------------------------------------

class TokenRefreshError(Exception):
    pass


def refresh_access_token(refresh_token_str: str, request) -> dict:
    try:
        old_refresh = RefreshToken(refresh_token_str)
        user_id     = old_refresh.payload.get("user_id")
        user        = User.objects.select_related("organization").get(id=user_id)
        old_refresh.blacklist()
        tokens = generate_tokens_for_user(user)
        _log_audit(AuditLog.EventType.TOKEN_REFRESH, request, user=user)
        return tokens
    except (TokenError, User.DoesNotExist) as exc:
        raise TokenRefreshError(str(exc))


# ---------------------------------------------------------------------------
# Password Reset
# ---------------------------------------------------------------------------

class PasswordResetError(Exception):
    pass


def initiate_password_reset(email: str, request) -> None:
    try:
        user = User.objects.get(email=email.lower(), is_active=True)
    except User.DoesNotExist:
        logger.info("password_reset_no_account email=%s", email)
        return  # silent — prevent enumeration

    PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

    reset_token = PasswordResetToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS),
    )
    send_password_reset_email.delay(str(user.id), str(reset_token.token))
    _log_audit(AuditLog.EventType.PASSWORD_RESET, request, user=user)
    logger.info("password_reset_initiated email=%s", email)


@transaction.atomic
def confirm_password_reset(token_str: str, new_password: str, request) -> None:
    try:
        token_uuid  = uuid.UUID(token_str)
        reset_token = PasswordResetToken.objects.select_related("user").get(
            token=token_uuid,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
    except (ValueError, PasswordResetToken.DoesNotExist):
        raise PasswordResetError("Invalid or expired password reset token.")

    user = reset_token.user
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])

    reset_token.is_used = True
    reset_token.save(update_fields=["is_used"])

    _log_audit(AuditLog.EventType.PASSWORD_CHANGE, request, user=user)
    logger.info("password_reset_complete email=%s", user.email)


# ---------------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------------

class EmailVerificationError(Exception):
    pass


@transaction.atomic
def verify_email(token_str: str) -> User:
    try:
        token_uuid   = uuid.UUID(token_str)
        verification = EmailVerificationToken.objects.select_related("user").get(
            token=token_uuid,
            expires_at__gt=timezone.now(),
        )
    except (ValueError, EmailVerificationToken.DoesNotExist):
        raise EmailVerificationError("Invalid or expired verification token.")

    user             = verification.user
    user.is_verified = True
    user.save(update_fields=["is_verified", "updated_at"])
    verification.delete()

    logger.info("email_verified email=%s", user.email)
    return user
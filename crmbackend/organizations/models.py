"""
organizations/models.py

Core multi-tenant models. Every resource in the system traces back to
an Organization. The architecture is designed for SaaS growth:
  - Slug-based addressing for clean URLs and external references
  - Subscription plan stored here so billing checks stay in one place
  - seat_limit drives per-plan capacity enforcement in services.py
  - OrganizationInvite handles the full invite → accept flow with expiry
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class SubscriptionPlan(models.TextChoices):
    FREE       = "FREE",       _("Free")
    PRO        = "PRO",        _("Pro")
    ENTERPRISE = "ENTERPRISE", _("Enterprise")


class InviteStatus(models.TextChoices):
    PENDING  = "PENDING",  _("Pending")
    ACCEPTED = "ACCEPTED", _("Accepted")
    EXPIRED  = "EXPIRED",  _("Expired")
    REVOKED  = "REVOKED",  _("Revoked")


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class Organization(models.Model):
    """
    The top-level tenant boundary. Every user belongs to exactly one
    organization; every resource is scoped to one organization.
    """

    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("URL-safe identifier, auto-generated from name if omitted."),
    )

    subscription_plan = models.CharField(
        _("subscription plan"),
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
        db_index=True,
    )

    # -1 means unlimited (ENTERPRISE shorthand — check in service layer)
    seat_limit = models.IntegerField(
        _("seat limit"),
        default=5,
        help_text=_("Maximum number of members. -1 = unlimited."),
    )

    is_active = models.BooleanField(_("active"), default=True, db_index=True)

    # Billing / external references — ready for Stripe, etc.
    billing_email     = models.EmailField(_("billing email"), blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _("organization")
        verbose_name_plural = _("organizations")
        ordering            = ["-created_at"]
        indexes = [
            models.Index(fields=["slug", "is_active"]),
            models.Index(fields=["subscription_plan", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def member_count(self) -> int:
        """Live count of active members (avoids annotation on hot paths)."""
        return self.members.filter(is_active=True).count()

    @property
    def has_seats_available(self) -> bool:
        if self.seat_limit == -1:
            return True
        return self.member_count < self.seat_limit

    def seats_remaining(self) -> int | str:
        if self.seat_limit == -1:
            return "unlimited"
        return max(0, self.seat_limit - self.member_count)

    def save(self, *args, **kwargs):
        # Auto-generate unique slug from name on first save
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self) -> str:
        base = slugify(self.name)
        slug = base
        qs   = Organization.objects.all()
        n    = 1
        while qs.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n   += 1
        return slug or f"org-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Organization Invite
# ---------------------------------------------------------------------------

class OrganizationInvite(models.Model):
    """
    Tracks email invitations sent by org admins. Supports:
      - Invite-by-email (recipient may not have an account yet)
      - Role assignment on acceptance
      - Expiry + revocation
      - Idempotent re-invite (reuses pending invite for same email+org)
    """

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invites",
    )
    email = models.EmailField(_("invited email"), db_index=True)
    role  = models.CharField(
        _("assigned role"),
        max_length=20,
        # imported at runtime to avoid circular — see __init__ note
        default="MEMBER",
    )

    token      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    status     = models.CharField(
        max_length=20,
        choices=InviteStatus.choices,
        default=InviteStatus.PENDING,
        db_index=True,
    )
    expires_at  = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _("organization invite")
        verbose_name_plural = _("organization invites")
        ordering            = ["-created_at"]
        # Prevent duplicate pending invites for the same email in one org
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "email"],
                condition=models.Q(status="PENDING"),
                name="unique_pending_invite_per_org_email",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["email", "status"]),
        ]

    def __str__(self) -> str:
        return f"Invite → {self.email} @ {self.organization.name} [{self.status}]"

    @property
    def is_valid(self) -> bool:
        from django.utils import timezone
        return self.status == InviteStatus.PENDING and self.expires_at > timezone.now()


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="contacts"
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_contacts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


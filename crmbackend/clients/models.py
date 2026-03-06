"""
clients/models.py

CRM Client model — scoped to an Organization (tenant boundary).

Design notes:
  ─ `organization` FK is indexed as the primary tenant filter on every query.
  ─ Composite indexes cover the most common CRM query shapes:
      * list all active clients in org  →  (organization, status, created_at)
      * search by email within org      →  (organization, email)
      * filter by creator               →  (organization, created_by)
  ─ `email` is NOT globally unique: the same contact email can exist in
    different organizations (common in CRM SaaS). Uniqueness is enforced
    per-organization via the UniqueConstraint below.
  ─ All optional contact fields use blank=True so the form layer treats them
    as optional without needing null=True on char fields (Django best practice).
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ClientStatus(models.TextChoices):
    ACTIVE   = "ACTIVE",   _("Active")
    INACTIVE = "INACTIVE", _("Inactive")


class Client(models.Model):
    # ── Identity ──────────────────────────────────────────────────────────────
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ── Tenant boundary ───────────────────────────────────────────────────────
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="clients",
        db_index=True,
        verbose_name=_("organization"),
    )

    # ── Core contact info ─────────────────────────────────────────────────────
    name = models.CharField(_("name"), max_length=255)

    email = models.EmailField(
        _("email"),
        db_index=True,
        help_text=_("Unique within the organization."),
    )

    phone = models.CharField(
        _("phone"),
        max_length=20,
        blank=True,
        default="",
    )

    company_name = models.CharField(
        _("company name"),
        max_length=255,
        blank=True,
        default="",
    )

    address = models.TextField(
        _("address"),
        blank=True,
        default="",
    )

    notes = models.TextField(
        _("notes"),
        blank=True,
        default="",
    )

    # ── Status ────────────────────────────────────────────────────────────────
    status = models.CharField(
        _("status"),
        max_length=10,
        choices=ClientStatus.choices,
        default=ClientStatus.ACTIVE,
        db_index=True,
    )

    # ── Authorship ────────────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_clients",
        verbose_name=_("created by"),
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _("client")
        verbose_name_plural = _("clients")
        ordering            = ["-created_at"]

        constraints = [
            # Prevent duplicate email addresses within the same organization
            models.UniqueConstraint(
                fields=["organization", "email"],
                name="unique_client_email_per_org",
            )
        ]

        indexes = [
            # Primary list + status filter
            models.Index(
                fields=["organization", "status", "-created_at"],
                name="client_org_status_created_idx",
            ),
            # Email lookup within tenant
            models.Index(
                fields=["organization", "email"],
                name="client_org_email_idx",
            ),
            # "Clients I created"
            models.Index(
                fields=["organization", "created_by"],
                name="client_org_creator_idx",
            ),
            # Company-based filtering
            models.Index(
                fields=["organization", "company_name"],
                name="client_org_company_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
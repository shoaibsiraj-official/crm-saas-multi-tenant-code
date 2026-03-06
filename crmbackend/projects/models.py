"""
projects/models.py
Clean, production-ready Projects domain models.
"""

import uuid
from django.conf import settings
from django.db import models

from clients.models import Client

from django.utils.translation import gettext_lazy as _


# ============================================================
# Choices
# ============================================================

class ProjectStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    COMPLETED = "COMPLETED", _("Completed")
    ARCHIVED = "ARCHIVED", _("Archived")


class TaskPriority(models.TextChoices):
    LOW = "LOW", _("Low")
    MEDIUM = "MEDIUM", _("Medium")
    HIGH = "HIGH", _("High")


class TaskStatus(models.TextChoices):
    TODO = "TODO", _("To Do")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    REVIEW = "REVIEW", _("In Review")
    DONE = "DONE", _("Done")


# ============================================================
# Soft Delete Managers
# ============================================================

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


# ============================================================
# Project
# ============================================================

class Project(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="projects",
        db_index=True,
    )
    client = models.ForeignKey(
    Client,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="projects"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.ACTIVE,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_projects",
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "is_deleted", "status"]),
            models.Index(fields=["organization", "created_by"]),
        ]

    def __str__(self):
        return f"{self.name} [{self.organization}]"

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()

    @property
    def progress(self) -> int:
        total = self.tasks.filter(is_deleted=False).count()
        if total == 0:
            return 0

        done = self.tasks.filter(
            status=TaskStatus.DONE,
            is_deleted=False
        ).count()

        return int((done / total) * 100)


# ============================================================
# Project Membership
# ============================================================

class ProjectMembership(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    is_active = models.BooleanField(default=True, db_index=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_assignments_made",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_user_membership",
            )
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["project", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.project.name}"


# ============================================================
# Task
# ============================================================

class Task(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="tasks",
        db_index=True,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    priority = models.CharField(
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        db_index=True,
    )

    # 🔥 Kanban ordering
    position = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Order inside a status column",
    )

    due_date = models.DateField(null=True, blank=True, db_index=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_tasks",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        ordering = ["status", "position"]
        indexes = [
            models.Index(fields=["project", "status", "position"]),
            models.Index(fields=["organization", "assigned_to", "is_deleted"]),
            models.Index(fields=["organization", "due_date", "status"]),
        ]

    def __str__(self):
        return f"{self.title} [{self.project.name}]"

    def save(self, *args, **kwargs):
        # Auto sync organization from project
        if not self.organization_id and self.project_id:
            self.organization_id = self.project.organization_id
        super().save(*args, **kwargs)


from clients.models import Client


"""
projects/services.py
Final stable service layer — fully compatible with views.py
"""

import logging
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.db.models import F, Max

from .models import Project, ProjectMembership, Task, ProjectStatus
from clients.models import Client

logger = logging.getLogger(__name__)
User = get_user_model()


# ============================================================
# DOMAIN EXCEPTIONS
# ============================================================

class ProjectError(Exception): pass
class ProjectNotFound(ProjectError): pass
class TaskNotFound(ProjectError): pass
class MemberNotFound(ProjectError): pass
class PermissionDenied(ProjectError): pass
class ValidationError(ProjectError): pass
class AlreadyMember(ProjectError): pass
class MemberInactive(ProjectError): pass
class CrossTenantError(ProjectError): pass


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _get_project_for_org(project_id, organization):
    try:
        return Project.objects.select_for_update().get(
            id=project_id,
            organization=organization,
            is_deleted=False
        )
    except Project.DoesNotExist:
        raise ProjectNotFound("Project not found.")


def _get_task_for_org(task_id, organization):
    try:
        return Task.objects.select_for_update().get(
            id=task_id,
            organization=organization,
            is_deleted=False
        )
    except Task.DoesNotExist:
        raise TaskNotFound("Task not found.")


def _get_org_user(user_id, organization):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise MemberNotFound("User not found.")

    if str(user.organization_id) != str(organization.id):
        raise CrossTenantError("User does not belong to your organization.")

    if not user.is_active:
        raise MemberInactive("Cannot assign inactive user.")

    return user


def _get_client_for_org(client_id, organization):
    if not client_id:
        return None

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise ValidationError("Client not found.")

    if str(client.organization_id) != str(organization.id):
        raise CrossTenantError("Client does not belong to your organization.")

    return client


# ============================================================
# PROJECT CRUD
# ============================================================

@transaction.atomic
def create_project(
    *,
    organization,
    name,
    description="",
    status=ProjectStatus.ACTIVE,
    created_by,
    client_id=None,
):

    client = _get_client_for_org(client_id, organization)

    project = Project.objects.create(
        organization=organization,
        name=name,
        description=description,
        status=status,
        created_by=created_by,
        client=client,
    )

    ProjectMembership.objects.create(
        project=project,
        user=created_by,
        assigned_by=created_by,
    )

    return project


@transaction.atomic
def update_project(
    *,
    project_id,
    organization,
    validated_data,
    updated_by,
):

    project = _get_project_for_org(project_id, organization)

    for field in ["name", "description", "status"]:
        if field in validated_data:
            setattr(project, field, validated_data[field])

    if "client" in validated_data:
        project.client = _get_client_for_org(
            validated_data.get("client"),
            organization
        )

    project.save()
    return project


@transaction.atomic
def delete_project(*, project_id, organization, deleted_by):

    project = _get_project_for_org(project_id, organization)

    Task.objects.filter(project=project).update(
        is_deleted=True,
        deleted_at=timezone.now(),
        deleted_by=deleted_by,
    )

    project.is_deleted = True
    project.deleted_at = timezone.now()
    project.deleted_by = deleted_by
    project.save()

    return None


# ============================================================
# MEMBER MANAGEMENT
# ============================================================

@transaction.atomic
def assign_member_to_project(
    *,
    project_id,
    organization,
    user_id,
    assigned_by,
):

    project = _get_project_for_org(project_id, organization)
    user = _get_org_user(user_id, organization)

    existing = ProjectMembership.objects.filter(
        project=project,
        user=user
    ).first()

    if existing and existing.is_active:
        raise AlreadyMember("User already assigned.")

    if existing:
        existing.is_active = True
        existing.save(update_fields=["is_active"])
        return existing

    return ProjectMembership.objects.create(
        project=project,
        user=user,
        assigned_by=assigned_by,
    )


@transaction.atomic
def remove_member_from_project(
    *,
    project_id,
    organization,
    user_id,
    removed_by,
):

    project = _get_project_for_org(project_id, organization)

    try:
        membership = ProjectMembership.objects.get(
            project=project,
            user_id=user_id,
            is_active=True,
        )
    except ProjectMembership.DoesNotExist:
        raise MemberNotFound("Membership not found.")

    membership.is_active = False
    membership.save(update_fields=["is_active"])


# ============================================================
# TASK MANAGEMENT
# ============================================================

@transaction.atomic
def create_task(
    *,
    project_id,
    organization,
    title,
    description="",
    assigned_to_id=None,
    priority="MEDIUM",
    status="TODO",
    due_date=None,
    created_by,
):

    project = _get_project_for_org(project_id, organization)

    assigned_to = None
    if assigned_to_id:
        assigned_to = _get_org_user(assigned_to_id, organization)

    last_position = (
        Task.objects
        .filter(project=project, status=status)
        .aggregate(Max("position"))
        .get("position__max")
    )

    next_position = (last_position or 0) + 1

    return Task.objects.create(
        organization=organization,
        project=project,
        title=title,
        description=description,
        assigned_to=assigned_to,
        priority=priority,
        status=status,
        due_date=due_date,
        created_by=created_by,
        position=next_position,
    )


@transaction.atomic
def update_task(
    *,
    task_id,
    organization,
    validated_data,
    updated_by,
):

    task = _get_task_for_org(task_id, organization)

    for field, value in validated_data.items():
        setattr(task, field, value)

    task.save()
    return task


@transaction.atomic
def change_task_status(
    *,
    task_id,
    organization,
    new_status,
    changed_by,
):

    task = _get_task_for_org(task_id, organization)
    task.status = new_status
    task.save(update_fields=["status", "updated_at"])
    return task


@transaction.atomic
def delete_task(
    *,
    task_id,
    organization,
    deleted_by,
):

    task = _get_task_for_org(task_id, organization)

    task.is_deleted = True
    task.deleted_at = timezone.now()
    task.deleted_by = deleted_by
    task.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "updated_at"])


# ============================================================
# QUERY HELPERS
# ============================================================

def get_projects_for_user(user):
    return Project.objects.filter(
        organization_id=user.organization_id,
        is_deleted=False
    ).select_related("created_by", "client")


def get_tasks_for_project(project_id, organization, user):
    return Task.objects.filter(
        project_id=project_id,
        organization=organization,
        is_deleted=False
    ).select_related("assigned_to", "created_by", "project")


# ============================================================
# TASK MOVE (KANBAN DRAG & DROP)
# ============================================================

@transaction.atomic
def move_task(task, new_status, new_position):
    """
    Move task inside same column or different column.
    Handles position reordering safely.
    """

    old_status = task.status
    old_position = task.position

    # If status changed (moving to another column)
    if old_status != new_status:

        # Close gap in old column
        Task.objects.filter(
            project=task.project,
            status=old_status,
            position__gt=old_position
        ).update(position=F("position") - 1)

        # Make space in new column
        Task.objects.filter(
            project=task.project,
            status=new_status,
            position__gte=new_position
        ).update(position=F("position") + 1)

        task.status = new_status
        task.position = new_position

    else:
        # Moving inside same column

        if new_position > old_position:
            Task.objects.filter(
                project=task.project,
                status=old_status,
                position__gt=old_position,
                position__lte=new_position
            ).update(position=F("position") - 1)

        elif new_position < old_position:
            Task.objects.filter(
                project=task.project,
                status=old_status,
                position__gte=new_position,
                position__lt=old_position
            ).update(position=F("position") + 1)

        task.position = new_position

    task.save(update_fields=["status", "position", "updated_at"])

    return task
"""
projects/permissions.py

Permission classes for the Projects domain.

Layer architecture (same as organizations/):
  1. IsOrgMember   — authenticated + has an org            (always first)
  2. Role checks   — ORG_ADMIN / MANAGER / MEMBER gates
  3. Object-level  — "does this object belong to my org?"
                     "am I a member of this project?"
                     "is this task assigned to me?"

Every object-level check is called via view.check_object_permissions(request, obj)
AFTER the row has been fetched. The view must always use get_queryset() that
filters by organization first — so a 404 is returned for cross-tenant objects,
and the object-level permission is a secondary defence.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated

# ── Role constants (mirrors accounts.models.RoleChoices) ──────────────────
SUPER_ADMIN = "SUPER_ADMIN"
ORG_ADMIN   = "ORG_ADMIN"
MANAGER     = "MANAGER"
MEMBER      = "MEMBER"

ROLE_HIERARCHY = {
    SUPER_ADMIN: 4,
    ORG_ADMIN:   3,
    MANAGER:     2,
    MEMBER:      1,
}

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def _role_gte(user_role: str, required_role: str) -> bool:
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class IsOrgMember(IsAuthenticated):
    """Authenticated user who belongs to an organization."""

    message = "You must be a member of an organization to access this resource."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return bool(request.user.organization_id)


# ---------------------------------------------------------------------------
# Role gates
# ---------------------------------------------------------------------------

class IsManagerOrAbove(IsOrgMember):
    """MANAGER, ORG_ADMIN, or SUPER_ADMIN."""

    message = "Manager or higher access required."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and _role_gte(
            request.user.role, MANAGER
        )


class IsOrgAdminOrAbove(IsOrgMember):
    """ORG_ADMIN or SUPER_ADMIN."""

    message = "Organization Admin access required."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and _role_gte(
            request.user.role, ORG_ADMIN
        )


# ---------------------------------------------------------------------------
# Project object-level permissions
# ---------------------------------------------------------------------------

class CanAccessProject(IsOrgMember):
    """
    View-level:  any org member.
    Object-level:
      ─ ORG_ADMIN / MANAGER: full access to all org projects.
      ─ MEMBER: read-only unless they are a project member.
    """

    message = "You do not have access to this project."

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Tenant boundary — hard fail for any other org
        if str(obj.organization_id) != str(user.organization_id):
            return False

        # Admins / managers see everything
        if _role_gte(user.role, MANAGER):
            return True

        # Members must be assigned to the project
        return obj.memberships.filter(user=user, is_active=True).exists()


class CanMutateProject(IsOrgMember):
    """
    Write operations on a Project (update, delete, assign member).
    Read allowed for any org member; writes restricted to MANAGER+.
    """

    message = "Only Managers and Admins can modify projects."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _role_gte(request.user.role, MANAGER)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if str(obj.organization_id) != str(user.organization_id):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _role_gte(user.role, MANAGER)


class CanDeleteProject(IsOrgMember):
    """Only ORG_ADMIN can delete a project."""

    message = "Only Organization Admins can delete projects."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and _role_gte(
            request.user.role, ORG_ADMIN
        )

    def has_object_permission(self, request, view, obj):
        if str(obj.organization_id) != str(request.user.organization_id):
            return False
        return _role_gte(request.user.role, ORG_ADMIN)


# ---------------------------------------------------------------------------
# Task object-level permissions
# ---------------------------------------------------------------------------

class CanAccessTask(IsOrgMember):
    """
    View-level:  any org member.
    Object-level:
      ─ MANAGER+: full access to all tasks in the org.
      ─ MEMBER: can only see tasks in projects they belong to.
    """

    message = "You do not have access to this task."

    def has_object_permission(self, request, view, obj):
        user = request.user

        if str(obj.organization_id) != str(user.organization_id):
            return False

        if _role_gte(user.role, MANAGER):
            return True

        # Member must belong to the task's project
        return obj.project.memberships.filter(user=user, is_active=True).exists()


class CanMutateTask(IsOrgMember):
    """
    Write operations on a Task.

    ─ MANAGER+: can update any task in the org.
    ─ MEMBER: can only update tasks assigned to themselves.
    ─ Only MANAGER+ can delete tasks.
    """

    message = "You do not have permission to modify this task."

    def has_object_permission(self, request, view, obj):
        user = request.user

        if str(obj.organization_id) != str(user.organization_id):
            return False

        if request.method in SAFE_METHODS:
            # Read — same as CanAccessTask
            if _role_gte(user.role, MANAGER):
                return True
            return obj.project.memberships.filter(user=user, is_active=True).exists()

        # Write
        if _role_gte(user.role, MANAGER):
            return True

        # Member can only touch tasks assigned to them
        return str(obj.assigned_to_id) == str(user.id)


class CanDeleteTask(IsOrgMember):
    """Only MANAGER+ can hard-delete / soft-delete a task."""

    message = "Only Managers and Admins can delete tasks."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and _role_gte(
            request.user.role, MANAGER
        )

    def has_object_permission(self, request, view, obj):
        if str(obj.organization_id) != str(request.user.organization_id):
            return False
        return _role_gte(request.user.role, MANAGER)
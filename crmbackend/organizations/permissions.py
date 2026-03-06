"""
organizations/permissions.py

Permission classes enforce two orthogonal concerns:

  1. TENANT ISOLATION  – a user may only ever touch their own org's data.
                         This is checked first; failing it gives 403.
  2. ROLE HIERARCHY    – within a tenant, roles gate write operations.
                         SUPER_ADMIN > ORG_ADMIN > MANAGER > MEMBER

Design rule: never leak information about other tenants.  A 403 is
returned even when the resource doesn't exist, to avoid enumeration.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated

# Role constants (mirrors accounts.models.RoleChoices)
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


def _role_gte(user_role: str, required_role: str) -> bool:
    """Return True if user_role is equal to or above required_role."""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


# ---------------------------------------------------------------------------
# Base: authenticated + belongs to an org
# ---------------------------------------------------------------------------

class IsOrgMember(IsAuthenticated):
    """
    Baseline: authenticated + assigned to an organization.
    All organization views should start with this (or a subclass).
    """

    message = "You must be a member of an organization to access this resource."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return bool(request.user.organization_id)


# ---------------------------------------------------------------------------
# Role gates (all also enforce IsOrgMember)
# ---------------------------------------------------------------------------

class IsOrgAdmin(IsOrgMember):
    """ORG_ADMIN or higher within the user's organization."""

    message = "Organization Admin access required."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and _role_gte(
            request.user.role, ORG_ADMIN
        )


class IsManager(IsOrgMember):
    """MANAGER or higher."""

    message = "Manager or higher access required."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and _role_gte(
            request.user.role, MANAGER
        )


class IsSuperAdmin(IsAuthenticated):
    """Platform-level super admin — bypasses tenant isolation."""

    message = "Super Admin access required."

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.role == SUPER_ADMIN
        )


# ---------------------------------------------------------------------------
# Object-level: same organization
# ---------------------------------------------------------------------------

class IsSameOrganization(IsOrgMember):
    """
    Object-level permission.  Grants access only when the target object
    belongs to the same organization as the requesting user.

    Usage:
        permission_classes = [IsSameOrganization]
        ...
        self.check_object_permissions(request, obj)
    """

    message = "You do not have permission to access resources from another organization."

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        if request.user.role == SUPER_ADMIN:
            return True
        target_org_id = getattr(obj, "organization_id", None) or getattr(
            getattr(obj, "organization", None), "id", None
        )
        return str(target_org_id) == str(request.user.organization_id)


# ---------------------------------------------------------------------------
# Composite: read-only for members, write for admins
# ---------------------------------------------------------------------------

class OrgAdminOrReadOnly(IsOrgMember):
    """
    Safe methods (GET, HEAD, OPTIONS) allowed for any org member.
    Mutating methods restricted to ORG_ADMIN+.
    """

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return _role_gte(request.user.role, ORG_ADMIN)
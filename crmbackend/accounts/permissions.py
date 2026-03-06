"""
Permission classes for role-based access control.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsVerified(IsAuthenticated):
    """Requires an authenticated user whose email is verified."""

    message = "Email verification required."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_verified


class IsSuperAdmin(IsAuthenticated):
    """Restricts access to SUPER_ADMIN role only."""

    message = "Super Admin access required."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == "SUPER_ADMIN"


class IsOrgAdmin(IsAuthenticated):
    """Allows SUPER_ADMIN or ORG_ADMIN."""

    message = "Organization Admin access required."

    ALLOWED_ROLES = {"SUPER_ADMIN", "ORG_ADMIN"}

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.role in self.ALLOWED_ROLES
        )


class IsManager(IsAuthenticated):
    """Allows SUPER_ADMIN, ORG_ADMIN, or MANAGER."""

    message = "Manager or higher access required."

    ALLOWED_ROLES = {"SUPER_ADMIN", "ORG_ADMIN", "MANAGER"}

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.role in self.ALLOWED_ROLES
        )


class IsSameOrganization(IsAuthenticated):
    """Object-level: user must belong to the same organization as the target."""

    message = "You do not have permission to access resources from another organization."

    def has_object_permission(self, request, view, obj):
        if not super().has_permission(request, view):
            return False
        if request.user.role == "SUPER_ADMIN":
            return True
        target_org = getattr(obj, "organization_id", None)
        return target_org and target_org == request.user.organization_id
"""
core/middleware.py

TenantContextMiddleware attaches the authenticated user's Organization
to `request.org` so views can access it without a DB call.

Also validates that the org is active — deactivated tenants get 403
on every request without special-casing every view.
"""

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class TenantContextMiddleware:
    """
    Attaches `request.org` for authenticated users with an organization.

    Placed AFTER AuthenticationMiddleware so `request.user` is resolved.
    Does NOT block unauthenticated requests — that's the job of
    permission classes on each view.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.org = None

        user = getattr(request, "user", None)
        if user and user.is_authenticated and user.organization_id:
            # Use select_related only on first access; subsequent accesses
            # hit the FK cache Django maintains on the instance.
            try:
                org = user.organization
                if org and not org.is_active:
                    logger.warning(
                        "tenant_deactivated org_id=%s user_id=%s",
                        org.id, user.id,
                    )
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Your organization account has been deactivated. "
                                       "Please contact support.",
                            "errors": None,
                        },
                        status=403,
                    )
                request.org = org
            except Exception:
                pass  # org may not exist yet mid-registration; views handle that

        return self.get_response(request)
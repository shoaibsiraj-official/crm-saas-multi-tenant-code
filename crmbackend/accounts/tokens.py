"""
accounts/tokens.py  (updated for multi-tenant organization support)

Changes from v1:
  - Adds `org_slug` claim so clients can build org-scoped URLs without
    an extra API call
  - Uses select_related("organization") to avoid N+1 on token generation
"""

import logging
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class CustomRefreshToken(RefreshToken):
    """
    Refresh token that embeds identity + tenant claims into the payload.
    Access token mirrors the same claims for stateless authorization.
    """

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)

        org    = getattr(user, "organization", None)
        org_id = str(org.id)   if org else None
        org_slug = org.slug    if org else None

        token["user_id"]        = str(user.id)
        token["email"]          = user.email
        token["role"]           = user.role
        token["organization_id"] = org_id
        token["org_slug"]       = org_slug
        token["is_verified"]    = user.is_verified
        token["full_name"]      = user.full_name

        logger.debug(
            "token_generated user_id=%s role=%s org_id=%s",
            user.id, user.role, org_id,
        )
        return token

    @property
    def access_token(self):
        access = super().access_token
        for claim in (
            "user_id", "email", "role", "organization_id",
            "org_slug", "is_verified", "full_name",
        ):
            access[claim] = self.payload.get(claim)
        return access


def generate_tokens_for_user(user) -> dict:
    """Return a ready-to-serialize access + refresh pair for `user`."""
    # Ensure org is loaded to avoid extra query in token generation
    if hasattr(user, "_state") and not hasattr(user, "_organization_cache"):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.select_related("organization").get(pk=user.pk)

    refresh = CustomRefreshToken.for_user(user)
    return {
        "access":  str(refresh.access_token),
        "refresh": str(refresh),
    }
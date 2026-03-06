"""
Signals — keep side-effects decoupled from model/service code.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def on_user_created(sender, instance: User, created: bool, **kwargs):
    """Hook fired after every User save; acts only on creation."""
    if created:
        logger.info(
            "New user created | id=%s email=%s role=%s",
            instance.id,
            instance.email,
            instance.role,
        )
        # Extension point: push to analytics, provision default workspace, etc.
        # Example: provision_default_workspace.delay(str(instance.id))
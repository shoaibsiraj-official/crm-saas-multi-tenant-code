"""
projects/signals.py

Lifecycle hooks decoupled from model/service code.
Extend these for analytics, notifications, webhooks, etc.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, Task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Project)
def on_project_save(sender, instance: Project, created: bool, **kwargs):
    if created:
        logger.info(
            "project_created_signal project_id=%s org_id=%s name=%r",
            instance.id, instance.organization_id, instance.name,
        )
    elif instance.is_deleted:
        logger.info(
            "project_soft_deleted_signal project_id=%s org_id=%s",
            instance.id, instance.organization_id,
        )


@receiver(post_save, sender=Task)
def on_task_save(sender, instance: Task, created: bool, **kwargs):
    if created:
        logger.info(
            "task_created_signal task_id=%s project_id=%s org_id=%s",
            instance.id, instance.project_id, instance.organization_id,
        )
    # Extension point: send notification when task is assigned
    # if created and instance.assigned_to_id:
    #     notify_task_assignment.delay(str(instance.id))
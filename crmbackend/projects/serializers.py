"""
projects/serializers.py
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Project, ProjectMembership, Task

User = get_user_model()


# ============================================================
# USER MINI SERIALIZER
# ============================================================

class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model  = User
        fields = ["id", "email", "full_name", "role"]
        read_only_fields = fields


# ============================================================
# PROJECT MEMBERSHIP
# ============================================================

class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model  = ProjectMembership
        fields = ["id", "user", "is_active", "joined_at"]
        read_only_fields = fields


# ============================================================
# PROJECT LIST
# ============================================================

class ProjectListSerializer(serializers.ModelSerializer):

    created_by     = UserMiniSerializer(read_only=True)
    member_count   = serializers.IntegerField(read_only=True)
    progress       = serializers.IntegerField(read_only=True)  # ✅ FIXED
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model  = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "status_display",
            "member_count",
            "progress",
            "created_by",
            "created_at",
            "updated_at",
            "client",
            "client_name",
        ]
        read_only_fields = fields


# ============================================================
# PROJECT DETAIL
# ============================================================

class ProjectDetailSerializer(serializers.ModelSerializer):

    created_by     = UserMiniSerializer(read_only=True)
    members        = serializers.SerializerMethodField()
    task_summary   = serializers.SerializerMethodField()
    progress       = serializers.IntegerField(read_only=True)  # ✅ FIXED
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    client=serializers.PrimaryKeyRelatedField(read_only=True)
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model  = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "status_display",
            "progress",
            "created_by",
            "members",
            "task_summary",
            "created_at",
            "updated_at",
            "client",
            "client_name",
        ]
        read_only_fields = fields

    def get_members(self, obj):
        memberships = obj.memberships.filter(
            is_active=True
        ).select_related("user")
        return ProjectMembershipSerializer(memberships, many=True).data

    def get_task_summary(self, obj):
        tasks = obj.tasks.filter(is_deleted=False)
        return {
            "total": tasks.count(),
            "todo": tasks.filter(status="TODO").count(),
            "in_progress": tasks.filter(status="IN_PROGRESS").count(),
            "review": tasks.filter(status="REVIEW").count(),
            "done": tasks.filter(status="DONE").count(),
        }


# ============================================================
# PROJECT CREATE
# ============================================================

class ProjectCreateSerializer(serializers.Serializer):

    name        = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    status      = serializers.ChoiceField(
        choices=Project.status.field.choices,
        default="ACTIVE",
        required=False,
    )
    client = serializers.UUIDField(required=False, allow_null=True)

    def validate_name(self, value):
        return value.strip()


# ============================================================
# PROJECT UPDATE
# ============================================================

class ProjectUpdateSerializer(serializers.Serializer):

    name        = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status      = serializers.ChoiceField(
        choices=Project.status.field.choices,
        required=False
    )
    client = serializers.UUIDField(required=False, allow_null=True)

    def validate_name(self, value):
        return value.strip()

    def validate(self, data):
        if not data:
            raise serializers.ValidationError("At least one field must be provided.")
        return data


# ============================================================
# MEMBER ACTIONS
# ============================================================

class AssignMemberSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


class RemoveMemberSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


# ============================================================
# TASK SERIALIZERS
# ============================================================

class TaskListSerializer(serializers.ModelSerializer):

    assigned_to      = UserMiniSerializer(read_only=True)
    status_display   = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)

    class Meta:
        model  = Task
        fields = [
            "id",
            "title",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "assigned_to",
            "due_date",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TaskDetailSerializer(serializers.ModelSerializer):

    assigned_to      = UserMiniSerializer(read_only=True)
    created_by       = UserMiniSerializer(read_only=True)
    status_display   = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    project_name     = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model  = Task
        fields = [
            "id",
            "project",
            "project_name",
            "title",
            "description",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "assigned_to",
            "created_by",
            "due_date",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ============================================================
# TASK CREATE
# ============================================================

class TaskCreateSerializer(serializers.Serializer):

    title       = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    assigned_to = serializers.UUIDField(required=False, allow_null=True)
    priority    = serializers.ChoiceField(
        choices=Task.priority.field.choices,
        default="MEDIUM",
        required=False
    )
    status = serializers.ChoiceField(
        choices=Task.status.field.choices,
        default="TODO",
        required=False
    )
    due_date = serializers.DateField(required=False, allow_null=True)


# ============================================================
# TASK UPDATE
# ============================================================

class TaskUpdateSerializer(serializers.Serializer):

    title       = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    assigned_to = serializers.UUIDField(required=False, allow_null=True)
    priority    = serializers.ChoiceField(
        choices=Task.priority.field.choices,
        required=False
    )
    status = serializers.ChoiceField(
        choices=Task.status.field.choices,
        required=False
    )
    due_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError("At least one field must be provided.")
        return data


# ============================================================
# TASK STATUS UPDATE
# ============================================================

class TaskStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.status.field.choices)


# ============================================================
# TASK DRAG & DROP MOVE
# ============================================================

class TaskMoveSerializer(serializers.Serializer):
    status   = serializers.ChoiceField(
        choices=["TODO", "IN_PROGRESS", "REVIEW", "DONE"]
    )
    position = serializers.IntegerField(min_value=0)


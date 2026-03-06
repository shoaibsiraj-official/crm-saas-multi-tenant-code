"""
projects/views.py

ViewSets for the Projects domain.

Architecture rules followed:
  ─ get_queryset() ALWAYS scopes by request.user.organization.
    Cross-tenant objects return 404, not 403, to avoid enumeration.
  ─ Views contain zero business logic — every write delegates to services.py.
  ─ All responses use the project-wide success_response / error_response
    envelope for consistency.
  ─ Object-level permissions are called with check_object_permissions()
    AFTER the object is fetched via the scoped queryset.
"""

import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from .services import move_task
from .serializers import TaskMoveSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.exceptions import success_response, error_response

from core.exceptions import error_response, success_response

from .models import Project, Task
from .permissions import (
    CanAccessProject,
    CanAccessTask,
    CanDeleteProject,
    CanDeleteTask,
    CanMutateProject,
    CanMutateTask,
    IsManagerOrAbove,
    IsOrgMember,
)
from .serializers import (
    AssignMemberSerializer,
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskStatusUpdateSerializer,
    TaskUpdateSerializer,
)
from .services import (
    AlreadyMember,
    CrossTenantError,
    MemberInactive,
    MemberNotFound,
    PermissionDenied,
    ProjectNotFound,
    TaskNotFound,
    ValidationError,
    assign_member_to_project,
    change_task_status,
    create_project,
    create_task,
    delete_project,
    delete_task,
    get_projects_for_user,
    get_tasks_for_project,
    remove_member_from_project,
    update_project,
    update_task,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: resolve organization from request
# ---------------------------------------------------------------------------

def _org(request):
    """Return the org attached by TenantContextMiddleware or via FK."""
    return getattr(request, "org", None) or getattr(request.user, "organization", None)


# ---------------------------------------------------------------------------
# Project ViewSet
# ---------------------------------------------------------------------------

class ProjectViewSet(ViewSet):
    """
    /api/projects/

    list         GET  /projects/
    create       POST /projects/
    retrieve     GET  /projects/<pk>/
    partial_update PATCH /projects/<pk>/
    destroy      DELETE /projects/<pk>/
    assign_member POST /projects/<pk>/assign-member/
    remove_member DELETE /projects/<pk>/members/<user_id>/
    list_tasks   GET  /projects/<pk>/tasks/
    create_task  POST /projects/<pk>/tasks/
    """

    def _get_project_or_404(self, pk, user):
        """Fetch project scoped to user's org — returns 404 for cross-tenant."""
        try:
            return (
                Project.objects
                .filter(organization_id=user.organization_id)
                .select_related("created_by", "organization")
                .prefetch_related("memberships__user")
                .get(pk=pk)
            )
        except Project.DoesNotExist:
            return None

    # ── List ────────────────────────────────────────────────────────────────

    def list(self, request):
        """GET /projects/ — returns projects visible to the caller."""
        self.permission_classes = [IsOrgMember]
        self.check_permissions(request)

        qs = get_projects_for_user(request.user)

        # Filtering
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        serializer = ProjectListSerializer(qs, many=True)
        return success_response(
            data={"count": qs.count(), "projects": serializer.data},
            message="Projects retrieved.",
        )

    # ── Create ──────────────────────────────────────────────────────────────

    def create(self, request):
        """POST /projects/ — MANAGER+ only."""
        self.permission_classes = [IsManagerOrAbove]
        self.check_permissions(request)

        serializer = ProjectCreateSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        org = _org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        project = create_project(
            organization=org,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            status=serializer.validated_data.get("status", "ACTIVE"),
            created_by=request.user,
        )

        return success_response(
            data=ProjectDetailSerializer(project).data,
            message="Project created.",
            status_code=status.HTTP_201_CREATED,
        )

    # ── Retrieve ─────────────────────────────────────────────────────────────

    def retrieve(self, request, pk=None):
        """GET /projects/<pk>/"""
        self.permission_classes = [CanAccessProject]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, project)

        return success_response(
            data=ProjectDetailSerializer(project).data,
            message="Project retrieved.",
        )

    # ── Update ───────────────────────────────────────────────────────────────

    def partial_update(self, request, pk=None):
        """PATCH /projects/<pk>/ — MANAGER+"""
        self.permission_classes = [CanMutateProject]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, project)

        serializer = ProjectUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        org = _org(request)
        try:
            updated = update_project(
                project_id=pk,
                organization=org,
                validated_data=serializer.validated_data,
                updated_by=request.user,
            )
        except ProjectNotFound:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=ProjectDetailSerializer(updated).data,
            message="Project updated.",
        )

    # ── Delete ───────────────────────────────────────────────────────────────

    def destroy(self, request, pk=None):
        """DELETE /projects/<pk>/ — ORG_ADMIN only."""
        self.permission_classes = [CanDeleteProject]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, project)

        org = _org(request)
        try:
            delete_project(
                project_id=pk,
                organization=org,
                deleted_by=request.user,
            )
        except ProjectNotFound:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(message="Project deleted.", status_code=status.HTTP_200_OK)

    # ── Assign member  ───────────────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="assign-member")
    def assign_member(self, request, pk=None):
        """POST /projects/<pk>/assign-member/ — MANAGER+"""
        self.permission_classes = [IsManagerOrAbove]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = AssignMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        org = _org(request)
        try:
            membership = assign_member_to_project(
                project_id=pk,
                organization=org,
                user_id=serializer.validated_data["user_id"],
                assigned_by=request.user,
            )
        except AlreadyMember as exc:
            return error_response(message=str(exc), status_code=status.HTTP_409_CONFLICT)
        except (MemberNotFound, CrossTenantError) as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        except MemberInactive as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(
            data={"membership_id": str(membership.id)},
            message="Member assigned to project.",
            status_code=status.HTTP_201_CREATED,
        )

    # ── Remove member ────────────────────────────────────────────────────────

    @action(detail=True, methods=["delete"], url_path=r"members/(?P<user_id>[^/.]+)")
    def remove_member(self, request, pk=None, user_id=None):
        """DELETE /projects/<pk>/members/<user_id>/ — MANAGER+"""
        self.permission_classes = [IsManagerOrAbove]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        org = _org(request)
        try:
            remove_member_from_project(
                project_id=pk,
                organization=org,
                user_id=user_id,
                removed_by=request.user,
            )
        except (MemberNotFound, ProjectNotFound) as exc:
            return error_response(message=str(exc), status_code=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as exc:
            return error_response(message=str(exc), status_code=status.HTTP_403_FORBIDDEN)

        return success_response(message="Member removed from project.")

    # ── List tasks  ──────────────────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="tasks")
    def list_tasks(self, request, pk=None):
        """GET /projects/<pk>/tasks/"""
        self.permission_classes = [CanAccessProject]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, project)

        org = _org(request)
        tasks = get_tasks_for_project(pk, org, request.user)

        # Filtering
        status_filter = request.query_params.get("status")
        if status_filter:
            tasks = tasks.filter(status=status_filter.upper())

        priority_filter = request.query_params.get("priority")
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter.upper())

        assigned_to = request.query_params.get("assigned_to")
        if assigned_to == "me":
            tasks = tasks.filter(assigned_to=request.user)

        serializer = TaskListSerializer(tasks, many=True)
        return success_response(
            data={"count": tasks.count(), "tasks": serializer.data},
            message="Tasks retrieved.",
        )

    # ── Create task  ─────────────────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="tasks", url_name="tasks-create")
    def create_task_for_project(self, request, pk=None):
        """POST /projects/<pk>/tasks/ — MANAGER+"""
        self.permission_classes = [IsManagerOrAbove]
        self.check_permissions(request)

        project = self._get_project_or_404(pk, request.user)
        if not project:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        data = serializer.validated_data
        org = _org(request)

        try:
            task = create_task(
                project_id=pk,
                organization=org,
                title=data["title"],
                description=data.get("description", ""),
                assigned_to_id=data.get("assigned_to"),
                priority=data.get("priority", "MEDIUM"),
                status=data.get("status", "TODO"),
                due_date=data.get("due_date"),
                created_by=request.user,
            )
        except (MemberNotFound, CrossTenantError, MemberInactive, ValidationError) as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        except ProjectNotFound:
            return error_response(
                message="Project not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=TaskDetailSerializer(task).data,
            message="Task created.",
            status_code=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Task ViewSet
# ---------------------------------------------------------------------------

class TaskViewSet(ViewSet):
    """
    /api/tasks/

    retrieve       GET   /tasks/<pk>/
    partial_update PATCH /tasks/<pk>/
    destroy        DELETE /tasks/<pk>/
    status_update  PATCH /tasks/<pk>/status/
    """

    def _get_task_or_404(self, pk, user):
        """Fetch task scoped to user's org."""
        try:
            return (
                Task.objects
                .filter(organization_id=user.organization_id)
                .select_related(
                    "assigned_to", "created_by",
                    "project", "project__organization",
                )
                .get(pk=pk)
            )
        except Task.DoesNotExist:
            return None

    # ── Retrieve ─────────────────────────────────────────────────────────────

    def retrieve(self, request, pk=None):
        """GET /tasks/<pk>/"""
        self.permission_classes = [CanAccessTask]
        self.check_permissions(request)

        task = self._get_task_or_404(pk, request.user)
        if not task:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, task)

        return success_response(
            data=TaskDetailSerializer(task).data,
            message="Task retrieved.",
        )

    # ── Full update (MANAGER+) ────────────────────────────────────────────────

    def partial_update(self, request, pk=None):
        """PATCH /tasks/<pk>/ — MANAGER+"""
        self.permission_classes = [CanMutateTask]
        self.check_permissions(request)

        task = self._get_task_or_404(pk, request.user)
        if not task:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, task)

        serializer = TaskUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        org = _org(request)
        try:
            updated = update_task(
                task_id=pk,
                organization=org,
                validated_data=serializer.validated_data,
                updated_by=request.user,
            )
        except (ValidationError, MemberNotFound, CrossTenantError) as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        except TaskNotFound:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=TaskDetailSerializer(updated).data,
            message="Task updated.",
        )

    # ── Delete ───────────────────────────────────────────────────────────────

    def destroy(self, request, pk=None):
        """DELETE /tasks/<pk>/ — MANAGER+"""
        self.permission_classes = [CanDeleteTask]
        self.check_permissions(request)

        task = self._get_task_or_404(pk, request.user)
        if not task:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, task)

        org = _org(request)
        try:
            delete_task(task_id=pk, organization=org, deleted_by=request.user)
        except TaskNotFound:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(message="Task deleted.")

    # ── Status-only update (MEMBER) ───────────────────────────────────────────

    @action(detail=True, methods=["patch"], url_path="status")
    def status_update(self, request, pk=None):
        """
        PATCH /tasks/<pk>/status/

        Available to all org members, but MEMBER can only change status
        on tasks assigned to themselves (enforced via CanMutateTask
        object-level check).
        """
        self.permission_classes = [CanMutateTask]
        self.check_permissions(request)

        task = self._get_task_or_404(pk, request.user)
        if not task:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, task)

        serializer = TaskStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid status.",
                errors=serializer.errors,
            )

        org = _org(request)
        try:
            updated = change_task_status(
                task_id=pk,
                organization=org,
                new_status=serializer.validated_data["status"],
                changed_by=request.user,
            )
        except TaskNotFound:
            return error_response(
                message="Task not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=TaskDetailSerializer(updated).data,
            message=f"Task status updated to {updated.status}.",
        )




class TaskMoveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        try:
            task = Task.objects.select_related("project").get(
                id=task_id,
                project__organization=request.user.organization
            )
        except Task.DoesNotExist:
            return error_response("Task not found.", 404)

        serializer = TaskMoveSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Invalid data.", errors=serializer.errors)

        task = move_task(
            task=task,
            new_status=serializer.validated_data["status"],
            new_position=serializer.validated_data["position"],
        )

        return success_response(
            data={"id": str(task.id), "status": task.status},
            message="Task moved successfully."
        )
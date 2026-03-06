"""
projects/urls.py

URL routing for the Projects domain.

All project-scoped task creation/listing is on /projects/<pk>/tasks/.
Standalone task operations (retrieve, update, delete, status) are on /tasks/<pk>/.
This gives both "project inbox" and "my tasks" views clean URLs.
"""

from django.urls import path

from .views import ProjectViewSet, TaskViewSet, TaskMoveView

# ── Project routes ─────────────────────────────────────────────────────────

project_list    = ProjectViewSet.as_view({"get": "list",    "post": "create"})
project_detail  = ProjectViewSet.as_view({"get": "retrieve", "patch": "partial_update",
                                           "delete": "destroy"})
project_assign  = ProjectViewSet.as_view({"post": "assign_member"})
project_member  = ProjectViewSet.as_view({"delete": "remove_member"})
project_tasks   = ProjectViewSet.as_view({"get": "list_tasks", "post": "create_task_for_project"})

# ── Task routes ────────────────────────────────────────────────────────────

task_detail     = TaskViewSet.as_view({"get": "retrieve", "patch": "partial_update",
                                        "delete": "destroy"})
task_status     = TaskViewSet.as_view({"patch": "status_update"})

urlpatterns = [
    # ── Projects ────────────────────────────────────────────────────────
    # GET  /api/projects/         — list projects
    # POST /api/projects/         — create project
    path("",           project_list,   name="project-list"),

    # GET    /api/projects/<pk>/  — retrieve
    # PATCH  /api/projects/<pk>/  — update
    # DELETE /api/projects/<pk>/  — soft-delete
    path("<uuid:pk>/", project_detail, name="project-detail"),

    # POST /api/projects/<pk>/assign-member/
    path("<uuid:pk>/assign-member/",              project_assign, name="project-assign-member"),

    # DELETE /api/projects/<pk>/members/<user_id>/
    path("<uuid:pk>/members/<uuid:user_id>/",      project_member, name="project-remove-member"),

    # GET  /api/projects/<pk>/tasks/  — list tasks in project
    # POST /api/projects/<pk>/tasks/  — create task in project
    path("<uuid:pk>/tasks/",                       project_tasks,  name="project-tasks"),

    # ── Tasks ───────────────────────────────────────────────────────────
    # GET    /api/tasks/<pk>/         — retrieve task
    # PATCH  /api/tasks/<pk>/         — full update (MANAGER+)
    # DELETE /api/tasks/<pk>/         — soft-delete (MANAGER+)
    path("tasks/<uuid:pk>/",          task_detail, name="task-detail"),

    # PATCH /api/tasks/<pk>/status/   — status-only update (any member)
    path("tasks/<uuid:pk>/status/",   task_status, name="task-status"),
    path("tasks/<uuid:task_id>/move/", TaskMoveView.as_view()),
]
from django.contrib import admin
from django.utils.html import format_html

from .models import Project, ProjectMembership, Task


class ProjectMembershipInline(admin.TabularInline):
    model   = ProjectMembership
    extra   = 0
    readonly_fields = ["id", "user", "is_active", "joined_at", "assigned_by"]
    can_delete = False


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display   = ["name", "organization", "status", "member_count_display",
                       "is_deleted", "created_by", "created_at"]
    list_filter    = ["status", "is_deleted", "organization__name"]
    search_fields  = ["name", "organization__name", "created_by__email"]
    readonly_fields = ["id", "created_at", "updated_at", "deleted_at", "member_count_display"]
    ordering       = ["-created_at"]
    inlines        = [ProjectMembershipInline]

    fieldsets = (
        (None,         {"fields": ("id", "organization", "name", "description", "status")}),
        ("Authorship", {"fields": ("created_by",)}),
        ("Soft Delete",{"fields": ("is_deleted", "deleted_at", "deleted_by")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def member_count_display(self, obj):
        return obj.member_count
    member_count_display.short_description = "Members"

    def get_queryset(self, request):
        return Project.all_objects.select_related("organization", "created_by")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ["title", "project", "status", "priority", "assigned_to",
                      "due_date", "is_deleted", "created_at"]
    list_filter   = ["status", "priority", "is_deleted", "project__organization__name"]
    search_fields = ["title", "project__name", "assigned_to__email"]
    readonly_fields = ["id", "organization", "created_at", "updated_at", "deleted_at"]
    ordering      = ["-created_at"]

    fieldsets = (
        (None,       {"fields": ("id", "organization", "project", "title", "description")}),
        ("Status",   {"fields": ("status", "priority", "due_date")}),
        ("People",   {"fields": ("assigned_to", "created_by")}),
        ("Soft Delete", {"fields": ("is_deleted", "deleted_at", "deleted_by")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return Task.all_objects.select_related(
            "organization", "project", "assigned_to", "created_by"
        )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display  = ["user", "project", "is_active", "joined_at", "assigned_by"]
    list_filter   = ["is_active"]
    search_fields = ["user__email", "project__name"]
    readonly_fields = ["id", "joined_at"]
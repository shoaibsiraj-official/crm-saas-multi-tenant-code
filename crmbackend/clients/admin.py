from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display   = ["name", "email", "company_name", "status", "organization", "created_by", "created_at"]
    list_filter    = ["status", "organization"]
    search_fields  = ["name", "email", "company_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering       = ["-created_at"]

    fieldsets = (
        ("Identity",     {"fields": ("id", "organization", "status")}),
        ("Contact Info", {"fields": ("name", "email", "phone", "company_name")}),
        ("Details",      {"fields": ("address", "notes")}),
        ("Authorship",   {"fields": ("created_by",)}),
        ("Timestamps",   {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return super().get_queryset().select_related("organization", "created_by")
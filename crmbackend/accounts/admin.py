from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AuditLog, EmailVerificationToken, PasswordResetToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "role", "is_active", "is_verified", "created_at"]
    list_filter = ["role", "is_active", "is_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Organization"), {"fields": ("role", "organization_id")}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")},
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["email", "event_type", "ip_address", "created_at"]
    list_filter = ["event_type"]
    search_fields = ["email", "ip_address"]
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "is_used", "created_at", "expires_at"]
    list_filter = ["is_used"]
    readonly_fields = [f.name for f in PasswordResetToken._meta.fields]


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "expires_at"]
    readonly_fields = [f.name for f in EmailVerificationToken._meta.fields]
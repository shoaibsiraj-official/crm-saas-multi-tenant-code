from django.contrib import admin
from .models import Organization, OrganizationInvite


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug", "subscription_plan", "member_count", "seat_limit", "is_active", "created_at"]
    list_filter   = ["subscription_plan", "is_active"]
    search_fields = ["name", "slug", "billing_email"]
    readonly_fields = ["id", "slug", "created_at", "updated_at", "member_count"]
    ordering      = ["-created_at"]

    fieldsets = (
        (None,           {"fields": ("id", "name", "slug", "is_active")}),
        ("Subscription", {"fields": ("subscription_plan", "seat_limit")}),
        ("Billing",      {"fields": ("billing_email", "stripe_customer_id")}),
        ("Timestamps",   {"fields": ("created_at", "updated_at")}),
    )

    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = "Members"


@admin.register(OrganizationInvite)
class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display  = ["email", "organization", "role", "status", "invited_by", "expires_at", "created_at"]
    list_filter   = ["status", "role"]
    search_fields = ["email", "organization__name"]
    readonly_fields = ["id", "token", "created_at", "updated_at", "accepted_at"]
    ordering      = ["-created_at"]
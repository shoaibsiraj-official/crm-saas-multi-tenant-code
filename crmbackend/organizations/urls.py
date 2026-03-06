from django.urls import path
from .views import (
    OrganizationDetailView,
    OrganizationUpdateView,
    OrganizationMembersView,
    MemberRoleUpdateView,
    MemberRemoveView,
    OrganizationInviteView,
    OrganizationInviteListView,
    InviteAcceptView,
    InviteRevokeView,
)

urlpatterns = [
    # Organization profile
    path("me/",     OrganizationDetailView.as_view(), name="org-detail"),
    path("update/", OrganizationUpdateView.as_view(), name="org-update"),

    # Member management
    path("members/",                    OrganizationMembersView.as_view(), name="org-members"),
    path("members/<uuid:user_id>/role/", MemberRoleUpdateView.as_view(),   name="org-member-role"),
    path("members/<uuid:user_id>/",     MemberRemoveView.as_view(),        name="org-member-remove"),

    # Invite management
    path("invite/",                        OrganizationInviteView.as_view(),     name="org-invite"),
    path("invite/accept/",                 InviteAcceptView.as_view(),           name="org-invite-accept"),
    path("invites/",                       OrganizationInviteListView.as_view(), name="org-invites"),
    path("invites/<uuid:invite_id>/",      InviteRevokeView.as_view(),           name="org-invite-revoke"),
]
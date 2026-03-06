"""
organizations/views.py
Thin controllers — parse → validate → call service → format response.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView

from core.exceptions import error_response, success_response

from .models import Organization, OrganizationInvite, InviteStatus
from .permissions import IsOrgAdmin, IsManager, IsOrgMember
from .serializers import (
    InviteAcceptSerializer,
    InviteCreateSerializer,
    MemberRoleUpdateSerializer,
    OrganizationInviteSerializer,
    OrganizationMemberSerializer,
    OrganizationSerializer,
    OrganizationUpdateSerializer,
    ContactSerializer
)
from .services import (
    InviteError,
    NotFoundError,
    OrganizationError,
    PermissionError,
    SeatLimitExceeded,
    accept_invite,
    change_member_role,
    get_org_members,
    invite_member,
    remove_member,
    revoke_invite,
    update_organization,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_user_org(request):
    if not request.user.organization_id:
        return None

    try:
        return Organization.objects.get(
            id=request.user.organization_id,
            is_active=True,
        )
    except Organization.DoesNotExist:
        return None


# ---------------------------------------------------------------------------
# Organization Detail
# ---------------------------------------------------------------------------

class OrganizationDetailView(APIView):

    permission_classes = [IsOrgMember]

    def get(self, request):
        print("USER:", request.user)
        print("AUTH:", request.auth)
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="You are not associated with any organization.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=OrganizationSerializer(org).data,
            message="Organization retrieved.",
        )


# ---------------------------------------------------------------------------
# Organization Update
# ---------------------------------------------------------------------------

class OrganizationUpdateView(APIView):

    permission_classes = [IsOrgAdmin]

    def patch(self, request):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        if not serializer.validated_data:
            return error_response(message="No fields provided to update.")

        try:
            updated_org = update_organization(org, serializer.validated_data)
        except OrganizationError as exc:
            return error_response(message=str(exc))

        return success_response(
            data=OrganizationSerializer(updated_org).data,
            message="Organization updated.",
        )


# ---------------------------------------------------------------------------
# Members List
# ---------------------------------------------------------------------------

class OrganizationMembersView(APIView):

    permission_classes = [IsManager]

    def get(self, request):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        members = get_org_members(org)
        serializer = OrganizationMemberSerializer(members, many=True)

        return success_response(
            data={
                "count": members.count(),
                "members": serializer.data,
            },
            message="Members retrieved.",
        )


# ---------------------------------------------------------------------------
# Change Member Role
# ---------------------------------------------------------------------------

class MemberRoleUpdateView(APIView):

    permission_classes = [IsOrgAdmin]

    def patch(self, request, user_id):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = MemberRoleUpdateSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return error_response(
                message="Invalid data.",
                errors=serializer.errors,
            )

        try:
            member = change_member_role(
                org=org,
                target_user_id=str(user_id),
                new_role=serializer.validated_data["role"],
                requesting_user=request.user,
            )
        except NotFoundError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return error_response(str(exc), status.HTTP_403_FORBIDDEN)

        return success_response(
            data=OrganizationMemberSerializer(member).data,
            message="Member role updated.",
        )


# ---------------------------------------------------------------------------
# Remove Member
# ---------------------------------------------------------------------------

class MemberRemoveView(APIView):

    permission_classes = [IsOrgAdmin]

    def delete(self, request, user_id):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        try:
            remove_member(
                org=org,
                target_user_id=str(user_id),
                requesting_user=request.user,
            )
        except NotFoundError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return error_response(str(exc), status.HTTP_403_FORBIDDEN)

        return success_response(message="Member removed from organization.")


# ---------------------------------------------------------------------------
# Send Invite
# ---------------------------------------------------------------------------

class OrganizationInviteView(APIView):

    permission_classes = [IsOrgAdmin]

    def post(self, request):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = InviteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid invite data.",
                errors=serializer.errors,
            )

        try:
            invite = invite_member(
                org=org,
                email=serializer.validated_data["email"],
                role=serializer.validated_data["role"],
                invited_by=request.user,
            )
        except SeatLimitExceeded as exc:
            return error_response(str(exc), status.HTTP_402_PAYMENT_REQUIRED)
        except InviteError as exc:
            return error_response(str(exc))

        return success_response(
            data=OrganizationInviteSerializer(invite).data,
            message="Invitation sent.",
            status_code=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Accept Invite
# ---------------------------------------------------------------------------

class InviteAcceptView(APIView):

    permission_classes = []  # AllowAny

    def post(self, request):
        if not request.user.is_authenticated:
            return error_response(
                message="Authentication required.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = InviteAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid token.",
                errors=serializer.errors,
            )

        try:
            org = accept_invite(
                token=serializer.validated_data["token"],
                user=request.user,
            )
        except (InviteError, SeatLimitExceeded) as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        return success_response(
            data=OrganizationSerializer(org).data,
            message="Invite accepted successfully.",
        )


# ---------------------------------------------------------------------------
# List Invites
# ---------------------------------------------------------------------------

class OrganizationInviteListView(APIView):

    permission_classes = [IsOrgAdmin]

    def get(self, request):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        invites = (
            OrganizationInvite.objects.filter(
                organization=org,
                status=InviteStatus.PENDING,
            )
            .select_related("invited_by")
            .order_by("-created_at")
        )

        serializer = OrganizationInviteSerializer(invites, many=True)

        return success_response(
            data={
                "count": invites.count(),
                "invites": serializer.data,
            },
            message="Pending invites retrieved.",
        )


# ---------------------------------------------------------------------------
# Revoke Invite
# ---------------------------------------------------------------------------

class InviteRevokeView(APIView):

    permission_classes = [IsOrgAdmin]

    def delete(self, request, invite_id):
        org = _get_user_org(request)
        if not org:
            return error_response(
                message="Organization not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        try:
            revoke_invite(
                invite_id=str(invite_id),
                org=org,
                requesting_user=request.user,
            )
        except NotFoundError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)

        return success_response(message="Invite revoked.")

class ContactListCreateView(APIView):
    permission_classes = [IsOrgMember]

    def get(self, request):
        contacts = request.user.organization.contacts.all()
        serializer = ContactSerializer(contacts, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                organization=request.user.organization,
                created_by=request.user
            )
            return success_response(data=serializer.data)
        return error_response(errors=serializer.errors)
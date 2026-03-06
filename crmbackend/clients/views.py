"""
clients/views.py

ClientViewSet — full CRUD for the Client resource.

Tenant isolation is structural:
  ─ get_queryset()  always filters by request.user.organization
  ─ perform_create() injects organization from request.user (never from payload)
  ─ get_object()    raises 404 (not 403) for cross-tenant IDs to prevent enumeration

All responses use the project-wide { success, message, data } envelope.
Search and ordering use DRF's built-in filter backends so they compose
cleanly with any future pagination or additional filters.
"""

import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from core.exceptions import error_response, success_response

from .models import Client
from .serializers import (
    ClientCreateSerializer,
    ClientDetailSerializer,
    ClientListSerializer,
    ClientUpdateSerializer,
)

logger = logging.getLogger(__name__)


class ClientViewSet(ViewSet):
    """
    /api/clients/

    list      GET    /clients/
    create    POST   /clients/
    retrieve  GET    /clients/<pk>/
    update    PATCH  /clients/<pk>/
    destroy   DELETE /clients/<pk>/

    Query parameters for list:
      ?search=<term>         — searches name, email, company_name
      ?status=ACTIVE|INACTIVE
      ?ordering=created_at|-created_at|name|email|company_name
    """

    permission_classes = [IsAuthenticated]

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_org(self, request):
        """Return the organization from middleware or FK."""
        return getattr(request, "org", None) or getattr(
            request.user, "organization", None
        )

    def _base_queryset(self, request):
        """
        All queries start here — scoped to the caller's org.
        select_related avoids N+1 on org + created_by for detail views.
        """
        org = self._get_org(request)
        if not org:
            return Client.objects.none()

        return (
            Client.objects.filter(organization=org)
            .select_related("organization", "created_by")
            .order_by("-created_at")
        )

    def _get_client_or_404(self, request, pk):
        """
        Fetch a single client scoped to the caller's org.
        Returns None (→ 404 in view) for cross-tenant IDs.
        """
        try:
            return self._base_queryset(request).get(pk=pk)
        except Client.DoesNotExist:
            return None

    def _apply_list_filters(self, queryset, request):
        """Apply search, status, and ordering from query params."""

        # ── Search: name, email, company_name ─────────────────────────────
        search = request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(company_name__icontains=search)
            )

        # ── Status filter ──────────────────────────────────────────────────
        status_filter = request.query_params.get("status", "").upper()
        if status_filter in ("ACTIVE", "INACTIVE"):
            queryset = queryset.filter(status=status_filter)

        # ── Ordering ───────────────────────────────────────────────────────
        ALLOWED_ORDERINGS = {
            "created_at":   "created_at",
            "-created_at":  "-created_at",
            "name":         "name",
            "-name":        "-name",
            "email":        "email",
            "-email":       "-email",
            "company_name": "company_name",
            "-company_name":"-company_name",
            "updated_at":   "updated_at",
            "-updated_at":  "-updated_at",
        }
        ordering_param = request.query_params.get("ordering", "-created_at")
        ordering = ALLOWED_ORDERINGS.get(ordering_param, "-created_at")
        queryset = queryset.order_by(ordering)

        return queryset

    # ── LIST ─────────────────────────────────────────────────────────────────

    def list(self, request):
        """GET /clients/ — paginated, searchable, filterable list."""
        org = self._get_org(request)
        if not org:
            return error_response(
                message="You are not associated with any organization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        queryset = self._apply_list_filters(self._base_queryset(request), request)

        # ── Manual pagination (no DRF pagination class wired in) ──────────
        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        page      = max(int(request.query_params.get("page", 1)), 1)
        offset    = (page - 1) * page_size
        total     = queryset.count()
        clients   = queryset[offset : offset + page_size]

        serializer = ClientListSerializer(clients, many=True)

        return success_response(
            data={
                "count":     total,
                "page":      page,
                "page_size": page_size,
                "results":   serializer.data,
            },
            message="Clients retrieved.",
        )

    # ── RETRIEVE ─────────────────────────────────────────────────────────────

    def retrieve(self, request, pk=None):
        """GET /clients/<pk>/"""
        client = self._get_client_or_404(request, pk)
        if client is None:
            return error_response(
                message="Client not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=ClientDetailSerializer(client).data,
            message="Client retrieved.",
        )

    # ── CREATE ───────────────────────────────────────────────────────────────

    def create(self, request):
        """POST /clients/"""
        org = self._get_org(request)
        if not org:
            return error_response(
                message="You are not associated with any organization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = ClientCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        # Check email uniqueness within this org before hitting the DB constraint
        email = data["email"]
        if Client.objects.filter(organization=org, email=email).exists():
            return error_response(
                message=f"A client with email '{email}' already exists in your organization.",
                status_code=status.HTTP_409_CONFLICT,
            )

        try:
            client = Client.objects.create(
                organization=org,
                created_by=request.user,
                **data,
            )
        except IntegrityError:
            # Race condition safety net
            return error_response(
                message=f"A client with email '{email}' already exists in your organization.",
                status_code=status.HTTP_409_CONFLICT,
            )

        logger.info(
            "client_created client_id=%s org_id=%s by=%s",
            client.id, org.id, request.user.id,
        )

        return success_response(
            data=ClientDetailSerializer(client).data,
            message="Client created.",
            status_code=status.HTTP_201_CREATED,
        )

    # ── UPDATE (PATCH) ────────────────────────────────────────────────────────

    def partial_update(self, request, pk=None):
        """PATCH /clients/<pk>/"""
        client = self._get_client_or_404(request, pk)
        if client is None:
            return error_response(
                message="Client not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = ClientUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        # If email is being changed, check uniqueness within org
        new_email = data.get("email")
        if new_email and new_email != client.email:
            if Client.objects.filter(
                organization=client.organization, email=new_email
            ).exclude(pk=client.pk).exists():
                return error_response(
                    message=f"A client with email '{new_email}' already exists in your organization.",
                    status_code=status.HTTP_409_CONFLICT,
                )

        for field, value in data.items():
            setattr(client, field, value)

        try:
            client.save(update_fields=list(data.keys()) + ["updated_at"])
        except IntegrityError:
            return error_response(
                message="A client with that email already exists in your organization.",
                status_code=status.HTTP_409_CONFLICT,
            )

        logger.info(
            "client_updated client_id=%s org_id=%s by=%s fields=%s",
            client.id, client.organization_id, request.user.id, list(data.keys()),
        )

        return success_response(
            data=ClientDetailSerializer(client).data,
            message="Client updated.",
        )

    # ── DELETE ───────────────────────────────────────────────────────────────

    def destroy(self, request, pk=None):
        """DELETE /clients/<pk>/"""
        client = self._get_client_or_404(request, pk)
        if client is None:
            return error_response(
                message="Client not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        client_id  = str(client.id)
        client_email = client.email
        client.delete()

        logger.info(
            "client_deleted client_id=%s org_id=%s by=%s",
            client_id, request.user.organization_id, request.user.id,
        )

        return success_response(
            message=f"Client '{client_email}' deleted.",
        )
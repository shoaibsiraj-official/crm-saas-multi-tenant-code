"""
core/exceptions.py — Global DRF exception handler + structured response helpers.
"""
import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Structured response builder
# ---------------------------------------------------------------------------

def success_response(data=None, message: str = "Success", status_code: int = status.HTTP_200_OK) -> Response:
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    message: str = "An error occurred",
    errors=None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=status_code,
    )


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

def custom_exception_handler(exc, context):
    """
    Wraps DRF's default handler so every error comes back in our
    structured { success, message, errors } envelope.
    """
    # Let DRF handle what it knows about first
    response = drf_exception_handler(exc, context)

    # --- Errors DRF didn't handle ---
    if response is None:
        if isinstance(exc, DjangoValidationError):
            return error_response(
                message="Validation error.",
                errors=exc.message_dict if hasattr(exc, "message_dict") else list(exc),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(exc, PermissionDenied):
            return error_response(
                message="Permission denied.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if isinstance(exc, Http404):
            return error_response(
                message="Not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Unexpected server error — log it but do not leak internals
        logger.exception("Unhandled exception: %s", exc)
        return error_response(
            message="An internal server error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # --- Reformat DRF's standard error responses ---
    original_data = response.data

    # DRF validation errors: { field: [msgs] }
    if isinstance(original_data, dict) and any(
        k not in ("detail", "code") for k in original_data
    ):
        # It's a field-level validation error dict
        message = "Validation failed."
        errors = original_data
    elif "detail" in original_data:
        message = str(original_data["detail"])
        errors = None
    else:
        message = "An error occurred."
        errors = original_data

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return response
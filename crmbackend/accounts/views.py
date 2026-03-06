"""
views.py — Thin controllers. Parse input → call service → format output.
No business logic lives here.
"""
import logging
from rest_framework import request

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from core.exceptions import error_response, success_response

from .permissions import IsVerified
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    UserSerializer,
)
from .services import (
    AuthenticationError,
    EmailVerificationError,
    LogoutError,
    PasswordResetError,
    RegistrationError,
    TokenRefreshError,
    confirm_password_reset,
    initiate_password_reset,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
    verify_email,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom throttle classes (rates defined in settings.py)
# ---------------------------------------------------------------------------

class AuthAnonThrottle(AnonRateThrottle):
    scope = "auth_anon"


class AuthUserThrottle(UserRateThrottle):
    scope = "auth_user"


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class RegisterView(APIView):
    """POST /api/auth/register/"""
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        print(request.data) 
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Registration failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tokens = register_user(serializer.validated_data, request)
        except RegistrationError as exc:
            return error_response(message=str(exc), status_code=status.HTTP_409_CONFLICT)

        return success_response(
            data=tokens,
            message="Registration successful. Please verify your email.",
            status_code=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginView(APIView):
    """POST /api/auth/login/"""

    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid input.",
                errors=serializer.errors,
            )

        data = serializer.validated_data
        try:
            result = login_user(data["email"], data["password"], request)
        except AuthenticationError as exc:
            return error_response(
                message=str(exc), status_code=status.HTTP_401_UNAUTHORIZED
            )

        return success_response(
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            message="Login successful.",
        )


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class LogoutView(APIView):
    """POST /api/auth/logout/"""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthUserThrottle]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid token.",
                errors=serializer.errors,
            )

        try:
            logout_user(serializer.validated_data["refresh"], request, request.user)
        except LogoutError as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(message="Logged out successfully.")


# ---------------------------------------------------------------------------
# Token Refresh
# ---------------------------------------------------------------------------

class TokenRefreshView(APIView):
    """POST /api/auth/refresh/"""

    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid token.",
                errors=serializer.errors,
            )

        try:
            tokens = refresh_access_token(serializer.validated_data["refresh"], request)
        except TokenRefreshError as exc:
            return error_response(
                message=str(exc), status_code=status.HTTP_401_UNAUTHORIZED
            )

        return success_response(data=tokens, message="Token refreshed.")


# ---------------------------------------------------------------------------
# Password Reset
# ---------------------------------------------------------------------------

class PasswordResetView(APIView):
    """POST /api/auth/password-reset/"""

    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid input.",
                errors=serializer.errors,
            )

        # Always return 200 regardless of whether email exists (prevent enumeration)
        initiate_password_reset(serializer.validated_data["email"], request)

        return success_response(
            message="If an account with that email exists, a reset link has been sent."
        )


class PasswordResetConfirmView(APIView):
    """POST /api/auth/password-reset-confirm/"""

    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid input.",
                errors=serializer.errors,
            )

        data = serializer.validated_data
        try:
            confirm_password_reset(
                str(data["token"]), data["new_password"], request
            )
        except PasswordResetError as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(message="Password has been reset successfully.")


# ---------------------------------------------------------------------------
# Me (Current User Profile)
# ---------------------------------------------------------------------------

class MeView(APIView):
    """GET /api/auth/me/"""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthUserThrottle]

    def get(self, request):
        return success_response(
            data=UserSerializer(request.user).data,
            message="User profile retrieved.",
        )


# ---------------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------------

class EmailVerifyView(APIView):
    """POST /api/auth/verify-email/"""

    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return error_response(message="Verification token is required.")

        try:
            verify_email(token)
        except EmailVerificationError as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(message="Email verified successfully.")
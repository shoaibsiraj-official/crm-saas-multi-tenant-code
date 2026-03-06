from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    PasswordResetView,
    PasswordResetConfirmView,
    MeView,
    EmailVerifyView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("password-reset/", PasswordResetView.as_view(), name="auth-password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("verify-email/", EmailVerifyView.as_view(), name="auth-verify-email"),
    path("me/", MeView.as_view(), name="auth-me"),
]
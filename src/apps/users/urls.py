from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.users.views import (
    EmailVerificationCompleteView,
    EmailVerificationView,
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetInvalidLinkView,
    PasswordResetView,
    SendVerificationCodeView,
    details_view,
    privacy_policy_view,
    signup_view,
)
from project.views import StandardSuccess

app_name = "registration"
urlpatterns = [
    # Registration
    path(_("sign-up/"), signup_view, name="signup"),
    path(_("sign-in/"), LoginView.as_view(), name="login"),
    path(
        _("log-out/"),
        auth_views.LogoutView.as_view(
            next_page=reverse_lazy("home"),
        ),
        name="logout",
    ),
    path(
        _("password-reset/"),
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        _("password-reset/<uidb64>/<token>/"),
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        _("password-reset/invalid-link/"),
        PasswordResetInvalidLinkView.as_view(),
        name="invalid_link",
    ),
    path(
        _("password-reset/done/"),
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        _("password-reset/complete/"),
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        _("password-change/"),
        PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        _("password-change/done/"),
        PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # Profile
    path(
        _("profile/modified/"),
        StandardSuccess.as_view(
            url=reverse_lazy("registration:profile_details"),
        ),
        name="profile_details_success",
    ),
    path(
        _("profile/details/"),
        details_view,
        name="profile_details",
    ),
    path(
        _("user-validation/"),
        EmailVerificationView.as_view(),
        name="user_validation",
    ),
    path(
        _("send-verification-code/"),
        SendVerificationCodeView.as_view(),
        name="send_verification_code",
    ),
    path(
        _("email-verification-complete/"),
        EmailVerificationCompleteView.as_view(),
        name="email_verification_complete",
    ),
    path(
        _("privacy-policy/"),
        privacy_policy_view,
        name="privacy_policy",
    ),
]

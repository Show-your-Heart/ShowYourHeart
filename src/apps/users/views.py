from itertools import islice

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
)
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.contrib.auth.views import (
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.contrib.auth.views import (
    PasswordResetView as BasePasswordResetView,
)
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from apps.users.forms import (
    AuthenticationForm,
    EmailVerificationCodeForm,
    PasswordChangeForm,
    PasswordResetConfirmForm,
    PasswordResetForm,
    ProfileDetailsForm,
    SendVerificationCodeForm,
    UserSignUpForm,
)
from apps.users.services import send_confirmation_mail
from project.decorators import anonymous_required
from project.mixins import AnonymousRequiredMixin
from project.views import StandardSuccess


class LoginView(AnonymousRequiredMixin, BaseLoginView):
    template_name = "registration/login.html"
    success_url = reverse_lazy("registration:profile_details")
    form_class = AuthenticationForm


@login_not_required
@anonymous_required
def signup_view(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST, None)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=email, password=password)
            login(request, user)
            return redirect("registration:profile_details")
    else:
        form = UserSignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def details_view(request):
    form = ProfileDetailsForm(request.POST or None, instance=request.user)
    new_email = request.user.email
    if form.is_valid():
        user = form.save(commit=False)
        if new_email != user.email:
            user.email_verified = False
        user.save()
        return redirect("registration:profile_details_success")
    return render(request, "profile/details.html", {"form": form})


class EmailVerificationView(FormView, StandardSuccess):
    form_class = EmailVerificationCodeForm
    template_name = "registration/user_validation.html"
    success_url = reverse_lazy("registration:email_verification_complete")

    def form_valid(self, form):
        if (
            str(form.cleaned_data["email_verification_code"])
            == self.request.user.email_verification_code
        ):
            self.request.user.email_verified = True
            self.request.user.save()
            return super().form_valid(form)
        else:
            form.add_error(
                "email_verification_code",
                ValidationError(
                    "Code entered is not correct and the user cannot "
                    "be verified. Please try again."
                ),
            )
            return super().form_invalid(form)


class SendVerificationCodeView(FormView):
    template_name = "registration/send_verification_code.html"
    form_class = SendVerificationCodeForm
    success_url = reverse_lazy("registration:user_validation")

    def form_valid(self, form):
        send_confirmation_mail(self.request.user)
        return super().form_valid(form)


class EmailVerificationCompleteView(StandardSuccess):
    template_name = "standard_success.html"
    title = _("Done!")
    page_title = _("Account verified")
    description = _("Account has been successfully verified.")
    url = reverse_lazy("registration:profile_details")
    link_text = _("Go back")


class PasswordResetView(AnonymousRequiredMixin, BasePasswordResetView):
    form_class = PasswordResetForm
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("registration:password_reset_done")

    def form_valid(self, form):
        user = form.get_users(form.cleaned_data["email"])
        # get_users is a generator, but our email field is unique.
        # This is the simplest way to retrieve only 1 item from a generator:
        user_list = list(islice(user, 1))
        if len(user_list) == 0 or not user_list[0].is_active:
            error = ValidationError(
                _(
                    "This email address does not match any registered account, "
                    "please check the spelling."
                ),
                code="inexistent_email",
            )
            form.add_error(None, error)
            return super().form_invalid(form)
        return super().form_valid(form)


class PasswordResetConfirmView(AnonymousRequiredMixin, BasePasswordResetConfirmView):
    form_class = PasswordResetConfirmForm
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("registration:password_reset_complete")

    def dispatch(self, *args, **kwargs):
        INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"  # noqa: N806
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )
        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])
        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)
            if not self.validlink:
                return redirect("registration:invalid_link")


class PasswordResetInvalidLinkView(AnonymousRequiredMixin, StandardSuccess):
    template_name = "standard_success.html"
    title = _("Invalid link")
    success_title = _("Invalid link")
    page_title = _("Invalid link")
    description = _("The link is invalid. Please try again.")
    url = reverse_lazy("registration:password_reset")
    link_text = _("Go back")


class PasswordResetDoneView(AnonymousRequiredMixin, StandardSuccess):
    template_name = "standard_success.html"
    title = _("Password reset sent")
    page_title = _("Password reset sent")
    description = _(
        "An email has been sent to your inbox. "
        "Please check it and follow the instructions to "
        "change your password."
    )
    url = reverse_lazy("registration:login")
    link_text = _("Go back")


class PasswordResetCompleteView(AnonymousRequiredMixin, StandardSuccess):
    template_name = "standard_success.html"
    title = _("Password reset complete")
    page_title = _("Password reset complete")
    description = _("Password reset complete")
    url = reverse_lazy("registration:login")
    link_text = _("Login")


class PasswordChangeView(BasePasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("registration:password_change_done")


class PasswordChangeDoneView(StandardSuccess):
    template_name = "standard_success.html"
    title = _("Done!")
    page_title = _("Password change")
    description = _("Password change successful.")
    url = reverse_lazy("registration:profile_details")
    link_text = _("Go back")


@login_not_required
def privacy_policy_view(request):
    return render(request, "registration/privacy_policy.html")

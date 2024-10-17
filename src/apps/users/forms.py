from constance import config
from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm as BaseAuthenticationForm,
)
from django.contrib.auth.forms import (
    PasswordChangeForm as BasePasswordChangeForm,
)
from django.contrib.auth.forms import (
    PasswordResetForm as BasePasswordResetForm,
)
from django.contrib.auth.forms import (
    SetPasswordForm as BaseSetPasswordForm,
)
from django.contrib.auth.forms import (
    UserCreationForm,
)
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from project.helpers import absolute_url
from project.post_office import send


class AuthenticationForm(BaseAuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "placeholder": _("Email adress"),
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("Password")}),
        label=_("Password"),
    )
    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(), label=_("Remember me")
    )


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users with a different approach to password changing.
    """

    new_password = forms.CharField(
        label=_("Change password"),
        help_text=_(
            "The current password is not displayed for security reasons. "
            "Use this field and save the changes to set a new password. "
            "While writing the new password will be visible to make it easier "
            "for you to copy and send it to the user."
        ),
        max_length=150,
        required=False,
    )

    class Meta:
        model = User
        fields = ("email", "password", "is_active", "is_superuser")

    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data.get("new_password", ""):
            instance.set_password(self.cleaned_data["new_password"])
        return instance


class UserSignUpForm(UserCreationForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Name")}),
    )
    surnames = forms.CharField(
        label=_("Surnames"),
        widget=forms.TextInput(attrs={"placeholder": _("Surnames")}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("Password")}),
        label=_("Password"),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("Password confirmation")}),
        label=_("Password confirmation"),
    )
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "placeholder": _("Email address")}
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "name",
            "surnames",
            "password1",
            "password2",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        privacy_policy_url = self.get_privacy_policy_url()
        privacy_policy_link = '<a href="{}" class="text-primary-500 font-bold hover:underline" target="_blank">privacy policy</a>'.format(  # noqa: E501
            privacy_policy_url
        )
        label_html = _("I have read and agree with the {}").format(privacy_policy_link)
        self.fields["accept_conditions"] = forms.BooleanField(
            label=format_html(label_html), required=True
        )

    def get_privacy_policy_url(self):
        return reverse("registration:privacy_policy")

    def save(self, commit=True):
        obj = super().save(commit)
        obj.set_boolean_datetime(
            "privacy_policy_accepted", self.cleaned_data["accept_conditions"]
        )
        return obj


class ProfileDetailsForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"placeholder": _("Name")}),
    )
    surnames = forms.CharField(
        label=_("Surnames"),
        widget=forms.TextInput(attrs={"placeholder": _("Surnames")}),
    )
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": _("Email address"),
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "name",
            "surnames",
            "email",
        )


class PasswordResetForm(BasePasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "placeholder": _("Email address"),
            }
        ),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        password_reset_url = absolute_url(
            reverse(
                "registration:password_reset_confirm",
                kwargs={
                    "uidb64": context["uid"],
                    "token": context["token"],
                },
            )
        )
        context = {
            "project_name": config.PROJECT_NAME,
            "user_name": context["user"].full_name,
            "date": str(
                formats.date_format(
                    timezone.now().date(),
                    format="SHORT_DATE_FORMAT",
                    use_l10n=True,
                )
            ),
            "time": str(formats.time_format(timezone.localtime(timezone.now()).time())),
            "user_email": context["email"],
            "absolute_url": settings.ABSOLUTE_URL,
            "password_reset_url": password_reset_url,
        }
        send(
            recipients=[
                to_email,
            ],
            template="password_reset",
            context=context,
        )


class PasswordResetConfirmForm(BaseSetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"autofocus": True, "placeholder": _("New password")}
        ),
        label=_("New password"),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": _("New password confirmation")}
        ),
        label=_("New password confirmation"),
    )


class PasswordChangeForm(BasePasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autofocus": True,
                "placeholder": _("Old password"),
            }
        ),
        label=_("Old password"),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("New password")}),
        label=_("New password"),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": _("New password confirmation")}
        ),
        label=_("New password confirmation"),
    )


class EmailVerificationCodeForm(forms.Form):
    email_verification_code = forms.IntegerField(
        widget=forms.TextInput(
            attrs=({"autofocus": True, "placeholder": _("Verification code")})
        ),
        label=_("Verification code"),
    )


class SendVerificationCodeForm(forms.Form):
    pass

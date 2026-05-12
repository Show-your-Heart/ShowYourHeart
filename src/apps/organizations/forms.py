from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.forms import ExportForm
from unfold.widgets import UnfoldAdminSelect2Widget

from apps.geodata.models import City, Country, Region1, ZipCode
from apps.methods.models import Method
from apps.organizations.widgets import syh_forms
from apps.settings.models import LegalStructure
from apps.users.models import User, UserProfile
from apps.users.services import send_registration_mail

from .models import Organization, Project


class OrganizationSignUpForm(forms.ModelForm):
    error_messages = {
        "invalid_signup": _("Invalid signup, check that you don't have an account."),
    }

    name = forms.CharField(
        label=_("Organisation name"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Name")}),
    )
    description = forms.CharField(
        label=_("Organisation description"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Description")}
        ),
    )
    vat_number = forms.CharField(
        label=_("VAT Number"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("VAT Number")}
        ),
    )
    contact_name = forms.CharField(
        label=_("Name of the contact person"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Name")}),
    )
    contact_telephone = forms.CharField(
        label=_("Phone number of the contact person"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Phone number")}
        ),
    )
    contact_mail = forms.CharField(
        label=_("Email address of the contact person"),
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "placeholder": _("Email"),
                "autocomplete": "email",
            }
        ),
    )
    website = forms.CharField(
        label=_("Website"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Website")}),
        required=False,
    )
    country = forms.ModelChoiceField(
        label=_("Country"),
        queryset=Country.objects.all(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_region1"),
                "hx-target": "#id_region1",
                "hx-trigger": "change",
                "hx-include": "#id_country",
            }
        ),
    )
    region1 = forms.ModelChoiceField(
        label=_("Region1"),
        queryset=Region1.objects.all(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_city"),
                "hx-target": "#id_city",
                "hx-trigger": "change",
                "hx-sync": "closest form:abort",
                "autocomplete": "off",
            }
        ),
    )
    city = forms.ModelChoiceField(
        label=_("City"),
        queryset=City.objects.none(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_zip_code"),
                "hx-target": "#id_zip_code",
                "hx-trigger": "change",
                "hx-sync": "closest form:abort",
                "autocomplete": "off",
            }
        ),
    )
    address = forms.CharField(
        label=_("Address"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Address")}),
    )
    zip_code = forms.ModelChoiceField(
        label=_("Zip Code"), queryset=ZipCode.objects.none()
    )
    legal_structure = forms.ModelChoiceField(
        label=_("Legal entity type"),
        queryset=LegalStructure.objects.all(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_methods"),
                "hx-target": "#id_methods",
                "hx-include": "#id_region1",
                "hx-trigger": "load, change",
                "autocomplete": "off",
            }
        ),
    )
    methods = forms.ModelMultipleChoiceField(
        label=_("Method of impact mesurement"),
        queryset=Method.objects.all(),
        required=False,
        widget=syh_forms.CheckboxSelectMultiple(
            attrs={
                "autocomplete": "off",
            }
        ),
    )
    bs_allow_public = forms.BooleanField(
        label=_("Allow infographics to be public"),
        widget=forms.CheckboxInput(),
        required=False,
    )

    class Meta:
        model = Organization
        widgets = {
            "logo": syh_forms.FileInput(),
        }
        fields = (
            "name",
            "description",
            "logo",
            "vat_number",
            "contact_name",
            "contact_telephone",
            "contact_mail",
            "website",
            "country",
            "region1",
            "city",
            "zip_code",
            "address",
            "legal_structure",
            "methods",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region1_id = self.data.get("region1")
        self.fields["city"].queryset = City.objects.filter(region1_id=region1_id)

        city_id = self.data.get("city")
        self.fields["zip_code"].queryset = ZipCode.objects.filter(city_id=city_id)

        privacy_policy_url = self.get_privacy_policy_url()
        privacy_policy_link = '<a href="{}" class="text-primary-500 font-bold hover:underline" target="_blank">terms and conditions</a>'.format(  # noqa: E501
            privacy_policy_url
        )
        label_html = _("I have read and accept the {}").format(privacy_policy_link)
        self.fields["accept_conditions"] = forms.BooleanField(
            label=format_html(label_html), required=True
        )

    def clean(self):
        contact = User.objects.filter(email=self.cleaned_data["contact_mail"])
        if contact.exists():
            raise self.get_invalid_signup_error()

    @transaction.atomic
    def save(self, commit=True):
        organization = super().save(commit=False)
        organization.set_boolean_datetime(
            "privacy_policy_accepted", self.cleaned_data["accept_conditions"]
        )

        user = User.objects.create_user(
            email=self.cleaned_data["contact_mail"],
            name=self.cleaned_data["contact_name"],
            user_profile_data={
                "telephone": self.cleaned_data["contact_telephone"],
                "organization": organization,
            },
        )
        if commit:
            organization.save()
            # save(commit=False) used before does not save the many to
            # many relations as it needs the instance to be created before
            # setting their values
            self.save_m2m()

            send_registration_mail(user, organization)

        return organization

    def get_privacy_policy_url(self):
        return reverse("registration:privacy_policy")

    def get_invalid_signup_error(self):
        return ValidationError(
            self.error_messages["invalid_signup"],
            code="invalid_signup",
        )


class OrganizationAdminForm(forms.ModelForm):
    class Meta:
        htmx_attrs = {
            "hx-get": reverse_lazy("organizations:load_methods"),
            "hx-swap": "innerHTML",
            "hx-trigger": "change",
            "hx-target": "#id_methods_from",
        }
        model = Organization
        fields = "__all__"  # noqa: DJ007
        widgets = {
            "legal_structure": UnfoldAdminSelect2Widget(attrs=htmx_attrs),
            "region1": UnfoldAdminSelect2Widget(attrs=htmx_attrs),
        }


class OrganizationAdminExportForm(ExportForm):
    region1 = forms.ModelChoiceField(queryset=Region1.objects.all(), required=True)


class OrganizationUpdateForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Organisation name"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Name")}),
    )
    description = forms.CharField(
        label=_("Organisation description"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Description")}
        ),
    )
    vat_number = forms.CharField(
        label=_("VAT Number"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("VAT Number")}
        ),
    )
    contact_name = forms.CharField(
        label=_("Name of the contact person"), max_length=100
    )
    contact_email = forms.EmailField(
        label=_("Email address of the contact person"),
        max_length=255,
    )
    contact_telephone = forms.CharField(
        label=_("Phone number of the contact person"), max_length=20
    )
    website = forms.CharField(
        label=_("Website"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Website")}),
        required=False,
    )
    country = forms.ModelChoiceField(
        label=_("Country"),
        queryset=Country.objects.all(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_region1"),
                "hx-target": "#id_region1",
                "hx-trigger": "change",
                "hx-include": "#id_country",
            }
        ),
    )
    region1 = forms.ModelChoiceField(
        label=_("Region1"),
        queryset=Region1.objects.all(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_city"),
                "hx-target": "#id_city",
                "hx-trigger": "change",
                "autocomplete": "off",
                "hx-sync": "closest form:abort",
            }
        ),
    )
    city = forms.ModelChoiceField(
        label=_("City"),
        queryset=City.objects.none(),
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("organizations:load_zip_code"),
                "hx-target": "#id_zip_code",
                "hx-trigger": "change",
                "autocomplete": "off",
                "hx-sync": "closest form:abort",
            }
        ),
    )
    address = forms.CharField(
        label=_("Address"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Address")}),
    )
    zip_code = forms.ModelChoiceField(
        label=_("Zip Code"), queryset=ZipCode.objects.none()
    )
    legal_structure = forms.ModelChoiceField(
        label=_("Legal entity type"),
        queryset=LegalStructure.objects.all(),
    )
    bs_allow_public = forms.BooleanField(
        label=_("Allow infographics to be public"),
        widget=forms.CheckboxInput(),
        required=False,
    )

    class Meta:
        model = Organization
        widgets = {
            "logo": syh_forms.FileInput(),
        }
        fields = [
            "name",
            "description",
            "logo",
            "vat_number",
            "contact_name",
            "contact_telephone",
            "contact_email",
            "website",
            "country",
            "region1",
            "city",
            "zip_code",
            "address",
            "legal_structure",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            region1_id = self.data.get("region1") or self.instance.region1_id
            self.fields["city"].queryset = City.objects.filter(region1_id=region1_id)

            city_id = self.data.get("city") or self.instance.city_id
            self.fields["zip_code"].queryset = ZipCode.objects.filter(city_id=city_id)

            user_profile = UserProfile.objects.filter(organization__id=self.instance.id)
            if user_profile:
                user_profile = user_profile.first()

                self.fields["contact_name"].initial = user_profile.user.name
                self.fields["contact_email"].initial = user_profile.user.email
                self.fields[
                    "contact_telephone"
                ].initial = user_profile.user.profile.telephone

    def save(self, commit=True):
        org = super().save(commit=False)
        user_profile = UserProfile.objects.filter(organization__id=self.instance.id)
        if user_profile:
            user_profile = user_profile.first()
            user_profile.user.name = self.cleaned_data["contact_name"]
            user_profile.user.email = self.cleaned_data["contact_email"]
            user_profile.telephone = self.cleaned_data["contact_telephone"]
            user_profile.save()
            user_profile.user.save()
        if commit:
            org.save()
        return org


class ProjectCreationForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Project name"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Project name")}
        ),
    )
    description = forms.CharField(
        label=_("Brief description"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Brief description")}
        ),
    )
    start_date = forms.DateField(
        label=_("Start date"),
        help_text=_("If there is no start date, put first january"),
        widget=syh_forms.DateInput(
            format="%Y-%m-%d", attrs={"autofocus": True, "type": "date"}
        ),
        input_formats=["%Y-%m-%d"],
    )
    main_action_scope = forms.ChoiceField(
        label=_("Main action scope"),
        choices=Project.ActionScope.choices,
        required=True,
    )
    secondary_action_scope = forms.ChoiceField(
        label=_("Secondary action scope"), choices=Project.ActionScope.choices
    )
    main_legal_entity_type = forms.ChoiceField(
        choices=Project.LegalEntityType.choices,
        required=True,
    )
    secondary_legal_entity_type = forms.ChoiceField(
        choices=Project.LegalEntityType.choices,
        required=True,
    )
    contact_name = forms.CharField(
        label=_("Name of the contact person"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Contact name")}
        ),
    )
    contact_telephone = forms.CharField(
        label=_("Phone number of the contact person"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Contact phone number")}
        ),
    )
    contact_email = forms.CharField(
        label=_("Email address of the contact person"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": _("Contact email")}
        ),
    )
    publish_results = forms.BooleanField(
        label=_("I want to make the results public"), widget=forms.CheckboxInput()
    )
    authorize = forms.BooleanField(
        label=_("Authorise the use of my data for inclusion in the final report"),
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "start_date",
            "main_action_scope",
            "secondary_action_scope",
            "main_legal_entity_type",
            "secondary_legal_entity_type",
            "contact_name",
            "contact_telephone",
            "contact_email",
            "publish_results",
            "authorize",
        )

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

    @transaction.atomic
    def save(self, commit=True):
        project = super().save(commit=False)

        if self.organization:
            project.organization = self.organization

        if commit:
            project.save()
            # save(commit=False) used before does not save the many to
            # many relations as it needs the instance to be created before
            # setting their values
            self.save_m2m()

        return project


class ProjectSelectionForm(forms.Form):
    project = forms.ModelChoiceField(
        label=_("Choose Existing Project"),
        queryset=Project.objects.all(),
        widget=forms.Select(
            attrs={
                "x-on:change": "setSelectedProjectId($event.target.value); setSelectedMethodId();"  # noqa: E501
            }
        ),
    )

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = (
            organization.projects.all() if organization else Project.objects.none()
        )

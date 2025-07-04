from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.settings.models import LegalStructure
from apps.users.models import User

from .models import Organization


class OrganizationSignUpForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Name")}),
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
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Email")}),
    )
    website = forms.CharField(
        label=_("Website"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Website")}),
    )
    country = forms.CharField(
        label=_("Country"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Country")}),
    )
    region = forms.CharField(
        label=_("Region"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Region")}),
    )
    city = forms.CharField(
        label=_("City"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("City")}),
    )
    legal_structure = forms.ModelChoiceField(
        label=_("Primary legal entity type"), queryset=LegalStructure.objects.all()
    )

    class Meta:
        model = Organization
        fields = (
            "name",
            "vat_number",
            "contact_name",
            "contact_telephone",
            "contact_mail",
            "website",
            "country",
            "region",
            "city",
            "legal_structure",
        )

    @transaction.atomic
    def save(self, commit=True):
        organization = super().save(commit=False)

        contact = User.objects.filter(email=self.cleaned_data["contact_mail"])
        if contact.exists():
            contact = contact[0]
        else:
            contact = User.objects.create_user(
                email=self.cleaned_data["contact_mail"],
                name=self.cleaned_data["contact_name"],
                user_profile_data={
                    "telephone": self.cleaned_data["contact_telephone"],
                },
            )

        organization.contact = contact

        if commit:
            organization.save()

        return organization

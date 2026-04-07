from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import (
    UnfoldAdminEmailInputWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminTextInputWidget,
)

from apps.methods.widgets import syh_forms

from .models import Indicator, IndicatorsSet, Invitation, Method, Section


class MethodForm(forms.ModelForm):
    class Meta:
        model = Method
        fields = "__all__"  # noqa: DJ007

        htmx_attrs = {
            "hx-get": reverse_lazy("methods:load_ext_surveys"),
            "hx-swap": "innerHTML",
            "hx-trigger": "change",
            "hx-target": "#id_external_surveys",
        }
        widgets = {
            "networks": UnfoldAdminSelect2Widget(attrs=htmx_attrs),
        }

    def clean_pdf_file(self):
        file = self.cleaned_data.get("pdf_file", False)
        if file and not file.name.endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        return file


def get_choices(options_list):
    result = []
    if options_list:
        for option in options_list.items.all():
            result.append((option, option))
    return result


def get_field(indicator):
    field_name = indicator.name

    if indicator.is_group_indicator:
        return {
            Indicator.DataType.STRING: forms.CharField(
                label=field_name, required=False, widget=syh_forms.GroupTextInput
            ),
            Indicator.DataType.INTEGER: forms.IntegerField(
                label=field_name, required=False, widget=syh_forms.GroupIntegerInput
            ),
            Indicator.DataType.DECIMAL: forms.DecimalField(
                label=field_name, required=False, widget=syh_forms.GroupDecimalInput
            ),
        }.get(indicator.data_type)

    else:
        return {
            Indicator.DataType.STRING: forms.CharField(
                label=field_name, required=False, widget=syh_forms.TextInput
            ),
            Indicator.DataType.TEXT: forms.CharField(
                label=field_name, required=False, widget=syh_forms.TextArea
            ),
            Indicator.DataType.INTEGER: forms.IntegerField(
                label=field_name, required=False, widget=syh_forms.IntegerInput
            ),
            Indicator.DataType.DECIMAL: forms.DecimalField(
                label=field_name, required=False, widget=syh_forms.DecimalInput
            ),
            Indicator.DataType.BOOLEAN: forms.BooleanField(
                label=field_name, required=False, widget=syh_forms.BooleanInput
            ),
            Indicator.DataType.DATE: forms.DateField(
                label=field_name,
                required=False,
                widget=syh_forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
                input_formats=["%Y-%m-%d"],
            ),
            Indicator.DataType.ATTACHMENT: forms.FileField(
                label=field_name, required=False, widget=syh_forms.AttachmentInput
            ),
            Indicator.DataType.CHECKBOX: forms.MultipleChoiceField(
                label=field_name,
                required=False,
                widget=syh_forms.CheckboxSelectMultiple,
                choices=get_choices(indicator.list_options),
            ),
            Indicator.DataType.RADIOBUTTON: forms.ChoiceField(
                label=field_name,
                required=False,
                choices=get_choices(indicator.list_options),
                widget=syh_forms.RadioButtonInput,
            ),
            Indicator.DataType.DROPDOWN: forms.ChoiceField(
                label=field_name,
                required=False,
                choices=get_choices(indicator.list_options),
                widget=syh_forms.DropdownInput,
            ),
            Indicator.DataType.INTEGERGENDER: syh_forms.GenderInput(
                required=False, input_type="integer"
            ),
            Indicator.DataType.DECIMALGENDER: syh_forms.GenderInput(
                required=False, input_type="decimal"
            ),
        }.get(indicator.data_type)


def get_dynamic_form(method, indicator_result_list, readonly, placeholder_dict):
    class DynamicSurveyForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for i in method.indicators.all():
                field_name = f"question_{i.id}"
                field = get_field(i)

                if field is None:
                    continue

                self.fields[field_name] = field
                self.fields[field_name].widget.attrs["readonly"] = readonly
                self.fields[field_name].widget.attrs["placeholder"] = (
                    placeholder_dict.get(i.code, "")
                )
                self.fields[field_name].widget.attrs["description"] = i.description
                self.fields[field_name].widget.attrs["code"] = i.code

                # Handle gendered indicators (3 fields)
                if isinstance(field, syh_forms.GenderInput):
                    if i.data_type == Indicator.DataType.DECIMALGENDER:
                        self.fields[field_name].widget.attrs["input_type"] = "decimal"

    return DynamicSurveyForm


class InvitationInlineForm(forms.ModelForm):
    # Without this form the styles of the inputs are not applied
    name = forms.CharField(widget=UnfoldAdminTextInputWidget, required=False)
    email = forms.EmailField(
        widget=UnfoldAdminEmailInputWidget,
        required=True,
    )


class InvitationCreationForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Name")}),
    )
    surnames = forms.CharField(
        label=_("Surnames"),
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("Surnames")}),
    )
    #   TODO: Choose the language of the external survey
    #   language = forms.ChoiceField(
    #       choices=settings.LANGUAGES,
    #       label=_("Language"),
    #       widget=forms.Select(attrs={"class": "form-select"}),
    #   )
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=Invitation.Gender.choices,
        widget=forms.Select(
            attrs={
                "hx-trigger": "change",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Invitation
        fields = ("name", "surnames", "email", "gender")


class SectionInlineForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Section.objects.all(), widget=UnfoldAdminSelect2Widget, required=False
    )

    class Meta:
        model = Section
        fields = (
            "title",
            "description",
            "parent",
            "indicators",
            "indicators_sets",
        )

        widgets = {
            "title": UnfoldAdminTextInputWidget,
            "description": WysiwygWidget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.method_id:
            method_indicators = self.instance.method.indicators.all()
            assigned_indicators = (
                Section.objects.filter(method=self.instance.method)
                .exclude(pk=self.instance.pk)
                .values_list("indicators__id", flat=True)
            )
            assigned_indicators = [pk for pk in assigned_indicators if pk is not None]
            self.fields["indicators"].queryset = method_indicators.exclude(
                pk__in=assigned_indicators
            )
            method_indicators_sets = self.instance.method.indicators_sets.all()
            assigned_indicators_sets = (
                Section.objects.filter(method=self.instance.method)
                .exclude(pk=self.instance.pk)
                .values_list("indicators_sets__id", flat=True)
            )
            assigned_indicators_sets = [
                pk for pk in assigned_indicators_sets if pk is not None
            ]
            self.fields["indicators_sets"].queryset = method_indicators_sets.exclude(
                pk__in=assigned_indicators_sets
            )
            self.fields["parent"].queryset = Section.objects.filter(
                method=self.instance.method, parent__isnull=True
            ).exclude(pk=self.instance.id)
        else:
            self.fields["indicators"].queryset = Indicator.objects.none()
            self.fields["indicators_sets"].queryset = IndicatorsSet.objects.none()
            self.fields["parent"].queryset = Section.objects.none()


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"  # noqa: DJ007

        widgets = {
            "name": WysiwygWidget,
            "description": WysiwygWidget,
        }


class IndicatorsSetForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"  # noqa: DJ007

        widgets = {
            "description": WysiwygWidget,
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = "__all__"  # noqa

        widgets = {
            "description": WysiwygWidget,
        }

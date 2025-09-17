from django import forms
from django.urls import reverse_lazy
from unfold.widgets import (
    UnfoldAdminEmailInputWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
)

from apps.methods.widgets import syh_forms

from .models import Indicator, IndicatorResult, Method, Section


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
            "network_owner": UnfoldAdminSelectWidget(attrs=htmx_attrs),
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
                self.fields[field_name].initial = get_field_value(
                    indicator_result_list, i
                )
                self.fields[field_name].widget.attrs["readonly"] = readonly
                self.fields[field_name].widget.attrs["placeholder"] = (
                    placeholder_dict.get(field_name, "")
                )
                self.fields[field_name].widget.attrs["code"] = i.code
                self.fields[field_name].widget.attrs["dependant_indicators"] = (
                    i.dependant_indicators
                )

                if i.is_direct_indicator:
                    self.fields[field_name].widget.attrs["condition"] = i.condition
                else:
                    self.fields[field_name].widget.attrs["formula"] = i.formula

                self.fields[field_name].widget.attrs["validation"] = i.validation

                # Handle gendered indicators (3 fields)
                if isinstance(field, syh_forms.GenderInput):
                    if i.data_type == Indicator.DataType.DECIMALGENDER:
                        self.fields[field_name].widget.attrs["input_type"] = "decimal"

                    self.fields[field_name].widget.attrs["value"] = {
                        "non_binary": get_gender_field_value(
                            indicator_result_list, i, "non_binary"
                        ),
                        "male": get_gender_field_value(
                            indicator_result_list, i, "male"
                        ),
                        "female": get_gender_field_value(
                            indicator_result_list, i, "female"
                        ),
                    }

    return DynamicSurveyForm


def get_gender_field_value(indicator_result_list, indicator, suffix):
    field_value = None

    gender_lookup = {
        "male": IndicatorResult.Gender.MALE,
        "female": IndicatorResult.Gender.FEMALE,
        "non_binary": IndicatorResult.Gender.NON_BINARY,
    }
    indicator_result = next(
        (
            res
            for res in indicator_result_list
            if res.indicator == indicator and res.gender == gender_lookup[suffix]
        ),
        None,
    )

    if indicator_result:
        field_value = indicator_result.value

    return field_value


def get_field_value(indicator_result_list, indicator):
    field_value = None
    if len(indicator_result_list):
        indicator_result = indicator_result_list.filter(indicator=indicator).first()
        if indicator_result:
            if indicator.data_type == Indicator.DataType.CHECKBOX:
                field_value = indicator_result.value.split("|")
            else:
                field_value = indicator_result.value
    return field_value


def get_form_sections(method):
    result = {}
    sections = Section.objects.filter(method=method).order_by("order")

    for section in sections.filter(parent__isnull=True):
        indicators = get_indicators_list(section.indicators.all())

        children = sections.filter(parent=section)
        subsections = []
        for child in children:
            child_indicators = get_indicators_list(child.indicators.all())
            subsections.append({child.title: child_indicators})

        result[section] = {
            "indicators": indicators,
            "subsections": subsections,
        }

    return result


def get_indicators_list(indicators_list):
    indicators = []
    for i in indicators_list:
        indicators.append({"field_name": "question_" + str(i.id), "indicator": i})
    return indicators


class InvitationInlineForm(forms.ModelForm):
    # Without this form the styles of the inputs are not applied
    name = forms.CharField(widget=UnfoldAdminTextInputWidget, required=False)
    email = forms.EmailField(
        widget=UnfoldAdminEmailInputWidget,
        required=True,
    )


class SectionInlineForm(forms.ModelForm):
    title = forms.CharField(widget=UnfoldAdminTextInputWidget, required=True)
    parent = forms.ModelChoiceField(
        queryset=Section.objects.all(), widget=UnfoldAdminSelectWidget, required=False
    )

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
            self.fields["parent"].queryset = Section.objects.filter(
                method=self.instance.method, parent__isnull=True
            ).exclude(pk=self.instance.id)
        else:
            self.fields["indicators"].queryset = Indicator.objects.none()
            self.fields["parent"].queryset = Section.objects.none()


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"  # noqa: DJ007

        widgets = {
            "description": UnfoldAdminTextareaWidget,
        }

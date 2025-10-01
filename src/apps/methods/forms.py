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
        Indicator.DataType.INTEGERGENDER: {
            "male": forms.IntegerField(
                label="Male", required=False, widget=syh_forms.IntegerInput
            ),
            "female": forms.IntegerField(
                label="Female", required=False, widget=syh_forms.IntegerInput
            ),
            "non_binary": forms.IntegerField(
                label="Non-binary", required=False, widget=syh_forms.IntegerInput
            ),
        },
        Indicator.DataType.DECIMALGENDER: {
            "male": forms.DecimalField(
                label="Male", required=False, widget=syh_forms.DecimalInput
            ),
            "female": forms.DecimalField(
                label="Female", required=False, widget=syh_forms.DecimalInput
            ),
            "non_binary": forms.DecimalField(
                label="Non-binary", required=False, widget=syh_forms.DecimalInput
            ),
        },
    }.get(indicator.data_type)


def get_dynamic_form(method, indicator_result_list, readonly, placeholder_dict):
    class DynamicSurveyForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for i in method.indicators.filter(is_direct_indicator=True):
                field_name = f"question_{i.id}"
                field = get_field(i)

                if field is None:
                    continue

                # Handle gendered indicators (3 fields)
                if isinstance(field, dict):
                    for suffix, f in field.items():
                        full_name = f"{field_name}_{suffix}"
                        self.fields[full_name] = f
                        self.fields[full_name].widget.attrs["readonly"] = readonly
                        self.fields[full_name].initial = get_gender_field_value(
                            indicator_result_list, i, suffix
                        )
                        self.fields[full_name].widget.attrs["label"] = i.name
                        self.fields[full_name].widget.attrs["description"] = (
                            i.description
                        )
                        self.fields[full_name].widget.attrs["msg"] = i.message
                        self.fields[full_name].widget.attrs["placeholder"] = (
                            placeholder_dict.get(full_name, "")
                        )

                # Handle normal indicators (single field)
                else:
                    self.fields[field_name] = field
                    self.fields[field_name].widget.attrs["readonly"] = readonly
                    self.fields[field_name].initial = get_field_value(
                        indicator_result_list, i
                    )
                    self.fields[field_name].widget.attrs["label"] = i.name
                    self.fields[field_name].widget.attrs["description"] = i.description
                    self.fields[field_name].widget.attrs["msg"] = i.message
                    self.fields[field_name].widget.attrs["placeholder"] = (
                        placeholder_dict.get(field_name, "")
                    )

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
        if (
            i.data_type == Indicator.DataType.INTEGERGENDER
            or i.data_type == Indicator.DataType.DECIMALGENDER
        ):
            indicators.append(
                {"field_name": "question_" + str(i.id) + "_male", "indicator": i}
            )
            indicators.append(
                {"field_name": "question_" + str(i.id) + "_female", "indicator": i}
            )
            indicators.append(
                {
                    "field_name": "question_" + str(i.id) + "_non_binary",
                    "indicator": i,
                }
            )
        else:
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

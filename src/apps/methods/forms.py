from django import forms
from unfold.widgets import (
    UnfoldAdminEmailInputWidget,
    UnfoldAdminTextInputWidget,
)

from .models import Indicator, Method


class MethodForm(forms.ModelForm):
    class Meta:
        model = Method
        fields = "__all__"  # noqa: DJ007

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
        Indicator.DataType.STRING: forms.CharField(label=field_name, required=True),
        Indicator.DataType.TEXT: forms.CharField(
            label=field_name, required=True, widget=forms.Textarea
        ),
        Indicator.DataType.INTEGER: forms.IntegerField(label=field_name, required=True),
        Indicator.DataType.DECIMAL: forms.DecimalField(label=field_name, required=True),
        Indicator.DataType.BOOLEAN: forms.BooleanField(label=field_name, required=True),
        Indicator.DataType.DATE: forms.DateField(
            label=field_name,
            required=True,
            widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            input_formats=["%Y-%m-%d"],
        ),
        Indicator.DataType.ATTACHMENT: forms.FileField(label=field_name, required=True),
        Indicator.DataType.CHECKBOX: forms.MultipleChoiceField(
            label=field_name,
            required=True,
            widget=forms.CheckboxSelectMultiple,
            choices=get_choices(indicator.list_options),
        ),
        Indicator.DataType.RADIOBUTTON: forms.ChoiceField(
            label=field_name,
            required=True,
            choices=get_choices(indicator.list_options),
            widget=forms.RadioSelect,
        ),
        Indicator.DataType.DROPDOWN: forms.ChoiceField(
            label=field_name,
            required=True,
            choices=get_choices(indicator.list_options),
        ),
    }.get(indicator.data_type)


def get_dynamic_form(method, indicator_result_list, readonly):
    class DynamicSurveyForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for i in method.indicators.filter(is_direct_indicator=True):
                field_name = f"question_{i.id}"
                field = get_field(i)

                if field is not None:  # Skip unknown types
                    field.initial = (
                        indicator_result_list.get(indicator=i).value
                        if len(indicator_result_list)
                        else ""
                    )
                    self.fields[field_name] = field
                    self.fields[field_name].widget.attrs["readonly"] = readonly

    return DynamicSurveyForm


class InvitationInlineForm(forms.ModelForm):
    # Without this form the styles of the inputs are not applied
    name = forms.CharField(widget=UnfoldAdminTextInputWidget, required=False)
    email = forms.EmailField(
        widget=UnfoldAdminEmailInputWidget,
        required=True,
    )

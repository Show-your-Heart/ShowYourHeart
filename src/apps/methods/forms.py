from django import forms
from django.urls import reverse_lazy
from unfold.widgets import (
    UnfoldAdminEmailInputWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
)

from .models import Indicator, Method, Section


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
        Indicator.DataType.STRING: forms.CharField(label=field_name, required=False),
        Indicator.DataType.TEXT: forms.CharField(
            label=field_name, required=False, widget=forms.Textarea
        ),
        Indicator.DataType.INTEGER: forms.IntegerField(
            label=field_name, required=False
        ),
        Indicator.DataType.DECIMAL: forms.DecimalField(
            label=field_name, required=False
        ),
        Indicator.DataType.BOOLEAN: forms.BooleanField(
            label=field_name, required=False
        ),
        Indicator.DataType.DATE: forms.DateField(
            label=field_name,
            required=False,
            widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            input_formats=["%Y-%m-%d"],
        ),
        Indicator.DataType.ATTACHMENT: forms.FileField(
            label=field_name, required=False
        ),
        Indicator.DataType.CHECKBOX: forms.MultipleChoiceField(
            label=field_name,
            required=False,
            widget=forms.CheckboxSelectMultiple,
            choices=get_choices(indicator.list_options),
        ),
        Indicator.DataType.RADIOBUTTON: forms.ChoiceField(
            label=field_name,
            required=False,
            choices=get_choices(indicator.list_options),
            widget=forms.RadioSelect,
        ),
        Indicator.DataType.DROPDOWN: forms.ChoiceField(
            label=field_name,
            required=False,
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
                    if len(indicator_result_list):
                        indicator = indicator_result_list.filter(indicator=i).first()
                        if indicator:
                            field.initial = (
                                indicator.value.split("|")
                                if i.data_type == Indicator.DataType.CHECKBOX
                                else indicator.value
                            )

                    self.fields[field_name] = field
                    self.fields[field_name].widget.attrs["readonly"] = readonly

    return DynamicSurveyForm


def get_form_sections(method):
    result = {}
    sections = Section.objects.filter(method=method, parent__isnull=True).order_by(
        "order"
    )

    for section in sections:
        indicators = []
        for i in section.indicators.all():
            indicators.append({"field_name": "question_" + str(i.id), "indicator": i})

        result[section] = indicators

    return result


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
            self.fields["indicators"].queryset = self.instance.method.indicators.all()
            self.fields["parent"].queryset = Section.objects.filter(
                method=self.instance.method
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

from django import forms


class FileInput(forms.ClearableFileInput):
    template_name = "organizations/components/file.html"


class DateInput(forms.DateInput):
    template_name = "organizations/components/date_input.html"
    input_type = "date"


class CheckboxSelectMultiple(forms.SelectMultiple):
    template_name = "organizations/components/checkbox_select.html"
    option_template_name = "organizations/components/checkbox.html"
    use_fieldset = False

from django import forms


class FileInput(forms.ClearableFileInput):
    template_name = "organizations/components/file.html"


class DateInput(forms.DateInput):
    template_name = "organizations/components/date_input.html"
    input_type = "date"

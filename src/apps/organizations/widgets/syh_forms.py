from django import forms


class FileInput(forms.ClearableFileInput):
    template_name = "organizations/components/file.html"

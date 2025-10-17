from django import forms


class FileInput(forms.ClearableFileInput):
    template_name = "components/forms/image.html"

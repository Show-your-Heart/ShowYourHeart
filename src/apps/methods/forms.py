from django import forms

from .models import Method


class MethodForm(forms.ModelForm):
    class Meta:
        model = Method
        fields = "__all__"  # noqa: DJ007

    def clean_pdf_file(self):
        file = self.cleaned_data.get("pdf_file", False)
        if file and not file.name.endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        return file

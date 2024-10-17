from django import forms


class CheckboxInput(forms.CheckboxInput):
    template_name = "widgets/checkbox.html"

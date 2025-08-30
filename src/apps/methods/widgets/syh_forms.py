from django import forms


class TextInput(forms.TextInput):
    template_name = "components/forms/input.html"

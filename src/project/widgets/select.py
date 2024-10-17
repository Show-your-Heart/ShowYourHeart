from django import forms


class Select(forms.Select):
    template_name = "widgets/select.html"

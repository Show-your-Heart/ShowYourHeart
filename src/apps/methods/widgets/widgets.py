from django import forms


class GenderInputWidget(forms.Widget):
    template_name = "components/methods/gender.html"

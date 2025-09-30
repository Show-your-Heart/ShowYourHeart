from django import forms


class TextInput(forms.TextInput):
    template_name = "components/forms/input.html"


class TextArea(forms.Textarea):
    template_name = "components/forms/textarea.html"


class IntegerInput(forms.NumberInput):
    template_name = "components/forms/input.html"
    input_type = "number"


class DecimalInput(forms.NumberInput):
    template_name = "components/forms/input.html"


class BooleanInput(forms.CheckboxInput):
    template_name = "components/forms/boolean.html"


class DateInput(forms.DateInput):
    template_name = "components/forms/input.html"
    input_type = "date"


class AttachmentInput(forms.ClearableFileInput):
    template_name = "components/forms/file.html"


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "components/forms/checkbox.html"


class RadioButtonInput(forms.RadioSelect):
    template_name = "components/forms/radio.html"


class DropdownInput(forms.Select):
    template_name = "components/forms/dropdown.html"


class IntegerGenderInput(forms.NumberInput):
    template_name = "components/forms/gender.html"


class DecimalGenderInput(forms.NumberInput):
    template_name = "components/forms/gender.html"

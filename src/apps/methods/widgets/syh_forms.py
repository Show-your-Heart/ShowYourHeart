from django import forms

from .widgets import GenderInputWidget


class TextInput(forms.TextInput):
    template_name = "components/methods/input.html"


class TextArea(forms.Textarea):
    template_name = "components/methods/textarea.html"


class IntegerInput(forms.NumberInput):
    template_name = "components/methods/input.html"
    input_type = "number"


class DecimalInput(forms.NumberInput):
    template_name = "components/methods/input.html"


class BooleanInput(forms.CheckboxInput):
    template_name = "components/methods/boolean.html"


class DateInput(forms.DateInput):
    template_name = "components/methods/input.html"
    input_type = "date"


class AttachmentInput(forms.ClearableFileInput):
    template_name = "components/methods/file.html"


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "components/methods/checkbox.html"


class RadioButtonInput(forms.RadioSelect):
    template_name = "components/methods/radio.html"


class DropdownInput(forms.Select):
    template_name = "components/methods/dropdown.html"


class GenderInput(forms.MultiValueField):
    widget = GenderInputWidget

    def __init__(self, input_type, *args, **kwargs):
        widget = IntegerInput
        if input_type == "decimal":
            widget = DecimalInput

        fields = (
            forms.IntegerField(required=False, widget=widget),
            forms.IntegerField(required=False, widget=widget),
            forms.IntegerField(required=False, widget=widget),
        )
        super().__init__(*args, **kwargs, fields=fields, require_all_fields=False)


class GroupTextInput(forms.TextInput):
    template_name = "components/methods/group_input.html"


class GroupIntegerInput(forms.NumberInput):
    template_name = "components/methods/group_input.html"
    input_type = "number"


class GroupDecimalInput(forms.NumberInput):
    template_name = "components/methods/group_input.html"

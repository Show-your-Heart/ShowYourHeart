from django import forms

from .widgets import IntegerGenderInputWidget


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


class IntegerGenderInput(forms.MultiValueField):
    widget = IntegerGenderInputWidget
    input_type = "integer"

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(required=False, widget=IntegerInput),
            forms.IntegerField(required=False, widget=IntegerInput),
            forms.IntegerField(required=False, widget=IntegerInput),
        )
        super().__init__(*args, **kwargs, fields=fields, require_all_fields=False)


#     def compress(self, data_list):
#         # data_list is [non_binary, male, female]
#         if data_list:
#             return {
#                 "non_binary": data_list[0],
#                 "male": data_list[1],
#                 "female": data_list[2],
#             }
#         return {"non_binary": None, "male": None, "female": None}


class DecimalGenderInput(forms.NumberInput):
    template_name = "components/forms/gender.html"
    input_type = "decimal"

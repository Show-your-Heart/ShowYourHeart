from django import forms


class IntegerGenderInputWidget(forms.Widget):
    template_name = "components/forms/gender.html"
    input_type = "integer"

    # def get_context(self, name, _, attrs):
    #     value = self.attrs.get("value", "")

    #     if isinstance(value, list):
    #         values = {
    #             "female": value[0] if len(value) > 0 else "",
    #             "male": value[1] if len(value) > 1 else "",
    #             "non_binary": value[2] if len(value) > 2 else "",
    #         }
    #     else:
    #         values = {"non_binary": "", "male": "", "female": ""}

    #     context = super().get_context(name, value, attrs)
    #     context["widget"].update(
    #         {
    #             "values": values,
    #             "input_type": "number",
    #             #         "name": name,
    #             #         "label": label,
    #             #         "description": description,
    #             #         "msg": msg,
    #         }
    #     )
    #     return context

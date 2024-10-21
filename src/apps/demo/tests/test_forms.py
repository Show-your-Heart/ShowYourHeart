from django import forms
from django.test import TestCase

from apps.demo.forms import DataForm


class DataFormTest(TestCase):
    def setUp(self):
        self.form = DataForm(
            data={
                "field_text_1": "",
                "field_text_2": "",
                "field_email": "test",
                "field_radio": "",
                "field_boolean_checkbox": "",
                "field_select_dropdown": "",
                "field_password": "test_password",
                "field_password_confirm": "test",
                "field_number": "string",
            }
        )

    def test_form_errors(self):
        self.assertFalse(self.form.is_valid())

        with self.subTest("Required fields"):
            required_fields = [
                "field_text_1",
                "field_text_2",
                "field_radio",
                "field_select_dropdown",
            ]

            for field in required_fields:
                self.assertEqual(
                    self.form.errors[field], ["This field is required."]
                )

        with self.subTest("Other validations"):
            self.assertEqual(
                self.form.errors["field_number"], ["Enter a whole number."]
            )


    def test_clean(self):
        form_error_password = DataForm(
            data={
                "field_text_1": "test",
                "field_text_2": "test",
                "field_email": "test@test.com",
                "field_radio": "test",
                "field_boolean_checkbox": "test",
                "field_select_dropdown": "test",
                "field_password": "password",
                "field_password_confirm": "unequal password",
                "field_number": 10,
            }
        )
        self.assertFalse(form_error_password.is_valid())

        with self.assertRaises(forms.ValidationError) as error:
            form_error_password.clean()

        self.assertEqual(
            "['The two password fields must match.']", str(error.exception)
        )

from django.test import TestCase

from apps.demo.models import Data
from apps.demo.tests.factories import DataFactory


class DataTest(TestCase):
    def setUp(self):
        self.full_data = DataFactory(
            field_text_1="test_field_text_1",
            field_text_2="test_field_text_2",
            field_email="test@field_email.test",
            field_radio=Data.RadioChoices.OPTION_1,
            field_boolean_checkbox=True,
            field_select_dropdown=Data.SelectChoices.OPTION_2,
            field_password="test_field_password",
            field_password_confirm="test_field_password_confirm",
            field_number=10,
            field_select_checkbox=Data.SelectCheckboxChoices.OPTION_3,
        )
        self.empty_data = DataFactory(
            field_text_1="",
            field_text_2="",
            field_email="",
            field_radio="",
            field_select_dropdown="",
            field_password="",
            field_password_confirm="",
        )

    def test_save(self):
        with self.subTest("Full_data"):
            self.assertIsInstance(self.full_data, Data)
            self.assertEqual(self.full_data.field_text_1, "test_field_text_1")
            self.assertEqual(self.full_data.field_text_2, "test_field_text_2")
            self.assertEqual(self.full_data.field_email, "test@field_email.test")
            self.assertEqual(self.full_data.field_radio, "OP1")
            self.assertTrue(self.full_data.field_boolean_checkbox)
            self.assertEqual(self.full_data.field_select_dropdown, "OP2")
            self.assertEqual(self.full_data.field_password, "test_field_password")
            self.assertEqual(
                self.full_data.field_password_confirm, "test_field_password_confirm"
            )
            self.assertEqual(self.full_data.field_number, 10)
            self.assertEqual(self.full_data.field_select_checkbox, "OP3")

        with self.subTest("Empty_data"):
            self.assertIsInstance(self.empty_data, Data)
            self.assertEqual(self.empty_data.field_text_1, "")
            self.assertEqual(self.empty_data.field_text_2, "")
            self.assertEqual(self.empty_data.field_email, "")
            self.assertEqual(self.empty_data.field_radio, "")
            self.assertFalse(self.empty_data.field_boolean_checkbox)
            self.assertEqual(self.empty_data.field_select_dropdown, "")
            self.assertEqual(self.empty_data.field_password, "")
            self.assertEqual(self.empty_data.field_password_confirm, "")
            self.assertIsNone(self.empty_data.field_number)
            self.assertEqual(self.empty_data.field_select_checkbox, "OP1")

    def test_choices(self):
        with self.subTest("Radio Choices"):
            self.assertEqual(Data.RadioChoices.OPTION_1, "OP1")
            self.assertEqual(Data.RadioChoices.OPTION_2, "OP2")
            self.assertEqual(Data.RadioChoices.OPTION_3, "OP3")

        with self.subTest("Select Choices"):
            self.assertEqual(Data.SelectChoices.OPTION_1, "OP1")
            self.assertEqual(Data.SelectChoices.OPTION_2, "OP2")
            self.assertEqual(Data.SelectChoices.OPTION_3, "OP3")

        with self.subTest("Select Checkbox Choices"):
            self.assertEqual(Data.SelectCheckboxChoices.OPTION_1, "OP1")
            self.assertEqual(Data.SelectCheckboxChoices.OPTION_2, "OP2")
            self.assertEqual(Data.SelectCheckboxChoices.OPTION_3, "OP3")

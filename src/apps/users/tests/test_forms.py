from django.test import TestCase

from apps.users.forms import (
    AuthenticationForm,
    EmailVerificationCodeForm,
    PasswordResetForm,
    ProfileDetailsForm,
    UserChangeForm,
    UserSignUpForm,
)
from apps.users.models import User


class AuthenticationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test_name",
            surnames="test_surnames",
            email="test@test.com",
            password="test_password",
        )
        self.form = AuthenticationForm(
            data={
                "email": self.user.email,
                "password": self.user.password,
                "remember_me": False,
            }
        )

    def test_form(self):
        self.assertFalse(self.form.is_valid())
        self.assertEqual(
            self.form.data,
            {
                "email": self.user.email,
                "password": self.user.password,
                "remember_me": False,
            },
        )


class UserChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test_name",
            surnames="test_surnames",
            email="test@test.com",
            password="test_password",
        )
        self.form = UserChangeForm(
            data={
                "new_password": "new password",
            }
        )
        self.old_user_password = self.user.password
        self.user.set_password(self.form.data["new_password"])

    def test_form(self):
        self.assertEqual(self.form.data, {"new_password": "new password"})
        self.assertNotEqual(
            self.old_user_password,
            self.user.password,
        )


class UserSignUpFormTest(TestCase):
    def test_form(self):
        self.form = UserSignUpForm(
            data={
                "name": "test_name",
                "surnames": "test_surnames",
                "password1": "password1",
                "password2": "password2",
                "email": "test@test.com",
                "accept_conditions": True,
            }
        )
        self.assertEqual(
            self.form.data,
            {
                "name": "test_name",
                "surnames": "test_surnames",
                "password1": "password1",
                "password2": "password2",
                "email": "test@test.com",
                "accept_conditions": True,
            },
        )


class ProfileDetailsFormTest(TestCase):
    def test_form(self):
        self.form = ProfileDetailsForm(
            data={
                "name": "test_name",
                "surnames": "test_surnames",
                "email": "test@test.com",
            }
        )
        self.assertTrue(self.form.is_valid)
        self.assertEqual(
            self.form.data,
            {
                "name": "test_name",
                "surnames": "test_surnames",
                "email": "test@test.com",
            },
        )


class PasswordResetFormTest(TestCase):
    def test_form(self):
        self.form = PasswordResetForm(
            data={
                "email": "test@test.com",
            }
        )
        self.assertTrue(self.form.is_valid())
        self.assertEqual(
            self.form.data,
            {
                "email": "test@test.com",
            },
        )


class EmailVerificationCodeFormTest(TestCase):
    def test_form(self):
        self.form = EmailVerificationCodeForm(
            data={
                "email_verification_code": "1234",
            }
        )
        self.assertTrue(self.form.is_valid())
        self.assertEqual(
            self.form.data,
            {
                "email_verification_code": "1234",
            },
        )

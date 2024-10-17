from django.test import TestCase

from apps.users.models import User
from apps.users.utils import email_verification_code_regeneration


class UtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test_name",
            surnames="test_surnames",
            email="test@test.com",
            password="test_password",
            email_verification_code="1234",
        )

    def test_email_verification_code_regeneration(self):
        """
        Test generates a new email verification code randomly for the user
        and stores it in the database.
        """

        self.assertEqual(self.user.email_verification_code, "1234")
        new_code = email_verification_code_regeneration(self.user)
        self.assertEqual(self.user.email_verification_code, new_code)
        self.assertEqual(len(self.user.email_verification_code), 4)

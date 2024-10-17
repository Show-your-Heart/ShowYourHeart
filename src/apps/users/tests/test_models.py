from django.test import TestCase

from apps.users.models import User


class UserManagerTestCase(TestCase):
    def test_create_user(self):
        """
        Test creates and saves a User with the given email, password
        and extra fields.
        """
        with self.subTest("User creation successfully"):
            self.user = User.objects.create_user(
                name="test_name",
                surnames="test_surnames",
                email="test@test.com",
                password="test_password",
            )
            self.assertEqual(self.user.name, "test_name")
            self.assertEqual(self.user.surnames, "test_surnames")
            self.assertEqual(self.user.email, "test@test.com")
            self.assertEqual(self.user.email_verification_code, "0000")
            self.assertEqual(self.user.email_verified, False)
            self.assertEqual(self.user.is_active, True)
            self.assertEqual(self.user.is_staff, False)
            self.assertTrue(self.user.check_password("test_password"))

        with self.subTest("User creation failed"):
            with self.assertRaises(ValueError) as error:
                self.user = User.objects.create_user(
                    name="test_name",
                    surnames="test_surnames",
                    email=None,
                    password="test_password",
                )
            self.assertEqual(str(error.exception), "Users must have an email address")

    def test_create_superuser(self):
        """
        Test creates and saves a superuser with the given email, password
        and extra fields.
        """
        with self.subTest("Superuser creation successfully"):
            self.superuser = User.objects.create_superuser(
                name="test_name",
                surnames="test_surnames",
                email="test@test.com",
                password="test_password",
                is_staff=True,
                is_superuser=True,
            )
            self.assertTrue(self.superuser.is_staff)
            self.assertTrue(self.superuser.is_superuser)

        with self.subTest("Superuser creation failed"):
            with self.assertRaises(ValueError) as error:
                self.superuser = User.objects.create_superuser(
                    name="test_name",
                    surnames="test_surnames",
                    email="test@test.com",
                    password=None,
                    is_staff=True,
                    is_superuser=True,
                )
            self.assertEqual(str(error.exception), "Superusers must have a password")

    def test_full_name(self):
        """
        Tests the full_name property.
        """
        self.user = User.objects.create_user(
            name="test_name",
            surnames="test_surnames",
            email="test@test.com",
            password="test_password",
        )
        self.assertEqual(self.user.full_name, "test_name test_surnames")

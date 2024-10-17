from django.test import Client, TestCase

from apps.users.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            name="test_name",
            surnames="test_surnames",
            email="test@test.com",
        )
        self.user.set_password("password")
        self.user.save()

    def test_login(self):
        self.client.login(username=self.user.email, password="password")
        self.assertTrue(self.user.is_authenticated)
        self.assertFalse(self.user.is_anonymous)

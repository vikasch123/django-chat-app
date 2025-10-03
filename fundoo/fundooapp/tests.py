from django.test import TestCase
from django.contrib.auth.models import User

class FundooAppTests(TestCase):
    def test_dummy(self):
        self.assertTrue(True)

    def test_user_creation(self):
        user = User.objects.create_user(username="testuser", password="password123")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, "testuser")


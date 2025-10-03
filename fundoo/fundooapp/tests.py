from django.test import TestCase
from django.contrib.auth.models import User

class SimpleTests(TestCase):
    def test_homepage_loads(self):
        response = self.client.get('/')  # Homepage
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get('/login/')  # Login page
        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        response = self.client.get('/signup/')  # Signup page
        self.assertEqual(response.status_code, 200)

    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, 'testuser')

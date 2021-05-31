from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.user = User.objects.create(username='testuser', password='example')
        pass

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
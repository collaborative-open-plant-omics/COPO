# Created by AProvidence 20052022
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase  # Client
from htmlvalidator.client import ValidatingClient
from django.urls import reverse


class TestLoggedUser(TestCase):
    "HTML validator is integrated "

    @classmethod
    def setUpClass(cls):
        super(TestLoggedUser, cls).setUpClass()
        settings.UNIT_TESTING = True
        cls.client = ValidatingClient()
        cls.user = User.objects.create_user(settings.TEST_USER_NAME, 'user@test.net', 'secret')
        cls.user.save()
        cls.client.login(username='test_user', password='secret')

    @classmethod
    def tearDown(cls):
        u = User.objects.get(username=settings.TEST_USER_NAME)
        # u.delete()

    def test_logged_user_get_homepage(self):
        response = self.client.get(reverse('web_copo:index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_get_user_details_page(self):
        response = self.client.get(reverse('web_copo:view_user_info'), follow=True)
        self.assertEqual(response.status_code, 200)

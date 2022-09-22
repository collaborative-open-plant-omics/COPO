# Created by AProvidence 20-05-2022
from django.urls import reverse
from tests.test_base import BaseTest
from web.apps.web_copo.utils.group_functions import get_group_membership_asString

class TestLAuthentication(BaseTest):
    """ HTML validator is integrated """

    def test_logged_user_can_access_homepage(self):
        response = self.loggedin_client.get(reverse('web_copo:index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_get_user_details_page(self):
        response = self.loggedin_client.get(reverse('web_copo:view_user_info'), follow=True)
        self.assertEqual(response.status_code, 200)

# class RegistrationTest(BaseTest):
    def test_user_cannot_register_with_invalid_email(self):
        # response = self.client.post(self.register_url, self.user_invalid_email, format='text/html')
        # self.assertEqual(response.status_code, 400)
        pass

    def test_user_cannot_register_with_existing_email(self):
        # response = self.client.post(self.register_url, self.user, format='text/html')
        # self.assertEqual(response.status_code, 400)
        pass
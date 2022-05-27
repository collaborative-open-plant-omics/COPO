# Created by AProvidence 20-05-2022
from django.urls import reverse
from tests.test_base import BaseTest

""" 
(venv) $ coverage run manage.py test -v 2
(venv) $ coverage report --omit="/usr/users/EI_ga012/providen/Documents/EI/Projects/COPO/venv/*"
(venv) $ coverage html
"""


class TestLAuthentication(BaseTest):
    """ HTML validator is integrated """

    def test_logged_user_can_access_homepage(self):
        response = self.loggedin_client.get(reverse('web_copo:index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_get_user_details_page(self):
        response = self.loggedin_client.get(reverse('web_copo:view_user_info'), follow=True)
        self.assertEqual(response.status_code, 200)

# class RegistrationTest(BaseTest):

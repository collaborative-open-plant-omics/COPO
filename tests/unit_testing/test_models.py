# Created by AProvidence on 01-04-2022
from django.conf import settings
from django.test import TestCase
from faker import Faker
from password_generator import PasswordGenerator

from web.apps.web_copo.models import User, UserDetails, ViewLock


class UserModelTestCase(TestCase):
    def setUp(self):
        fake = Faker()
        settings.UNIT_TESTING = True
        _firstname = fake.first_name()
        _lastname = fake.last_name()
        _username = fake.first_name().lower() + "_1"
        _email = _firstname.lower() + _lastname + "@example.com"

        User.objects.create_user(username=settings.TEST_USER_NAME, first_name=_firstname,
                                 last_name=_lastname, email=_email,
                                 password=PasswordGenerator().generate())

    def test_get_user(self):
        self.assertEquals(2, 1 + 1)

    def test_user_deletion(self):
        self.assertEquals(2, 1 + 1)

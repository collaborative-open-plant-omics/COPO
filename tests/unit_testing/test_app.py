# Created by AProvidence on 17-03-2022
from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from faker import Faker
from password_generator import PasswordGenerator


class AppTest(TestCase):
    """Simple tests"""

    @classmethod
    def setUpClass(cls):
        settings.UNIT_TESTING = True
        fake = Faker()
        _firstname = fake.first_name()
        _lastname = fake.last_name()
        _username = fake.first_name().lower() + "_1"
        _email = _firstname.lower() + _lastname + "@example.com"

        settings.TEST_USER_NAME= _username

        # Create a user
        cls.user = User.objects.create_user(username=settings.TEST_USER_NAME, first_name=_firstname,
                                            last_name=_lastname, email=_email,
                                            password=PasswordGenerator().generate())
        cls.user.save()

        # Create a profile
        p_dict = {"copo_id": "000000000", "description": "Test Description", "user_id": cls.user.id,
                  "title": "Test Title"}
        cls.pid = Profile().save_record(dict(), **p_dict)

    def test_user_creation(self):
        self.assertIsInstance(self.user, User)

    def test_user_name(self):
        user1 = authenticate(username=self.user.username, password=self.user.password)
        print(user1)

    # self.assertIsInstance(u1, User, "error authenticating user")

    def test_get_profile(self):
        profile = Profile().get_record(self.pid["_id"])
        self.assertEquals(profile["description"], "Test Description", "EError creating profile")

    @classmethod
    def tearDownClass(cls):
        user = User.objects.get(username=settings.TEST_USER_NAME)
        user.delete()
        Profile().get_collection_handle().remove({"copo_id": "000000000"})

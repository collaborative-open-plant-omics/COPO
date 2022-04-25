# Created by AProvidence on 01-04-2022
from django.conf import settings
from django.test import TestCase
# from django.urls import reverse
from faker import Faker
from password_generator import PasswordGenerator
from web.apps.web_copo.models import User, UserDetails  # ViewLock, test_model, banner_view

""" setUp() is called before each test is run. It prepares test dataset for each test run"""

""" setUpTestData() creates initial test data per TestCase. It is called once for TestCase """

""" setUpClass() creates database connections, sessions and loading webdrivers etc.
    It is called once for the TestCase before running any of the tests """


class ModelsTest(TestCase):
    superuser = None  # admin user
    user = None

    """ Set up fake/mock data for the TestCase in the tests database"""
    @classmethod
    def setUpTestData(cls):
        settings.UNIT_TESTING = True
        settings.TEST_USER_NAME = "tester101"
        fake = Faker()

        # Create a user model object and save it in the temporary database
        cls.user = User.objects.create_user(username=settings.TEST_USER_NAME, first_name=fake.first_name(),
                                            last_name=fake.last_name(), email=fake.email(),
                                            password=PasswordGenerator().generate())
        # Create a admin user model object
        cls.superuser = User.objects.create_superuser(username=settings.TEST_USER_NAME.join('2'),
                                                      first_name=fake.first_name(),
                                                      last_name=fake.last_name(), email=fake.email(),
                                                      password=PasswordGenerator().generate())

        # banner_view = banner_view(header_txt='', body_txt='', active=False)
        # view_lock = ViewLock(url='', user='', timeLocked='', timeout='')
        # test_model = test_model(url='', c='')

        cls.user.save()
        cls.superuser.save()

    def test_user_creation(self):
        """ Test the creation of a new user """
        print("Test user creation")
        self.assertTrue(isinstance(self.user, User))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff, self.user.is_superuser)
        self.assertEqual(self.user.get_user_permissions(), set(), "No permissions have been set")
        self.assertEqual(self.user.get_group_permissions(), set(), "No permissions have been set")
        self.assertEqual(self.user.get_username(), settings.TEST_USER_NAME)
        self.assertTrue(self.user.is_authenticated)
        self.assertFalse(self.user.is_anonymous)

    def test_superuser_creation(self):
        """ Test the creation of an admin user """
        print('Test admin creation')
        self.assertTrue(isinstance(self.superuser, User))
        self.assertTrue(self.superuser.is_active, self.superuser.is_superuser)
        self.assertIn('admin.view_logentry', self.superuser.get_user_permissions(),
                      "Admin has permission to view log entry")
        self.assertIn('auth.add_permission', self.superuser.get_user_permissions(),
                      "Admin has permission to view log entry")
        self.assertIn('chunked_upload.add_chunkedupload', self.superuser.get_group_permissions(),
                      "Admin has group permission to add chunked upload")
        self.assertIn('auth.add_group', self.superuser.get_group_permissions(),
                      "Admin has group permission to a group")

        self.assertEqual(self.superuser.get_username(), settings.TEST_USER_NAME.join('2'))
        self.assertTrue(self.superuser.is_authenticated)
        self.assertFalse(self.user.is_anonymous)

    def test_user_details_model(self):
        """ Test the creation of an admin user """
        print('Test user details model')
        user_details = UserDetails(user=self.user, orcid_id='000000000')
        # concatenate strings using f'strings
        firstname, lastname = self.user.first_name, self.user.last_name
        self.assertTrue(isinstance(user_details, UserDetails))
        self.assertEqual(user_details.orcid_id, '000000000')
        self.assertEqual(user_details.repo_manager, user_details.repo_submitter)
        self.assertEqual(settings.TEST_USER_NAME, user_details.user.username)
        self.assertEqual('{} {}'.format(firstname, lastname), user_details.user.get_full_name())
        self.assertEqual(self.user.first_name, user_details.user.get_short_name())

    # def test_view_lock_model(self):
    #     """ Test the creation of an admin user """
    #     print('Test view lock model')
    #     login_url = reverse('web_copo:auth')
    #     view_lock = ViewLock(url=login_url, user=self.user)
    #     print(view_lock.isViewLockedCreate(url=login_url))
        # self.assertEqual(view_lock.lockView(login_url))
        # self.assertEqual()

    @classmethod
    def tearDownClass(cls):
        # Clean up after each test
        user = User.objects.get(username=settings.TEST_USER_NAME)
        superuser = User.objects.get(username=settings.TEST_USER_NAME.join('2'))
        user.delete()
        superuser.delete()

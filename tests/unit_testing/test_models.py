# Created by AProvidence on 01-04-2022
from dal.copo_da import Profile
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from faker import Faker
from password_generator import PasswordGenerator
from web.apps.web_copo.models import User, UserDetails  # ViewLock, test_model, banner_view

# To execute the Django’s test suite: $ python manage.py test


class ModelsTest(TestCase):
    """ Simple tests """
    @classmethod
    def setUpTestData(cls):
        """ Set up fake/mock data for the TestCase in the "test_copo" database"""
        super().setUpTestData()
        settings.UNIT_TESTING = True
        fake = Faker()

        cls.current_month = datetime.now().month
        cls.username = fake.first_name().lower() + "_1"
        cls.admin_username = fake.first_name().lower() + "_admin"

        user_firstname = fake.first_name()
        user_lastname = fake.last_name()
        user_email = user_firstname.lower() + user_lastname.lower() + "@example.com"

        admin_firstname = fake.first_name()
        admin_lastname = fake.last_name()
        admin_email = admin_firstname.lower() + admin_lastname.lower() + "@admin.com"

        # Create a user model object and save it in the temporary database
        cls.user = User.objects.create_user(username=cls.username, first_name=fake.first_name(),
                                            last_name=fake.last_name(), email=user_email,
                                            password=PasswordGenerator().generate())

        # Create a admin user model object
        cls.superuser = User.objects.create_superuser(username=cls.admin_username,
                                                      first_name=admin_firstname,
                                                      last_name=admin_lastname, email=admin_email,
                                                      password=PasswordGenerator().generate())

        # Create an ERGA profile on the COPO website
        erga_profile_dict = {"copo_id": "000000001", "description": "ERGA Test Description", "user_id": cls.user.id,
                             "type": "European Reference Genome Atlas (ERGA)", "title": "ERGA Test Title"}

        # banner_view = banner_view(header_txt='', body_txt='', active=False)
        # view_lock = ViewLock(url='', user='', timeLocked='', timeout='')
        # test_model = test_model(url='', c='')

        cls.user.save()
        cls.superuser.save()
        cls.profile_ID = Profile().get_collection_handle().insert(erga_profile_dict)

    def test_user_creation(self):
        """ Test the creation of a new user """
        print("Test user creation")
        self.assertTrue(isinstance(self.user, User))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff, self.user.is_superuser)
        self.assertEqual(self.user.get_user_permissions(), set(), "No permissions have been set")
        self.assertEqual(self.user.get_group_permissions(), set(), "No permissions have been set")
        self.assertEqual(self.user.get_username(), self.username)
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

        self.assertEqual(self.superuser.get_username(), self.admin_username)
        self.assertTrue(self.superuser.is_authenticated)
        self.assertFalse(self.user.is_anonymous)

    def test_user_details_model(self):
        """ Test the creation of an admin user """
        print('Test user details model')
        user_details = UserDetails(user=self.user, orcid_id='000000001')
        # concatenate strings using f'strings
        firstname, lastname = self.user.first_name, self.user.last_name
        self.assertTrue(isinstance(user_details, UserDetails))
        self.assertEqual(user_details.orcid_id, '000000001')
        self.assertEqual(user_details.repo_manager, user_details.repo_submitter)
        self.assertEqual(self.username, user_details.user.username)
        self.assertEqual('{} {}'.format(firstname, lastname), user_details.user.get_full_name())
        self.assertEqual(self.user.first_name, user_details.user.get_short_name())

    def test_user_model(self):
        """"Test the objects created in the User model and stored in the "copo" PostgreSQL database"""
        print("Test user model")
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username=self.superuser).date_joined.month,
                         User.objects.get(username=self.user).date_joined.month)
        self.assertEqual(User.objects.get(username=self.superuser).date_joined.year,
                         User.objects.get(username=self.user).date_joined.year)

    def test_user_object_attributes_are_correct(self):
        """ Test that the user object attributes have been assigned correctly """
        print("Test user object attributes")
        self.assertEqual(self.user.username, User.objects.get(username=self.user).username)
        self.assertEqual(self.user.first_name, User.objects.get(username=self.user).first_name)
        self.assertEqual(self.user.last_name, User.objects.get(username=self.user).last_name)
        self.assertEqual(self.user.email, User.objects.get(username=self.user).email)
        self.assertEqual(self.current_month, User.objects.get(username=self.user).date_joined.month)

        """ Test that the admin user object attributes have been assigned correctly """
        print("Test admin user object attributes")
        User.objects.get(username=self.user).set_password('newadminpw')  # Changes admin user password
        self.assertEqual(self.superuser.username, User.objects.get(username=self.superuser).username)
        self.assertEqual(self.superuser.first_name, User.objects.get(username=self.superuser).first_name)
        self.assertEqual(self.superuser.last_name, User.objects.get(username=self.superuser).last_name)
        self.assertEqual(self.superuser.email, User.objects.get(username=self.superuser).email)
        self.assertEqual(self.current_month, User.objects.get(username=self.superuser).date_joined.month)

    def test_get_profile(self):
        profile = Profile().get_record(str(self.profile_ID))
        self.assertEqual(6, len(profile))
        self.assertTrue(profile["description"], "ERGA Test Description")
        self.assertTrue(type(profile) is dict)

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
        # Clean up after each test by removing the objects stored in the "test_copo" database
        User.objects.get(username=cls.user).delete()
        User.objects.get(username=cls.superuser).delete()
        Profile().get_collection_handle().remove({"copo_id": "000000001"})

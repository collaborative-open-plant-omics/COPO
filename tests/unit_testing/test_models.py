# Created by AProvidence on 01-04-2022
from dal.copo_da import Profile
from datetime import datetime
from tests.test_base import BaseTest
from web.apps.web_copo.models import User, UserDetails  # ViewLock, test_model, banner_view
from web.apps.web_copo.utils.group_functions import get_group_membership_asString


class ModelsTest(BaseTest):
    """ Simple tests """
    # banner_view = banner_view(header_txt='', body_txt='', active=False)
    # view_lock = ViewLock(url='', user='', timeLocked='', timeout='')
    # test_model = test_model(url='', c='')

    def test_user_creation(self):
        """ Test the creation of a new user """
        print("Test user creation")
        self.assertTrue(isinstance(self.user, User))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff, self.user.is_superuser)
        self.assertEqual(self.user.get_user_permissions(), set(), "No permissions have been set")
        self.assertEqual(self.user.get_group_permissions(), set(), "No permissions have been set")
        self.assertEqual(self.user.get_username(), self.user.username)
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

        self.assertEqual(self.superuser.get_username(), self.superuser.username)
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
        self.assertEqual(self.user.username, user_details.user.username)
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
        self.assertEqual(datetime.now().month, User.objects.get(username=self.user).date_joined.month)

        """ Test that the admin user object attributes have been assigned correctly """
        print("Test admin user object attributes")
        User.objects.get(username=self.user).set_password('newadminpw')  # Changes admin user password
        self.assertEqual(self.superuser.username, User.objects.get(username=self.superuser).username)
        self.assertEqual(self.superuser.first_name, User.objects.get(username=self.superuser).first_name)
        self.assertEqual(self.superuser.last_name, User.objects.get(username=self.superuser).last_name)
        self.assertEqual(self.superuser.email, User.objects.get(username=self.superuser).email)
        self.assertEqual(datetime.now().month, User.objects.get(username=self.superuser).date_joined.month)

    def test_get_profile(self):
        profile = Profile().get_record(str(self.erga_pid))
        self.assertEqual(6, len(profile))
        self.assertTrue(profile["description"], "ERGA Test Description")
        self.assertTrue(type(profile) is dict)

    groups = get_group_membership_asString()
    self.assertTrue(groups, "dtol_sample_managers")

    # def test_view_lock_model(self):
    #     """ Test the creation of an admin user """
    #     print('Test view lock model')
    #     login_url = reverse('web_copo:auth')
    #     view_lock = ViewLock(url=login_url, user=self.user)
    #     print(view_lock.isViewLockedCreate(url=login_url))
    # self.assertEqual(view_lock.lockView(login_url))
    # self.assertEqual()


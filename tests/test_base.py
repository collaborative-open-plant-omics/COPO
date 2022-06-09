# Created by AProvidence on 27-05-2022

from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from htmlvalidator.client import ValidatingClient
from faker import Faker
from password_generator import PasswordGenerator
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Ensure that the “copodev” django server is running before running selenium tests
# Run this command before running the selenium tests:
# $ supervisord -c celery.conf && supervisorctl -c celery.conf start all
# To execute the Django’s test suite: $ python manage.py test

""" 
(venv) $ coverage run manage.py test -v 2
(venv) $ coverage report -m --omit="/usr/users/EI_ga012/providen/Documents/EI/Projects/COPO/venv/*"
(venv) $ coverage html
"""


class BaseTest(TestCase):
    # setUp method and tearDown method are ran before and after each testcase respectively
    """ Set up fake/mock data for the TestCase in the "test_copo" database"""
    def setUp(self):
        super().setUp()
        settings.UNIT_TESTING = True
        fake = Faker()

        """ User and Profile """

        self.loggedin_client = ValidatingClient()
        self.not_loggedin_client = ValidatingClient()

        # Create an user model object and save it in the "test_copo" temporary PostgreSQL database
        self.user = User.objects.create_user(username=fake.first_name().lower(),
                                             first_name=fake.first_name(),
                                             last_name=fake.last_name(), email=fake.free_email(),
                                             password=PasswordGenerator().generate())
        # Create an admin user model object
        self.superuser = User.objects.create_superuser(username=fake.first_name().lower(),
                                                       first_name=fake.first_name(),
                                                       last_name=fake.last_name(), email=fake.company_email(),
                                                       password=PasswordGenerator().generate())

        # Create an ASG profile on the COPO website
        asg_profile = {"copo_id": "000000002", "description": "ASG Test Description", "user_id": self.user.id,
                       "type": "Aquatic Symbiosis Genomics (ASG)", "title": "ASG Test Title"}

        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": self.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}

        # Create a ERGA profile on the COPO website
        erga_profile = {"copo_id": "000000001", "description": "ERGA Test Description", "user_id": self.user.id,
                        "type": "European Reference Genome Atlas (ERGA)", "title": "ERGA Test Title"}

        self.user.save()
        self.superuser.save()
        self.asg_pid = Profile().get_collection_handle().insert(asg_profile)
        self.dtol_pid = Profile().get_collection_handle().insert(dtol_profile)
        self.erga_pid = Profile().get_collection_handle().insert(erga_profile)

        self.loggedin_client.login(username=self.user.username, password=PasswordGenerator().generate())



        """" Rest URLs declaration"""
        self._define_rest_urls()

        self._define_user_authentication()

    def tearDown(self):
        # Clean up after each test by removing the objects stored in the "test_copo" database
        User.objects.get(username=self.user.username).delete()
        User.objects.get(username=self.superuser.username).delete()
        Profile().get_collection_handle().remove({"copo_id": "000000000"})
        Profile().get_collection_handle().remove({"copo_id": "000000001"})
        Profile().get_collection_handle().remove({"copo_id": "000000002"})

        super().tearDown()

    def _define_rest_urls(self):
        # app name: rest
        # pattern name: data_wiz
        # reverse('rest:data_wiz')
        self.data_wiz_url = reverse('rest:data_wiz')
        self.sample_wiz_url = reverse('rest:sample_wiz')
        self.receive_data_file_url = reverse('rest:receive_data_file')
        self.receive_data_file_chunked_url = reverse('rest:receive_data_file')
        self.complete_upload_url = reverse('rest:complete_data_file')
        self.hash_upload_url = reverse('rest:hash_upload')
        self.inspect_file_url = reverse('rest:inspect_file')
        self.zip_file_url = reverse('rest:zip_file')
        self.check_figshare_credentials_url = reverse('rest:check_figshare_credentials')
        self.set_figshare_credentials_url = reverse('rest:set_figshare_credentials')
        self.small_file_upload_url = reverse('rest:receive_data_file')
        self.forward_to_figshare_url = reverse('rest:forward_to_figshare')
        self.get_upload_information_url = reverse('rest:get_upload_information')
        self.get_submission_status_url = reverse('rest:get_submission_status')
        self.release_ena_study_url = reverse('rest:release_ena_study')
        self.resume_chunked_url = reverse('rest:resume_chunked')
        self.get_partial_uploads_url = reverse('rest:get_partial_uploads')
        self.save_ss_annotation_url = reverse('rest:save_ss_annotation')
        self.delete_ss_annotation_url = reverse('rest:delete_ss_annotation')
        self.copo_get_submission_table_data_url = reverse('rest:get_submissions')
        self.get_accession_data_url = reverse('rest:get_accession_data')
        self.set_session_variable_url = reverse('rest:set_session_variable')
        self.test_sword_url = reverse('rest:test_module')
        self.call_get_dataset_details_url = reverse('rest:call_get_dataset_details')
        self.samples_from_study_url = reverse('rest:get_samples_for_study')
        self.get_users_url = reverse('rest:get_users')
        self.get_ontologies_url = reverse('rest:get_ontologies')
        self.export_generic_annotation_url = reverse('rest:export_generic_annotation')

    def _define_user_authentication(self):
        fake = Faker()
        username = 'username'
        firstname = 'first_name'
        lastname = 'last_name'
        email = 'email'
        password = 'password'

        self.user_mismatched_password = {
            username: fake.first_name().lower(),
            firstname: fake.first_name(),
            lastname: fake.last_name(),
            email: fake.email(),
            password: PasswordGenerator().generate(),


        }


class SeleniumBaseTest(LiveServerTestCase):
    """ Selenium test setup"""

    @classmethod
    def setUpClass(cls):
        super(SeleniumBaseTest, cls).setUpClass()
        options = Options()
        options.headless = False
        cls.webdriver = webdriver.Firefox(options=options)
        cls.host = "http://127.0.0.1:8000"

        """ URL declaration"""
        cls.index_url = reverse('web_copo:index')
        cls.login_url = reverse('web_copo:auth')
        cls.logout_url = reverse('web_copo:logout')

    @classmethod
    def tearDownClass(cls):
        cls.webdriver.close()
        super().tearDownClass()

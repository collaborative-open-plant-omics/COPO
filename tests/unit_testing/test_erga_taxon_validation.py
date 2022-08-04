# Created by AProvidence on 23-05-2022

from dal.copo_da import Profile, Sample
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from faker import Faker
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tests.utilities.helpers import one_of_these_elements_is_visible
from tools import resolve_env
from web.apps.web_copo.utils.dtol.tol_validators.validation_messages import MESSAGES as validation_messages

import os
import tools.resolve_env as env


# Ensure that the "copodev" django server is running before running this test
# Run this command before running the tests: $ supervisord -c celery.conf && supervisorctl -c celery.conf start all


class ERGATaxonValidationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True
        fake = Faker()
        options = Options()
        options.headless = False
        erga_manifests_filename = "ERGA_SAMPLE_MANIFESTS.xlsx"
        erga_sample1_sheetname = 'ERGA_SM1'
        cls.cwd = os.getcwd()  # Get current working directory path
        cls.webdriver = webdriver.Firefox(options=options)
        cls.erga_manifest = dict()
        cls.manifests_dir_path = os.path.join(cls.cwd, "tests", "manifests")
        # DtolSpreadsheet(file="tests/manifests/ERGA_SAMPLE_MANIFESTS.xlsx")

        firstname = fake.first_name()
        lastname = fake.last_name()
        username = firstname.lower() + "_1"
        email = firstname.lower() + lastname.lower() + "@example.com"

        # settings.TEST_USER_NAME = username

        # Create a user model object and save it in the test_copo temporary database
        cls.user = User.objects.create_user(username=username, first_name=firstname,
                                            last_name=lastname, email=email,
                                            password=User.objects.make_random_password())
        cls.user.save()

        # Create a ERGA profile on the COPO website
        p_dict = {"copo_id": "000000001", "description": "ERGA Test Description", "user_id": cls.user.id,
                  "type": "European Reference Genome Atlas (ERGA)", "title": "ERGA Test Title"}
        cls.pid = Profile().get_collection_handle().insert(p_dict)

    def test_working_erga_manifest_validation_and_submission(self):
        self.webdriver.get("http://127.0.0.1:8000/copo/")
        if "login" in self.webdriver.current_url:
            self._login()
        element = self._get_to_manifest_upload_point()
        erga_sample2_file = os.path.join(self.manifests_dir_path, "ERGA_SAMPLE_MANIFEST_2.xlsx")
        element.send_keys(erga_sample2_file)
        # Launch the "Upload Spreadsheet" dialog
        element = WebDriverWait(self.webdriver, 20).until(
            one_of_these_elements_is_visible("finish_button", "export_errors_button"))

        try:
            self.assertIn("finish_button", element.get_attribute('id').split())
            element.click()
            # Launch the Submission manifest dialog
            # Find the "Confirm" button in the pop-up dialog. A CSS class was added
            # for tag purposes in the copo_sample_parse_spreadsheet.js file
            confirm_dialog_button = WebDriverWait(self.webdriver, 20).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".dialog_confirm"))
            )
            confirm_dialog_button.click()
            samples = Sample().get_collection_handle().find({"profile_id": str(self.pid), "tol_project": "ERGA"})
            self.assertEqual(len(list(samples)), 39)
        except AssertionError:
            """ Manifest submission is rejected because the samples to be submitted are duplicates.
             They already exist in the SampleCollection in the database"""
            print("Errors are found")
            self.assertIn("export_errors_button", element.get_attribute('id').split())
            self.assertRaisesMessage(AssertionError,
                                     validation_messages["validation_msg_duplicate_tube_or_well_id_in_copo"])
            Sample().get_collection_handle().remove({"profile_id": str(self.pid)})

    # check database to see if samples are already in it, drop it then, upload the spreadsheet with the same samples

    def test_blank_manifest(self):
        """ If manifest is blank, an appropriate message is displayed"""
        # element = self._get_to_manifest_upload_point()
        # self.erga_manifest.values()
        # print(len(self.erga_manifest))

        pass

    # Query API and check for the correct number of results

    def test_erga_manifest_samples_submitted_to_ena(self):
        pass

    def test_erga_manifest_samples_submitted_to_ena(self):
        pass

    def test_working_erga_manifest(self):
        pass

    def test_wrong_taxonnomy(self):
        pass

    def test_taxonID_association_to_several_specimenIDs(self):
        pass

    def test_taxonID_map_to_correct_species_name(self):
        pass

    def test_taxonID(self):
        pass

    def test_date_in_correct_format(self):
        pass

    def test_occurrences_of_whole_organism(self):
        pass

    def test_alphanumeric_characters_used(self):
        #  Special characters and pipe (|) should not be used
        pass

    def test_connection_to_test_mongodb(self):
        """" Verifies that the current database being used is the "test_copo_mongo" database
        and not the production database """
        # db.currentOp(true).inprog

        client = MongoClient(resolve_env.get_env("MONGO_HOST"), int(resolve_env.get_env("MONGO_PORT")))
        db = client.database_name
        # collection = db.collection_name
        # print(db.currentOp(True).inprog)
        print(db)
        self.assertEqual(db, "test_copo_mongo")

    def _login(self):
        self.webdriver.get("http://127.0.0.1:8000/copo")
        element = WebDriverWait(self.webdriver, 5).until(
            ec.presence_of_element_located((By.LINK_TEXT, "Sign in with Orcid.org"))
        )
        element.click()
        element = WebDriverWait(self.webdriver, 5).until(
            ec.presence_of_element_located((By.ID, "username"))
        )
        assert "orcid" in self.webdriver.current_url
        username = env.get_env("SELENIUM_TEST_USERNAME")
        password = env.get_env("SELENIUM_TEST_PASSWORD")
        element.send_keys(username)
        element = self.webdriver.find_element(By.ID, "password")
        element.send_keys(password)
        element.send_keys(Keys.ENTER)
        WebDriverWait(self.webdriver, 10).until(
            ec.presence_of_element_located((By.ID, "copo-global-nav"))
        )

        assert "COPO" in self.webdriver.title
        try:
            element = self.webdriver.find_element(By.ID, "profile_table_div")

        except NoSuchElementException:
            assert False
        assert True

    def _get_to_manifest_upload_point(self):
        self.webdriver.get("http://127.0.0.1:8000/copo/copo_samples/" + str(self.pid) + "/view")
        assert "/copo/copo_samples/" in self.webdriver.current_url
        element = WebDriverWait(self.webdriver, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, ".new-samples-spreadsheet-template"))
        )
        element.click()
        return self.webdriver.find_element(By.ID, "file")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.webdriver.close()
        """ Clear objects stored in the test database """
        # Removes user from "web_copo_userdetails" table  and "auth_user" table in "copo" PostgreSQL database
        # User.objects.get(username=cls.user.username).delete()
        print(Sample().get_collection_handle().find({"profile_id": str(cls.pid)}))
        Sample().get_collection_handle().remove({"profile_id": str(cls.pid)})
        Profile().get_collection_handle().remove({"_id": cls.pid})

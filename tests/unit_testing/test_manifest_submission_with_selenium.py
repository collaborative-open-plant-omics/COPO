# Created by AProvidence on 23-03-2022
from dal.copo_da import Profile, Sample
from django.conf import settings
from django.test import TestCase
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from tests.utilities.helpers import one_of_these_elements_is_visible
from web.apps.web_copo.models import User
import os
import pandas
import tools.resolve_env as env

from web.apps.web_copo.lookup import dtol_lookups as lookup


# Ensure that the copodev django server is running before running this test
# Run this command before running the tests, $ supervisord -c celery.conf && supervisorctl -c celery.conf start all
# iF "Apps aren't loaded yet" message is raised, run this command: python manage.py check
class DTOLManifestSubmissionTest(TestCase):

    @classmethod
    def setUpClass(cls):
        settings.UNIT_TESTING = True
        settings.TEST_USER_NAME = 'aaliyah'
        cls.cwd = os.getcwd()  # get current working directory path
        cls.dtol_manifest = dict()
        cls.dtol_manifest = pandas.read_excel('tests/manifests/sample_manifest.xlsx', sheet_name='DTOLSAMPLE1.3')
        options = Options()
        options.headless = False
        cls.driver = webdriver.Firefox(options=options)
        user_id = 2
        # Create a DTOL profile
        p_dict = {"copo_id": "000000000", "description":
            "Test Description", "user_id": user_id, "type": "Darwin Tree of Life (DTOL)", "title": "Test Title"}
        cls.pid = Profile().save_record(dict(), **p_dict)

    def test_working_dtol_manifest_validation_and_submission(self):
        self.driver.get("http://127.0.0.1:8000/copo/")
        if "login" in self.driver.current_url:
            self._login()
        element = self._get_to_manifest_upload_point()
        # manifests_folder_path = os.path.join(self.cwd, "manifests", self.dtol_manifest)
        element.send_keys(self.dtol_manifest)
        element = WebDriverWait(self.driver, 20).until(one_of_these_elements_is_visible("finish_button",
                                                                                        "export_errors_button"))
        assert "finish_button" in element.get_attribute('id').split()
        element.click()
        element = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#final_submit"))
        )
        element.click()
        WebDriverWait(self.driver, 20).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#sample_spreadsheet_modal"))
        )
        samples = Sample().get_collection_handle().find({"profile_id": str(self.pid["_id"])})
        assert len(list(samples)) == 39

        # now query api and check for right number of results

    def _get_to_manifest_upload_point(self):
        self.driver.get("http://127.0.0.1:8000/copo/copo_samples/" + str(self.pid["_id"]) + "/view")
        assert "/copo/copo_samples/" in self.driver.current_url
        element = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".new-samples-spreadsheet-template"))
        )
        element.click()
        return self.driver.find_element(By.ID, "file")

    def _login(self):
        self.driver.get("http://127.0.0.1:8000/copo")
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Sign in with Orcid.org"))
        )
        element.click()
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert "orcid" in self.driver.current_url
        username = env.get_env("SELENIUM_TEST_USERNAME")
        password = env.get_env("SELENIUM_TEST_PASSWORD")
        element.send_keys(username)
        element = self.driver.find_element(By.ID, "password")
        element.send_keys(password)
        element.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "copo-global-nav"))
        )
        assert "COPO" in self.driver.title
        try:
            element = self.driver.find_element(By.ID, "profile_table_div")
        except NoSuchElementException:
            assert False
        assert True

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        Sample().get_collection_handle().remove({"profile_id": str(cls.pid["_id"])})
        Profile().get_collection_handle().remove({"_id": cls.pid["_id"]})
        pass

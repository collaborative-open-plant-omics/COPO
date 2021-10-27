import unittest
from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from .test_helpers import one_of_these_elements_is_visible
from django.conf import settings
from django.contrib.auth.models import User
from dal.copo_da import Profile, Sample
import os
import tools.resolve_env as env


class LoginTest(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.manifest_files = dict()
        cls.manifest_files["DTOL_1.3_WORKING"] = "SAMPLE_DTOL_1.3.xlsx"
        cls.manifest_files["DTOL_1.3_MISSING_TAXON_AND_SPECIMEN_ID"] = ""
        options = Options()
        options.headless = False
        cls.driver = webdriver.Firefox(options=options)
        settings.UNIT_TESTING = True
        # N.B. change this to your userid
        user_id = 1
        # create profile
        p_dict = {"copo_id": "000000000", "description":
            "Test Description", "user_id": 1, "type": "Darwin Tree of Life (DTOL)", "title": "Test Title"}
        cls.pid = Profile().save_record(dict(), **p_dict)
        cls.cwd = os.path.dirname(os.path.realpath(__file__))

    def test_working_dtol_manifest_valiation_and_saving(self):
        self.driver.get("http://127.0.0.1:8000/copo/")
        if "login" in self.driver.current_url:
            self._login()
        element = self._get_to_manifest_upload_point()
        manifest_path = os.path.join(self.cwd, "manifests", self.manifest_files["DTOL_1.3_WORKING"])
        element.send_keys(manifest_path)
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

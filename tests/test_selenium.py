import unittest
from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from django.conf import settings
from django.contrib import U


class LoginTest(TestCase):

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.headless = True
        cls.driver = webdriver.Firefox(options=options)
        settings.UNIT_TESTING = True
        # create user
        cls.user = User.objects.create_user(username='jonny', first_name="jonny", last_name="appleseed",
                                            email='jonny@appleseed.com', password='jonnyappleseed')
        cls.user.save()

        # create profile
        p_dict = {"copo_id": "000000000", "description": "Test Description", "user_id": 1, "title": "Test Title"}
        cls.pid = Profile().save_record(dict(), **p_dict)

    def test_manifest(self):
        self._login()

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
        element.send_keys("felix.shaw@tgac.ac.uk")
        element = self.driver.find_element(By.ID, "password")
        element.send_keys("Apple123")
        element.send_keys(Keys.ENTER)
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".copo-dt"))
        )
        assert "/copo" in self.driver.current_url

    @classmethod
    def tearDownClass(cls):
        # self.driver.close()
        pass

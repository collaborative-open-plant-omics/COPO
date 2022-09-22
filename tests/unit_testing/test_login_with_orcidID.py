# Created by AProvidence 20052022

from django.conf import settings
from unittest import TestCase, TestLoader
from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tests.utilities.helpers import one_of_these_elements_is_visible

import os
import tools.resolve_env as env


class TestSuccessfulORCIDLogin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.UNIT_TESTING = True
        options = Options()
        options.headless = False
        cls.webdriver = webdriver.Firefox(options=options)
        cls.base_url = "http://127.0.0.1:8000/"
        TestLoader.sortTestMethodsUsing = None

    def test_valid_orcid_login_credentials(self):
        """Test """
        self.webdriver.get(self.base_url + "copo/")
        self.assertIn("login", self.webdriver.current_url)
        orcid_signin_button = WebDriverWait(self.webdriver, 5).until(
            ec.presence_of_element_located((By.LINK_TEXT, "Sign in with Orcid.org"))
        )
        orcid_signin_button.click()
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

    def test_logout(self):
        """Test """
        self.webdriver.get(self.base_url + "copo/logout")
        self.assertIn("logout", self.webdriver.current_url)
        orcid_logout_button = WebDriverWait(self.webdriver, 5).until(
            ec.presence_of_element_located((By.LINK_TEXT, "Sign Out"))
        )
        orcid_logout_button.click()
        assert "login" in self.webdriver.current_url
        element = WebDriverWait(self.webdriver, 5).until(
            ec.presence_of_element_located((By.ID, "username"))
        )
        assert "orcid" in self.webdriver.current_url

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.webdriver.close()

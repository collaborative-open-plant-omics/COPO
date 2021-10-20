import unittest
from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options


class LoginTest(TestCase):
    def setUp(self):
        options = Options()
        options.headless = False
        self.driver = webdriver.Firefox(options=options)

    def test_login(self):
        self.driver.get("http://127.0.0.1:8000/copo")

        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Sign in with Orcid.org"))
        )
        element.click()
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        element.send_keys("felix.shaw@tgac.ac.uk")
        element = self.driver.find_element(By.ID, "password")
        element.send_keys("Apple123")
        element.send_keys(Keys.ENTER)
        assert True

    def tearDown(self):
        pass
        ##self.driver.close()

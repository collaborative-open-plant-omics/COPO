# Created by AProvidence on 29-03-2022
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

class SeleniumTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(SeleniumTestCase, self).setUp()

    def test_tab_title(self):
        """
        Test that the title for each possible url contains COPO
        """
        print("Test tab title")
        driver = self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('web_copo:index')))
        self.assertIn("COPO", self.selenium.title)
        driver.get("%s%s" % (self.live_server_url, reverse('web_copo:auth')))
        self.assertIn("COPO", self.selenium.title)
        driver.get("%s%s" % (self.live_server_url, reverse('web_copo:logout')))
        self.assertIn("COPO", self.selenium.title)

    def test_links(self):
        """
        test that the cyverse logo works as a link to the main page.
        Will test only one url as this is in the base and it's always the same
        -already verify this in the previous test-
        """
        print("test_links")
        timeout = 180  # if an error arise looking for #earlham_logo selector try to increase this before assess the failure
        driver = self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('web_copo:index')))
        WebDriverWait(driver, timeout).until(lambda web_driver: web_driver.find_element_by_css_selector('a > img#logo7-white-leaves-trans'))
        result = driver.find_element_by_css_selector("a > img#logo7-white-leaves-trans")
        result.click()

    # http://127.0.0.1:8000/static/copo/img/logo7-white-leaves-trans.png
    def tearDown(self):
        self.selenium.quit()

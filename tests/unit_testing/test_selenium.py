from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from selenium import webdriver


class SeleniumTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(SeleniumTestCase, self).setUp()

    def test_tab_title(self):
        """
        test that the title for each possible url contains CyVerse
        """
        print("test_tab_title")
        driver = self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('copo:i')))
        self.assertIn("COPO", self.selenium.title)
        driver.get("%s%s" % (self.live_server_url, reverse('japps:go-to-index')))
        self.assertIn("CyVerse", self.selenium.title)
        # selenium.get("%s%s" % (self.live_server_url, reverse('japps:submission', args=["fakeapp"])))
        # self.assertIn("CyVerse", self.selenium.title)
        driver.get("%s%s" % (self.live_server_url, reverse('japps:job_submitted')))
        self.assertIn("CyVerse", self.selenium.title)

    def tearDown(self):
        self.selenium.quit()

# Created by AProvidence on 29-03-2022
from django.conf import settings
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

# Ensure that the "copodev" django server is running before running this test
# Run this command before running the tests: $ supervisord -c celery.conf && supervisorctl -c celery.conf start all

class WebsiteLinksTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(WebsiteLinksTest, cls).setUpClass()
        settings.UNIT_TESTING = True
        options = Options()
        options.headless = False
        cls.webdriver = webdriver.Firefox(options=options)

    def test_tab_title(self):
        """ Test that the title for each possible url contains COPO """
        print("Test tab title")
        self.webdriver.get("%s%s" % (self.live_server_url, reverse('web_copo:index')))
        self.assertIn("COPO", self.webdriver.title)
        self.webdriver.get("%s%s" % (self.live_server_url, reverse('web_copo:auth')))
        self.assertIn("COPO", self.webdriver.title)
        self.webdriver.get("%s%s" % (self.live_server_url, reverse('web_copo:logout')))
        self.assertIn("COPO", self.webdriver.title)

    def test_links(self):
        """ 
            Test that the "COPO" logo works as a link to the main page.
            Test only one URL because it is in the base therefore, the result will 
            always be the same (This has been verified in the previous test)
        """
        print("Test links")
        timeout = 180  # if an error arise looking for #earlham_logo selector try to increase this before assess the
                       # failure
        self.webdriver.get("%s%s" % (self.live_server_url, reverse('web_copo:index')))
        WebDriverWait(self.webdriver, timeout).until(lambda web_driver: web_driver.find_element_by_css_selector('a > img#logo7-white-leaves-trans'))
        result = self.webdriver.find_element_by_css_selector("a > img#logo7-white-leaves-trans")
        result.click()

    # http://127.0.0.1:8000/static/copo/img/logo7-white-leaves-trans.png
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.webdriver.quit()

# Created by AProvidence on 29-03-2022
from tests.test_base import SeleniumBaseTest
# Ensure that the “copodev” django server is running before running selenium tests
# Run this command before running the selenium tests:
# $ supervisord -c celery.conf && supervisorctl -c celery.conf start all


class WebsiteLinksTest(SeleniumBaseTest):
    def test_tab_title(self):
        """ Test the visibility of 'COPO' in the website title """
        print("Test tab title")
        self.webdriver.get("%s%s" % (self.host, self.index_url))
        self.assertIn("COPO", self.webdriver.title)
        self.webdriver.get("%s%s" % (self.host, self.login_url))
        self.assertIn("COPO", self.webdriver.title)
        self.webdriver.get("%s%s" % (self.host, self.logout_url))
        self.assertIn("COPO", self.webdriver.title)

    # def test_links(self):
    #     """
    #         Test that the "COPO" logo works as a link to the main page.
    #         Test only one URL because it is in the base therefore, the result will
    #         always be the same (This has been verified in the previous test)
    #     """
    #     print("Test links")
    #     timeout = 180  # if an error arise looking for #earlham_logo selector try to increase this before assess the
    #     # failure
    #     print(self.live_server_url)
    #     self.webdriver.get("%s%s" % (self.host, reverse('web_copo:index')))
    #     WebDriverWait(self.webdriver, timeout).until(
    #         lambda web_driver: web_driver.find_element_by_css_selector('a > img#logo7-white-leaves-trans'))
    #     result = self.webdriver.find_element_by_css_selector("a > img#logo7-white-leaves-trans")
    #     result.click()

    # http://127.0.0.1:8000/static/copo/img/logo7-white-leaves-trans.png

    def test_redirection_without_logging_in(self):
        """ Test redirection for unauthorised user """
        print("Test website redirection")
        # # response = self.webdriver.get(self.accept_reject_sample_url)
        # self.not_loggedin_client.get(self.accept_reject_sample_url)
        # self.assertEqual(response.status_code, 301)  # this is the code for redirection
        pass
    # @classmethod
    # def tearDownClass(cls):
    #     super().tearDownClass()
    #     cls.webdriver.quit()

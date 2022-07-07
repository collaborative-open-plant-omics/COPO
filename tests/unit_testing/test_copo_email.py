from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from faker import Faker
from web.apps.web_copo.copo_email import CopoEmail
import smtplib
import web.settings.email as email_settings
from web.apps.web_copo.views import copo_sample_accept_reject


# from tests.utilities.helpers import DummySMTP, inbox as test_inbox

@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend')
class CopoEmailTest(TestCase):
    # Assume our app has a signup view that accepts an email address...
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True
        cls.fake = Faker()
        # cls.client = ValidatingClient()
        # Mailserver
        cls.mailserver = smtplib.SMTP(host=email_settings.mail_server, port=email_settings.mail_server_port)
        # smtplib.SMTP = DummySMTP
        # cls.test_mailserver = DummySMTP

        """ User and Profile """
        # Create a user model object and save it in the "test_copo" temporary PostgreSQL database
        cls.username = cls.fake.first_name().lower()
        cls.user_password = User.objects.make_random_password()
        cls.user = User.objects.create_user(username=settings.TEST_USER_NAME,
                                            first_name=cls.fake.first_name(),
                                            last_name=cls.fake.last_name(),
                                            email='aaliyah.providence@earlham.ac.uk',  # cls.fake.free_email(),
                                            password=cls.user_password)
        cls.user.save()

        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": cls.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}

        # Create a ERGA profile on the COPO website
        erga_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": cls.user.id,
                        "type": "European Reference Genome Atlas (ERGA)", "title": "ERGA Test Title"}

        # cls.user_pid = Profile().get_collection_handle().insert(dtol_profile)
        cls.dtol_pid = Profile().save_record(dict(), **dtol_profile)
        cls.erga_pid = Profile().save_record(dict(), **erga_profile)
        cls.copo_accept_reject_sample_url = reverse('web_copo:accept_reject')

    def test_smtp_connection(self):
        # Connect to an actual host on an actual port
        self.mailserver.ehlo()
        self.mailserver.starttls()

        # Check that an open socket exists/ mailserver is connected
        self.assertIsNotNone(self.mailserver.sock)

        # Run a no-operation i.e. a server-side pass-through
        (port, bytes_message) = self.mailserver.noop()
        self.assertEqual((port, bytes_message.decode('utf-8')), (250, '2.0.0 OK'))  # Convert bytes to string

        # Check that mailserver connection is disconnected
        (port, bytes_message) = self.mailserver.quit()
        self.assertEqual((port, bytes_message.decode('utf-8')), (221, '2.0.0 Service closing transmission channel'))
        self.assertIsNone(self.mailserver.sock)

    def test_send_email_on_demo_server_using_erga_profile_type(self):
        # Using ERGA profile with HTML enabled
        demo_server_url = 'https://demo.copo-project.org/' + self.copo_accept_reject_sample_url
        message = CopoEmail().messages["new_manifest"].format(str(self.erga_pid["title"]),
                                                              "DEMO SERVER NOTIFICATION - " + str(
                                                                  self.erga_pid["description"]), demo_server_url,
                                                              demo_server_url)
        subject = "DEMO SERVER NOTIFICATION: New " + "ERGA " + "Manifest - " + str(
            self.erga_pid["title"])
        # Start the mailserver
        test_inbox = []  # clears the inbox
        self.mailserver.ehlo()
        self.mailserver.starttls()
        # self.assertContains(demo_server_url, "demo")
        request = HttpRequest()
        self.client.login(username=settings.TEST_USER_NAME, password=self.user_password)
        response = self.client.get(self.copo_accept_reject_sample_url)
        CopoEmail().notify_new_manifest(demo_server_url, project="ERGA",
                                        title=str(self.erga_pid["title"]),
                                        description=str(self.erga_pid["description"]))
        # self.client.session.

        html = response.content.decode('utf8')
        self.assertIn(message, html)

        # CopoEmail().mailserver.

        # .send(to=self.user.email, sub=subject, content=message, html=True)
        # CopoEmail.
        # assert len(test_inbox) == 1  # check one email was sent
        # assert test_inbox[0].
        #                .to_address == self.user.email

        # self.assertIn(b'hello', self.mailserver.)
        # # Test that one message was sent:
        # self.assertEqual(len(self.mailserver.
        #                      .outbox), 1)
        #
        # # Verify attributes of the EmailMessage that was sent:
        # self.assertEqual(mail.outbox[0].to, [self.user.email])
        # self.assertEqual(mail.outbox[0].tags, ["confirmation"])  # an Anymail custom attr
        #
        # # Or verify the Anymail params, including any merged settings defaults:
        # self.assertTrue(mail.outbox[0].anymail_test_params["track_clicks"])
        # Disconnect from the mailserver
        self.mailserver.quit()

    def test_send_email_on_prod_server_using_dtol_profile_type(self):
        # Using DTOL profile with HTML disabled
        prod_server_url = 'https://copo-project.org/' + self.copo_accept_reject_sample_url
        subject = "New " + str(self.dtol_pid["project"]) + " Manifest - " + str(self.dtol_pid["title"])
        message = CopoEmail().messages["new_manifest"].format(str(self.dtol_pid["title"]),
                                                              str(self.dtol_pid["description"]), prod_server_url,
                                                              prod_server_url)
        CopoEmail.send(to=self.user.email, sub=subject, content=message, html=False)
        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)

        # Verify attributes of the EmailMessage that was sent:
        self.assertEqual(mail.outbox[0].to, ["user@example.com"])
        self.assertEqual(mail.outbox[0].tags, ["confirmation"])  # an Anymail custom attr

        # Or verify the Anymail params, including any merged settings defaults:
        self.assertTrue(mail.outbox[0].anymail_test_params["track_clicks"])

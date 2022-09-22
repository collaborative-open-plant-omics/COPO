from django.test import TestCase
from web.apps.web_copo.templatetags.html_tags import get_providers_orcid_first
from web.apps.web_copo.models import User


class HTMLTemplateTagsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # don't use the manager because we want to ensure the site exists
        # with pk=1, regardless of whether or not it already exists.
        cls.user = User.objects.create_user("testuser", "test@example.com", "s3krit")

    #  Test get_providers_orcid_first
    def test_social_authentication_providers_with_orcid_as_first_entry(self):
        result = get_providers_orcid_first()
        print(result)
        # self.assertEqual(result, -1)

    def test_input_smaller_than_minus_one(self):
        result = get_providers_orcid_first(-15)
        self.assertEqual(result, -2)

from django.test import TestCase
from django.urls import reverse, resolve
import api.handlers.general as api_views


class TestApiUrls(TestCase):
    """ Tests api urls """

    # path('login_orcid/', api_views.login_orcid, name='login_orcid'),
    # path('check_orcid_credentials/', api_views.check_orcid_credentials, name='check_orcid_credentials'),
    # path('get_collection_type/', api_views.get_collection_type, name='get_collection_type'),
    # path('convert_to_sra/', api_views.convert_to_sra, name='convert_to_sra'),
    # path('refactor_collection_schema/', api_views.refactor_collection_schema, name='refactor_collection_schema')
    #
    """ Test views urls """

    # setUp() method - the test runner runs the method prior each tests
    # @classmethod
    # def setUp(cls):

    def test_generate_ena_template_url_is_resolved(self):
        self.assertEquals('generate_ena_template', 'generate_ena_template')

    def test_login_orchid_url_is_resolved(self):
        self.assertEquals('login_orcid', api_views.login_orcid)

    def test_check_orcid_credentials_url_is_resolved(self):
        self.assertEquals(resolve('check_orcid_credentials').func, api_views.check_orcid_credentials)

    def test_get_collection_type_url_is_resolved(self):
        self.assertEquals('get_collection_type', api_views.get_collection_type)

    def test_convert_to_sra_url_is_resolved(self):
        self.assertEquals('convert_to_sra', api_views.convert_to_sra)

    def test_refactor_collection_schema_url_is_resolved(self):
        self.assertEquals('refactor_collection_schema', api_views.refactor_collection_schema)

    # tearDown() method -  the test runner invokes that method after each test

    # @classmethod
    # def tearDown(cls):

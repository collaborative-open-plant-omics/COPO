# Created by AProvidence on 14-03-2022
from django.conf import settings
from django.test import TestCase
from django.urls import reverse, resolve, NoReverseMatch, Resolver404


class TestApiUrls(TestCase):
    """ Tests api urls """
    settings.UNIT_TESTING = True

    def test_submit_to_figshare(self):
        with self.assertRaises(NoReverseMatch):
            reverse('submit_figshare_collection')

    def test_get_figshare_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('view_figshare_collection')

    def test_delete_figshare_article_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('delete_article')

    def test_generate_ena_template_url_is_resolved(self):
        with self.assertRaises(Resolver404):
            resolve('generate_ena_template/')

    def test_doi2publication_metadata_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('doi2publication_metadata')

    def test_login_orcid_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('login_orcid')

    def test_check_orcid_credentials_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('check_orcid_credentials')

    def test_get_collection_type_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('get_collection_type')

    def test_convert_to_sra_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('convert_to_sra')

    def test_refactor_collection_schema_url_is_resolved(self):
        with self.assertRaises(NoReverseMatch):
            reverse('refactor_collection_schema')

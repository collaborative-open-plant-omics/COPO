from django.test import TestCase
from django.urls import reverse


class ViewsTestCase(TestCase):
    def test_index_page_loads_correctly(self):
        """ Verifies that the index page loads properly"""
        print("Tests the loading of index webpage")
        response = self.client.get('/')
        ip_server_response = self.client.get('127.0.0.1:8000')
        # html = response.content.decode('utf8')
        # self.assertTrue(html.startswith('<!DOCTYPE html>'))
        # self.assertIn('<title>COPO - Collaborative Omics</title>', html)
        # self.assertTrue(html.endswith('</html>'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ip_server_response.status_code, 200)
        self.assertTemplateUsed(response, 'index_new.html')


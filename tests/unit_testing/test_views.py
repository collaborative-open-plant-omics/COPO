# Created by AProvidence on 02-04-2022
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client
from django.urls import reverse, resolve
from web.apps.web_copo import views


class ViewsTestCase(TestCase):
# copo/error_page.html, copo/base_simple.html
    @classmethod
    def setUp(cls):
        cls.client = Client()
        cls.login_url = reverse('web_copo:auth')
        cls.error_url = reverse('web_copo:error_page')

    def test_index_page_loads_correctly(self):
        """ Verifies that the index page loads properly"""
        print("Tests the loading of index webpage")
        response = self.client.get('/')
        response2 = self.client.get('web_copo:index')
        ip_server_response = self.client.get('127.0.0.1:8000')
        html = response.content.decode('utf8')
        # self.assertTrue(html.startswith('<!DOCTYPE html>'))
        # self.assertIn('<title>COPO - Collaborative Omics</title>', html)
        self.assertTrue(html.endswith('</html>'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ip_server_response.status_code, 200)
        self.assertTemplateUsed(response, 'index_new.html')
        self.assertTemplateUsed(response2, 'copo/index.html')
        self.assertEquals(resolve(reverse('index')).func, views.index)

    def test_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'copo/auth/login.html')

    def test_stats_page(self):
        self.assertEquals(resolve(reverse('cart')).func, cart)

    def test_error_page(self):
        response = self.client.get(self.error_url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateUsed(response, 'copo/error_page.html')


    # send copo request so 200 should be returned which means
    # some parts can be logged in since login authentication is needs

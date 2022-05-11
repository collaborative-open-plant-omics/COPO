# Created by AProvidence on 02-04-2022
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.views.generic import TemplateView
from web.apps.web_copo import views


class TestViews(TestCase):
    # Main templates used: copo/error_page.html, copo/base_simple.html
    @classmethod
    def setUp(cls):
        settings.UNIT_TESTING = True

        cls.client = Client()
        cls.about_resolver = resolve('/about/')
        cls.people_resolver = resolve('/people/')
        cls.dtol_resolver = resolve('/dtol/')
        cls.news_resolver = resolve('/news/')
        cls.manifests_resolver = resolve('/manifests/')
        cls.ebp_resolver = resolve('/ebp/')
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
        self.assertTemplateUsed(response2, 'copo/base_simple.html') # 'copo/index.html'
        self.assertEquals(resolve(reverse('web_copo:index')).func, views.index)

    def test_login_page(self):
        """ Verifies that the login page loads properly"""
        print("Tests that the login page loads well")
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'copo/auth/login.html')

    def test_stats_page(self):
        pass

    def test_error_page(self):
        """ Verifies that the error page loads properly"""
        print("Tests that the error page loads well")
        response = self.client.get(self.error_url)
        self.assertEquals(response.status_code, 302)
        print(response)
        # self.assertTemplateUsed(response, 'copo/login?next=/copo/error/')

    def test_landing_views(self):
        pass

    def test_resolve_to_about_page_view(self):
        """ Verifies that the about page loads properly"""
        print("Tests that the about page operates how it should well")
        response = self.client.get(self.about_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html') # 'about.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.about_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.about_resolver.url_name, "about")
        self.assertEqual(self.about_resolver.route, "about/")

    def test_resolve_to_people_page_view(self):
        """ Verifies that the people page loads properly"""
        print("Tests that the people page operates how it should well")
        response = self.client.get(self.people_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html') # 'people.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.people_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.people_resolver.url_name, "people")
        self.assertEqual(self.people_resolver.route, "people/")

    def test_resolve_to_dtol_page_view(self):
        """ Verifies that the dtol page loads properly"""
        print("Tests that the dtol page operates how it should well")
        response = self.client.get(self.dtol_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html') # 'dtol.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.dtol_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.dtol_resolver.url_name, "dtol")
        self.assertEqual(self.dtol_resolver.route, "dtol/")

    def test_resolve_to_news_page_view(self):
        """ Verifies that the news page loads properly"""
        print("Tests that the news page operates how it should well")
        response = self.client.get(self.news_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html') # 'news.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.news_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.news_resolver.url_name, "news")
        self.assertEqual(self.news_resolver.route, "news/")

    def test_resolve_to_manifests_page_view(self):
        """ Verifies that the manifests page loads properly"""
        print("Tests that the manifests page operates how it should well")
        response = self.client.get(self.manifests_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html') # 'manifests.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.manifests_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.manifests_resolver.url_name, "manifests")
        self.assertEqual(self.manifests_resolver.route, "manifests/")

    def test_resolve_to_ebp_page_view(self):
        """ Verifies that the about page loads properly"""
        print("Tests that the ebp page operates how it should well")
        response = self.client.get(self.ebp_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html') # 'ebp_resources.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ebp_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.ebp_resolver.url_name, "ebp")
        self.assertEqual(self.ebp_resolver.route, "ebp/")

    # Other tests to be done:
    # send copo request so 200 should be returned which means is needs
    # some parts can be logged in since login authentication
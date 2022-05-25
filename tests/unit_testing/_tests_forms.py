# Created by AProvidence on 29-03-2022
from django.conf import settings
from django.test import TestCase


class TestForms(TestCase):
    settings.UNIT_TESTING = True

    def test_author_form_valid(self):
        # form = LoginForm(data={
        #     'name': 'John Cena',
        #     'age': 25
        # })
        # self.assertTrue(form.is_valid())
        pass

    def test_author_form_invalid(self):
        # form = LoginForm(data={
        #     'name': 11,
        #     'age': 'zxa'
        # })
        # self.assertFalse(form.is_valid())
        pass


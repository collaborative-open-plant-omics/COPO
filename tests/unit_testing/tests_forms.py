from django.test import TestCase
from api_basic.forms import LoginForm

# Create your tests here.
class LoginFormTestCase(TestCase):

    def test_author_form_valid(self):
        form = LoginForm(data={
            'name': 'John Cena',
            'age': 25
        })
        self.assertTrue(form.is_valid())

    def test_author_form_invalid(self):
        form = LoginForm(data={
            'name': 11,
            'age': 'zxa'
        })
        self.assertFalse(form.is_valid())


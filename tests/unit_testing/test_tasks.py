
from django.conf import settings
from django.test import TestCase


class TestTasks(TestCase):
    settings.UNIT_TESTING = True

    def test_something(self):
        pass



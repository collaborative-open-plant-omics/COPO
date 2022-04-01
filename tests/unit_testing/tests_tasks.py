from django.test import TestCase


class MyTestCase(TestCase):
    def test_something(self):
        self.assertEqual(True, 3 < 4)  # add assertion here



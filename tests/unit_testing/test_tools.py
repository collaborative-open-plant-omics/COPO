# Created by AProvidence on 25-04-2022
from django.conf import settings
from django.test import TestCase
from tools import resolve_env


class TestTools(TestCase):
    @classmethod
    def setUpClass(cls):
        settings.UNIT_TESTING = True
        settings.TEST_USER_NAME = "tester101"
        # Environment variable keys
        cls.environment_type_key = "ENVIRONMENT_TYPE"
        cls.virtual_machine_name_key = "COPO_VM_NAME"
        cls.debug_type_key = "DEBUG"

    def test_environment_variables_and_file_assignments(self):
        """Test that environment variables are set up correctly"""
        print('Test that correct values are returned for a variable key in the environment variables')
        self.assertNotEqual(resolve_env.get_env(self.environment_type_key), "prod")
        self.assertEqual(resolve_env.get_env(self.virtual_machine_name_key), "copo_env")
        self.assertTrue(self.debug_type_key)

    @classmethod
    def tearDownClass(cls):
        pass

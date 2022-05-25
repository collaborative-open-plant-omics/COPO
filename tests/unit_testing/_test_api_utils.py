from api.utils import get_return_template, extract_to_template, finish_request
from django.conf import settings
from django.test import TestCase

from dal.copo_da import Sample, Person


class TestAPIUtils(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True
        cls.wrapper_template = get_return_template('WRAPPER')
        cls.person_template = get_return_template('PERSON')
        cls.source_template = get_return_template('SOURCE')
        cls.sample_template = get_return_template('SAMPLE')

    def test_get_return_template_method_with_valid_type(self):
        """Test that a template (Python object) is returned from a given API template return type """
        self.assertTrue(type(self.wrapper_template) is dict)
        self.assertTrue(type(self.person_template) is dict)
        self.assertTrue(type(self.source_template) is dict)
        self.assertTrue(type(self.sample_template) is dict)

        self.assertTrue(isinstance(self.wrapper_template, dict))
        self.assertTrue(isinstance(self.person_template, dict))
        self.assertTrue(isinstance(self.source_template, dict))
        self.assertTrue(isinstance(self.sample_template, dict))

    def test_get_return_template_with_invalid_type(self):
        """Test that an exception is returned when no API template return type is given """
        with self.assertRaises(KeyError):
            get_return_template('USER')

    def test_extract_template_method(self):
        """ Test that fields are extracted from a SAMPLE, PERSON OR SOURCE """
        print('Test that fields are extracted from a SAMPLE template, PERSON template or SOURCE template')
        # ss = Sample().get_record(id)
        # sample = ss['sample']
        # source = ss['source']
        # person = Person().GET(id) # get person object

       # source_template_fields_extraction = extract_to_template(object=source, template=self.source_template)
        # self.assertTrue(type(self.wrapper_template) is dict)
        # self.assertTrue(type(self.person_template) is dict)
        # self.assertTrue(type(self.source_template) is dict)
        # self.assertTrue(type(self.sample_template) is dict)
        #
        # self.assertTrue(isinstance(self.wrapper_template, dict))
        # self.assertTrue(isinstance(self.person_template, dict))
        # self.assertTrue(isinstance(self.source_template, dict))
        # self.assertTrue(isinstance(self.sample_template, dict))
        pass



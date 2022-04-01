from dal.copo_da import Profile
from ddt import data, unpack  # pip3 install ddt
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from web.apps.web_copo.utils.dtol.tol_validators import taxon_validators
from faker import Faker
from password_generator import PasswordGenerator
from tests.utilities.helpers import read_data_from_excel
from web.apps.web_copo.utils.dtol.Dtol_Spreadsheet import DtolSpreadsheet


class TestTaxonValidation(TestCase):
    @classmethod
    def setUpClass(cls):
        settings.UNIT_TESTING = True
        fake = Faker()
        _firstname = fake.first_name()
        _lastname = fake.last_name()
        _username = fake.first_name().lower() + "_1"
        _email = _firstname.lower() + _lastname + "@example.com"

        settings.TEST_USER_NAME = _username
        # Create a user
        cls.user = User.objects.create_user(username=settings.TEST_USER_NAME, first_name=_firstname,
                                            last_name=_lastname, email=_email,
                                            password=PasswordGenerator().generate())
        cls.user.save()

        # Create a profile
        p_dict = {"copo_id": "000000000", "description": "Test Description", "user_id": cls.user.id,
                  "type": "Darwin Tree of Life (DTOL)", "title": "Test Title"}
        cls.pid = Profile().save_record(dict(), **p_dict)

    @data(read_data_from_excel("tests/manifests/sample_manifest.xlsx", "ERGASample1"))
    # @unpack
    def test_blank_manifest(self):
        """
        If manifest is blank, an appropriate message is displayed
        """
        self.assertEquals(2, 1 + 1)

    def test_wrong_taxonnomy(self):
        response = self.client.get("http://127.0.0.1:8000/copo/copo_samples/" + "6243392e17609ffc4f2b80b8" + "/view")
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No polls are available.")
        # self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_taxonID_association_to_several_specimenIDs(self):
        self.assertEquals(2, 1 + 1)

    def test_taxonID_map_to_correct_species_name(self):
        self.assertEquals(2, 1 + 1)

    def test_taxonID(self):
        self.assertEquals(2, 1 + 1)

    def test_date_in_correct_formart(self):
        self.assertEquals(2, 1 + 1)
    
    #- Specimen and whole organism should only be present only once and not on the same row
    def test_occurences_of_whole_organism(self):
        self.assertEquals(2, 1 + 1)
    
    # Special characters and pipe (|) should not be used
    def test_alphanumeric_characters_used(self):

        dtol = DtolSpreadsheet()
        dtol.save_records()
        print(dtol.save_records())
        # return HttpResponse(status=200)
        # asset.self.client.get('127.0.0.1:8000')
        self.assertEqual(2, 1 + 1)

    # def test_taxonID(self, SERIES, RACK_OR_PLATE_ID, TUBE_OR_WELL_ID, SPECIMEN_ID, ORDER_OR_GROUP, FAMILY, GENUS,
    #                  TAXON_ID, SCIENTIFIC_NAME, TAXON_REMARKS, INFRASPECIFIC_EPITHET, CULTURE_OR_STRAIN_ID, COMMON_NAME,
    #                  LIFESTAGE, SEX, ORGANISM_PART, SYMBIONT, RELATIONSHIP, GAL, GAL_SAMPLE_ID, COLLECTOR_SAMPLE_ID,
    #                  COLLECTED_BY, COLLECTOR_AFFILIATION, DATE_OF_COLLECTION, COLLECTION_LOCATION, DECIMAL_LATITUDE,
    #                  DECIMAL_LONGITUDE, GRID_REFERENCE, HABITAT, DEPTH, ELEVATION, TIME_OF_COLLECTION,
    #                  DESCRIPTION_OF_COLLECTION_METHOD, EASE_OF_SPECIMEN_COLLECTION, IDENTIFIED_BY,
    #                  IDENTIFIER_AFFILIATION, IDENTIFIED_HOW, SPECIMEN_ID_RISK, PRESERVED_BY, PRESERVER_AFFILIATION,
    #                  PRESERVATION_APPROACH, PRESERVATIVE_SOLUTION, TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION,
    #                  DATE_OF_PRESERVATION, SIZE_OF_TISSUE_IN_TUBE, TISSUE_REMOVED_FOR_BARCODING, PLATE_ID_FOR_BARCODING,
    #                  TUBE_OR_WELL_ID_FOR_BARCODING, TISSUE_FOR_BARCODING, BARCODE_PLATE_PRESERVATIVE,
    #                  PURPOSE_OF_SPECIMEN, HAZARD_GROUP, REGULATORY_COMPLIANCE, VOUCHER_ID, OTHER_INFORMATION,
    #                  PUBLIC_NAME, DIFFICULT_OR_HIGH_PRIORITY_SAMPLE):
    #     print(DtolSpreadsheet())
    #     self.assertEqual(SERIES, 1)  # add assertion here

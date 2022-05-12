# Created by AProvidence on 29-03-2022
from dal.copo_da import Profile, Sample
from django.conf import settings
from django.test import TestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tests.utilities.helpers import one_of_these_elements_is_visible
import os
import time
import pandas
import tools.resolve_env as env
from web.apps.web_copo.utils.dtol.Dtol_Spreadsheet import DtolSpreadsheet
from django.contrib.auth.models import User
from faker import Faker
from password_generator import PasswordGenerator


# Ensure that the copodev django server is running before running this test
# Run this command before running the tests: $ supervisord -c celery.conf && supervisorctl -c celery.conf start all
# Error: "Apps aren't loaded yet"; Solution: $ python manage.py check
# Error: django.contrib.auth.models.User.DoesNotExist: User matching query does not exist.
# Solution: Run copodev django server/ Run test file from

# Creates an object for the manifest file
# different validation for dtol adn erga
# setattr(person, 'name', 'Adam')
# set an attribute at creation time so that the profile id can be set since it is a required attribute for the
# Alternative: use parts of the code to do the test instead of calling the DTOLSpreadsheet class since the profile id is needed and the website
# needs to be running to get the profile id
# set profile id attribute before the manifest object is create

# pandas.read_excel('tests/manifests/sample_manifest.xlsx', sheet_name='DTOLSAMPLE1.3')
# # Specimen and whole organism should only ITAT, DEPTH, ELEVATION, TIME_OF_COLLECTION,
#                   DESCRIPTION_OF_COLLECTION_METHOD, EASE_OF_SPECIMEN_COLLECTION, IDENTIFIED_BY,
#                 IDENTIFIER_AFFILIATION, IDENTIFIED_HOW, SPECIMEN_ID_RISK, PRESERVED_BY, PRESERVER_AFFILIATION,
#                 PRESERVATION_APPROACH, PRESERVATIVE_SOLUTION, TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION,
#                  DATE_OF_PRESERVATION, SIZE_OF_TISSUE_IN_TUBE, TISSUE_REMOVED_FOR_BARCODING, PLATE_ID_FOR_BARCODING,
#                   TUBE_OR_WELL_ID_FOR_BARCODING, TISSUE_FOR_BARCODING, BARCODE_PLATE_PRESERVATIVE,
#                   PURPOSE_OF_SPECIMEN, HAZARD_GROUP, REGULATORY_COMPLIANCE, VOUCHER_ID, OTHER_INFORMATION,
#                   PUBLIC_NAME, DIFFICULT_OR_HIGH_PRIORITY_SAMPLE):
#      print(DtolSpreadsheet())
#      self.assertEqual(SERIES, 1)  # add assertion here
# be present only once and not on the same row
# def test_occurences_of_whole_organism(self):
#     self.assertEquals(2, 1 + 1)
#
#  Special characters and pipe (|) should not be used
# def test_alphanumeric_characters_used(self):
#
#     dtol = DtolSpreadsheet()
#     dtol.save_records()
#     print(dtol.save_records())
#     # return HttpResponse(status=200)
#     # asset.self.client.get('127.0.0.1:8000')
#     self.assertEqual(2, 1 + 1)
#
#  def test_taxonID(self, SERIES, RACK_OR_PLATE_ID, TUBE_OR_WELL_ID, SPECIMEN_ID, ORDER_OR_GROUP, FAMILY, GENUS,
#                   TAXON_ID, SCIENTIFIC_NAME, TAXON_REMARKS, INFRASPECIFIC_EPITHET, CULTURE_OR_STRAIN_ID, COMMON_NAME,
#                   LIFESTAGE, SEX, ORGANISM_PART, SYMBIONT, RELATIONSHIP, GAL, GAL_SAMPLE_ID, COLLECTOR_SAMPLE_ID,
#                   COLLECTED_BY, COLLECTOR_AFFILIATION, DATE_OF_COLLECTION, COLLECTION_LOCATION, DECIMAL_LATITUDE,
#                   DECIMAL_LONGITUDE, GRID_REFERENCE, HAB

class TestDTOLTaxonValidation(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        options = Options()
        options.headless = False
        sample_manifest_filename = "sample_manifest.xlsx"
        dtol_sample_1_3_sheetname = 'DTOLSAMPLE1.3'
        dtol_sample_1_3_filename = "DTOL_SAMPLE_1.xlsx"
        cls.cwd = os.getcwd()  # get current working directory path
        cls.driver = webdriver.Firefox(options=options)
        cls.dtol_manifest = dict()
        # DtolSpreadsheet(file="tests/manifests/sample_manifest.xlsx")

        _firstname = fake.first_name()
        _lastname = fake.last_name()
        _username = _firstname.lower() + "_1"
        _email = _firstname.lower() + _lastname + "@example.com"

        settings.TEST_USER_NAME = _username

        # Create a user model object and save it in the test_copo temporary database
        cls.user = User.objects.create_user(username=_username, first_name=_firstname,
                                            last_name=_lastname, email=_email,
                                            password=PasswordGenerator().generate())
        cls.user.save()

        # # Create an ERGA or DTOL profile on the COPO website
        p_dict = {"copo_id": "000000000", "description": "Test Description", "user_id": cls.user.id,
                  "type": "Darwin Tree of Life (DTOL)", "title": "Test Title"}
        cls.pid = Profile().get_collection_handle().insert(p_dict)

    def test_working_dtol_manifest_validation_and_submission(self):
        self.driver.get("http://127.0.0.1:8000/copo/")
        if "login" in self.driver.current_url:
            self._login()
        element = self._get_to_manifest_upload_point()
        manifests_dir_path = os.path.join(self.cwd, "tests", "manifests")
        # sample_manifest_path = os.path.join(manifests_dir_path, self.sample_manifest_filename)
        # dtol_sample1_3_worksheet_file = pandas.read_excel(sample_manifest_path, sheet_name=self.dtol_sample_1_3_sheetname)
        dtol_sample_1_file = os.path.join(manifests_dir_path, "DTOL_SAMPLE_1.xlsx")
        element.send_keys(dtol_sample_1_file)
        element = WebDriverWait(self.driver, 20).until(
            one_of_these_elements_is_visible("finish_button", "export_errors_button"))

    def _get_to_manifest_upload_point(self):
        self.driver.get("http://127.0.0.1:8000/copo/copo_samples/" + str(self.pid) + "/view")
        assert "/copo/copo_samples/" in self.driver.current_url
        element = WebDriverWait(self.driver, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, ".new-samples-spreadsheet-template"))
        )
        element.click()
        return self.driver.find_element(By.ID, "file")

    def _login(self):
        self.driver.get("http://127.0.0.1:8000/copo")
        element = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.LINK_TEXT, "Sign in with Orcid.org"))
        )
        element.click()
        element = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.ID, "username"))
        )
        assert "orcid" in self.driver.current_url
        username = env.get_env("SELENIUM_TEST_USERNAME")
        password = env.get_env("SELENIUM_TEST_PASSWORD")
        element.send_keys(username)
        element = self.driver.find_element(By.ID, "password")
        element.send_keys(password)
        element.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.ID, "copo-global-nav"))
        )
        assert "COPO" in self.driver.title
        try:
            element = self.driver.find_element(By.ID, "profile_table_div")

        except NoSuchElementException:
            assert False
        assert True

        '''
        # find confirm button the click in order to proceed.
                assert "finish_button" in element.get_attribute('id').split()
                element.click()
                element = WebDriverWait(self.driver, 20).until(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, "#final_submit"))
                )
                element.click()
                WebDriverWait(self.driver, 20).until_not(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, "#sample_spreadsheet_modal"))
                )
        
                samples = Sample().get_collection_handle().find({"profile_id": str(self.pid)})
                assert len(list(samples)) == 39
        
            
            def test_blank_manifest(self):
                """ If manifest is blank, an appropriate message is displayed"""
                # self.dtol_manifest.values()
                # print(len(self.dtol_manifest))
        
                pass
        
            # Query API and check for the correct number of results
            def test_erga_manifest_samples_submitted_to_ena(self):
                pass
        
            def test_dtol_manifest_samples_submitted_to_ena(self):
                pass
        
            def test_working_dtol_manifest(self):
                pass
        
            def test_wrong_taxonnomy(self):
                pass
        
            def test_taxonID_association_to_several_specimenIDs(self):
                pass
        
            def test_taxonID_map_to_correct_species_name(self):
                pass
        
            def test_taxonID(self):
                pass
        
            def test_date_in_correct_format(self):
                pass
        
            def test_occurrences_of_whole_organism(self):
                pass
        
            def test_alphanumeric_characters_used(self):
                #  Special characters and pipe (|) should not be used
                pass
            '''

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.driver.close()
        Sample().get_collection_handle().remove({"profile_id": str(cls.pid)})
        Profile().get_collection_handle().remove({"_id": cls.pid})

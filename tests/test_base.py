# Created by AProvidence on 27-05-2022

from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from htmlvalidator.client import ValidatingClient
from faker import Faker
from password_generator import PasswordGenerator
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Ensure that the “copodev” django server is running before running selenium tests
# Run this command before running the selenium tests:
# $ supervisord -c celery.conf && supervisorctl -c celery.conf start all
# To execute the Django’s test suite: $ python manage.py test



class BaseTest(TestCase):
    # setUp method and tearDown method are ran before and after each testcase respectively
    """ Set up fake/mock data for the TestCase in the "test_copo" database"""
    def setUp(self):
        super().setUp()
        settings.UNIT_TESTING = True
        fake = Faker()

        """ User and Profile """

        self.loggedin_client = ValidatingClient()
        self.not_loggedin_client = ValidatingClient()

        # Create a user model object and save it in the "test_copo" temporary PostgreSQL database
        self.user = User.objects.create_user(username=fake.first_name().lower(),
                                             first_name=fake.first_name(),
                                             last_name=fake.last_name(), email=fake.free_email,
                                             password=PasswordGenerator().generate())
        # Create an admin user model object
        self.superuser = User.objects.create_superuser(username=fake.first_name().lower(),
                                                       first_name=fake.first_name(),
                                                       last_name=fake.last_name(), email=fake.company_email(),
                                                       password=PasswordGenerator().generate())

        # Create an ASG profile on the COPO website
        asg_profile = {"copo_id": "000000002", "description": "ASG Test Description", "user_id": self.user.id,
                       "type": "Aquatic Symbiosis Genomics (ASG)", "title": "ASG Test Title"}

        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": self.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}

        # Create a ERGA profile on the COPO website
        erga_profile = {"copo_id": "000000001", "description": "ERGA Test Description", "user_id": self.user.id,
                        "type": "European Reference Genome Atlas (ERGA)", "title": "ERGA Test Title"}

        self.user.save()
        self.superuser.save()
        self.asg_pid = Profile().get_collection_handle().insert(asg_profile)
        self.dtol_pid = Profile().get_collection_handle().insert(dtol_profile)
        self.erga_pid = Profile().get_collection_handle().insert(erga_profile)

        self.loggedin_client.login(username=self.user.username, password=PasswordGenerator().generate())

        """" URLs declaration """
        self._define_urls()

        """" Rest URLs declaration"""
        self._define_rest_urls()

    def tearDown(self):
        # Clean up after each test by removing the objects stored in the "test_copo" database
        User.objects.get(username=self.user.username).delete()
        User.objects.get(username=self.superuser.username).delete()
        Profile().get_collection_handle().remove({"copo_id": "000000000"})
        Profile().get_collection_handle().remove({"copo_id": "000000001"})
        Profile().get_collection_handle().remove({"copo_id": "000000002"})
        self.webdriver.close()
        super().tearDown()

    def _define_urls(self):
        # app name: web_copo
        # pattern name: index
        # reverse('web_copo:index')

        self.admin_url = reverse('admin:index')
        self.about_url = reverse('about')
        self.people_url = reverse('people')
        self.dtol_url = reverse('dtol')
        self.news_url = reverse('news')
        self.manifests_url = reverse('manifests')
        self.ebp_url = reverse('ebp')
        # copo_url = reverse('copo')
        self.index_url = reverse('web_copo:index')
        self.landing_url = reverse('index')
        self.accept_reject_sample_url = reverse('web_copo:accept_reject')
        self.dataverse_submit_url = reverse('web_copo:test_dataverse_submit')
        # self.test_submission_url = reverse('web_copo:test_submission')
        self.stats_url = reverse('web_copo:stats')
        self.login_url = reverse('web_copo:auth')
        self.logout_url = reverse('web_copo:logout')
        self.register_url = reverse('web_copo:register')
        self.get_profile_counts_url = reverse('web_copo:update_counts')
        self.view_user_info_url = reverse('web_copo:view_user_info')
        self.error_url = reverse('web_copo:error_page')
        self.register_to_irods_url = reverse('web_copo:register_to_irods')
        # self.author_template_url = reverse('web_copo:author_template')
        self.forms_url = reverse('web_copo:copo_forms')
        self.delete_profile_url = reverse('web_copo:delete_profile')
        self.visualize_url = reverse('web_copo:copo_visualize')
        self.authenticate_figshare_url = reverse('web_copo:authenticate_figshare')
        self.publish_figshare_url = reverse('web_copo:publish_figshare')
        self.view_oauth_tokens_url = reverse('web_copo:view_oauth_tokens')
        self.get_tokens_for_user_url = reverse('web_copo:get_tokens_for_user')
        self.delete_token_url = reverse('web_copo:delete_token')
        self.get_annotation_url = reverse('web_copo:annotate_data')
        self.agave_oauth_url = reverse('web_copo:agave_oauth')
        self.import_ena_accession_url = reverse('web_copo:import_ena_accession')

        self.groups_url = reverse('web_copo:groups')
        self.create_group_url = reverse('web_copo:create_group')
        self.delete_group_url = reverse('web_copo:delete_group')
        self.add_profile_to_group_url = reverse('web_copo:add_profile_to_group')
        self.remove_profile_from_group_url = reverse('web_copo:remove_profile_from_group')
        self.get_profiles_in_group_url = reverse('web_copo:get_profiles_in_group')

        self.get_users_in_group_url = reverse('web_copo:add_users_in_group')
        self.add_user_to_group_url = reverse('web_copo:add_user_to_group')
        self.remove_user_from_group_url = reverse('web_copo:remove_user_from_group')
        self.administer_repos_url = reverse('web_copo:administer_repos')
        self.manage_repos_url = reverse('web_copo:manage_repos')
        self.manage_repositories_url = reverse('web_copo:manage_repositories')
        self.repositories_url = reverse('web_copo:copo_repositories')
        self.create_new_repo_url = reverse('web_copo:create_new_repo')
        self.get_repos_data_url = reverse('web_copo:get_repos_data')
        self.add_user_to_repo_url = reverse('web_copo:add_user_to_repo')
        self.assign_repo_users_url = reverse('web_copo:assign_repo_users')

        self.deassign_repo_users_url = reverse('web_copo:deassign_repo_users')
        self.remove_user_from_repo_url = reverse('web_copo:remove_user_from_repo')
        self.get_users_in_repo_url = reverse('web_copo:get_users_in_repo')
        self.get_users_repo_users_url = reverse('web_copo:get_users_repo_users')
        self.get_repos_for_user_url = reverse('web_copo:get_repos_for_user')
        self.add_repo_to_group_url = reverse('web_copo:add_repo_to_group')
        self.remove_repo_from_group_url = reverse('web_copo:remove_repo_from_group')
        self.get_repo_info_url = reverse('web_copo:get_repo_info')
        self.get_dspace_communities_url = reverse('web_copo:get_dspace_communities')
        self.retrieve_dspace_objects_url = reverse('web_copo:retrieve_dspace_objects')
        self.get_dspace_items_url = reverse('web_copo:get_dspace_items')
        self.get_dataverse_url = reverse('web_copo:get_dataverse')
        self.get_dataverse_vf_url = reverse('web_copo:search_dataverse_vf')
        self.get_dataverse_content_vf_url = reverse('web_copo:get_dataverse_content_vf')
        self.ckan_package_search_url = reverse('web_copo:ckan_package_search')
        self.get_collection_url = reverse('web_copo:get_dspace_collections')
        self.get_dataverse_content_url = reverse('web_copo:get_dataverse_content')
        self.get_info_for_new_dataverse_url = reverse('web_copo:get_info_for_new_dataverse')
        self.update_submission_repo_data_url = reverse('web_copo:update_submission_repo_data')
        self.set_destination_repository_url = reverse('web_copo:set_destination_repository')

        self.update_submission_meta_url = reverse('web_copo:update_submission_meta')
        self.dataverse_publish_url = reverse('web_copo:publish_dataverse')
        self.get_existing_metadata_url = reverse('web_copo:get_dspace_item_metadata')
        self.get_submission_metadata_url = reverse('web_copo:get_submission_metadata')
        self.get_ckan_items_url = reverse('web_copo:get_ckan_items')
        self.delete_repo_entry_url = reverse('web_copo:delete_repo_entry')
        self.refresh_annotation_display_url = reverse('web_copo:refresh_annotation_display')
        self.send_file_annotation_url = reverse('web_copo:send_file_annotation')
        self.refresh_annotations_url = reverse('web_copo:refresh_annotations')
        self.refresh_text_annotations_url = reverse('web_copo:refresh_text_annotations')
        self.delete_annotation_url = reverse('web_copo:delete_annotation')
        self.refresh_annotations_for_user_url = reverse('web_copo:refresh_annotations_for_user')
        self.get_dataset_info_url = reverse('web_copo:get_dataset_info')
        self.annotations_url = reverse('web_copo:new_text_annotation')
        self.search_url = reverse('web_copo:new_text_annotation')
        # self.annotations/<str:id>' = reverse('web_copo:delete_text_annotation')
        self.update_metadata_template_name_url = reverse('web_copo:update_metadata_template_name')
        self.new_metadata_template_url = reverse('web_copo:new_metadata_template')
        self.update_template_url = reverse('web_copo:update_template')
        self.load_metadata_template_terms_url = reverse('web_copo:load_metadata_template_terms')
        self.get_wizard_types_url = reverse('web_copo:get_wizard_types')
        self.export_template_url = reverse('web_copo:export_template')
        self.view_my_repos_url = reverse('web_copo:view_my_repos')
        self.add_personal_dataverse_url = reverse('web_copo:add_personal_dataverse')
        self.get_personal_dataverses_url = reverse('web_copo:get_personal_dataverses')
        self.delete_personal_dataverse_url = reverse('web_copo:delete_personal_dataverse')

        self.get_primer_fields_url = reverse('web_copo:get_primer_fields')
        self.add_primer_fields_url = reverse('web_copo:add_primer_fields')
        self.automate_num_cols_url = reverse('web_copo:automate_num_cols')
        self.term_lookup_url = reverse('web_copo:term_lookup')
        self.resolve_taxon_id_url = reverse('web_copo:resolve_taxon_id')
        self.search_species_url = reverse('web_copo:search_species')
        self.get_subsample_stages_url = reverse('web_copo:get_subsample_stages')
        self.sample_spreadsheet_url = reverse('web_copo:sample_spreadsheet')
        self.sample_images_url = reverse('web_copo:sample_images')
        self.create_spreadsheet_samples_url = reverse('web_copo:create_spreadsheet_samples')
        self.update_spreadsheet_samples_url = reverse('web_copo:update_spreadsheet_samples')
        self.update_pending_samples_table_url = reverse('web_copo:update_pending_samples_table')
        self.get_samples_for_profile_url = reverse('web_copo:get_samples_for_profile')
        self.mark_sample_rejected_url = reverse('web_copo:mark_sample_rejected')
        self.add_sample_to_dtol_submission_url = reverse('web_copo:add_sample_to_dtol_submission')
        self.delete_dtol_samples_url = reverse('web_copo:delete_dtol_samples')
        self.handle_csv_column_update_spreadsheet_url = reverse('web_copo:handle_csv_column_update_spreadsheet')
        self.handle_csv_column_validate_spreadsheet_url = reverse('web_copo:handle_csv_column_validate_spreadsheet')
        self.handle_csv_column_update_samples_url = reverse('web_copo:handle_csv_column_update_samples')

    def _define_rest_urls(self):
        # app name: rest
        # pattern name: data_wiz
        # reverse('rest:data_wiz')
        self.data_wiz_url = reverse('rest:data_wiz')
        self.sample_wiz_url = reverse('rest:sample_wiz')
        self.receive_data_file_url = reverse('rest:receive_data_file')
        self.receive_data_file_chunked_url = reverse('rest:receive_data_file')
        self.complete_upload_url = reverse('rest:complete_data_file')
        self.hash_upload_url = reverse('rest:hash_upload')
        self.inspect_file_url = reverse('rest:inspect_file')
        self.zip_file_url = reverse('rest:zip_file')
        self.check_figshare_credentials_url = reverse('rest:check_figshare_credentials')
        self.set_figshare_credentials_url = reverse('rest:set_figshare_credentials')
        self.small_file_upload_url = reverse('rest:receive_data_file')
        self.forward_to_figshare_url = reverse('rest:forward_to_figshare')
        self.get_upload_information_url = reverse('rest:get_upload_information')
        self.get_submission_status_url = reverse('rest:get_submission_status')
        self.release_ena_study_url = reverse('rest:release_ena_study')
        self.resume_chunked_url = reverse('rest:resume_chunked')
        self.get_partial_uploads_url = reverse('rest:get_partial_uploads')
        self.save_ss_annotation_url = reverse('rest:save_ss_annotation')
        self.delete_ss_annotation_url = reverse('rest:delete_ss_annotation')
        self.copo_get_submission_table_data_url = reverse('rest:get_submissions')
        self.get_accession_data_url = reverse('rest:get_accession_data')
        self.set_session_variable_url = reverse('rest:set_session_variable')
        self.test_sword_url = reverse('rest:test_module')
        self.call_get_dataset_details_url = reverse('rest:call_get_dataset_details')
        self.samples_from_study_url = reverse('rest:get_samples_for_study')
        self.get_users_url = reverse('rest:get_users')
        self.get_ontologies_url = reverse('rest:get_ontologies')
        self.export_generic_annotation_url = reverse('rest:export_generic_annotation')


class SeleniumBaseTest(LiveServerTestCase):
    """ Selenium test setup"""

    @classmethod
    def setUpClass(cls):
        super(SeleniumBaseTest, cls).setUpClass()
        options = Options()
        options.headless = False
        cls.webdriver = webdriver.Firefox(options=options)
        cls.host = "http://127.0.0.1:8000"

        """ URL declaration"""
        cls.index_url = reverse('web_copo:index')
        cls.login_url = reverse('web_copo:auth')
        cls.logout_url = reverse('web_copo:logout')

    @classmethod
    def tearDownClass(cls):
        cls.webdriver.close()
        super().tearDownClass()

# Created by AProvidence on 29-03-2022
from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from htmlvalidator.client import ValidatingClient


# Ensure that the "copodev" django server is running before running this test
# Run this command before running the tests: $ supervisord -c celery.conf && supervisorctl -c celery.conf start all


class UrlsTest(TestCase):
    # Test urls
    """ If urlpattern includes:
        "name='<url-name>'", then, url= reverse('<url-name>'
        "namespace='<url-name>'", then, url= reverse('<url-name>'
    """

    # To view all urls that the Django app uses: $ python manage.py show_urls
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True
        cls.client = ValidatingClient()
        cls.fake = Faker()

        """" Admin URL declaration """
        cls.admin_login_url = reverse('admin:login')
        cls.admin_password_change_url = reverse('admin:password_change')
        cls.admin_password_change_done_url = reverse('admin:password_change_done')
        cls.admin_sites_site_changelist_url = reverse('admin:sites_site_changelist')
        cls.admin_sites_site_change_url = reverse('admin:sites_site_change', args=[1])
        cls.admin_sites_site_add_url = reverse('admin:sites_site_add')
        cls.admin_socialaccount_socialaccount_changelist_url = reverse('admin:socialaccount_socialaccount_changelist')
        cls.admin_socialaccount_socialapp_changelist_url = reverse('admin:socialaccount_socialapp_changelist')
        cls.admin_web_copo_banner_view_changelist_url = reverse('admin:web_copo_banner_view_changelist')

        """ Accounts URL declaration """
        cls.account_login_url = reverse('account_login')
        cls.account_set_password_url = reverse('account_set_password')
        cls.account_signup_url = reverse('account_signup')
        cls.socialaccount_signup_url = reverse('socialaccount_signup')

        """ COPO URL declaration """
        cls.copo_index_url = reverse('web_copo:index')
        cls.copo_add_personal_dataverse_url = reverse('web_copo:add_personal_dataverse')
        cls.copo_add_primer_fields_url = reverse('web_copo:add_primer_fields')
        cls.copo_accept_reject_sample_url = reverse('web_copo:accept_reject')

    # @classmethod
    # def tearDownClass(cls):
    #     User.delete(username=cls.admin_username)
    #     User.delete(username=cls.username)

    def set_accounts_urls(self):
        account_email_verification_sent_url = reverse('account_email_verification_sent')
        account_email_url = reverse('account_email')
        account_inactive_url = reverse('account_inactive')
        account_logout_url = reverse('account_logout')
        orcid_callback_url = reverse('orcid_callback')
        account_change_password_url = reverse('account_change_password')
        account_reset_password_url = reverse('account_reset_password')
        account_reset_password_done_url = reverse('account_reset_password_done')
        account_reset_password_from_key_done_url = reverse('account_reset_password_from_key_done')
        socialaccount_connections_url = reverse('socialaccount_connections')
        socialaccount_login_cancelled_url = reverse('socialaccount_login_cancelled')
        socialaccount_login_error_url = reverse('socialaccount_login_error')

        # Get a list of strings of the accounts urls
        accounts_urls_list = [
            account_email_verification_sent_url,
            account_email_url,
            account_inactive_url,
            self.account_login_url,
            account_logout_url,
            orcid_callback_url,
            account_change_password_url,
            account_reset_password_url,
            account_reset_password_done_url,
            account_reset_password_from_key_done_url,
            self.account_set_password_url,
            self.account_signup_url,
            socialaccount_connections_url,
            socialaccount_login_cancelled_url,
            socialaccount_login_error_url,
            self.socialaccount_signup_url
        ]

        return accounts_urls_list

    def set_copo_urls(self):
        # app name: web_copo
        # pattern name: index
        # reverse('web_copo:index')

        copo_add_profile_to_group_url = reverse('web_copo:add_profile_to_group')
        copo_add_repo_to_group_url = reverse('web_copo:add_repo_to_group')
        copo_add_sample_to_dtol_submission_url = reverse('web_copo:add_sample_to_dtol_submission')
        copo_add_user_to_group_url = reverse('web_copo:add_user_to_group')
        copo_add_user_to_repo_url = reverse('web_copo:add_user_to_repo')
        copo_administer_repos_url = reverse('web_copo:administer_repos')
        copo_agave_oauth_url = reverse('web_copo:agave_oauth')
        copo_ajax_search_copo_local_999_url = reverse('web_copo:ajax_search_copo_local', args=['999'])
        copo_ajax_search_copo_local_sample_type_options_url = reverse('web_copo:ajax_search_copo_local',
                                                                      args=['sample_type_options'])
        copo_ajax_search_copo_local_repository_options_url = reverse('web_copo:ajax_search_copo_local',
                                                                     args=['repository_options'])
        copo_ajax_search_copo_local_repository_types_list_url = reverse('web_copo:ajax_search_copo_local',
                                                                        args=['repository_types_list'])
        copo_ajax_search_ontology_999_url = reverse('web_copo:ajax_search_ontology', args=["999"])
        copo_ajax_search_ontology_ncbitaxon_url = reverse('web_copo:ajax_search_ontology', args=["ncbitaxon"])
        copo_annotate_meta_url = reverse('web_copo:annotate_meta', args=['999'])
        copo_annotations_url = reverse('web_copo:new_text_annotation')
        # copo_annotations_delete_url = reverse('web_copo:delete_text_annotation', args=[])
        copo_assign_repo_users_url = reverse('web_copo:assign_repo_users')
        copo_authenticate_figshare_url = reverse('web_copo:authenticate_figshare')
        # copo_author_template_url = reverse('web_copo:author_template', args=[])
        copo_automate_num_cols_url = reverse('web_copo:automate_num_cols')
        copo_ckan_package_search_url = reverse('web_copo:ckan_package_search')

        copo_forms_url = reverse('web_copo:copo_forms')

        copo_repositories_url = reverse('web_copo:copo_repositories')

        copo_visualize_url = reverse('web_copo:copo_visualize')
        copo_create_group_url = reverse('web_copo:create_group')
        copo_create_new_repo_url = reverse('web_copo:create_new_repo')
        copo_create_spreadsheet_samples_url = reverse('web_copo:create_spreadsheet_samples')
        copo_dataverse_publish_url = reverse('web_copo:publish_dataverse')
        copo_dataverse_submit = reverse('web_copo:test_dataverse_submit')
        copo_deassign_repo_users_url = reverse('web_copo:deassign_repo_users')
        copo_delete_annotation_url = reverse('web_copo:delete_annotation')
        copo_delete_dtol_samples_url = reverse('web_copo:delete_dtol_samples')
        copo_delete_group_url = reverse('web_copo:delete_group')
        copo_delete_personal_dataverse_url = reverse('web_copo:delete_personal_dataverse')
        copo_delete_profile_url = reverse('web_copo:delete_profile')
        copo_delete_repo_entry_url = reverse('web_copo:delete_repo_entry')
        copo_delete_token_url = reverse('web_copo:delete_token')
        copo_error_url = reverse('web_copo:error_page')
        copo_export_template_url = reverse('web_copo:export_template')
        copo_get_annotation_url = reverse('web_copo:annotate_data')
        copo_get_ckan_items_url = reverse('web_copo:get_ckan_items')
        copo_get_collection_url = reverse('web_copo:get_dspace_collections')
        copo_get_dataset_info_url = reverse('web_copo:get_dataset_info')
        copo_get_dataverse_url = reverse('web_copo:get_dataverse')
        copo_get_dataverse_content_url = reverse('web_copo:get_dataverse_content')
        copo_get_dataverse_content_vf_url = reverse('web_copo:get_dataverse_content_vf')
        copo_get_dataverse_vf_url = reverse('web_copo:search_dataverse_vf')
        copo_get_dspace_communities_url = reverse('web_copo:get_dspace_communities')
        copo_get_dspace_items_url = reverse('web_copo:get_dspace_items')
        copo_get_existing_metadata_url = reverse('web_copo:get_dspace_item_metadata')
        copo_get_info_for_new_dataverse_url = reverse('web_copo:get_info_for_new_dataverse')
        copo_get_personal_dataverses_url = reverse('web_copo:get_personal_dataverses')
        copo_get_primer_fields_url = reverse('web_copo:get_primer_fields')
        copo_get_profiles_in_group_url = reverse('web_copo:get_profiles_in_group')
        copo_get_repo_info_url = reverse('web_copo:get_repo_info')
        copo_get_repos_data_url = reverse('web_copo:get_repos_data')
        copo_get_repos_for_user_url = reverse('web_copo:get_repos_for_user')
        copo_get_samples_for_profile_url = reverse('web_copo:get_samples_for_profile')
        copo_get_source_count_url = reverse('web_copo:get_source_count')
        copo_get_submission_metadata_url = reverse('web_copo:get_submission_metadata')
        copo_get_subsample_stages_url = reverse('web_copo:get_subsample_stages')
        copo_get_tokens_for_user_url = reverse('web_copo:get_tokens_for_user')
        copo_get_users_in_group_url = reverse('web_copo:add_users_in_group')
        copo_get_users_in_repo_url = reverse('web_copo:get_users_in_repo')
        copo_get_users_repo_users_url = reverse('web_copo:get_users_repo_users')
        copo_get_wizard_types_url = reverse('web_copo:get_wizard_types')
        copo_groups_url = reverse('web_copo:groups')
        copo_handle_csv_column_update_samples_url = reverse('web_copo:handle_csv_column_update_samples')
        copo_handle_csv_column_update_spreadsheet_url = reverse('web_copo:handle_csv_column_update_spreadsheet')
        copo_handle_csv_column_validate_spreadsheet_url = reverse('web_copo:handle_csv_column_validate_spreadsheet')
        copo_import_ena_accession_url = reverse('web_copo:import_ena_accession')
        copo_load_metadata_template_terms_url = reverse('web_copo:load_metadata_template_terms')
        copo_login_url = reverse('web_copo:auth')
        copo_logout_url = reverse('web_copo:logout')
        copo_manage_repos_url = reverse('web_copo:manage_repos')
        copo_manage_repositories_url = reverse('web_copo:manage_repositories')
        copo_mark_sample_rejected_url = reverse('web_copo:mark_sample_rejected')
        copo_new_metadata_template_url = reverse('web_copo:new_metadata_template')
        copo_profile_counts_url = reverse('web_copo:update_counts')
        copo_publish_figshare_url = reverse('web_copo:publish_figshare')
        copo_refresh_annotation_display_url = reverse('web_copo:refresh_annotation_display')
        copo_refresh_annotations_url = reverse('web_copo:refresh_annotations')
        copo_refresh_annotations_for_user_url = reverse('web_copo:refresh_annotations_for_user')
        copo_refresh_text_annotations_url = reverse('web_copo:refresh_text_annotations')
        copo_register_url = reverse('web_copo:register')
        copo_register_to_irods_url = reverse('web_copo:register_to_irods')
        copo_remove_profile_from_group_url = reverse('web_copo:remove_profile_from_group')
        copo_remove_repo_from_group_url = reverse('web_copo:remove_repo_from_group')
        copo_remove_user_from_group_url = reverse('web_copo:remove_user_from_group')
        copo_remove_user_from_repo_url = reverse('web_copo:remove_user_from_repo')
        # copo_resolve_url = reverse('web_copo:resolve_submission_id', args=[])
        copo_resolve_taxon_id_url = reverse('web_copo:resolve_taxon_id')
        copo_retrieve_dspace_objects_url = reverse('web_copo:retrieve_dspace_objects')
        copo_sample_images_url = reverse('web_copo:sample_images')
        copo_sample_spreadsheet_url = reverse('web_copo:sample_spreadsheet')
        copo_search_url = reverse('web_copo:new_text_annotation')
        copo_search_species_url = reverse('web_copo:search_species')
        copo_send_file_annotation_url = reverse('web_copo:send_file_annotation')
        copo_set_destination_repository_url = reverse('web_copo:set_destination_repository')
        copo_stats_url = reverse('web_copo:stats')
        copo_stats_timeseries_url = reverse('web_copo:stats', args=['timeseries'])
        copo_stats_variable_histogram_url = reverse('web_copo:stats', args=['variable_histogram'])
        copo_term_lookup_url = reverse('web_copo:term_lookup')
        copo_update_metadata_template_name_url = reverse('web_copo:update_metadata_template_name')
        copo_update_pending_samples_table_url = reverse('web_copo:update_pending_samples_table')
        copo_update_spreadsheet_samples_url = reverse('web_copo:update_spreadsheet_samples')
        copo_update_submission_meta_url = reverse('web_copo:update_submission_meta')
        copo_update_submission_repo_data_url = reverse('web_copo:update_submission_repo_data')
        copo_update_template_url = reverse('web_copo:update_template')
        copo_view_my_repos_url = reverse('web_copo:view_my_repos')
        copo_view_oauth_tokens_url = reverse('web_copo:view_oauth_tokens')

        copo_view_user_info_url = reverse('web_copo:view_user_info')

        # Get a list of strings of the copo urls
        copo_urls_list = [
            self.copo_index_url,
            self.copo_accept_reject_sample_url,
            copo_add_profile_to_group_url,
            copo_add_repo_to_group_url,
            copo_add_sample_to_dtol_submission_url,
            copo_add_user_to_group_url,
            copo_add_user_to_repo_url,
            copo_administer_repos_url,
            copo_agave_oauth_url,
            copo_ajax_search_copo_local_999_url,
            copo_ajax_search_copo_local_sample_type_options_url,
            copo_ajax_search_copo_local_repository_options_url,
            copo_ajax_search_copo_local_repository_types_list_url,
            copo_ajax_search_ontology_999_url,
            copo_ajax_search_ontology_ncbitaxon_url,
            copo_annotate_meta_url,
            copo_annotations_url,
            copo_assign_repo_users_url,
            copo_authenticate_figshare_url,
            copo_automate_num_cols_url,
            copo_ckan_package_search_url,
            copo_forms_url,
            copo_repositories_url,
            copo_visualize_url,
            copo_create_group_url,
            copo_create_new_repo_url,
            copo_create_spreadsheet_samples_url,
            copo_dataverse_publish_url,
            copo_dataverse_submit,
            copo_deassign_repo_users_url,
            copo_delete_annotation_url,
            copo_delete_dtol_samples_url,
            copo_delete_group_url,
            copo_delete_personal_dataverse_url,
            copo_delete_profile_url,
            copo_delete_repo_entry_url,
            copo_delete_token_url,
            copo_error_url,
            copo_export_template_url,
            copo_get_annotation_url,
            copo_get_ckan_items_url,
            copo_get_collection_url,
            copo_get_dataset_info_url,
            copo_get_dataverse_url,
            copo_get_dataverse_content_url,
            copo_get_dataverse_content_vf_url,
            copo_get_dataverse_vf_url,
            copo_get_dspace_communities_url,
            copo_get_dspace_items_url,
            copo_get_existing_metadata_url,
            copo_get_info_for_new_dataverse_url,
            copo_get_personal_dataverses_url,
            copo_get_primer_fields_url,
            copo_get_profiles_in_group_url,
            copo_get_repo_info_url,
            copo_get_repos_data_url,
            copo_get_repos_for_user_url,
            copo_get_samples_for_profile_url,
            copo_get_source_count_url,
            copo_get_submission_metadata_url,
            copo_get_subsample_stages_url,
            copo_get_tokens_for_user_url,
            copo_get_users_in_group_url,
            copo_get_users_in_repo_url,
            copo_get_users_repo_users_url,
            copo_get_wizard_types_url,
            copo_groups_url,
            copo_handle_csv_column_update_samples_url,
            copo_handle_csv_column_update_spreadsheet_url,
            copo_handle_csv_column_validate_spreadsheet_url,
            copo_import_ena_accession_url,
            copo_load_metadata_template_terms_url,
            copo_login_url,
            copo_logout_url,
            copo_manage_repos_url,
            copo_manage_repositories_url,
            copo_mark_sample_rejected_url,
            copo_new_metadata_template_url,
            copo_profile_counts_url,
            copo_publish_figshare_url,
            copo_refresh_annotation_display_url,
            copo_refresh_annotations_url,
            copo_refresh_annotations_for_user_url,
            copo_refresh_text_annotations_url,
            copo_register_url,
            copo_register_to_irods_url,
            copo_remove_profile_from_group_url,
            copo_remove_repo_from_group_url,
            copo_remove_user_from_group_url,
            copo_remove_user_from_repo_url,
            copo_resolve_taxon_id_url,
            copo_retrieve_dspace_objects_url,
            copo_sample_images_url,
            copo_sample_spreadsheet_url,
            copo_search_url,
            copo_search_species_url,
            copo_send_file_annotation_url,
            copo_set_destination_repository_url,
            copo_stats_url,
            copo_stats_timeseries_url,
            copo_stats_variable_histogram_url,
            copo_term_lookup_url,
            copo_update_metadata_template_name_url,
            copo_update_pending_samples_table_url,
            copo_update_spreadsheet_samples_url,
            copo_update_submission_meta_url,
            copo_update_submission_repo_data_url,
            copo_update_template_url,
            copo_view_my_repos_url,
            copo_view_oauth_tokens_url,
            copo_view_user_info_url
        ]

        return copo_urls_list

    def create_user(self):
        self.username = self.fake.first_name().lower()
        self.user_password = User.objects.make_random_password()
        self.user = User.objects.create_user(username=self.username,
                                             first_name=self.fake.first_name(),
                                             last_name=self.fake.last_name(),
                                             email=self.fake.free_email(),
                                             password=self.user_password)
        self.user.save()

    """
    def create_user_profile(self):
        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": self.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}

        self.user_pid = Profile().get_collection_handle().insert(dtol_profile)
    """
    """ To run only this test:  
        $ python manage.py test tests.unit_testing.test_urls.UrlsTest.test_admin_urls 
    """

    def test_accounts_urls(self):
        """ Test the urls for "accounts" """
        print('Accounts URLs test')
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        accounts_webpages = self.set_accounts_urls()

        for webpage in accounts_webpages:
            response = self.client.get(webpage)
            if webpage == self.account_login_url or webpage == self.account_set_password_url or webpage == self.account_signup_url or webpage == self.socialaccount_signup_url:
                self.assertEqual(response.status_code, 302)
            else:
                self.assertEqual(response.status_code, 200)

    def test_api_urls(self):
        pass

    def test_about_url_exists(self):
        """ Test the url for "about" """
        print("About URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        about_url = reverse('about')
        response = self.client.get(about_url)
        self.assertEqual(response.status_code, 200)

    def test_copo_urls(self):
        """Test the urls for "copo" """
        print('COPO URLs test')
        self.create_user()
        # self.create_user_profile()

        group_ids = set()
        dtol_test_group, created = Group.objects.get_or_create(name='dtol_users')
        erga_test_group, created = Group.objects.get_or_create(name='erga_users')
        group_ids.add(dtol_test_group.id)
        group_ids.add(erga_test_group.id)

        print(group_ids)

        self.assertNotIn(dtol_test_group, self.user.groups.all())
        self.assertNotIn(erga_test_group, self.user.groups.all())
        self.user.groups.add(dtol_test_group)
        self.user.groups.add(erga_test_group)

        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": self.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}
        self.user_pid = Profile().get_collection_handle().insert(dtol_profile)

        copo_data_url = reverse('web_copo:copo_data', args=[self.user_pid])
        copo_people_url = reverse('web_copo:copo_people', args=[self.user_pid])
        copo_profile_url = reverse('web_copo:view_copo_profile', args=[self.user_pid])
        copo_publications_url = reverse('web_copo:copo_publications', args=[self.user_pid])
        copo_repository_url = reverse('web_copo:copo_repository', args=[self.user_pid])
        copo_samples_url = reverse('web_copo:copo_samples', args=[self.user_pid])
        copo_submissions_url = reverse('web_copo:copo_submissions', args=[self.user_pid])
        copo_view_templates_url = reverse('web_copo:view_templates', args=[self.user_pid])

        copo_webpages = self.set_copo_urls()
        copo_webpages.extend([copo_data_url, copo_people_url, copo_profile_url, copo_publications_url,
                              copo_repository_url, copo_samples_url, copo_submissions_url, copo_view_templates_url])

        # self.assertTemplateUsed(response, 'copo/auth/login.html')
        # print(self.client.get(reverse('web_copo:index')).status_code)

        for webpage in copo_webpages:
            response = self.client.get(webpage)
            # self.client.login(username=self.username, password=self.user_password)
            # if webpage == self.copo_index_url or webpage == self.copo_add_personal_dataverse_url or webpage == self.copo_add_primer_fields_url or webpage == self.copo_accept_reject_sample_url:
            #     print("302 status: ", webpage)
            #     self.assertEqual(response.status_code, 302, response)
            #     # self.client.login(username=self.username, password=self.user_password)
            #     # print("200 status: ", webpage)
            #     # self.assertEqual(response.status_code, 200, response)
            #
            # else:
            #     print("200 status: ", webpage)
            #     self.assertEqual(response.status_code, 200, response)
            self.assertEqual(response.status_code, 302, response)
            print(f"{response.status_code}: ", webpage)

    def test_rest_urls(self):
        pass

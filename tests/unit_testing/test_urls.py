# Created by AProvidence on 29-03-2022
from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from htmlvalidator.client import ValidatingClient


class UrlsTest(TestCase):
    """ Test urls """

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
        # Create a user
        cls.username = cls.fake.first_name().lower()
        cls.user_password = User.objects.make_random_password()
        cls.user = User.objects.create_user(username=cls.username,
                                            first_name=cls.fake.first_name(),
                                            last_name=cls.fake.last_name(),
                                            email=cls.fake.free_email(),
                                            password=cls.user_password)
        cls.user.save()

        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": cls.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}

        cls.user_pid = Profile().get_collection_handle().insert(dtol_profile)

    """ If urlpattern includes:
        "name='<url-name>'", then, url= reverse('<url-name>'
        "namespace='<url-name>'", then, url= reverse('<url-name>'
        """

    # python manage.py test tests.unit_testing.test_urls.UrlsTest.test_admin_urls

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

    def set_admin_urls(self):
        # app name: admin
        # pattern name: index
        # reverse('admin:index')

        admin_index_url = reverse('admin:index')
        admin_account_emailaddress_changelist_url = reverse('admin:account_emailaddress_changelist')
        admin_account_emailaddress_add_url = reverse('admin:account_emailaddress_add')
        admin_auth_group_changelist_url = reverse('admin:auth_group_changelist')
        admin_auth_group_add_url = reverse('admin:auth_group_add')
        admin_auth_user_changelist_url = reverse('admin:auth_user_changelist')
        admin_auth_user_password_change_url = reverse('admin:auth_user_password_change', args=[1])
        admin_auth_user_change_url = reverse('admin:auth_user_change', args=[1])
        admin_auth_user_add_url = reverse('admin:auth_user_add')
        admin_chunked_upload_chunkedupload_changelist_url = reverse('admin:chunked_upload_chunkedupload_changelist')
        admin_chunked_upload_chunkedupload_add_url = reverse('admin:chunked_upload_chunkedupload_add')
        admin_jsi18n_url = reverse('admin:jsi18n')
        admin_logout_url = reverse('admin:logout')

        # Get a list of strings of the admin urls
        admin_urls_list = [
            admin_index_url,
            admin_account_emailaddress_changelist_url,
            admin_account_emailaddress_add_url,
            admin_auth_group_changelist_url,
            admin_auth_group_add_url,
            admin_auth_user_changelist_url,
            admin_auth_user_password_change_url,
            admin_auth_user_change_url,
            admin_auth_user_add_url,
            admin_chunked_upload_chunkedupload_changelist_url,
            admin_chunked_upload_chunkedupload_add_url,
            admin_jsi18n_url,
            self.admin_login_url,
            admin_logout_url,
            self.admin_password_change_url,
            self.admin_password_change_done_url,
            self.admin_sites_site_changelist_url,
            self.admin_sites_site_change_url,
            self.admin_sites_site_add_url,
            self.admin_socialaccount_socialaccount_changelist_url,
            self.admin_socialaccount_socialapp_changelist_url,
            self.admin_web_copo_banner_view_changelist_url,
        ]

        return admin_urls_list

    def set_copo_urls(self):
        # app name: web_copo
        # pattern name: index
        # reverse('web_copo:index')

        copo_index_url = reverse('web_copo:index')
        copo_accept_reject_sample_url = reverse('web_copo:accept_reject')
        copo_add_personal_dataverse_url = reverse('web_copo:add_personal_dataverse')
        copo_add_primer_fields_url = reverse('web_copo:add_primer_fields')
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
        copo_data_url = reverse('web_copo:copo_data', args=[self.user_pid])
        copo_forms_url = reverse('web_copo:copo_forms')
        copo_people_url = reverse('web_copo:copo_people', args=[self.user_pid])
        copo_profile_url = reverse('web_copo:view_copo_profile', args=[self.user_pid])
        copo_publications_url = reverse('web_copo:copo_publications', args=[self.user_pid])
        copo_repositories_url = reverse('web_copo:copo_repositories')
        copo_repository_url = reverse('web_copo:copo_repository', args=[self.user_pid])
        copo_samples_url = reverse('web_copo:copo_samples', args=[self.user_pid])
        copo_submissions_url = reverse('web_copo:copo_submissions', args=[self.user_pid])
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
        copo_view_templates_url = reverse('web_copo:view_templates', args=[self.user_pid])
        copo_view_user_info_url = reverse('web_copo:view_user_info')

        # Get a list of strings of the copo urls
        copo_urls_list = [
            copo_index_url,
            copo_accept_reject_sample_url,
            copo_add_personal_dataverse_url,
            copo_add_primer_fields_url,
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
            copo_data_url,
            copo_forms_url,
            copo_people_url,
            copo_profile_url,
            copo_publications_url,
            copo_repositories_url,
            copo_repository_url,
            copo_samples_url,
            copo_submissions_url,
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
            copo_view_templates_url,
            copo_view_user_info_url
        ]

        return copo_urls_list

    def create_admin_user(self):
        self.admin_username = self.fake.first_name().lower()
        self.admin_password = User.objects.make_random_password()
        self.admin_user = User.objects.create_superuser(username=self.admin_username,
                                                        first_name=self.fake.first_name(),
                                                        last_name=self.fake.last_name(),
                                                        email=self.fake.company_email(),
                                                        password=self.admin_password)
        self.admin_user.save()

    #
    # def create_user(self):
    #     self.username = self.fake.first_name().lower()
    #     self.user_password = User.objects.make_random_password()
    #     self.user = User.objects.create_user(username=self.username,
    #                                          first_name=self.fake.first_name(),
    #                                          last_name=self.fake.last_name(),
    #                                          email=self.fake.free_email(),
    #                                          password=self.user_password)
    #     self.user.save()
    #
    # def create_user_profile(self):
    #     # Create a DTOL profile on the COPO website
    #     dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": self.user.id,
    #                     "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}
    #
    #     self.user_pid = Profile().get_collection_handle().insert(dtol_profile)

    """ To run only this test:  
        $ python manage.py test tests.unit_testing.test_urls.UrlsTest.test_admin_urls 
    """

    def test_admin_urls(self):
        """Test the urls for "admin" """
        print('Admin URLs test')
        self.create_admin_user()
        self.client.login(username=self.admin_username, password=self.admin_password)
        admin_webpages = self.set_admin_urls()
        # self.assertTemplateUsed(response, 'copo/auth/login.html')

        for webpage in admin_webpages:
            response = self.client.get(webpage)
            if webpage == self.admin_login_url or webpage == self.admin_password_change_url \
                    or webpage == self.admin_password_change_done_url \
                    or webpage == self.admin_sites_site_changelist_url or webpage == self.admin_sites_site_change_url \
                    or webpage == self.admin_sites_site_add_url \
                    or webpage == self.admin_socialaccount_socialaccount_changelist_url \
                    or webpage == self.admin_socialaccount_socialapp_changelist_url \
                    or webpage == self.admin_web_copo_banner_view_changelist_url:
                self.assertEqual(response.status_code, 302)
            else:
                self.assertEqual(response.status_code, 200)

    def test_admin_change_view_loads_normally(self):
        print('Test change view url loads normally')
        self.create_admin_user()
        test_group = Group.objects.create(name='Test Group')
        admin_change_view_url = reverse(
            'admin:{}_{}_change'.format(
                test_group._meta.app_label,
                type(test_group).__name__.lower()
            ),
            args=(test_group.pk,)
        )
        self.client.login(username=self.admin_username, password=self.admin_password)
        change_view_response = self.client.get(admin_change_view_url)
        self.assertEqual(change_view_response.status_code, 200)

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

    def test_copo_urls(self):
        """Test the urls for "copo" """
        print('COPO URLs test')
        # self.create_user()
        # self.create_user_profile()
        self.client.login(username=self.username, password=self.user_password)
        copo_webpages = self.set_copo_urls()
        # self.assertTemplateUsed(response, 'copo/auth/login.html')

        for webpage in copo_webpages:
            response = self.client.get(webpage)
            # if webpage == self.admin_login_url or webpage == self.admin_password_change_url \
            #         or webpage == self.admin_password_change_done_url \
            #         or webpage == self.admin_sites_site_changelist_url or webpage == self.admin_sites_site_change_url \
            #         or webpage == self.admin_sites_site_add_url \
            #         or webpage == self.admin_socialaccount_socialaccount_changelist_url \
            #         or webpage == self.admin_socialaccount_socialapp_changelist_url \
            #         or webpage == self.admin_web_copo_banner_view_changelist_url:
            #     print("302 status: ", webpage)
            #     self.assertEqual(response.status_code, 302, response)
            # else:
            print("200 status: ", webpage)
            self.assertEqual(response.status_code, 200, response)

    def test_rest_urls(self):
        pass

    def test_index_url_is_correct(self):
        """ Test the url for "index" """
        print("Index URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        index_url = reverse('web_copo:index')
        response = self.client.get(index_url)
        self.assertEqual(response.status_code, 200)

    def test_landing_url_is_correct(self):
        """ Test the url for "landing" """
        print("Landing URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        landing_url = reverse('index')
        response = self.client.get(landing_url)
        self.assertEqual(response.status_code, 200)

        # self.assertEqual(self.index_url, '/copo/')

    def test_resolve_to_about_url(self):
        """ Test the url for "about" """
        print("About URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        about_url = reverse('about')
        response = self.client.get(about_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_dtol_url(self):
        """ Test the url for "dtol" """
        print("DTOL URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        dtol_url = reverse('dtol')
        response = self.client.get(dtol_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_ebp_url(self):
        """ Test the url for "ebp" """
        print("Ebp test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        ebp_url = reverse('ebp')
        response = self.client.get(ebp_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_manifests_url(self):
        """ Test the url for "manifests" """
        print("Manifests URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        manifests_url = reverse('manifests')
        response = self.client.get(manifests_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_news_url(self):
        """ Test the url for "news" """
        print("News URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        news_url = reverse('news')
        response = self.client.get(news_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_people_url(self):
        """ Test the url for "people" """
        print("People URL test")
        self.create_user()
        self.client.login(username=self.username, password=self.user_password)
        people_url = reverse('people')
        response = self.client.get(people_url)
        self.assertEqual(response.status_code, 200)

    def test_accept_reject_sample_url_is_correct(self):
        self.assertEqual(self.accept_reject_sample_url, '/copo/accept_reject_sample/')

    def test_dataverse_submit_url_is_correct(self):
        self.assertEqual(self.dataverse_submit_url, '/copo/dataverse_submit/')

    # path('stats/<str:view>', '/stats, name='stats')
    def test_status_url_is_correct(self):
        self.assertEqual(self.stats_url, '/copo/stats/')

    def test_login_url_is_correct(self):
        self.assertEqual(self.login_url, '/copo/login/')

    def test_logout_url_is_correct(self):
        self.assertEqual(self.logout_url, '/copo/logout/')

    def test_register_url_is_correct(self):
        self.assertEqual(self.register_url, '/copo/register/')

    def test_get_profile_counts_url_is_correct(self):
        self.assertEqual(self.get_profile_counts_url, '/copo/profile/update_counts/')

    def test_view_user_info_url_is_correct(self):
        self.assertEqual(self.view_user_info_url, '/copo/view_user_info/')

    def test_error_url_is_correct(self):
        self.assertEqual(self.error_url, '/copo/error/')

    def test_register_to_irods_url_is_correct(self):
        self.assertEqual(self.register_to_irods_url, '/copo/register_to_irods/')

    # path('author_template/<template_id>/view', '/author_template, name='author_template')

    def test_forms_url_is_correct(self):
        self.assertEqual(self.forms_url, '/copo/copo_forms/')

    def test_delete_profile_url_is_correct(self):
        self.assertEqual(self.delete_profile_url, '/copo/delete_profile/')

    def test_visualize__url_is_correct(self):
        self.assertEqual(self.visualize_url, '/copo/copo_visualize/')

    def test_authenticate_figshare_url_is_correct(self):
        self.assertEqual(self.authenticate_figshare_url, '/copo/authenticate_figshare/')

    def test_view_oauth_tokens_url_is_correct(self):
        self.assertEqual(self.view_oauth_tokens_url, '/copo/view_oauth_tokens/')

    def test_get_annotation_url_is_correct(self):
        self.assertEqual(self.get_annotation_url, '/copo/get_annotation/')

    def test_agave_oauth_url_is_correct(self):
        self.assertEqual(self.agave_oauth_url, '/copo/agave_oauth/')

    def test_import_ena_accession_url_is_correct(self):
        self.assertEqual(self.import_ena_accession_url, '/copo/import_ena_accession/')

    def test_groups_url_is_correct(self):
        self.assertEqual(self.groups_url, '/copo/groups/')

    def test_administer_repos_url_is_correct(self):
        self.assertEqual(self.administer_repos_url, '/copo/administer_repos/')

    def test_manage_repos_url_is_correct(self):
        self.assertEqual(self.manage_repos_url, '/copo/manage_repos/')

    def test_manage_repositories_url_is_correct(self):
        self.assertEqual(self.manage_repositories_url, '/copo/manage_repositories/')

    def test_repositories_url_is_correct(self):
        self.assertEqual(self.repositories_url, '/copo/copo_repositories/')

    def test_view_my_repos_url_is_correct(self):
        self.assertEqual(self.view_my_repos_url, '/copo/view_my_repos/')

    """ Test ajax handlers urls """

    def test_publish_figshare_url_is_correct(self):
        self.assertEqual(self.publish_figshare_url, '/copo/publish_figshare/')

    def test_get_tokens_for_user_url_is_correct(self):
        self.assertEqual(self.get_tokens_for_user_url, '/copo/get_tokens_for_user/')

    def test_delete_token_url_is_correct(self):
        self.assertEqual(self.delete_token_url, '/copo/delete_token/')

    def test_create_group_url_is_correct(self):
        self.assertEqual(self.create_group_url, '/copo/create_group/')

    def test_delete_group_url_is_correct(self):
        self.assertEqual(self.delete_group_url, '/copo/delete_group/')

    def test_add_profile_to_group_is_correct(self):
        self.assertEqual(self.add_profile_to_group_url, '/copo/add_profile_to_group/')

    def test_remove_profile_from_group_url_is_correct(self):
        self.assertEqual(self.remove_profile_from_group_url, '/copo/remove_profile_from_group/')

    def test_get_profiles_in_group_url_is_correct(self):
        self.assertEqual(self.get_profiles_in_group_url, '/copo/get_profiles_in_group/')

    def test_get_users_in_group_url_is_correct(self):
        self.assertEqual(self.get_users_in_group_url, '/copo/get_users_in_group/')

    def test_add_user_to_group_url_is_correct(self):
        self.assertEqual(self.add_user_to_group_url, '/copo/add_user_to_group/')

    def test_remove_user_from_group_url_is_correct(self):
        self.assertEqual(self.remove_user_from_group_url, '/copo/remove_user_from_group/')

    def test_create_new_repo_url_is_correct(self):
        self.assertEqual(self.create_new_repo_url, '/copo/create_new_repo/')

    def test_get_repos_data_url_is_correct(self):
        self.assertEqual(self.get_repos_data_url, '/copo/get_repos_data/')

    def test_add_user_to_repo_url_is_correct(self):
        self.assertEqual(self.add_user_to_repo_url, '/copo/add_user_to_repo/')

    def test_assign_repo_users_url_is_correct(self):
        self.assertEqual(self.assign_repo_users_url, '/copo/assign_repo_users/')

    def test_deassign_repo_users_url_is_correct(self):
        self.assertEqual(self.deassign_repo_users_url, '/copo/deassign_repo_users/')

    def test_remove_user_from_repo_url_is_correct(self):
        self.assertEqual(self.remove_user_from_repo_url, '/copo/remove_user_from_repo/')

    def test_get_users_in_repo_url_is_correct(self):
        self.assertEqual(self.get_users_in_repo_url, '/copo/get_users_in_repo/')

    def test_get_users_repo_users_url_is_correct(self):
        self.assertEqual(self.get_users_repo_users_url, '/copo/get_users_repo_users/')

    def test_get_repos_for_user_url_is_correct(self):
        self.assertEqual(self.get_repos_for_user_url, '/copo/get_repos_for_user/')

    def test_add_repo_to_group_url_is_correct(self):
        self.assertEqual(self.add_repo_to_group_url, '/copo/add_repo_to_group/')

    def test_remove_repo_from_group_url_is_correct(self):
        self.assertEqual(self.remove_repo_from_group_url, '/copo/remove_repo_from_group/')

    def test_get_repo_info_url_is_correct(self):
        self.assertEqual(self.get_repo_info_url, '/copo/get_repo_info/')

    def test_get_dspace_communities_url_is_correct(self):
        self.assertEqual(self.get_dspace_communities_url, '/copo/get_dspace_communities/')

    def test_retrieve_dspace_objects_url_is_correct(self):
        self.assertEqual(self.retrieve_dspace_objects_url, '/copo/retrieve_dspace_objects/')

    def test_get_dspace_items_url_is_correct(self):
        self.assertEqual(self.get_dspace_items_url, '/copo/get_dspace_items/')

    def test_get_dataverse_url_is_correct(self):
        self.assertEqual(self.get_dataverse_url, '/copo/get_dataverse/')

    def test_get_dataverse_vf_url_is_correct(self):
        self.assertEqual(self.get_dataverse_vf_url, '/copo/get_dataverse_vf/')

    def test_get_dataverse_content_vf_url_is_correct(self):
        self.assertEqual(self.get_dataverse_content_vf_url, '/copo/get_dataverse_content_vf/')

    def test_ckan_package_search_url_is_correct(self):
        self.assertEqual(self.ckan_package_search_url, '/copo/ckan_package_search/')

    def test_get_collection_url_is_correct(self):
        self.assertEqual(self.get_collection_url, '/copo/get_collection/')

    def test_get_dataverse_content_url_is_correct(self):
        self.assertEqual(self.get_dataverse_content_url, '/copo/get_dataverse_content/')

    def test_get_info_for_new_dataverse_url_is_correct(self):
        self.assertEqual(self.get_info_for_new_dataverse_url,
                         '/copo/get_info_for_new_dataverse/')

    def test_update_submission_repo_data_url_is_correct(self):
        self.assertEqual(self.update_submission_repo_data_url,
                         '/copo/update_submission_repo_data/')

    def test_set_destination_repository_url_is_correct(self):
        self.assertEqual(self.set_destination_repository_url,
                         '/copo/set_destination_repository/')

    def test_update_submission_meta_url_is_correct(self):
        self.assertEqual(self.update_submission_meta_url, '/copo/update_submission_meta/')

    def test_dataverse_publish_url_is_correct(self):
        self.assertEqual(self.dataverse_publish_url, '/copo/dataverse_publish/')

    def test_get_existing_metadata_url_is_correct(self):
        self.assertEqual(self.get_existing_metadata_url, '/copo/get_existing_metadata/')

    def test_get_submission_metadata_url_is_correct(self):
        self.assertEqual(self.get_submission_metadata_url, '/copo/get_submission_metadata/')

    def test_get_ckan_items_url_is_correct(self):
        self.assertEqual(self.get_ckan_items_url, '/copo/get_ckan_items/')

    def test_delete_repo_entry_url_is_correct(self):
        self.assertEqual(self.delete_repo_entry_url, '/copo/delete_repo_entry/')

    def test_get_dataset_info_url_is_correct(self):
        self.assertEqual(self.get_dataset_info_url, '/copo/get_dataset_info/')

    def test_add_personal_dataverse_url_is_correct(self):
        self.assertEqual(self.add_personal_dataverse_url, '/copo/add_personal_dataverse/')

    def test_get_personal_dataverse_url_is_correct(self):
        self.assertEqual(self.get_personal_dataverses_url, '/copo/get_personal_dataverses/')

    def test_delete_personal_dataverse_url_is_correct(self):
        self.assertEqual(self.delete_personal_dataverse_url, '/copo/delete_personal_dataverse/')

    def test_get_subsample_stages_url_is_correct(self):
        self.assertEqual(self.get_subsample_stages_url, '/copo/get_subsample_stages/')

    def test_sample_spreadsheet_url_is_correct(self):
        self.assertEqual(self.sample_spreadsheet_url, '/copo/sample_spreadsheet/')

    def test_sample_images_url_is_correct(self):
        self.assertEqual(self.sample_images_url, '/copo/sample_images/')

    def test_create_spreadsheet_samples_url_is_correct(self):
        self.assertEqual(self.create_spreadsheet_samples_url,
                         '/copo/create_spreadsheet_samples/')

    def test_update_spreadsheet_samples_url_is_correct(self):
        self.assertEqual(self.update_spreadsheet_samples_url,
                         '/copo/update_spreadsheet_samples/')

    def test_update_pending_samples_table_url_is_correct(self):
        self.assertEqual(self.update_pending_samples_table_url,
                         '/copo/update_pending_samples_table/')

    def test_get_samples_for_profile_url_is_correct(self):
        self.assertEqual(self.get_samples_for_profile_url, '/copo/get_samples_for_profile/')

    def test_mark_sample_rejected_url_is_correct(self):
        self.assertEqual(self.mark_sample_rejected_url, '/copo/mark_sample_rejected/')

    def test_add_sample_to_dtol_submission_url_is_correct(self):
        self.assertEqual(self.add_sample_to_dtol_submission_url,
                         '/copo/add_sample_to_dtol_submission/')

    def test_delete_dtol_samples_url_is_correct(self):
        self.assertEqual(self.delete_dtol_samples_url, '/copo/delete_dtol_samples/')

    def test_handle_csv_column_validate_spreadsheet_url_is_correct(self):
        self.assertEqual(self.handle_csv_column_validate_spreadsheet_url,
                         '/copo/handle_csv_column_validate_spreadsheet/')

    def test_handle_csv_column_update_samples_url_is_correct(self):
        self.assertEqual(self.handle_csv_column_update_samples_url,
                         '/copo/handle_csv_column_update_samples/')

    """ Test annotation handlers urls """

    def test_refresh_annotation_display_url_is_correct(self):
        self.assertEqual(self.refresh_annotation_display_url, '/copo/refresh_annotation_display/')

    def test_send_file_annotation_url_is_correct(self):
        self.assertEqual(self.send_file_annotation_url, '/copo/send_file_annotation/')

    def test_refresh_annotations_url_is_correct(self):
        self.assertEqual(self.refresh_annotations_url, '/copo/refresh_annotations/')

    def test_refresh_text_annotations_url_is_correct(self):
        self.assertEqual(self.refresh_text_annotations_url,
                         '/copo/refresh_text_annotations/')

    def test_delete_annotation_url_is_correct(self):
        self.assertEqual(self.delete_annotation_url, '/copo/delete_annotation/')

    def test_refresh_annotations_for_user_url_is_correct(self):
        self.assertEqual(self.refresh_annotations_for_user_url,
                         '/copo/refresh_annotations_for_user/')

    def test_annotations_url_is_correct(self):
        self.assertNotEquals(self.annotations_url, '/copo/new_text_annotation/')

    def test_search_url_is_correct(self):
        self.assertEqual(self.search_url, '/copo/search')

    # def test_delete_text_annotation_url_is_correct(self):
    # self.assertEqual(self.update_metadata_template_name_url,
    # /copo/edit_or_delete_text_annotation')
    def test_automate_num_cols_url_is_correct(self):
        self.assertEqual(self.automate_num_cols_url, '/copo/automate_num_cols/')

    def test_term_lookup_url_is_correct(self):
        self.assertEqual(self.term_lookup_url, '/copo/term_lookup/')

    def test_resolve_taxon_id_url_is_correct(self):
        self.assertEqual(self.resolve_taxon_id_url, '/copo/resolve_taxon_id/')

    def test_search_species_url_is_correct(self):
        self.assertEqual(self.search_species_url, '/copo/search_species/')
        """Test template handlers urls"""

    def test_update_metadata_template_name_url_is_correct(self):
        self.assertEqual(self.update_metadata_template_name_url,
                         '/copo/update_metadata_template_name/')

    def test_new_metadata_template_url_is_correct(self):
        self.assertEqual(self.new_metadata_template_url, '/copo/new_metadata_template/')

    def test_update_template_url_is_correct(self):
        self.assertEqual(self.update_template_url, '/copo/update_template/')

    def test_load_metadata_template_terms_url_is_correct(self):
        self.assertEqual(self.load_metadata_template_terms_url,
                         '/copo/load_metadata_template_terms/')

    def test_get_wizard_types_url_is_correct(self):
        self.assertEqual(self.get_wizard_types_url, '/copo/get_wizard_types/')

    def test_export_template_url_is_correct(self):
        self.assertEqual(self.export_template_url, '/copo/export_template/')

    def test_get_primer_fields_url_is_correct(self):
        self.assertEqual(self.get_primer_fields_url, '/copo/get_primer_fields/')

    def test_add_primer_fields_url_is_correct(self):
        self.assertEqual(self.add_primer_fields_url, '/copo/add_primer_fields/')

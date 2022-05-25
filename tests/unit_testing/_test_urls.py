# Created by AProvidence on 29-03-2022
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from web.urls import urlpatterns as app_urls


class UrlsTest(TestCase):
    """ Test urls """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True

        # app name: web_copo
        # pattern name: index
        # reverse('web_copo:index')

        cls.admin_url = reverse('admin:index')
        cls.about_url = reverse('about')
        cls.people_url = reverse('people')
        cls.dtol_url = reverse('dtol')
        cls.news_url = reverse('news')
        cls.manifests_url = reverse('manifests')
        cls.ebp_url = reverse('ebp')
        # copo_url = reverse('copo')
        cls.index_url = reverse('web_copo:index')
        cls.landing_url = reverse('index')
        cls.accept_reject_sample_url = reverse('web_copo:accept_reject')
        cls.dataverse_submit_url = reverse('web_copo:test_dataverse_submit')
        # cls.test_submission_url = reverse('web_copo:test_submission')
        cls.stats_url = reverse('web_copo:stats')
        cls.login_url = reverse('web_copo:auth')
        cls.logout_url = reverse('web_copo:logout')
        cls.register_url = reverse('web_copo:register')
        cls.get_profile_counts_url = reverse('web_copo:update_counts')
        cls.view_user_info_url = reverse('web_copo:view_user_info')
        cls.error_url = reverse('web_copo:error_page')
        cls.register_to_irods_url = reverse('web_copo:register_to_irods')
        # cls.author_template_url = reverse('web_copo:author_template')
        cls.forms_url = reverse('web_copo:copo_forms')
        cls.delete_profile_url = reverse('web_copo:delete_profile')
        cls.visualize_url = reverse('web_copo:copo_visualize')
        cls.authenticate_figshare_url = reverse('web_copo:authenticate_figshare')
        cls.publish_figshare_url = reverse('web_copo:publish_figshare')
        cls.view_oauth_tokens_url = reverse('web_copo:view_oauth_tokens')
        cls.get_tokens_for_user_url = reverse('web_copo:get_tokens_for_user')
        cls.delete_token_url = reverse('web_copo:delete_token')
        cls.get_annotation_url = reverse('web_copo:annotate_data')
        cls.agave_oauth_url = reverse('web_copo:agave_oauth')
        cls.import_ena_accession_url = reverse('web_copo:import_ena_accession')

        cls.groups_url = reverse('web_copo:groups')
        cls.create_group_url = reverse('web_copo:create_group')
        cls.delete_group_url = reverse('web_copo:delete_group')
        cls.add_profile_to_group_url = reverse('web_copo:add_profile_to_group')
        cls.remove_profile_from_group_url = reverse('web_copo:remove_profile_from_group')
        cls.get_profiles_in_group_url = reverse('web_copo:get_profiles_in_group')

        cls.get_users_in_group_url = reverse('web_copo:add_users_in_group')
        cls.add_user_to_group_url = reverse('web_copo:add_user_to_group')
        cls.remove_user_from_group_url = reverse('web_copo:remove_user_from_group')
        cls.administer_repos_url = reverse('web_copo:administer_repos')
        cls.manage_repos_url = reverse('web_copo:manage_repos')
        cls.manage_repositories_url = reverse('web_copo:manage_repositories')
        cls.repositories_url = reverse('web_copo:copo_repositories')
        cls.create_new_repo_url = reverse('web_copo:create_new_repo')
        cls.get_repos_data_url = reverse('web_copo:get_repos_data')
        cls.add_user_to_repo_url = reverse('web_copo:add_user_to_repo')
        cls.assign_repo_users_url = reverse('web_copo:assign_repo_users')

        cls.deassign_repo_users_url = reverse('web_copo:deassign_repo_users')
        cls.remove_user_from_repo_url = reverse('web_copo:remove_user_from_repo')
        cls.get_users_in_repo_url = reverse('web_copo:get_users_in_repo')
        cls.get_users_repo_users_url = reverse('web_copo:get_users_repo_users')
        cls.get_repos_for_user_url = reverse('web_copo:get_repos_for_user')
        cls.add_repo_to_group_url = reverse('web_copo:add_repo_to_group')
        cls.remove_repo_from_group_url = reverse('web_copo:remove_repo_from_group')
        cls.get_repo_info_url = reverse('web_copo:get_repo_info')
        cls.get_dspace_communities_url = reverse('web_copo:get_dspace_communities')
        cls.retrieve_dspace_objects_url = reverse('web_copo:retrieve_dspace_objects')
        cls.get_dspace_items_url = reverse('web_copo:get_dspace_items')
        cls.get_dataverse_url = reverse('web_copo:get_dataverse')
        cls.get_dataverse_vf_url = reverse('web_copo:search_dataverse_vf')
        cls.get_dataverse_content_vf_url = reverse('web_copo:get_dataverse_content_vf')
        cls.ckan_package_search_url = reverse('web_copo:ckan_package_search')
        cls.get_collection_url = reverse('web_copo:get_dspace_collections')
        cls.get_dataverse_content_url = reverse('web_copo:get_dataverse_content')
        cls.get_info_for_new_dataverse_url = reverse('web_copo:get_info_for_new_dataverse')
        cls.update_submission_repo_data_url = reverse('web_copo:update_submission_repo_data')
        cls.set_destination_repository_url = reverse('web_copo:set_destination_repository')

        cls.update_submission_meta_url = reverse('web_copo:update_submission_meta')
        cls.dataverse_publish_url = reverse('web_copo:publish_dataverse')
        cls.get_existing_metadata_url = reverse('web_copo:get_dspace_item_metadata')
        cls.get_submission_metadata_url = reverse('web_copo:get_submission_metadata')
        cls.get_ckan_items_url = reverse('web_copo:get_ckan_items')
        cls.delete_repo_entry_url = reverse('web_copo:delete_repo_entry')
        cls.refresh_annotation_display_url = reverse('web_copo:refresh_annotation_display')
        cls.send_file_annotation_url = reverse('web_copo:send_file_annotation')
        cls.refresh_annotations_url = reverse('web_copo:refresh_annotations')
        cls.refresh_text_annotations_url = reverse('web_copo:refresh_text_annotations')
        cls.delete_annotation_url = reverse('web_copo:delete_annotation')
        cls.refresh_annotations_for_user_url = reverse('web_copo:refresh_annotations_for_user')
        cls.get_dataset_info_url = reverse('web_copo:get_dataset_info')
        cls.annotations_url = reverse('web_copo:new_text_annotation')
        cls.search_url = reverse('web_copo:new_text_annotation')
        # cls.annotations/<str:id>' = reverse('web_copo:delete_text_annotation')
        cls.update_metadata_template_name_url = reverse('web_copo:update_metadata_template_name')
        cls.new_metadata_template_url = reverse('web_copo:new_metadata_template')
        cls.update_template_url = reverse('web_copo:update_template')
        cls.load_metadata_template_terms_url = reverse('web_copo:load_metadata_template_terms')
        cls.get_wizard_types_url = reverse('web_copo:get_wizard_types')
        cls.export_template_url = reverse('web_copo:export_template')
        cls.view_my_repos_url = reverse('web_copo:view_my_repos')
        cls.add_personal_dataverse_url = reverse('web_copo:add_personal_dataverse')
        cls.get_personal_dataverses_url = reverse('web_copo:get_personal_dataverses')
        cls.delete_personal_dataverse_url = reverse('web_copo:delete_personal_dataverse')

        cls.get_primer_fields_url = reverse('web_copo:get_primer_fields')
        cls.add_primer_fields_url = reverse('web_copo:add_primer_fields')
        cls.automate_num_cols_url = reverse('web_copo:automate_num_cols')
        cls.term_lookup_url = reverse('web_copo:term_lookup')
        cls.resolve_taxon_id_url = reverse('web_copo:resolve_taxon_id')
        cls.search_species_url = reverse('web_copo:search_species')
        cls.get_subsample_stages_url = reverse('web_copo:get_subsample_stages')
        cls.sample_spreadsheet_url = reverse('web_copo:sample_spreadsheet')
        cls.sample_images_url = reverse('web_copo:sample_images')
        cls.create_spreadsheet_samples_url = reverse('web_copo:create_spreadsheet_samples')
        cls.update_spreadsheet_samples_url = reverse('web_copo:update_spreadsheet_samples')
        cls.update_pending_samples_table_url = reverse('web_copo:update_pending_samples_table')
        cls.get_samples_for_profile_url = reverse('web_copo:get_samples_for_profile')
        cls.mark_sample_rejected_url = reverse('web_copo:mark_sample_rejected')
        cls.add_sample_to_dtol_submission_url = reverse('web_copo:add_sample_to_dtol_submission')
        cls.delete_dtol_samples_url = reverse('web_copo:delete_dtol_samples')
        cls.handle_csv_column_update_spreadsheet_url = reverse('web_copo:handle_csv_column_update_spreadsheet')
        cls.handle_csv_column_validate_spreadsheet_url = reverse('web_copo:handle_csv_column_validate_spreadsheet')
        cls.handle_csv_column_update_samples_url = reverse('web_copo:handle_csv_column_update_samples')

    def test_admin_url_is_correct(self):
        self.assertEqual(self.admin_url, '/admin/')

    def test_index_url_is_correct(self):
        self.assertEqual(self.index_url, '/copo/')

    def test_landing_url_is_correct(self):
        self.assertEqual(self.landing_url, '/')
        self.assertTrue(app_urls[6].name, '')

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

    def test_resolve_to_about_url(self):
        """ Verifies that the about page loads properly"""
        print("Tests that the about page operates well")
        self.assertTrue(self.about_url, '/about/')

    def test_resolve_to_people_url(self):
        """ Verifies that the people page loads properly"""
        print("Tests that the people page operates well")
        self.assertTrue(self.people_url, '/people/')

    def test_resolve_to_dtol_url(self):
        """ Verifies that the dtol page loads properly"""
        print("Tests that the dtol page operates well")
        self.assertTrue(self.dtol_url, '/dtol/')

    def test_resolve_to_news_url(self):
        """ Verifies that the news page loads properly"""
        print("Tests that the news page operates well")
        self.assertTrue(self.news_url, '/news/')

    def test_resolve_to_manifests_url(self):
        """ Verifies that the manifests page loads properly"""
        print("Tests that the manifests page operates well")
        self.assertTrue(self.manifests_url, '/manifests/')

    def test_resolve_to_ebp_url(self):
        """ Verifies that the about page loads properly"""
        print("Tests that the ebp page operates well")
        self.assertTrue(self.ebp_url, '/ebp/')

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

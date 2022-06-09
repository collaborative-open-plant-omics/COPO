# Created by AProvidence on 29-03-2022
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from htmlvalidator.client import ValidatingClient
from web.urls import urlpatterns as app_urls


class UrlsTest(TestCase):
    """ Test urls """

    @classmethod
    def setUpTestData(cls):
        settings.UNIT_TESTING = True
        cls.client = ValidatingClient()
        cls.fake = Faker()

        """" URLs declaration """
        cls._define_urls(cls)

    """ If urlpattern includes:
        "name='<url-name>'", then, url= reverse('<url-name>'
        "namespace='<url-name>'", then, url= reverse('<url-name>'
        """

    # ['admin/(?P<app_label>sites|auth|web_copo|account|socialaccount|chunked_upload)/$']
    # View all urls that the Django app uses: $ python manage.py show_urls
    # python manage.py test tests.unit_testing.test_urls.UrlsTest.test_admin_urls

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
        # cls.test_submission_url = reverse('web_copo:test_submission')
        self.stats_url = reverse('web_copo:stats')
        self.stats_timeseries_url = reverse('web_copo:stats', args=["timeseries"])
        self.stats_variable_histogram_url = reverse('web_copo:stats', args=["variable_histogram"])
        self.login_url = reverse('web_copo:auth')
        self.logout_url = reverse('web_copo:logout')
        self.register_url = reverse('web_copo:register')
        self.get_profile_counts_url = reverse('web_copo:update_counts')
        self.view_user_info_url = reverse('web_copo:view_user_info')
        self.error_url = reverse('web_copo:error_page')
        self.register_to_irods_url = reverse('web_copo:register_to_irods')
        # cls.author_template_url = reverse('web_copo:author_template')
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
        # cls.annotations/<str:id>' = reverse('web_copo:delete_text_annotation')
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

    def create_admin_user(self):
        self.admin_username = self.fake.first_name().lower()
        self.admin_password = User.objects.make_random_password()
        self.user = User.objects.create_superuser(username=self.admin_username,
                                                  first_name=self.fake.first_name(),
                                                  last_name=self.fake.last_name(), email=self.fake.company_email(),
                                                  password=self.admin_password)
        self.user.save()

    def admin_urls(self):
        admin_index_url = reverse('admin:index')

        admin_account_emailaddress_changelist_url = reverse('admin:account_emailaddress_changelist')
        # admin_account_emailaddress_change_url = reverse('admin:account_emailaddress_change')
        # admin_account_emailaddress_delete_url = reverse('admin:account_emailaddress_delete')
        # admin_account_emailaddress_history_url = reverse('admin:account_emailaddress_history')
        admin_account_emailaddress_add_url = reverse('admin:account_emailaddress_add')

        admin_auth_group_changelist_url = reverse('admin:auth_group_changelist')
        # admin_auth_group_change_url1 = reverse('admin:auth_group_change', args=[1])
        # admin_auth_group_change_url2 = reverse('admin:auth_group_change', args=[2])
        # admin_auth_group_change_url3 = reverse('admin:auth_group_change', args=[3])
        # admin_auth_group_change_url4 = reverse('admin:auth_group_change', args=[4])
        # admin_auth_group_change_url5 = reverse('admin:auth_group_change', args=[5])
        # admin_auth_group_change_url6 = reverse('admin:auth_group_change', args=[6])
        # admin_auth_group_change_url7 = reverse('admin:auth_group_change', args=[7])
        # admin_auth_group_delete_url = reverse('admin:auth_group_delete')
        # admin_auth_group_history_url = reverse('admin:auth_group_history')
        admin_auth_group_add_url = reverse('admin:auth_group_add')

        admin_auth_user_changelist_url = reverse('admin:auth_user_changelist')
        admin_auth_user_password_change_url = reverse('admin:auth_user_password_change', args=[1])
        admin_auth_user_change_url = reverse('admin:auth_user_change', args=[1])
        # admin_auth_user_delete_url = reverse('admin:auth_user_delete')
        # admin_auth_user_history_url = reverse('admin:auth_user_history')
        admin_auth_user_add_url = reverse('admin:auth_user_add')
        # admin_auth_user_autocomplete_url = reverse('admin:auth_user_autocomplete')
        admin_chunked_upload_chunkedupload_changelist_url = reverse('admin:chunked_upload_chunkedupload_changelist')
        # admin_chunked_upload_chunkedupload_change_url = reverse('admin:chunked_upload_chunkedupload_change')
        # admin_chunked_upload_chunkedupload_delete_url = reverse('admin:chunked_upload_chunkedupload_delete')
        # admin_chunked_upload_chunkedupload_history_url = reverse('admin:chunked_upload_chunkedupload_history')
        admin_chunked_upload_chunkedupload_add_url = reverse('admin:chunked_upload_chunkedupload_add')

        admin_jsi18n_url = reverse('admin:jsi18n')
        admin_login_url = reverse('admin:login')
        admin_logout_url = reverse('admin:logout')
        admin_password_change_url = reverse('admin:password_change')
        admin_password_change_done_url = reverse('admin:password_change_done')
        admin_sites_site_changelist_url = reverse('admin:sites_site_changelist')
        admin_sites_site_change_url = reverse('admin:sites_site_change', args=[1])
        admin_sites_site_add_url = reverse('admin:sites_site_add')
        admin_socialaccount_socialaccount_changelist_url = reverse('admin:socialaccount_socialaccount_changelist')
        admin_socialaccount_socialapp_changelist_url = reverse('admin:socialaccount_socialapp_changelist')
        admin_web_copo_banner_view_changelist_url = reverse('admin:web_copo_banner_view_changelist')

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
            admin_login_url,
            admin_logout_url,
            admin_password_change_url,
            admin_password_change_done_url,
            admin_sites_site_changelist_url,
            admin_sites_site_change_url,
            admin_sites_site_add_url,
            admin_socialaccount_socialaccount_changelist_url,
            admin_socialaccount_socialapp_changelist_url,
            admin_web_copo_banner_view_changelist_url,
        ]

        return admin_urls_list

    def create_user(self):
        self.username = self.fake.first_name().lower()
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.user = user

    # Run only this test:  $ python manage.py test tests.unit_testing.test_urls.UrlsTest.test_admin_urls
    def test_admin_urls(self):
        """Test the urls for "admin" """
        print('Admin URLs test')
        # response = self.client.get(admin_url)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.admin_url, '/admin/')
        self.create_admin_user()
        self.client.login(username=self.admin_username, password=self.admin_password)
        admin_webpages = self.admin_urls()
        # self.assertTemplateUsed(response, 'copo/auth/login.html')

        for webpage in admin_webpages:
            response = self.client.get(webpage)
            print(webpage)
            if webpage != reverse('admin:login') and webpage != reverse('admin:password_change') and webpage != reverse('admin:password_change_done'):
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 302)

    def test_change_view_loads_normally(self):
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

    def test_index_url_is_correct(self):
        # self.client.login(username='john', password='johnpassword')
        index_url = reverse('web_copo:index')
        response = self.client.get(index_url)
        print(self.client)
        print(index_url)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.index_url, '/copo/')

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
        """ Test the url for "about" """
        print("About URL test")
        about_url = reverse('about')
        response = self.client.get(about_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_people_url(self):
        """ Test the url for "people" """
        print("People URL test")
        people_url = reverse('people')
        response = self.client.get(people_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_dtol_url(self):
        """ Test the url for "dtol" """
        print("DTOL URL test")
        dtol_url = reverse('dtol')
        response = self.client.get(dtol_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_news_url(self):
        """ Test the url for "news" """
        print("News URL test")
        news_url = reverse('news')
        response = self.client.get(news_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_manifests_url(self):
        """ Test the url for "manifests" """
        print("Manifests URL test")
        manifests_url = reverse('manifests')
        response = self.client.get(manifests_url)
        self.assertEqual(response.status_code, 200)

    def test_resolve_to_ebp_url(self):
        """ Test the url for "ebp" """
        print("Ebp test")
        ebp_url = reverse('ebp')
        response = self.client.get(ebp_url)
        self.assertEqual(response.status_code, 200)

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

# Created by AProvidence on 02-04-2022
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse, resolve
from web.apps.web_copo import views
from web.apps.web_copo.utils import ajax_handlers, annotation_handlers, template_handlers
from web.landing import views as landing_views
from web.urls import urlpatterns as app_urls
from django.views.generic import TemplateView


class ViewsTest(TestCase):
    # Main templates used: copo/error_page.html, copo/base_simple.html
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True

        cls.client = Client()
        cls.error_url = reverse('web_copo:error_page')
        cls.stats_url = reverse('web_copo:stats')

        cls.admin_url = reverse('admin:index')
        cls.about_url = reverse('about')
        cls.people_url = reverse('people')
        cls.dtol_url = reverse('dtol')
        cls.news_url = reverse('news')
        cls.manifests_url = reverse('manifests')
        cls.ebp_url = reverse('ebp')

        cls.about_resolver = resolve('/about/')
        cls.people_resolver = resolve('/people/')
        cls.dtol_resolver = resolve('/dtol/')
        cls.news_resolver = resolve('/news/')
        cls.manifests_resolver = resolve('/manifests/')
        cls.ebp_resolver = resolve('/ebp/')

        # cls.copo_url = reverse('copo')
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

    def test_index_page_loads_correctly(self):
        """ Verifies that the index page loads properly"""
        print("Tests the loading of index webpage")
        response = self.client.get(path=resolve('/'))
        response2 = self.client.get('web_copo:index')
        ip_server_response = self.client.get('127.0.0.1:8000')
        html = response.content.decode('utf8')
        # self.assertTrue(html.startswith('<!DOCTYPE html>'))
        # self.assertIn('<title>COPO - Collaborative Omics</title>', html)
        self.assertTrue(html.endswith('</html>'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ip_server_response.status_code, 200)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'index_new.html'
        self.assertTemplateUsed(response2, 'copo/base_simple.html')  # 'copo/index.html'
        self.assertEquals(resolve(reverse('web_copo:index')).func, views.index)

    def test_login_page(self):
        """ Verifies that the login page loads properly"""
        print("Tests that the login page loads well")
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'copo/auth/login.html')

    def test_stats_page(self):
        # time_series_view = stats()
        # response = self.client.get(self.login_url, args[])
        pass

    def test_error_page(self):
        """ Verifies that the error page loads properly"""
        print("Tests that the error page loads well")
        response = self.client.get(self.error_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(resolve(self.error_url).route, 'copo/error/')

    def test_admin_url_is_resolved(self):
        self.assertEqual(resolve(self.admin_url).namespace, "admin")
        self.assertEqual(resolve(self.admin_url).url_name, "index")
        self.assertEqual(resolve(self.admin_url).route, "admin/")
        self.assertEqual(resolve(self.admin_url).args, ())

    # def test_copo_url_is_resolved(self):
    #     self.assertEqual(resolve(self.copo_url).namespace, "admin")
    #     self.assertEqual(resolve(self.copo_url).url_name, "index")
    #     self.assertEqual(resolve(self.copo_url).route, "admin/")
    #     self.assertEqual(resolve(self.copo_url).args, ())

    def test_index_url_is_resolved(self):
        self.assertEqual(resolve(self.index_url).func, views.index)

    def test_landing_url_is_resolved(self):
        self.assertEqual(resolve(self.landing_url).func, landing_views.index)
        self.assertTrue(app_urls[6].name, '')

    def test_accept_reject_sample_url_is_resolved(self):
        self.assertEqual(resolve(self.accept_reject_sample_url).func, views.copo_sample_accept_reject)

    def test_dataverse_submit_url_is_resolved(self):
        self.assertEqual(resolve(self.dataverse_submit_url).func, views.test_dataverse_submit)

    # def test_test_submission_url_is_resolved(self):
    #     self.assertEqual(resolve(self.test_submission_url).func, views.test_submission)

    # path('stats/<str:view>', views.stats, name='stats')
    def test_status_url_is_resolved(self):
        self.assertEqual(resolve(self.stats_url).func, views.stats)


    def test_login_url_is_resolved(self):
        self.assertEqual(resolve(self.login_url).func, views.login)

    def test_logout_url_is_resolved(self):
        self.assertEqual(resolve(self.logout_url).func, views.copo_logout)

    def test_register_url_is_resolved(self):
        self.assertEqual(resolve(self.register_url).func, views.copo_register)

    def test_get_profile_counts_url_is_resolved(self):
        self.assertEqual(resolve(self.get_profile_counts_url).func, views.get_profile_counts)

    def test_view_user_info_url_is_resolved(self):
        self.assertEqual(resolve(self.view_user_info_url).func, views.view_user_info)

    def test_error_url_is_resolved(self):
        self.assertEqual(resolve(self.error_url).func, views.goto_error)

    def test_register_to_irods_url_is_resolved(self):
        self.assertEqual(resolve(self.register_to_irods_url).func, views.register_to_irods)

    # path('author_template/<template_id>/view', views.author_template, name='author_template')

    def test_forms_url_is_resolved(self):
        self.assertEqual(resolve(self.forms_url).func, views.copo_forms)

    def test_delete_profile_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_profile_url).func, views.delete_profile)

    def test_visualize__url_is_resolved(self):
        self.assertEqual(resolve(self.visualize_url).func, views.copo_visualize)

    def test_authenticate_figshare_url_is_resolved(self):
        self.assertEqual(resolve(self.authenticate_figshare_url).func, views.authenticate_figshare)

    def test_view_oauth_tokens_url_is_resolved(self):
        self.assertEqual(resolve(self.view_oauth_tokens_url).func, views.view_oauth_tokens)

    def test_get_annotation_url_is_resolved(self):
        self.assertEqual(resolve(self.get_annotation_url).func, views.annotate_data)

    def test_agave_oauth_url_is_resolved(self):
        self.assertEqual(resolve(self.agave_oauth_url).func, views.agave_oauth)

    def test_import_ena_accession_url_is_resolved(self):
        self.assertEqual(resolve(self.import_ena_accession_url).func, views.import_ena_accession)

    def test_groups_url_is_resolved(self):
        self.assertEqual(resolve(self.groups_url).func, views.view_groups)

    def test_administer_repos_url_is_resolved(self):
        self.assertEqual(resolve(self.administer_repos_url).func, views.administer_repos)

    def test_manage_repos_url_is_resolved(self):
        self.assertEqual(resolve(self.manage_repos_url).func, views.manage_repos)

    def test_manage_repositories_url_is_resolved(self):
        self.assertEqual(resolve(self.manage_repositories_url).func, views.manage_repositories)

    def test_repositories_url_is_resolved(self):
        self.assertEqual(resolve(self.repositories_url).func, views.copo_repositories)

    def test_view_my_repos_url_is_resolved(self):
        self.assertEqual(resolve(self.view_my_repos_url).func, views.copo_repositories)

    def test_resolve_to_about_url(self):
        """ Verifies that the about page loads properly"""
        print("Tests that the about page operates well")
        response = self.client.get(self.about_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'about.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.about_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.about_resolver.url_name, "about")
        self.assertEqual(self.about_resolver.route, "about/")
        self.assertTrue(self.about_url, '/about/')
        self.assertTrue(app_urls[7].name, self.about_resolver.url_name)

    def test_resolve_to_people_url(self):
        """ Verifies that the people page loads properly"""
        print("Tests that the people page operates well")
        response = self.client.get(self.people_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'people.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.people_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.people_resolver.url_name, "people")
        self.assertEqual(self.people_resolver.route, "people/")
        self.assertTrue(self.people_url, '/people/')
        self.assertTrue(app_urls[8].name, self.people_resolver.url_name)

    def test_resolve_to_dtol_url(self):
        """ Verifies that the dtol page loads properly"""
        print("Tests that the dtol page operates well")
        response = self.client.get(self.dtol_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'dtol.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.dtol_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.dtol_resolver.url_name, "dtol")
        self.assertEqual(self.dtol_resolver.route, "dtol/")
        self.assertTrue(self.dtol_url, '/dtol/')
        self.assertTrue(app_urls[9].name, self.dtol_resolver.url_name)

    def test_resolve_to_news_url(self):
        """ Verifies that the news page loads properly"""
        print("Tests that the news page operates well")
        response = self.client.get(self.news_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'news.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.news_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.news_resolver.url_name, "news")
        self.assertEqual(self.news_resolver.route, "news/")
        self.assertTrue(self.news_url, '/news/')
        self.assertTrue(app_urls[10].name, self.news_resolver.url_name)

    def test_resolve_to_manifests_url(self):
        """ Verifies that the manifests page loads properly"""
        print("Tests that the manifests page operates well")
        response = self.client.get(self.manifests_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'manifests.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.manifests_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.manifests_resolver.url_name, "manifests")
        self.assertEqual(self.manifests_resolver.route, "manifests/")
        self.assertTrue(self.manifests_url, '/manifests/')
        self.assertTrue(app_urls[11].name, self.manifests_resolver.url_name)

    def test_resolve_to_ebp_url(self):
        """ Verifies that the about page loads properly"""
        print("Tests that the ebp page operates well")
        response = self.client.get(self.ebp_resolver.route)
        self.assertTemplateUsed(response, 'copo/base_simple.html')  # 'ebp_resources.html'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ebp_resolver.func.__name__, TemplateView.as_view().__name__)
        self.assertEqual(self.ebp_resolver.url_name, "ebp")
        self.assertEqual(self.ebp_resolver.route, "ebp/")
        self.assertTrue(self.ebp_url, '/ebp/')
        self.assertTrue(app_urls[12].name, self.ebp_resolver.url_name)

    """ Test ajax handlers urls """

    def test_publish_figshare_url_is_resolved(self):
        self.assertEqual(resolve(self.publish_figshare_url).func, ajax_handlers.publish_figshare)

    def test_get_tokens_for_user_url_is_resolved(self):
        self.assertEqual(resolve(self.get_tokens_for_user_url).func, ajax_handlers.get_tokens_for_user)

    def test_delete_token_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_token_url).func, ajax_handlers.delete_token)

    def test_create_group_url_is_resolved(self):
        self.assertEqual(resolve(self.create_group_url).func, ajax_handlers.create_group)

    def test_delete_group_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_group_url).func, ajax_handlers.delete_group)

    def test_add_profile_to_group_is_resolved(self):
        self.assertEqual(resolve(self.add_profile_to_group_url).func, ajax_handlers.add_profile_to_group)

    def test_remove_profile_from_group_url_is_resolved(self):
        self.assertEqual(resolve(self.remove_profile_from_group_url).func, ajax_handlers.remove_profile_from_group)

    def test_get_profiles_in_group_url_is_resolved(self):
        self.assertEqual(resolve(self.get_profiles_in_group_url).func, ajax_handlers.get_profiles_in_group)

    def test_get_users_in_group_url_is_resolved(self):
        self.assertEqual(resolve(self.get_users_in_group_url).func, ajax_handlers.get_users_in_group)

    def test_add_user_to_group_url_is_resolved(self):
        self.assertEqual(resolve(self.add_user_to_group_url).func, ajax_handlers.add_user_to_group)

    def test_remove_user_from_group_url_is_resolved(self):
        self.assertEqual(resolve(self.remove_user_from_group_url).func, ajax_handlers.remove_user_from_group)

    def test_create_new_repo_url_is_resolved(self):
        self.assertEqual(resolve(self.create_new_repo_url).func, ajax_handlers.create_new_repo)

    def test_get_repos_data_url_is_resolved(self):
        self.assertEqual(resolve(self.get_repos_data_url).func, ajax_handlers.get_repos_data)

    def test_add_user_to_repo_url_is_resolved(self):
        self.assertEqual(resolve(self.add_user_to_repo_url).func, ajax_handlers.add_user_to_repo)

    def test_assign_repo_users_url_is_resolved(self):
        self.assertEqual(resolve(self.assign_repo_users_url).func, ajax_handlers.assign_repo_users)

    def test_deassign_repo_users_url_is_resolved(self):
        self.assertEqual(resolve(self.deassign_repo_users_url).func, ajax_handlers.deassign_repo_users)

    def test_remove_user_from_repo_url_is_resolved(self):
        self.assertEqual(resolve(self.remove_user_from_repo_url).func, ajax_handlers.remove_user_from_repo)

    def test_get_users_in_repo_url_is_resolved(self):
        self.assertEqual(resolve(self.get_users_in_repo_url).func, ajax_handlers.get_users_in_repo)

    def test_get_users_repo_users_url_is_resolved(self):
        self.assertEqual(resolve(self.get_users_repo_users_url).func, ajax_handlers.get_users_repo_users)

    def test_get_repos_for_user_url_is_resolved(self):
        self.assertEqual(resolve(self.get_repos_for_user_url).func, ajax_handlers.get_repos_for_user)

    def test_add_repo_to_group_url_is_resolved(self):
        self.assertEqual(resolve(self.add_repo_to_group_url).func, ajax_handlers.add_repo_to_group)

    def test_remove_repo_from_group_url_is_resolved(self):
        self.assertEqual(resolve(self.remove_repo_from_group_url).func, ajax_handlers.remove_repo_from_group)

    def test_get_repo_info_url_is_resolved(self):
        self.assertEqual(resolve(self.get_repo_info_url).func, ajax_handlers.get_repo_info)

    def test_get_dspace_communities_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dspace_communities_url).func, ajax_handlers.get_dspace_communities)

    def test_retrieve_dspace_objects_url_is_resolved(self):
        self.assertEqual(resolve(self.retrieve_dspace_objects_url).func, ajax_handlers.retrieve_dspace_objects)

    def test_get_dspace_items_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dspace_items_url).func, ajax_handlers.get_dspace_items)

    def test_get_dataverse_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dataverse_url).func, ajax_handlers.search_dataverse)

    def test_get_dataverse_vf_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dataverse_vf_url).func, ajax_handlers.search_dataverse_vf)

    def test_get_dataverse_content_vf_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dataverse_content_vf_url).func, ajax_handlers.get_dataverse_content_vf)

    def test_ckan_package_search_url_is_resolved(self):
        self.assertEqual(resolve(self.ckan_package_search_url).func, ajax_handlers.ckan_package_search)

    def test_get_collection_url_is_resolved(self):
        self.assertEqual(resolve(self.get_collection_url).func, ajax_handlers.get_dspace_collection)

    def test_get_dataverse_content_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dataverse_content_url).func, ajax_handlers.get_dataverse_content)

    def test_get_info_for_new_dataverse_url_is_resolved(self):
        self.assertEqual(resolve(self.get_info_for_new_dataverse_url).func,
                         ajax_handlers.get_info_for_new_dataverse)

    def test_update_submission_repo_data_url_is_resolved(self):
        self.assertEqual(resolve(self.update_submission_repo_data_url).func,
                         ajax_handlers.update_submission_repo_data)

    def test_set_destination_repository_url_is_resolved(self):
        self.assertEqual(resolve(self.set_destination_repository_url).func,
                         ajax_handlers.set_destination_repository)

    def test_update_submission_meta_url_is_resolved(self):
        self.assertEqual(resolve(self.update_submission_meta_url).func, ajax_handlers.update_submission_meta)

    def test_dataverse_publish_url_is_resolved(self):
        self.assertEqual(resolve(self.dataverse_publish_url).func, ajax_handlers.publish_dataverse)

    def test_get_existing_metadata_url_is_resolved(self):
        self.assertEqual(resolve(self.get_existing_metadata_url).func, ajax_handlers.get_repo_info)

    def test_get_submission_metadata_url_is_resolved(self):
        self.assertEqual(resolve(self.get_submission_metadata_url).func, ajax_handlers.get_submission_metadata)

    def test_get_ckan_items_url_is_resolved(self):
        self.assertEqual(resolve(self.get_ckan_items_url).func, ajax_handlers.get_ckan_items)

    def test_delete_repo_entry_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_repo_entry_url).func, ajax_handlers.delete_repo_entry)

    def test_get_dataset_info_url_is_resolved(self):
        self.assertEqual(resolve(self.get_dataset_info_url).func, ajax_handlers.get_dataset_info)

    def test_add_personal_dataverse_url_is_resolved(self):
        self.assertEqual(resolve(self.add_personal_dataverse_url).func, ajax_handlers.add_personal_dataverse)

    def test_get_personal_dataverses_url_is_resolved(self):
        self.assertEqual(resolve(self.get_personal_dataverses_url).func, ajax_handlers.get_personal_dataverses)

    def test_delete_personal_dataverse_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_personal_dataverse_url).func, ajax_handlers.delete_personal_dataverse)

    def test_get_subsample_stages_url_is_resolved(self):
        self.assertEqual(resolve(self.get_subsample_stages_url).func, ajax_handlers.get_subsample_stages)

    def test_sample_spreadsheet_url_is_resolved(self):
        self.assertEqual(resolve(self.sample_spreadsheet_url).func, ajax_handlers.sample_spreadsheet)

    def test_sample_images_url_is_resolved(self):
        self.assertEqual(resolve(self.sample_images_url).func, ajax_handlers.sample_images)

    def test_create_spreadsheet_samples_url_is_resolved(self):
        self.assertEqual(resolve(self.create_spreadsheet_samples_url).func,
                         ajax_handlers.create_spreadsheet_samples)

    def test_update_spreadsheet_samples_url_is_resolved(self):
        self.assertEqual(resolve(self.update_spreadsheet_samples_url).func,
                         ajax_handlers.update_spreadsheet_samples)

    def test_update_pending_samples_table_url_is_resolved(self):
        self.assertEqual(resolve(self.update_pending_samples_table_url).func,
                         ajax_handlers.update_pending_samples_table)

    def test_get_samples_for_profile_url_is_resolved(self):
        self.assertEqual(resolve(self.get_samples_for_profile_url).func, ajax_handlers.get_samples_for_profile)

    def test_mark_sample_rejected_url_is_resolved(self):
        self.assertEqual(resolve(self.mark_sample_rejected_url).func, ajax_handlers.mark_sample_rejected)

    def test_add_sample_to_dtol_submission_url_is_resolved(self):
        self.assertEqual(resolve(self.add_sample_to_dtol_submission_url).func,
                         ajax_handlers.add_sample_to_dtol_submission)

    def test_delete_dtol_samples_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_dtol_samples_url).func, ajax_handlers.delete_dtol_samples)

    def test_handle_csv_column_validate_spreadsheet_url_is_resolved(self):
        self.assertEqual(resolve(self.handle_csv_column_validate_spreadsheet_url).func,
                         ajax_handlers.handle_csv_column_validate_spreadsheet)

    def test_handle_csv_column_update_samples_url_is_resolved(self):
        self.assertEqual(resolve(self.handle_csv_column_update_samples_url).func,
                         ajax_handlers.handle_csv_column_update_samples)

    """ Test annotation handlers urls """

    def test_refresh_annotation_display_url_is_resolved(self):
        self.assertEqual(resolve(self.refresh_annotation_display_url).func, annotation_handlers.refresh_display)

    def test_send_file_annotation_url_is_resolved(self):
        self.assertEqual(resolve(self.send_file_annotation_url).func, annotation_handlers.send_file_annotation)

    def test_refresh_annotations_url_is_resolved(self):
        self.assertEqual(resolve(self.refresh_annotations_url).func, annotation_handlers.refresh_annotations)

    def test_refresh_text_annotations_url_is_resolved(self):
        self.assertEqual(resolve(self.refresh_text_annotations_url).func,
                         annotation_handlers.refresh_text_annotations)

    def test_delete_annotation_url_is_resolved(self):
        self.assertEqual(resolve(self.delete_annotation_url).func, annotation_handlers.delete_annotation)

    def test_refresh_annotations_for_user_url_is_resolved(self):
        self.assertEqual(resolve(self.refresh_annotations_for_user_url).func,
                         annotation_handlers.refresh_annotations_for_user)

    def test_annotations_url_is_resolved(self):
        self.assertNotEquals(resolve(self.annotations_url).func, annotation_handlers.new_text_annotation)

    def test_search_url_is_resolved(self):
        self.assertEqual(resolve(self.search_url).func, annotation_handlers.search_text_annotation)

    # def test_delete_text_annotation_url_is_resolved(self):
    # self.assertEqual(resolve(self.update_metadata_template_name_url).func,
    # annotation_handlers.edit_or_delete_text_annotation)

    def test_automate_num_cols_url_is_resolved(self):
        self.assertEqual(resolve(self.automate_num_cols_url).func, annotation_handlers.automate_num_cols)

    def test_term_lookup_url_is_resolved(self):
        self.assertEqual(resolve(self.term_lookup_url).func, annotation_handlers.term_lookup)

    def test_resolve_taxon_id_url_is_resolved(self):
        self.assertEqual(resolve(self.resolve_taxon_id_url).func, annotation_handlers.resolve_taxon_id)

    def test_search_species_url_is_resolved(self):
        self.assertEqual(resolve(self.search_species_url).func, annotation_handlers.search_species)

        """Test template handlers urls"""

    def test_update_metadata_template_name_url_is_resolved(self):
        self.assertEqual(resolve(self.update_metadata_template_name_url).func,
                         template_handlers.update_metadata_template_name)

    def test_new_metadata_template_url_is_resolved(self):
        self.assertEqual(resolve(self.new_metadata_template_url).func, template_handlers.new_metadata_template)

    def test_update_template_url_is_resolved(self):
        self.assertEqual(resolve(self.update_template_url).func, template_handlers.update_template)

    def test_load_metadata_template_terms_url_is_resolved(self):
        self.assertEqual(resolve(self.load_metadata_template_terms_url).func,
                         template_handlers.load_metadata_template_terms)

    def test_get_wizard_types_url_is_resolved(self):
        self.assertEqual(resolve(self.get_wizard_types_url).func, template_handlers.get_wizard_types)

    def test_export_template_url_is_resolved(self):
        self.assertEqual(resolve(self.export_template_url).func, template_handlers.export_template)

    def test_get_primer_fields_url_is_resolved(self):
        self.assertEqual(resolve(self.get_primer_fields_url).func, template_handlers.get_primer_fields)

    def test_add_primer_fields_url_is_resolved(self):
        self.assertEqual(resolve(self.add_primer_fields_url).func, template_handlers.add_primer_fields)

    # tearDown() method -  the test runner invokes that method after each test

    # @classmethod
    # def tearDown(cls):

    def test_landing_views(self):
        pass


    # Other tests to be done:
    # Some parts can be logged in since login authentication
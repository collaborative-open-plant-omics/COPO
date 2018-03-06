from django.urls import path, re_path
from . import views
from web.apps.web_copo.utils import ajax_handlers

app_name = 'web_copo'

urlpatterns = [
    path('', views.index, name='index'),
    path('dataverse_submit/', views.test_dataverse_submit, name='test_dataverse_submit'),
    path('test_submission/', views.test_submission, name='test_submission'),
    path('test_pdf/', views.test_pdf, name='test_pdf'),
    path('test/', views.test, name='test'),
    path('login/', views.login, name='auth'),
    path('logout/', views.copo_logout, name='logout'),
    path('register/', views.copo_register, name='register'),
    path('profile/update_counts/', views.get_profile_counts, name='update_counts'),
    path('view_orcid_profile/', views.view_orcid_profile, name='view_orcid_profile'),
    path('error/', views.goto_error, name='error_page'),
    path('register_to_irods/', views.register_to_irods, name='register_to_irods'),
    re_path(r'^copo_profile/(?P<profile_id>[a-z0-9]+)/view', views.view_copo_profile, name='view_copo_profile'),
    re_path(r'^copo_publications/(?P<profile_id>[a-z0-9]+)/view', views.copo_publications, name='copo_publications'),
    re_path(r'^copo_data/(?P<profile_id>[a-z0-9]+)/view', views.copo_data, name='copo_data'),
    re_path(r'^copo_samples/(?P<profile_id>[a-z0-9]+)/view', views.copo_samples, name='copo_samples'),
    re_path(r'^copo_submissions/(?P<profile_id>[a-z0-9]+)/view', views.copo_submissions, name='copo_submissions'),
    re_path(r'^copo_people/(?P<profile_id>[a-z0-9]+)/view', views.copo_people, name='copo_people'),
    re_path(r'^copo_annotation/(?P<profile_id>[a-z0-9]+)/view', views.copo_annotation, name='copo_annotation'),
    path('get_source_count/', ajax_handlers.get_source_count, name="get_source_count"),
    re_path(r'^ajax_search_ontology/(?P<ontology_names>[a-zA-Z0-9,]+)/$', ajax_handlers.search_ontology_ebi, name='ajax_search_ontology'),
    path('ajax_search_ontology_test/', ajax_handlers.test_ontology, name='test_ontology'),
    path('copo_forms/', views.copo_forms, name="copo_forms"),
    path('copo_visualize/', views.copo_visualize, name="copo_visualize"),
    path('authenticate_figshare/', views.authenticate_figshare, name='authenticate_figshare'),
    path('publish_figshare/', ajax_handlers.publish_figshare, name='publish_figshare'),
    path('view_oauth_tokens/', views.view_oauth_tokens, name='view_oauth_tokens'),
    path('get_tokens_for_user/', ajax_handlers.get_tokens_for_user, name='get_tokens_for_user'),
    path('delete_token/', ajax_handlers.delete_token, name='delete_token'),
    path('get_annotation/', views.annotate_data, name='annotate_data'),
    path('agave_oauth/', views.agave_oauth, name='agave_oauth'),
    path('import_ena_accession/', views.import_ena_accession, name='import_ena_accession')
]
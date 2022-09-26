__author__ = 'felix.shaw@tgac.ac.uk - 14/05/15'

from django.urls import path, re_path

import api.views.general as api_views

urlpatterns = [
    re_path(r'^submit_to_figshare/(?P<article_id>[a-z0-9]+)', api_views.submit_to_figshare,
            name='submit_figshare_collection'),
    re_path(r'^get_figshare_url/(?P<article_id>[a-z0-9]+)', api_views.view_in_figshare,
            name='view_figshare_collection'),
    re_path(r'^delete_figshare_article/(?P<article_id>[a-z0-9]+)', api_views.delete_from_figshare,
            name='delete_article'),
    path('generate_ena_template/', 'generate_ena_template', name='generate_ena_template'),
    re_path(r'^doi2publication_metadata/(?P<id_handle>.*)', 'doi2publication_metadata',
            name='doi2publication_metadata'),
    path('login_orcid/', api_views.login_orcid, name='login_orcid'),
    path('check_orcid_credentials/', api_views.check_orcid_credentials, name='check_orcid_credentials'),
    path('get_collection_type/', api_views.get_collection_type, name='get_collection_type'),
    path('convert_to_sra/', api_views.convert_to_sra, name='convert_to_sra'),
    path('refactor_collection_schema/', api_views.refactor_collection_schema, name='refactor_collection_schema')
]

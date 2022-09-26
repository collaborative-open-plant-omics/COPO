__author__ = 'felix.shaw@tgac.ac.uk - 20/01/2016'

from django.urls import path, re_path

from .annotate_views import search_all, post_annotations, handle_upload
from .views import person, general, stats, profile
from .views import sample as s
from .views.sample import APIValidateManifest, APIGetManifestValidationReport, APIGetUserValidations
from django.views.decorators.csrf import csrf_exempt
from web.apps.web_copo.utils import ajax_handlers
from django.views.generic import TemplateView

app_name = 'api'

generic_api_patterns = [
    re_path(r'^person/get/(?P<id>[a-z0-9]+)', person.get, name='person/get'),
    path('person/get/', person.get_all, name='person/get/all'),
    path('sample/get/', s.get_all, name='sample/get/all'),
    path('search/', search_all, name='search_all'),
    path('annotations/', post_annotations, name='post_annotations'),
    path('upload_annotation_file/', handle_upload, name='handle_upload'),
    re_path(r'stats/numbers', general.numbers, name='stats/numbers'),
]

dtol_api_patterns = [
    path('', general.forward_to_swagger),
    path('apiKey/', csrf_exempt(general.CustomAuthToken.as_view())),
    re_path(r'sample/get/(?P<id>[A-Za-z0-9]+)', s.get, name='sample/get'),
    re_path(r'manifest/validations/', APIGetUserValidations.as_view(), name='/manifest/validate/report/'),
    re_path(r'manifest/validate/report/', APIGetManifestValidationReport.as_view(), name='/manifest/validate/report/'),
    re_path(r'manifest/validate/', APIValidateManifest.as_view(), name='manifest/validate'),
    re_path(r'manifest/(?P<manifest_id>[A-Z0-9a-f-]+)', s.get_samples_in_manifest, name='get_for_manifest'),
    re_path(r'manifest/', s.get_manifests, name='get_manifests'),

    # dates must be ISO 8601 formatted
    re_path(r'manifest/(?P<d_from>[A-Z0-9a-f- .:+]+)/(?P<d_to>[A-Z0-9a-f- .:+]+)',
            s.get_all_manifest_between_dates, name='get_all_manifests_between_dates'),

    re_path(r'manifest/(?P<project>[a-zA-Z, ]+)/(?P<d_from>[A-Z0-9a-f- .:+]+)/(?P<d_to>[A-Z0-9a-f- .:+]+)',
            s.get_project_manifests_between_dates, name='get_project_manifests_between_dates'),

    re_path(r'manifest/(?P<manifest_id>[A-Z0-9a-f-]+)/sample_statuses', s.get_sample_statuses_for_manifest,
            name='get_sample_statuses_for_manifest'),

    re_path(r'sample/biosample_id/(?P<biosample_ids>[A-Z0-9, ]+)', s.get_by_biosample_ids,
            name='get_by_biosample_ids'),
    re_path(r'sample/copo_id/(?P<copo_ids>[A-Za-z0-9, ]+)', s.get_by_copo_ids, name='get_by_biosample_ids'),
    re_path(r'sample/sample_field/(?P<dtol_field>[A-Za-z0-9-_]+)/(?P<value>[A-Za-z0-9-_ ,.@]+)', s.get_by_field,
            name='get_by_dtol_field'),
    re_path(r'sample/dtol/num_samples', s.get_num_dtol_samples, name='get_num_dtol_samples'),
    re_path(r'sample/(?P<project>[a-zA-Z, ]+)/', s.get_project_samples, name='get_project_samples'),
    re_path(r'sample/SampleFromStudyAccession/(?P<accessions>[A-Za-z0-9, ]+)', s.get_samples_from_study_accessions,
            name='get_samples_from_study_accession'),
    re_path(r'sample/StudyFromSampleAccession/(?P<accessions>[A-Za-z0-9, ]+)', s.get_study_from_sample_accession,
            name='get_study_from_sample_accession'),
    re_path(r'profile/make_profile/', profile.APICreateProfile.as_view(),
            name='make_profile'),
    re_path(r'profile/get_for_user/', profile.APIGetProfilesForUser.as_view(),
            name='get_for_user'),
]

stats_api_patterns = [
    re_path(r'stats/number_of_users', stats.get_number_of_users,
            name='get_number_of_users'),
    re_path(r'stats/number_of_samples', stats.get_number_of_samples,
            name='get_number_of_samples'),
    re_path(r'stats/number_of_profiles', stats.get_number_of_profiles,
            name='get_number_of_profiles'),
    re_path(r'stats/number_of_datafiles', stats.get_number_of_datafiles,
            name='get_number_of_datafiles'),
    re_path(r'stats/combined_stats_json', stats.combined_stats_json,
            name='combined_stats_csv'),
    re_path(r'stats/sample_stats_csv', stats.samples_stats_csv,
            name='samples_stats_csv'),
    re_path(r'stats/histogram_metric/(?P<metric>[A-Za-z0-9_]+)', stats.samples_hist_json,
            name='samples_hist_json'),
]

manifest_patterns = [
    re_path(r'get_manifest_fields/', ajax_handlers.get_manifest_fields,
            name="get_manifest_fields"),
    re_path(r'get_common_value_dropdown_list/', ajax_handlers.get_common_value_dropdown_list,
            name="get_common_value_dropdown_list"),
    re_path(r'generate_manifest_template', ajax_handlers.generate_manifest_template,
            name="generate_manifest_template"),
    re_path(r'validate_common_value', ajax_handlers.validate_common_value,
            name="validate_common_value"),
    re_path(r'index', TemplateView.as_view(template_name="manifests.html"), name='manifests'),
]

urlpatterns = generic_api_patterns + dtol_api_patterns + stats_api_patterns + manifest_patterns

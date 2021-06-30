__author__ = 'felix.shaw@tgac.ac.uk - 20/01/2016'

from django.urls import path, re_path

from .annotate_views import search_all, post_annotations, handle_upload
from .handlers import sample, person, general, stats

app_name = 'api'

generic_api_patterns = [
    re_path(r'^person/get/(?P<id>[a-z0-9]+)', person.get, name='person/get'),
    path('person/get/', person.get_all, name='person/get/all'),
    path('sample/get/', sample.get_all, name='sample/get/all'),
    path('search/', search_all, name='search_all'),
    path('annotations/', post_annotations, name='post_annotations'),
    path('upload_annotation_file/', handle_upload, name='handle_upload'),
    re_path(r'stats/numbers', general.numbers, name='stats/numbers'),
]

dtol_api_patterns = [
    path('', general.forward_to_swagger),
    re_path(r'sample/get/(?P<id>[A-Za-z0-9]+)', sample.get, name='sample/get'),
    re_path(r'manifest/(?P<manifest_id>[A-Z0-9a-f-]+)/sample_statuses', sample.get_sample_statuses_for_manifest,
            name='get_sample_statuses_for_manifest'),
    re_path(r'manifest/(?P<d_from>[A-Z0-9a-f- .:+]+)/(?P<d_to>[A-Z0-9a-f- .:+]+)',
            sample.get_dtol_manifests_between_dates, name='get_dtol_manifests_between_dates'),
    # dates must be ISO 8601 formatted
    re_path(r'manifest/(?P<manifest_id>[A-Z0-9a-f-]+)', sample.get_for_manifest, name='get_for_manifest'),

    re_path(r'manifest/', sample.get_dtol_manifests, name='get_manifests'),
    re_path(r'sample/biosample_id/(?P<biosample_ids>[A-Z0-9, ]+)', sample.get_by_biosample_ids,
            name='get_by_biosample_ids'),
    re_path(r'sample/copo_id/(?P<copo_ids>[A-Za-z0-9, ]+)', sample.get_by_copo_ids, name='get_by_biosample_ids'),
    re_path(r'sample/sample_field/(?P<dtol_field>[A-Za-z0-9-_]+)/(?P<value>[A-Za-z0-9-_ ,.@]+)', sample.get_by_field,
            name='get_by_dtol_field'),
    re_path(r'sample/dtol/num_samples', sample.get_num_dtol_samples, name='get_num_dtol_samples'),
    re_path(r'sample/dtol/', sample.get_dtol_samples, name='get_manifests'),
    re_path(r'sample/SampleFromStudyAccession/(?P<accessions>[A-Za-z0-9, ]+)', sample.get_samples_from_study_accessions,
            name='get_samples_from_study_accession'),
    re_path(r'sample/StudyFromSampleAccession/(?P<accessions>[A-Za-z0-9, ]+)', sample.get_study_from_sample_accession,
            name='get_study_from_sample_accession'),
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

urlpatterns = generic_api_patterns + dtol_api_patterns + stats_api_patterns

from django.urls import path

import api.views.general as api
import web.apps.web_copo.repos.figshare as figshare
import web.apps.web_copo.rest.EnaRest as rest
import web.apps.web_copo.views as views
import api.annotate_views as a_views
import web.apps.web_copo.wizard_views as wizard
import submission.submissionDelegator as submit
import web.apps.web_copo.utils.ajax_handlers as ajax
from web.apps.web_copo.rest.EnaRest import CopoChunkedUploadCompleteView, CopoChunkedUploadView

import submission.sword_utils as su

app_name = 'rest'

urlpatterns = [
    path('data_wiz/', wizard.data_wiz, name='data_wiz'),
    path('sample_wiz/', wizard.sample_wiz, name='sample_wiz'),
    path('receive_data_file/', rest.receive_data_file, name='receive_data_file'),
    path('receive_data_file_chunked/', CopoChunkedUploadView.as_view(), name='receive_data_file'),
    path('complete_upload/', CopoChunkedUploadCompleteView.as_view(), name='complete_data_file'),
    path('hash_upload/', rest.hash_upload, name='hash_upload'),
    path('inspect_file/', rest.inspect_file, name='inspect_file'),
    path('zip_file/', rest.zip_file, name='zip_file'),
    path('check_figshare_credentials/', figshare.check_figshare_credentials, name='check_figshare_credentials'),
    path('set_figshare_credentials/', figshare.set_figshare_credentials, name='set_figshare_credentials'),
    path('small_file_upload/', api.upload_to_figshare_profile, name='receive_data_file'),
    path('forward_to_figshare/', wizard.forward_to_figshare, name='forward_to_figshare'),
    path('get_upload_information/', ajax.get_upload_information, name='get_upload_information'),
    path('get_submission_status/', ajax.get_submission_status, name='get_submission_status'),
    path('submit_to_repo/', submit.delegate_submission, name='delegate_submission'),
    path('release_ena_study/', ajax.release_ena_study, name='release_ena_study'),
    #path('test_submission/', views.test_submission, name='test_ena_submission'),
    path('resume_chunked/', rest.resume_chunked, name='resume_chunked'),
    path('get_partial_uploads/', rest.get_partial_uploads, name='get_partial_uploads'),
    path('save_ss_annotation', a_views.save_ss_annotation, name='save_ss_annotation'),
    path('delete_ss_annotation/', a_views.delete_ss_annotation, name='delete_ss_annotation'),
    path('copo_get_submission_table_data/', views.copo_get_submission_table_data, name='get_submissions'),
    path('get_accession_data/', ajax.get_accession_data, name='get_accession_data'),
    path('set_session_variable/', ajax.set_session_variable, name='set_session_variable'),
    path('test_sword/', su.test_module, name='test_module'),
    path('call_get_dataset_details/', ajax.get_dataset_details, name='call_get_dataset_details'),
    path('samples_from_study/', ajax.get_samples_for_study, name='get_samples_for_study'),
    path('get_users/', ajax.get_users, name='get_users'),
    path('get_ontologies/', ajax.get_ontologies, name='get_ontologies'),
    path('export_generic_annotation/', ajax.export_generic_annotation, name='export_generic_annotation')
]

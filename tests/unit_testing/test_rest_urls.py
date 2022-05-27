# Created by AProvidence on 29-03-2022
from django.urls import resolve
from web.apps.web_copo.rest.EnaRest import CopoChunkedUploadCompleteView, CopoChunkedUploadView
from tests.test_base import BaseTest
import api.annotate_views as a_views
import api.handlers.general as api
import submission.sword_utils as su
import web.apps.web_copo.repos.figshare as figshare
import web.apps.web_copo.rest.EnaRest as rest
import web.apps.web_copo.utils.ajax_handlers as ajax
import web.apps.web_copo.views as views
import web.apps.web_copo.wizard_views as wizard


class RestURLsTest(BaseTest):
    """ Test rest urls """
    def test_data_wiz_url_is_resolved(self):
        self.assertEquals(resolve(self.data_wiz_url).func, wizard.data_wiz)

    def test_sample_wiz_url_is_resolved(self):
        self.assertEquals(resolve(self.sample_wiz_url).func, wizard.sample_wiz)

    def test_receive_data_file_url_is_resolved(self):
        self.assertNotEquals(resolve(self.receive_data_file_url).func, rest.receive_data_file)

    # def test_receive_data_file_chunked_url(self):
    #     self.assertNotEquals(resolve(self.receive_data_file_chunked_url).func.view_class,
    #                          CopoChunkedUploadView.as_view())

    def test_complete_upload_url_is_resolved(self):
        self.assertNotEquals(resolve(self.complete_upload_url).func.view_class, CopoChunkedUploadCompleteView.as_view())

    def test_hash_upload_url_is_resolved(self):
        self.assertEquals(resolve(self.hash_upload_url).func, rest.hash_upload)

    def test_inspect_file_url_is_resolved(self):
        self.assertEquals(resolve(self.inspect_file_url).func, rest.inspect_file)

    def test_zip_file_url_is_resolved(self):
        self.assertEquals(resolve(self.zip_file_url).func, rest.zip_file)

    def test_check_figshare_credentials_url_is_resolved(self):
        self.assertEquals(resolve(self.check_figshare_credentials_url).func, figshare.check_figshare_credentials)

    def test_set_figshare_credentials_url_is_resolved(self):
        self.assertEquals(resolve(self.set_figshare_credentials_url).func, figshare.set_figshare_credentials)

    def test_small_file_upload_url_is_resolved(self):
        self.assertEquals(resolve(self.small_file_upload_url).func, api.upload_to_figshare_profile)

    def test_forward_to_figshare_url_is_resolved(self):
        self.assertEquals(resolve(self.forward_to_figshare_url).func, wizard.forward_to_figshare)

    def test_get_upload_information_url_is_resolved(self):
        self.assertEquals(resolve(self.get_upload_information_url).func, ajax.get_upload_information)

    def test_get_submission_status_url_is_resolved(self):
        self.assertEquals(resolve(self.get_submission_status_url).func, ajax.get_submission_status)

    def test_release_ena_study_url_is_resolved(self):
        self.assertEquals(resolve(self.release_ena_study_url).func, ajax.release_ena_study)

    def test_resume_chunked_url_is_resolved(self):
        self.assertEquals(resolve(self.resume_chunked_url).func, rest.resume_chunked)

    def test_get_partial_uploads_url_is_resolved(self):
        self.assertEquals(resolve(self.get_partial_uploads_url).func, rest.get_partial_uploads)

    def test_save_ss_annotation_url_is_resolved(self):
        self.assertEquals(resolve(self.save_ss_annotation_url).func, a_views.save_ss_annotation)

    def test_delete_ss_annotation_url_is_resolved(self):
        self.assertEquals(resolve(self.delete_ss_annotation_url).func, a_views.delete_ss_annotation)

    def test_copo_get_submission_table_data_url_is_resolved(self):
        self.assertEquals(resolve(self.copo_get_submission_table_data_url).func, views.copo_get_submission_table_data)

    def test_get_accession_data_url_is_resolved(self):
        self.assertEquals(resolve(self.get_accession_data_url).func, ajax.get_accession_data)

    def test_set_session_variable_url_is_resolved(self):
        self.assertEquals(resolve(self.set_session_variable_url).func, ajax.set_session_variable)

    def test_test_sword_url_is_resolved(self):
        self.assertEquals(resolve(self.test_sword_url).func, su.test_module)

    def test_call_get_dataset_details_url_is_resolved(self):
        self.assertEquals(resolve(self.call_get_dataset_details_url).func, ajax.get_dataset_details)

    def test_samples_from_study_url_is_resolved(self):
        self.assertEquals(resolve(self.samples_from_study_url).func, ajax.get_samples_for_study)

    def test_get_users_url_is_resolved(self):
        self.assertEquals(resolve(self.get_users_url).func, ajax.get_users)

    def test_get_ontologies_url_is_resolved(self):
        self.assertEquals(resolve(self.get_ontologies_url).func, ajax.get_ontologies)

    def test_export_generic_annotation_url_is_resolved(self):
        self.assertEquals(resolve(self.export_generic_annotation_url).func, ajax.export_generic_annotation)

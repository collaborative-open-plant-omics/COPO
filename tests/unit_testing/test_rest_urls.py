# Created by AProvidence on 29-03-2022
from dal.copo_da import Profile
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from faker import Faker
# from htmlvalidator.client import ValidatingClient
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
import web.apps.web_copo.utils.ajax_handlers as ajax
from web.apps.web_copo.utils.ajax_handlers import get_dataset_details
from django.http import HttpResponse
import json


class RestURLsTest(TestCase):
    """ Test rest urls """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        settings.UNIT_TESTING = True
        cls.fake = Faker()
        cls.factory = RequestFactory()
        # # Create a new user
        # cls.username = fake.first_name().lower()
        # cls.user_password = User.objects.make_random_password()
        # cls.user = User.objects.create_user(username=cls.username,
        #                                     first_name=fake.first_name(),
        #                                     last_name=fake.last_name(),
        #                                     email=fake.free_email(),
        #                                     password=cls.user_password)
        # cls.user.save()

        """" Rest URL declaration """

    def set_rest_urls(self):
        rest_call_get_dataset_details_url = reverse('rest:call_get_dataset_details')
        rest_check_figshare_credentials_url = reverse('rest:check_figshare_credentials')
        rest_complete_data_file_url = reverse('rest:complete_data_file')
        rest_get_submissions_url = reverse('rest:get_submissions')
        rest_data_wiz_url = reverse('rest:data_wiz')
        rest_delete_ss_annotation_url = reverse('rest:delete_ss_annotation')
        rest_export_generic_annotation_url = reverse('rest:export_generic_annotation')
        rest_forward_to_figshare_url = reverse('rest:forward_to_figshare')
        rest_get_accession_data_url = reverse('rest:get_accession_data')
        rest_get_ontologies_url = reverse('rest:get_ontologies')
        rest_get_partial_uploads = reverse('rest:get_partial_uploads')
        rest_get_submission_status_url = reverse('rest:get_submission_status')
        rest_get_upload_information_url = reverse('rest:get_upload_information')
        rest_get_users_url = reverse('rest:get_users')
        rest_hash_upload_url = reverse('rest:hash_upload')
        rest_inspect_file_url = reverse('rest:inspect_file')
        rest_receive_data_file_url = reverse('rest:receive_data_file')
        rest_receive_data_file_chunked_url = reverse('rest:receive_data_file')
        rest_release_ena_study = reverse('rest:release_ena_study')
        rest_resume_chunked_url = reverse('rest:resume_chunked')
        rest_sample_wiz_url = reverse('rest:sample_wiz')
        rest_samples_from_study_url = reverse('rest:get_samples_for_study')
        rest_save_ss_annotation_url = reverse('rest:save_ss_annotation')
        rest_set_figshare_credentials_url = reverse('rest:set_figshare_credentials')
        rest_set_session_variable_url = reverse('rest:set_session_variable')
        rest_small_file_upload_url = reverse('rest:receive_data_file')
        rest_submit_to_repo_url = reverse('rest:delegate_submission')

        # Get a list of strings of the rests urls
        rests_urls_list = [
            rest_call_get_dataset_details_url,

        ]

        return rests_urls_list

    def create_user(self):
        self.username = settings.TEST_USER_NAME  # self.fake.first_name().lower()
        self.user_password = User.objects.make_random_password()
        self.user = User.objects.create_user(username=self.username,
                                             first_name=self.fake.first_name(),
                                             last_name=self.fake.last_name(),
                                             email=self.fake.free_email(),
                                             password=self.user_password)
        self.user.save()
        self.client.login(username=self.username, password=self.user_password)
        self.create_user_profile(self.user.id)

    def create_user_profile(self, userID):
        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": userID,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}
        self.user_pid = Profile().get_collection_handle().insert(dtol_profile)
        # Save the profile ID in the session
        # session = self.client.session
        # session['profile_id'] = str(self.user_pid)
        # session.save()

    def test_rest_urls(self):
        """Test the urls for "rest" """
        print('Rest URLs test')
        # self.create_user()
        # self.client.login(username=self.username, password=self.user_password)
        # Save the profile ID in the session

        # session = self.get_session()
        # session['profile_id'] = self.user_pid
        # session.save()
        # self.set_session_cookies(session)
        self.username = settings.TEST_USER_NAME  # self.fake.first_name().lower()
        self.user_password = User.objects.make_random_password()
        self.user = User.objects.create_user(username=self.username,
                                             first_name=self.fake.first_name(),
                                             last_name=self.fake.last_name(),
                                             email=self.fake.free_email(),
                                             password=self.user_password)
        self.user.save()
        self.client.login(username=self.username, password=self.user_password)
        # Create a DTOL profile on the COPO website
        dtol_profile = {"copo_id": "000000000", "description": "DTOL Test Description", "user_id": self.user.id,
                        "type": "Darwin Tree of Life (DTOL)", "title": "DTOL Test Title"}
        self.user_pid = Profile().save_record(dict(), **dtol_profile)

        # self.user_pid = Profile().get_collection_handle().insert(dtol_profile)
        rest_webpages = self.set_rest_urls()
        request = self.factory.get(reverse('rest:call_get_dataset_details'))
        # request.session = {'profile_id': str(self.user_pid["_id"])}
        # request.session = {'profile_id': str(self.user_pid)}
        # request.POST = {'profile_id': str(self.user_pid)}
        # data = Profile().check_for_dataset_details(str(self.user_pid))
        # response = HttpResponse(json.dumps(data))

        response = ajax.get_dataset_details(request)
        # response = self.factory.get(reverse('rest:call_get_dataset_details'))
        print(response)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.factory.get(reverse('rest:call_get_dataset_details')).status_code, 200,
        #                  self.factory.get(reverse('rest:call_get_dataset_details')))
        #
        # for webpage in rest_webpages:
        #     # self.client.login(username=self.username, password=self.user_password)
        #     # session = SessionStore()
        #     # session['profile_id'] = str(self.user_pid)
        #     # session.create()
        #     # sessionKey = SessionStore(session_key=session.session_key)
        #     # self.assertEqual(session['profile_id'], sessionKey['profile_id'])
        #     response = self.client.get(webpage)
        #     # session = self.client.session
        #
        #     # self.client.login(username=self.username, password=self.user_password)
        #     # if webpage == self.copo_index_url or webpage == self.copo_add_personal_dataverse_url or webpage == self.copo_add_primer_fields_url or webpage == self.copo_accept_reject_sample_url:
        #     #     print("302 status: ", webpage)
        #     #     self.assertEqual(response.status_code, 302, response)
        #     #     # self.client.login(username=self.username, password=self.user_password)
        #     #     # print("200 status: ", webpage)
        #     #     # self.assertEqual(response.status_code, 200, response)
        #     #
        #     # else:
        #     #     print("200 status: ", webpage)
        #     #     self.assertEqual(response.status_code, 200, response)
        #     # self.assertIn(
        #     #     ('profile_id', self.user_pid),
        #     #     response.client.session.items())
        #     self.assertEqual(response.status_code, 200, response)
        #     # print(f"{response.status_code}: ", webpage)

    # def test_data_wiz_url_is_resolved(self):
    #     self.assertEquals(resolve(self.data_wiz_url).func, wizard.data_wiz)
    #
    # def test_sample_wiz_url_is_resolved(self):
    #     self.assertEquals(resolve(self.sample_wiz_url).func, wizard.sample_wiz)
    #
    # def test_receive_data_file_url_is_resolved(self):
    #     self.assertNotEquals(resolve(self.receive_data_file_url).func, rest.receive_data_file)
    #
    # # def test_receive_data_file_chunked_url(self):
    # #     self.assertNotEquals(resolve(self.receive_data_file_chunked_url).func.view_class,
    # #                          CopoChunkedUploadView.as_view())
    #
    # def test_complete_upload_url_is_resolved(self):
    #     self.assertNotEquals(resolve(self.complete_upload_url).func.view_class, CopoChunkedUploadCompleteView.as_view())
    #
    # def test_hash_upload_url_is_resolved(self):
    #     self.assertEquals(resolve(self.hash_upload_url).func, rest.hash_upload)
    #
    # def test_inspect_file_url_is_resolved(self):
    #     self.assertEquals(resolve(self.inspect_file_url).func, rest.inspect_file)
    #
    # def test_zip_file_url_is_resolved(self):
    #     self.assertEquals(resolve(self.zip_file_url).func, rest.zip_file)
    #
    # def test_check_figshare_credentials_url_is_resolved(self):
    #     self.assertEquals(resolve(self.check_figshare_credentials_url).func, figshare.check_figshare_credentials)
    #
    # def test_set_figshare_credentials_url_is_resolved(self):
    #     self.assertEquals(resolve(self.set_figshare_credentials_url).func, figshare.set_figshare_credentials)
    #
    # def test_small_file_upload_url_is_resolved(self):
    #     self.assertEquals(resolve(self.small_file_upload_url).func, api.upload_to_figshare_profile)
    #
    # def test_forward_to_figshare_url_is_resolved(self):
    #     self.assertEquals(resolve(self.forward_to_figshare_url).func, wizard.forward_to_figshare)
    #
    # def test_get_upload_information_url_is_resolved(self):
    #     self.assertEquals(resolve(self.get_upload_information_url).func, ajax.get_upload_information)
    #
    # def test_get_submission_status_url_is_resolved(self):
    #     self.assertEquals(resolve(self.get_submission_status_url).func, ajax.get_submission_status)
    #
    # def test_release_ena_study_url_is_resolved(self):
    #     self.assertEquals(resolve(self.release_ena_study_url).func, ajax.release_ena_study)
    #
    # def test_resume_chunked_url_is_resolved(self):
    #     self.assertEquals(resolve(self.resume_chunked_url).func, rest.resume_chunked)
    #
    # def test_get_partial_uploads_url_is_resolved(self):
    #     self.assertEquals(resolve(self.get_partial_uploads_url).func, rest.get_partial_uploads)
    #
    # def test_save_ss_annotation_url_is_resolved(self):
    #     self.assertEquals(resolve(self.save_ss_annotation_url).func, a_views.save_ss_annotation)
    #
    # def test_delete_ss_annotation_url_is_resolved(self):
    #     self.assertEquals(resolve(self.delete_ss_annotation_url).func, a_views.delete_ss_annotation)
    #
    # def test_copo_get_submission_table_data_url_is_resolved(self):
    #     self.assertEquals(resolve(self.copo_get_submission_table_data_url).func, views.copo_get_submission_table_data)
    #
    # def test_get_accession_data_url_is_resolved(self):
    #     self.assertEquals(resolve(self.get_accession_data_url).func, ajax.get_accession_data)
    #
    # def test_set_session_variable_url_is_resolved(self):
    #     self.assertEquals(resolve(self.set_session_variable_url).func, ajax.set_session_variable)
    #
    # def test_test_sword_url_is_resolved(self):
    #     self.assertEquals(resolve(self.test_sword_url).func, su.test_module)
    #
    # def test_call_get_dataset_details_url_is_resolved(self):
    #     self.assertEquals(resolve(self.call_get_dataset_details_url).func, ajax.get_dataset_details)
    #
    # def test_samples_from_study_url_is_resolved(self):
    #     self.assertEquals(resolve(self.samples_from_study_url).func, ajax.get_samples_for_study)
    #
    # def test_get_users_url_is_resolved(self):
    #     self.assertEquals(resolve(self.get_users_url).func, ajax.get_users)
    #
    # def test_get_ontologies_url_is_resolved(self):
    #     self.assertEquals(resolve(self.get_ontologies_url).func, ajax.get_ontologies)
    #
    # def test_export_generic_annotation_url_is_resolved(self):
    #     self.assertEquals(resolve(self.export_generic_annotation_url).func, ajax.export_generic_annotation)

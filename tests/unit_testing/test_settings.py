# Created by AProvidence 10052022
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import SimpleTestCase
from web.settings.chunked_upload import *
from web.settings.logger import skip_static_requests
from django.templatetags.static import static


class SettingsTest(SimpleTestCase):
    settings.UNIT_TESTING = True

    def test_chunked_upload_settings(self):
        """"" Tests the settings with the chunked_upload file """
        print("Test chunked_upload settings")
        self.assertEqual(DEFAULT_EXPIRATION_DELTA, CHUNKED_UPLOAD_EXPIRATION_DELTA)
        self.assertEqual(os.path.join(os.getcwd(), "media", 'chunked_uploads'), DEFAULT_UPLOAD_PATH)
        # Test that the default upload path and the upload path are the same where files will be stored
        # until completion whilst being uploaded
        self.assertEqual(DEFAULT_UPLOAD_PATH, UPLOAD_PATH)
        self.assertFalse(CHUNKED_UPLOAD_ABSTRACT_MODEL)
        self.assertTrue('text', CHUNKED_UPLOAD_MIMETYPE)
        self.assertEqual(EXPIRATION_DELTA, DEFAULT_EXPIRATION_DELTA)
        # Test that there is no storage system in place
        self.assertTrue("None", STORAGE)
        # Test that the ChunkedUpload model is an abstract
        self.assertTrue(ABSTRACT_MODEL)
        self.assertTrue(DEFAULT_ENCODER, ENCODER)
        self.assertEqual(MIMETYPE, 'application/json')
        self.assertTrue("None", MAX_BYTES)
        # self.assertRaises(ImportError, ENCODER, DjangoJSONEncoder)


class LoggerTest(StaticLiveServerTestCase):
    def test_logger_settings(self):
        # <link rel = "stylesheet" href = "{% static 'copo/css/copo/index.css' %}" >
        # record = self.live_server_url + settings.STATIC_URL + 'index.html'
        # print(record)
        # record = static('assets/files/COPO_visual_user_documentation.pdf')
        # print(skip_static_requests(record))
        # self.assertTrue(skip_static_requests(record))
        pass

from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import (
    InMemoryUploadedFile, TemporaryUploadedFile,
)
import logging

logging = logging.getLogger(__name__)

class LogUploadHandler(FileUploadHandler):

    """
    Upload handler that streams data into a temporary file.
    """

    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset,
                                          self.content_type_extra)
        logging.info("uploading new file " + self.file_name)

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = file_size
        logging.info("file uploaded " + self.file_name)
        return self.file

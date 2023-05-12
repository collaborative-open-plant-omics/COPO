import boto3
#from boto3.session import Session
from botocore.config import Config
from django.conf import settings as s
from botocore.exceptions import EndpointConnectionError
from smart_open import open as s_open
from django_tools.middlewares.ThreadLocal import get_current_request
import time
from os import path
from submission.helpers.generic_helper import notify_frontend
from exceptions_and_logging.logger import Logger
from boto3.s3.transfer import TransferConfig
import logging

class S3Connection():
    """
    Class to handle interations with ECS cloud storage via s3 service
    """

    def __init__(self):
        self.ecs_endpoint =  s.ECS_ENDPOINT
        self.ecs_access_key_id = s.ECS_ACCESS_KEY_ID
        self.ecs_secret_key = s.ECS_SECRET_KEY

        self.expiration = 60 * 60 * 24
        self.path = '/'
        boto3.set_stream_logger(name='', level=logging.INFO, format_string=None)
        self.s3_client = boto3.client('s3', endpoint_url=self.ecs_endpoint, #verify=False,
                                      config=Config(signature_version='s3v4', connect_timeout=10, retries={"max_attempts":3}, s3={'addressing_style': "path"}),
                                      aws_access_key_id=self.ecs_access_key_id,
                                      aws_secret_access_key=self.ecs_secret_key)
        #self.transport_params = {'client': self.s3_client}
        Logger().debug(msg=f"endpoint: {self.ecs_endpoint}, access key: {self.ecs_access_key_id}, secret: {self.ecs_secret_key}")
 
    def list_buckets(self):
        response = self.s3_client.list_buckets()
        Logger().debug(msg=response['Buckets'])
        return response["Buckets"]

    def list_objects(self, bucket):
        try:
            response = self.s3_client.list_objects(Bucket=bucket)
        except Exception as e:
            Logger().exception(e)
            return False
        try:
            contents = response["Contents"]
        except KeyError as e:
            # empty buckets have no 'Contents' fields
            return list()
        return contents

    def get_object(self, bucket, key, loc):
        Logger().log("transfering file to: " + loc)
        KB = 1024
        MB = KB * KB 
        GB = KB * MB          
        
        config = TransferConfig(multipart_threshold=256 * MB, multipart_chunksize=128 * MB, io_chunksize= 32 * MB, max_concurrency=10, use_threads=True)
        self.s3_client.download_file(bucket, key, loc, Config=config)
        
        #with open(loc, 'wb') as data:
        #   self.s3_client.download_fileobj(bucket, key, data, Config=config)
        Logger().log("transfer complete: " + loc)
  

    def get_presigned_url(self, bucket, key, expires_seconds=60 * 60 * 24):
        '''
        Create a pre-signed url for uploading a single file to the s3 ECS
        :param bucket: name of the bucket to which the object sould be uploaded
        :param key: name of the file
        :param expires_seconds: how long until the url expires, default 24hrs
        :return:
        '''
        try:
            response = self.s3_client.generate_presigned_url('put_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires_seconds)
        except Exception as e:
            response = e
        return response

    def check_for_s3_bucket(self, uid):
        '''
        Check for the existence of an s3 bucket
        :param uid: the name of the bucket
        :return: True if exists, False if not
        '''
        response = self.s3_client.list_buckets()
        bucket_list = response['Buckets']
        for bucket in bucket_list:
            if bucket["Name"] == uid:
                return True
        return False

    def make_s3_bucket(self, bucket_name):
        '''
        make an s3 bucks
        :param bucket_name: name of bucket to make
        :return: the bucket
        '''

        #try:
        return self.s3_client.create_bucket(Bucket=str(bucket_name))
    
    
        #except Exception as e:
        #    response = "error"
        #    print(e)
        #return bucket

    def check_s3_bucket_for_files(self, bucket_name, file_list):
        '''
        Checks bucket_name for files supplied in file_list
        :param bucket_name: name of the s3 bucket to search
        :param file_list: list of files to look for
        :return: a list containing the names of files _not_ found
        '''
        try: 
            try:
                profile_id = get_current_request().session["profile_id"]
            except AttributeError:
                profile_id = "xxxx"
            channels_group_name = "s3_" + profile_id

            missing_files = list()
            etags = dict()
            # get objects in the supplied bucket name
            bucket_files = self.list_objects(bucket=bucket_name)
            
            if not bucket_files:
                msg = "Bucket not found: " + bucket_name
                notify_frontend(data={"profile_id": profile_id}, msg=msg, action="info",
                                html_id="sample_info", group_name=channels_group_name)
                return False
            
            for f in file_list:

                # if found, iterate list of given files to see if each if present in the bucket
                found_flag = 0
                files = f.split(",")
                for file in files:
                    print("Looking for", file)
                    file = file.strip()

                    notify_frontend(data={"profile_id": profile_id}, msg="Searching for: " + file, action="info",
                                    html_id="sample_info", group_name=channels_group_name)
                    # time.sleep(2)
                    for bucket_file in bucket_files:

                        if file == bucket_file["Key"]:
                            print("Found", bucket_file["Key"])
                            found_flag = 1
                            etag = bucket_file["ETag"]
                            etag = etag.replace('"', '')
                            etags[file] = etag
                            break
                    if not found_flag:
                        # if a file is not found it should be recorded as such
                        missing_files.append(file)
            if len(missing_files) > 0:
                # report missing files
                notify_frontend(data={"profile_id": profile_id}, msg="Files Missing: " + str(
                    missing_files) + ". Please upload these by clicking on 'Upload Data into COPO' and following the instructions", action="info",
                                html_id="sample_info", group_name=channels_group_name)
                # return false to halt execution
                return False
            else:
                return etags

        except KeyError as e:
            notify_frontend(data={"profile_id": profile_id}, msg="Key Error Occured...cannot find key: " + str(e), action="info",
                            html_id="sample_info", group_name=channels_group_name)
            return False
        except Exception as e:
            notify_frontend(data={"profile_id": profile_id}, msg="An error occured: " + str(e), action="info",
                            html_id="sample_info", group_name=channels_group_name)
            raise e

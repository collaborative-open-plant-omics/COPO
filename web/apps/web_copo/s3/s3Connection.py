import boto3
from boto3.session import Session, Config
from django.conf import settings as s
from botocore.exceptions import EndpointConnectionError
from smart_open import open as s_open


class S3Connection():

    def __init__(self):
        ecs_endpoint = s.ECS_ENDPOINT
        ecs_access_key_id = s.ECS_ACCESS_KEY_ID
        ecs_secret_key = s.ECS_SECRET_KEY  # long gibberish key here (begins 4kT)
        expiration = '3600'  # expiration for presigned URL
        path = '/'  # list of source paths for objects

        self.s3_client = boto3.client('s3', endpoint_url=ecs_endpoint, verify=False,
                                      config=Config(signature_version='s3', s3={'addressing_style': 'path'}), aws_access_key_id=ecs_access_key_id,
                                      aws_secret_access_key=ecs_secret_key)
        self.transport_params = {'client': self.s3_client}

    def list_buckets(self):
        try:
            response = self.s3_client.list_buckets()
        except EndpointConnectionError as e:
            print(e)
            return False
        print(response['Buckets'])
        return response["Buckets"]

    def list_objects(self, bucket):
        try:
            response = self.s3_client.list_objects(Bucket=bucket)

        except Exception as e:
            print(e)
            return False
        return response["Contents"]

    def get_object(self, bucket, key):
        try:
            tmp_key = key.split("/")[-1]
            with s_open(tmp_key, "w+") as fout:
                for l in s_open("s3://" + bucket + "/" + key, transport_params=self.transport_params):
                    fout.write(l)
        except Exception as e:
            print(e)
            return False
        return True

    def get_presigned_url(self, bucket, key, expires_seconds=60):
        try:
            response = self.s3_client.generate_presigned_url('put_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires_seconds)
        except:
            response = "error"
        return response

    def make_bucket(self, bucket_name):
        try:
            bucket = self.s3_client.create_bucket(str(bucket_name))
        except:
            response = "error"
        return response

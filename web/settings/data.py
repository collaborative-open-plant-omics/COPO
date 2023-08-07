# settings for services e.g. postgres, mongo, redis, irods...

from django.conf import settings

from pymongo import MongoClient
from tools import resolve_env
import sys
import os

# this value tells COPO whether we are in Development or Production environment
ENVIRONMENT_TYPE = resolve_env.get_env('ENVIRONMENT_TYPE')
if ENVIRONMENT_TYPE == "":
    sys.exit('ENVIRONMENT_TYPE environment variable not set. Value should be either "prod" or "dev"')

# settings for postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': resolve_env.get_env('POSTGRES_DB'),
        'USER': resolve_env.get_env('POSTGRES_USER'),
        'PASSWORD': resolve_env.get_env('POSTGRES_PASSWORD'),
        'HOST': resolve_env.get_env('POSTGRES_SERVICE'),
        'PORT': resolve_env.get_env('POSTGRES_PORT')
    }
}

# settings for mongodb
MONGO_DB = resolve_env.get_env('MONGO_DB')
MONGO_HOST = resolve_env.get_env('MONGO_HOST')
MONGO_USER = resolve_env.get_env('MONGO_USER')
MONGO_USER_PASSWORD = resolve_env.get_env('MONGO_USER_PASSWORD')
MONGO_PORT = int(resolve_env.get_env('MONGO_PORT'))
MONGO_MAX_POOL_SIZE = int(resolve_env.get_env('MONGO_MAX_POOL_SIZE'))
MONGO_DB_TEST = "test_copo_mongo"

# this is the global DB connection, either use get_collection_ref in dal.mongo_util.py or refer to this setting
# If unit testing is being done use the Mongo test database instead of the production/actual Mongo database
if settings.UNIT_TESTING:
    MONGO_CLIENT = MongoClient(host=MONGO_HOST, maxPoolSize=MONGO_MAX_POOL_SIZE)[MONGO_DB_TEST]
else:
    MONGO_CLIENT = MongoClient(host=MONGO_HOST, maxPoolSize=MONGO_MAX_POOL_SIZE)[MONGO_DB]

MONGO_CLIENT.authenticate(MONGO_USER, MONGO_USER_PASSWORD, source='admin')

# settings for redis
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = resolve_env.get_env('REDIS_HOST')
SESSION_REDIS_PORT = int(resolve_env.get_env('REDIS_PORT'))

# settings for figshare
FIGSHARE_CREDENTIALS = {
    'client_id': resolve_env.get_env('FIGSHARE_CLIENT_ID'),
    'consumer_secret': resolve_env.get_env('FIGSHARE_CONSUMER_SECRET'),
    'client_secret': resolve_env.get_env('FIGSHARE_CLIENT_SECRET')
}

# django channels settings
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(SESSION_REDIS_HOST, SESSION_REDIS_PORT)],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# settings for object stores
SAMPLE_OBJECT_STORE = os.path.join(settings.MEDIA_ROOT, 'object_store', 'samples.h5')
DATAFILE_OBJECT_STORE = os.path.join(settings.MEDIA_ROOT, 'object_store', 'datafiles.h5')
SAMPLE_OBJECT_PREFIX = "samples_"
DATAFILE_OBJECT_PREFIX = "datafiles_"
DESCRIPTION_GRACE_PERIOD = 10  # no of days after which pending descriptions are deleted

# settings for TOL schema (manifest) versions i.e. code modularisation
'''
CURRENT_ASG_VERSION = "2.4.1"
CURRENT_DTOL_VERSION = "2.4.1"
CURRENT_DTOLENV_VERSION = "2.4"
CURRENT_ERGA_VERSION = "2.4.2"
'''
# settings for ECS
ECS_ACCESS_KEY_ID = resolve_env.get_env('ECS_ACCESS_KEY_ID')
ECS_SECRET_KEY = resolve_env.get_env('ECS_SECRET_KEY')
ECS_ENDPOINT = resolve_env.get_env('ECS_ENDPOINT')


# settings for manifest
MANIFEST_VERSION = {
    "ASG":  "2.4.1",
    "DTOL": "2.4.1",
    "DTOLENV": "2.4",
    "DTOL_ENV": "2.4",
    "DTOL_EI": "2.4",
    "ERGA": "2.4.3",
    "DTOL_BARCODE": "",
}

BARCODING_CHECKLIST = ["ERT000002", "ERT000020"]

ENA_CHECKLIST_CONFIG = {
    "ERT000002" : {"skip": ["STRAIN","LAB_HOST"]},
    "ERT000020" : {"skip": ["STRAIN","SPECVOUCH", "VARIETY", "IDBY"]}
}

ENA_CHECKLIST_URL  = [
    "https://www.ebi.ac.uk/ena/submit/report/checklists/xml/ERT000002?type=sequence",
    "https://www.ebi.ac.uk/ena/submit/report/checklists/xml/ERT000020?type=sequence",
    "https://www.ebi.ac.uk/ena/submit/report/checklists/xml/*?type=sample"
]
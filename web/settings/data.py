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
MONGO_DB_TEST = "testing_copo"

# this is the global DB connection, either use get_collection_ref in dal.mongo_util.py or refer to this setting

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

# settings for TOL schemas
CURRENT_DTOL_VERSION = 2.2
CURRENT_ASG_VERSION = 2.3

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from tools import resolve_env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCHEMA_DIR = os.path.join(BASE_DIR, 'web', 'apps', 'web_copo', 'schemas')

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

PROFILE_LOG_BASE = os.path.join(BASE_DIR, 'profiler')
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = resolve_env.get_env('SECRET_KEY')

LOGIN_URL = '/accounts/auth/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if str(resolve_env.get_env('DEBUG')).lower() == 'true' else False

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', '.copo-project.org', '.demo.copo-project.org', 'localhost', '10.0.0.*']
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://0.0.0.0:8000",
    "http://0.0.0.0:80",
    "http://127.0.0.1:8000",
    "https://copo-project.org",
    "http://demo.copo-project.org",
    "http://copo_dev0.cyverseuk.org"
]
DEBUG_PROPAGATE_EXCEPTIONS = True
# Django's base applications definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.sites',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# user-defined applications definition
PROJECT_APPS = [
    'channels',
    'web.apps.web_copo',
    'web.apps.web_copo.rest',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.orcid',
    'rest_framework',
    'chunked_upload',
    'compressor',
    'django_extensions',
    'corsheaders'
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS
# sass, social accounts...
sass_exe = '/usr/local/bin/sass'
COMPRESS_PRECOMPILERS = (
    ('text/scss', sass_exe + ' --scss  {infile} {outfile}'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

SOCIALACCOUNT_PROVIDERS = \
    {'google':
         {'SCOPE': ['profile', 'email'],
          'AUTH_PARAMS': {'access_type': 'online'}}}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
    'django_brotli.middleware.BrotliMiddleware',
    'web.apps.web_copo.middleware.LocksMiddleware.LocksMiddleware'
]

AUTHENTICATION_BACKENDS = (
    # Needed to auth by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as auth by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 10
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:8000',
    'http://0.0.0.0:8001',
    'http://127.0.0.1:8000'
)
# CORS_ORIGIN_ALLOW_ALL = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/copo/login'

ROOT_URLCONF = 'web.urls'

LOGIN_URL = '/copo/login'

TEMPLATES = [

    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            #
            os.path.join(BASE_DIR, 'web', 'landing'),
            os.path.join(BASE_DIR, 'web', 'apps', 'web_copo', 'templates', 'copo'),
            os.path.join(BASE_DIR, 'static', 'swagger'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'web.wsgi.application'
ASGI_APPLICATION = 'web.routing.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# print(STATICFILES_DIRS)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# MEDIA_ROOT = STATIC_ROOT

MEDIA_ROOT = os.path.join(BASE_DIR, resolve_env.get_env('MEDIA_PATH'))
MEDIA_URL = 'media/'

ELASTIC_SEARCH_URL = 'http://localhost:9200/ontologies/plant_ontology/_search'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 48 * 60 * 60  #

SITE_ID = 1

COPO_URL = 'copo-project.org'

DATAVERSE = {
    "HARVARD_TEST_API": "https://demo.dataverse.org",
    "HARVARD_TEST_TOKEN": "fe6998df-c2a4-4103-9bf8-95200953fe0c",
    "HARVARD_LIVE_API": "https://dataverse.harvard.edu",
    "HARVARD_LIVE_TOKEN": "10731a84-b3d3-457e-999d-21f48fe8d812"
}

UNIT_TESTING = False
TEST_USER_NAME = 'jonny'

DATA_UPLOAD_MAX_MEMORY_SIZE = 500000000
FILE_UPLOAD_MAX_MEMORY_SIZE = 500000000

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'copo_cache_table',

    }
}

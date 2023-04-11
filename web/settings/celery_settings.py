# settings for celery
from .data import SESSION_REDIS_HOST, SESSION_REDIS_PORT
 
# celery settings
CELERY_BROKER_URL = f'redis://{SESSION_REDIS_HOST}:{SESSION_REDIS_PORT}'
CELERY_RESULT_BACKEND = f'redis://{SESSION_REDIS_HOST}:{SESSION_REDIS_PORT}'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

#CELERY_QUEUES = (
#    Queue('long_process', Exchange('media'), routing_key='long_process'),
#    Queue('default', Exchange('default'), routing_key='default'),
#)

#ELERY_TASK_ROUTES = {
#    'web.apps.web_copo.tasks.process_pending_file_transfers': {
#        'queue': 'long_process',
#        'routing_key': 'long_process',
#    },
#}

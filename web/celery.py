from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery

# from web.apps.web_copo.utils.dtol import DtolSpreadsheet

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings.all')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings.all')
# crontab(minute="*/1")
app = Celery('web')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# define periodic tasks here

app.conf.beat_schedule = {
    'process_ena_submission': {
        'task': 'web.apps.web_copo.tasks.process_ena_submission',
        'schedule': timedelta(seconds=20)  # execute every n minutes minute="*/n"
    },
    'process_ena_transfer': {
        'task': 'web.apps.web_copo.tasks.process_ena_transfer',
        'schedule': timedelta(seconds=20)  # execute every n minutes minute="*/n"
    },
    'process_dtol_sample_submission': {
        'task': 'web.apps.web_copo.tasks.process_dtol_sample_submission',
        'schedule': timedelta(seconds=10)
    },
    'find_incorrectly_rejected_samples': {
        'task': 'web.apps.web_copo.tasks.find_incorrectly_rejected_samples',
        'schedule': timedelta(seconds=60)
    },
    'update_stats': {
        'task': 'web.apps.web_copo.tasks.update_stats',
        'schedule': timedelta(hours=24)
    },
    'poll_missing_tolids' :{
        'task': 'web.apps.web_copo.tasks.poll_missing_tolids',
        'schedule': timedelta(seconds=60) #leave time for human creation of tolid
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

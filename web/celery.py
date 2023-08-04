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
    'process_bioimage_submission': {
        'task': 'web.apps.web_copo.tasks.process_bioimage_submission',
        'schedule': timedelta(seconds=30)
    },
    'process_tol_validations': {
        'task': 'web.apps.web_copo.tasks.process_tol_validations',
        'schedule': timedelta(seconds=3)
    },

    'find_incorrectly_rejected_samples': {
        'task': 'web.apps.web_copo.tasks.find_incorrectly_rejected_samples',
        'schedule': timedelta(seconds=60)
    },

    'update_stats': {
        'task': 'web.apps.web_copo.tasks.update_stats',
        'schedule': timedelta(hours=24)
    },
    'poll_missing_tolids': {
        'task': 'web.apps.web_copo.tasks.poll_missing_tolids',
        'schedule': timedelta(hours=2)  # shortened cause sometimes it doesn't work?
    },
    'poll_expired_viewlocks': {
        'task': 'web.apps.web_copo.tasks.poll_expired_viewlocks',
        'schedule': timedelta(seconds=60)
    },
    'process_ena_transfers': {
        'task': 'web.apps.web_copo.tasks.process_pending_file_transfers',
        'schedule': timedelta(seconds=5)
    },
    'check_for_stuck_transfers': {
        'task': 'web.apps.web_copo.tasks.check_for_stuck_transfers',
        'schedule': timedelta(seconds=20)
    },
    'process_housekeeping': {
        'task': 'web.apps.web_copo.tasks.process_housekeeping',
        'schedule': timedelta(seconds=3600)
    },
    'poll_asyn_ena_submission': {
        'task': 'web.apps.web_copo.tasks.poll_asyn_ena_submission',
        'schedule': timedelta(seconds=10)
    },
    'process_seq_annotation_submission': {
        'task': 'web.apps.web_copo.tasks.process_seq_annotation_submission',
        'schedule': timedelta(seconds=10)
    },
    'poll_asyn_seq_annotation_submission_receipt': {
        'task': 'web.apps.web_copo.tasks.poll_asyn_seq_annotation_submission_receipt',
        'schedule': timedelta(seconds=10)
    },
    'update_seq_annotation_submission_pending': {
        'task': 'web.apps.web_copo.tasks.update_seq_annotation_submission_pending',
        'schedule': timedelta(seconds=10)
    },
#    'update_tagsequence_checklist': {
#        'task': 'web.apps.web_copo.tasks.update_tagsequence_checklist',
#        'schedule': timedelta(days=1)
#    },     
    'update_ena_checklist': {
        'task': 'web.apps.web_copo.tasks.update_ena_checklist',
        'schedule': timedelta(days=1)
    },     
    'processing_pending_tagged_seq_submission': {
        'task': 'web.apps.web_copo.tasks.processing_pending_tagged_seq_submission',
        'schedule': timedelta(seconds=10)
    },  
    'update_ena_read_checklist': {
        'task': 'web.apps.web_copo.tasks.update_ena_read_checklist',
        'schedule': timedelta(days=1)
    }, 
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

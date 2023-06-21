import celery

import web.apps.web_copo.utils.dtol.Dtol_Submission as dtol
import web.apps.web_copo.utils.dtol.Dtol_Bioimage_Submission as dtol_bioimage
import web.apps.web_copo.utils.EnaAnnotation as enaAnnotation

from dal.copo_da import Sample, Stats
from web.apps.web_copo.models import ViewLock
from submission import enareadSubmission
from web.apps.web_copo.validators.validation_celery_handler import ProcessValidationQueue
from web.celery import app
from web.apps.web_copo.utils import FileTransferUtils as tx
from exceptions_and_logging.logger import Logger
import celery
import redis
from functools import wraps
from tools import resolve_env
from asgiref.sync import sync_to_async
SESSION_REDIS_HOST = resolve_env.get_env('REDIS_HOST')
SESSION_REDIS_PORT = int(resolve_env.get_env('REDIS_PORT'))
REDIS_CLIENT = redis.Redis(host=SESSION_REDIS_HOST, port=SESSION_REDIS_PORT)


def only_one(fun=None, key="", timeout=None):   
    def actual_only_one(fun): 
        """Enforce only one celery task at a time."""
        @wraps(fun)
        def inner_func(self, *args, **kwargs):
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    return fun(self, *args, **kwargs)
                else:
                    Logger().log("quit the task " + fun.__name__ + "as the previous one is still running" ) 
            finally:
                if have_lock:
                    try:
                        lock.release()
                    except Exception as e:
                        Logger().error(e)
        return inner_func
    return actual_only_one    


class CopoBaseClassForTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        Logger().error('{0!r} failed: {1!r}'.format(task_id, exc))
        Logger().error(einfo)
        Logger().error('{0!r} failed: {1!r}'.format(task_id, exc))
        Logger().error(einfo)
        #traceback.print_exc(file=os.path.join(settings.BASE_DIR, Logger().logfile_path , str(datetime.now().date()) + '.log'))
            

            

@app.task(bind=True, base=CopoBaseClassForTask)
def update_study_status():
    Logger().debug("Running update_study_status")
    enareadSubmission.EnaReads().update_study_status()
    return True


@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_ena_submission", timeout=5)
def process_ena_submission(self):
    Logger().debug("Running process_ena_submission")
    enareadSubmission.EnaReads().process_queue()
    return True


@app.task(bind=True,  base=CopoBaseClassForTask)
@only_one(key="process_ena_transfer", timeout=5)
def process_ena_transfer(self):
    Logger().debug("Running process_ena_transfer")
    enareadSubmission.EnaReads().process_file_transfer()
    return True

@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_dtol_sample_submission", timeout=5)
def process_dtol_sample_submission(self):
    Logger().debug("Running process_dtol_sample_submission")
    dtol.process_pending_dtol_samples()
    return True


@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_bioimage_submission", timeout=5)
def process_bioimage_submission(self):
    Logger().debug("Running process_bioimage_submission")
    dtol_bioimage.process_bioimage_pending_submission()
    return True


@app.task(bind=True,   base=CopoBaseClassForTask)
def find_incorrectly_rejected_samples(self):
    Logger().debug("Running find_incorrectly_rejected_samples")
    Sample().find_incorrectly_rejected_samples()
    return True


@app.task(bind=True,   base=CopoBaseClassForTask)
def update_stats(self):
    Logger().debug("Running update_stats")
    Stats().update_stats()
    return True


@app.task(bind=True,   base=CopoBaseClassForTask)
def poll_missing_tolids(self):
    Logger().debug("Running poll_missing_tolids")
    dtol.query_awaiting_tolids()
    return True


@app.task(bind=True,   base=CopoBaseClassForTask)
@only_one(key="process_poll_expired_viewlocks", timeout=5)
def poll_expired_viewlocks(self):
    Logger().debug("Running poll_expired_viewlocks")
    ViewLock().remove_expired_locks()
    return True


@app.task(bind=True,  base=CopoBaseClassForTask)
def process_tol_validations(self):
    Logger().debug("Running process_tol_validations")
    ProcessValidationQueue().process_validation_queue()
    return True


@app.task(bind=True,   base=CopoBaseClassForTask)
@only_one(key="process_pending_file_transfers", timeout=5)
def process_pending_file_transfers(self):
    Logger().debug("Running process_pending_file_transfers")
    tx.process_pending_file_transfers()
    return True


@app.task(bind=True,   base=CopoBaseClassForTask)
@only_one(key="process_check_for_stuck_transfers", timeout=5)
def check_for_stuck_transfers(self):
    Logger().debug("Running check_for_stuck_transfers")
    tx.check_for_stuck_transfers()
    return True

@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_poll_asyn_ena_submission", timeout=5)
def poll_asyn_ena_submission(self):
    Logger().debug("Running poll_asyn_ena_submission")
    dtol.poll_asyn_ena_submission()
    return True

@app.task(bind=True, base=CopoBaseClassForTask)
def process_housekeeping(self):
    Logger().debug("Running process_housekeeping")
    Logger().housekeeping_logfile()
    dtol_bioimage.housekeeping_bioimage_archive()
    return True

@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_poll_asyn_seq_annotation_submission_receipt", timeout=5)
def poll_asyn_seq_annotation_submission_receipt(self):           
    Logger().debug("poll_asyn_annotation_submission_receipt")
    enaAnnotation.poll_asyn_seq_annotation_submission_receipt()
    return True

@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_process_annotation_submission", timeout=5)
def process_seq_annotation_submission(self):
    Logger().debug("Running process_annotation_submission")
    enaAnnotation.process_seq_annotation_pending_submission()
    return True

@app.task(bind=True, base=CopoBaseClassForTask)
@only_one(key="process_update_seq_annotation_submission_pending", timeout=5)
def update_seq_annotation_submission_pending(self):
    Logger().debug("Running update_seq_annotation_submission_pending")
    enaAnnotation.update_seq_annotation_submission_pending()
    return True

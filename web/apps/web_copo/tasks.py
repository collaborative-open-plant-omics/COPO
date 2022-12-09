import web.apps.web_copo.utils.dtol.Dtol_Submission as dtol
import web.apps.web_copo.utils.dtol.Dtol_Bioimage_Submission as dtol_bioimage

from dal.copo_da import Sample, Stats
from web.apps.web_copo.models import ViewLock
from submission import enareadSubmission
from web.apps.web_copo.validators.validation_celery_handler import ProcessValidationQueue
from web.celery import app
from web.apps.web_copo.utils import FileTransferUtils as tx
from exceptions_and_logging.logger import Logger
@app.task
def update_study_status():
    Logger().log("Running update_study_status")
    enareadSubmission.EnaReads().update_study_status()
    return True


@app.task(bind=True)
def process_ena_submission(self):
    Logger().log("Running process_ena_submission")
    enareadSubmission.EnaReads().process_queue()
    return True


@app.task(bind=True)
def process_ena_transfer(self):
    Logger().log("Running process_ena_transfer")
    enareadSubmission.EnaReads().process_file_transfer()
    return True


@app.task(bind=True)
def process_dtol_sample_submission(self):
    Logger().log("Running process_dtol_sample_submission")
    dtol.process_pending_dtol_samples()
    return True

@app.task(bind=True)
def process_bioimage_submission(self):
    Logger().log("Running process_bioimage_submission")
    dtol_bioimage.process_bioimage_pending_submission()
    return True
@app.task(bind=True)
def find_incorrectly_rejected_samples(self):
    Logger().log("Running find_incorrectly_rejected_samples")
    Sample().find_incorrectly_rejected_samples()
    return True


@app.task(bind=True)
def update_stats(self):
    Logger().log("Running update_stats")
    Stats().update_stats()
    return True


@app.task(bind=True)
def poll_missing_tolids(self):
    Logger().log("Running poll_missing_tolids")
    dtol.query_awaiting_tolids()
    return True


@app.task(bind=True)
def poll_expired_viewlocks(self):
    Logger().log("Running poll_expired_viewlocks")
    ViewLock().remove_expired_locks()
    return True


@app.task(bind=True)
def process_tol_validations(self):
    Logger().log("Running process_tol_validations")
    ProcessValidationQueue().process_validation_queue()
    return True


@app.task(bind=True)
def process_pending_file_transfers(self):
    Logger().log("Running process_pending_file_transfers")
    tx.process_pending_file_transfers()
    return True


@app.task(bind=True)
def check_for_stuck_transfers(self):
    Logger().log("Running check_for_stuck_transfers")
    tx.check_for_stuck_transfers()
    return True

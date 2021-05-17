import web.apps.web_copo.utils.dtol.Dtol_Submission as dtol
from dal.copo_da import Sample, Stats
from submission import enareadSubmission
from web.celery import app


@app.task
def update_study_status():
    enareadSubmission.EnaReads().update_study_status()
    return True


@app.task(bind=True)
def process_ena_submission(self):
    enareadSubmission.EnaReads().process_queue()
    return True


@app.task(bind=True)
def process_ena_transfer(self):
    enareadSubmission.EnaReads().process_file_transfer()
    return True


@app.task(bind=True)
def process_dtol_sample_submission(self):
    dtol.process_pending_dtol_samples()
    return True

@app.task(bind=True)
def find_incorrectly_rejected_samples(self):
    Sample().find_incorrectly_rejected_samples()
    return True


@app.task(bind=True)
def update_stats(self):
    Stats().update_stats()
    return True

@app.task(bind=True)
def poll_missing_tolids(self):
    dtol.query_awaiting_tolids()
    return True

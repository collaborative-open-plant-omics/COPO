"""module contains simple and generic functions to facilitate data submission"""

__author__ = 'etuka'
__date__ = '25 September 2019'

import os
import pexpect
import requests
from bson import ObjectId
import dal.mongo_util as mutil
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from web.apps.web_copo.lookup.copo_enums import Loglvl, Logtype

lg = settings.LOGGER
BASE_DIR = settings.BASE_DIR
REPOSITORIES = settings.REPOSITORIES


def get_submission_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['SubmissionCollection']

    return collection_handle


def get_submission_queue_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['SubmissionQueueCollection']

    return collection_handle


def get_filetransfer_queue_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['FileTransferQueueCollection']

    return collection_handle


def get_description_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['DescriptionCollection']

    return collection_handle


def get_person_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['PersonCollection']

    return collection_handle


def get_datafiles_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['DataFileCollection']

    return collection_handle


def get_samples_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['SampleCollection']

    return collection_handle


def get_sources_handle():  # this can be safely called by forked process
    mongo_client = mutil.get_mongo_client()
    collection_handle = mongo_client['SourceCollection']

    return collection_handle


def logging_info(message=str(), submission_id=str()):
    """
    function provides a consistent way of logging submission status/information
    :param message:
    :param submission_id:
    :return:
    """

    lg.log('[Submission: ' + submission_id + '] ' + message, level=Loglvl.INFO, type=Logtype.FILE)

    return True


def logging_error(message=str(), submission_id=str()):
    """
    function provides a consistent way of logging error during submission
    :param message:
    :param submission_id:
    :return:
    """

    try:
        lg.log('[Submission: ' + submission_id + '] ' + message, level=Loglvl.ERROR, type=Logtype.FILE)
    except Exception as e:
        return False

    return True


def log_general_info(message):
    """
    logs info not tied to a specific submission record
    :param message:
    :return:
    """

    lg.log('[Submission:] ' + message, level=Loglvl.INFO, type=Logtype.FILE)

    return True


def log_general_error(message):
    """
    logs error not tied to a specific submission record
    :param message:
    :return:
    """
    try:
        lg.log('[Submission: ] ' + message, level=Loglvl.ERROR, type=Logtype.FILE)
    except Exception as e:
        return False

    return True


def update_submission_status(status=str(), message=str(), submission_id=str(), notify=True):
    """
    function updates status of submission
    :param status:
    :param message:
    :param submission_id:
    :param notify:
    :return:
    """

    if not submission_id:
        return False

    collection_handle = get_submission_handle()
    doc = collection_handle.find_one({"_id": ObjectId(submission_id)},
                                     {"transcript": 1, "profile_id": 1})

    if not doc:
        return False

    submission_record = doc
    transcript = submission_record.get("transcript", dict())
    status = dict(type=status, message=message)
    transcript['status'] = status

    if not message:
        transcript.pop('status', '')

    submission_record['transcript'] = transcript
    submission_record['date_modified'] = d_utils.get_datetime()

    collection_handle.update(
        {"_id": ObjectId(str(submission_record.pop('_id')))},
        {'$set': submission_record})

    # notify client agent on status change
    if notify:
        notify_status_change(profile_id=submission_record.get("profile_id", str()), submission_id=submission_id)

    return True


def notify_status_change(profile_id=str(), submission_id=str()):
    """
    this function notifies the client agent of potential change to submission status for the target record
    :param profile_id:
    :param submission_id:
    :return:
    """

    if submission_id and profile_id:
        event = dict(type='submission_status')
        event["submission_id"] = submission_id

        group_name = 'submission_status_%s' % profile_id

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            event
        )

    return True


def notify_sample_status(profile_id=str(), action="message", msg=str(), data={}, html_id=""):
    """
        function notifies client changes in Sample creation status
        :param profile_id:
        :param action:
        :param msg:
        :return:
    """
    # type points to the object type which will be passed to the socket and is a method defined in consumer.py
    group_name = 'sample_status_%s' % profile_id
    event = {"type": "msg", "action": action, "message": msg, "data": data, "html_id": html_id}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        event
    )
    return True


def notify_frontend(action="message", msg=str(), data={}, html_id="", profile_id=""):
    """
        function notifies client changes in Sample creation status
        :param profile_id:
        :param action:
        :param msg:
        :return:
    """
    # type points to the object type which will be passed to the socket and is a method defined in consumer.py
    group_name = 'dtol_status'
    event = {"type": "msg", "action": action, "message": msg, "data": data, "html_id": html_id}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        event
    )
    return True

def notify_transfer_status(profile_id=str(), submission_id=str(), status_message=str()):
    """
    function notifies client of ENA file transfer status
    :param profile_id:
    :param submission_id:
    :param status_message:
    :return:
    """

    if submission_id and profile_id:
        event = dict(type='file_transfer_status')
        event["submission_id"] = submission_id
        event["status_message"] = status_message

        group_name = 'submission_status_%s' % profile_id

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            event
        )

    return True


def schedule_file_transfer(submission_id=str(), remote_location=str()):
    """
    function schedules transfer of files associated with a submission to ENA Dropbox's /remote_location
    :param submission_id:
    :param remote_location:
    :return:
    """

    if not submission_id:
        message = 'Error scheduling file transfer. Submission identifier not found!.'
        log_general_error(message)
        return False

    transfer_handle = get_filetransfer_queue_handle()
    doc = transfer_handle.find_one({"submission_id": submission_id})

    submission_record = get_submission_handle().find_one(
        {'_id': ObjectId(submission_id)}, {"profile_id": 1})

    if not doc:  # submission not in queue, add to queue
        fields = dict(
            submission_id=submission_id,
            remote_location=remote_location,
            date_modified=d_utils.get_datetime(),
            processing_status='pending'  # pending or running
        )

        transfer_handle.insert(fields)
        message = 'Submission data files scheduled for upload.'

        status_message = 'Submission data files scheduled for upload. Progress will be reported.'
        notify_transfer_status(profile_id=submission_record['profile_id'], submission_id=submission_id,
                               status_message=status_message)

    else:
        message = 'File transfer already scheduled for this submission.'

    logging_info(message, submission_id)

    return True


def get_ena_remote_files(user_token=str(), pass_word=str()):
    """
    function returns unsubmitted files in ENA's Dropbox
    :param user_token:
    :param pass_word:
    :return:
    """

    headers = {
        'accept': '*/*',
    }

    params = (
        ('format', 'json'),
        ('max-results', '50000'),
    )

    try:
        response = requests.get('https://wwwdev.ebi.ac.uk/ena/submit/report/unsubmitted-files', headers=headers,
                                params=params, auth=(user_token, pass_word))
    except Exception as e:
        log_general_error('API call error ' + str(e))
        return list()

    if not response.status_code == 200:
        return list()

    return response.json()


def get_study_status(user_token=str(), pass_word=str(), project_accession=str()):
    """
    function returns the status of a study from ENA
    :param user_token:
    :param pass_word:
    :param project_accession:
    :return:
    """

    headers = {
        'accept': '*/*',
    }

    params = (
        ('format', 'json'),
        ('max-results', '1'),
    )

    try:
        response = requests.get('https://wwwdev.ebi.ac.uk/ena/submit/report/projects/' + project_accession,
                                headers=headers,
                                params=params,
                                auth=(user_token, pass_word))
    except Exception as e:
        log_general_error('API call error ' + str(e))
        return list()

    if not response.status_code == 200:
        return list()

    return response.json()


def touch_files(file_paths=list()):
    """
    function creates empty files as specified in file_paths
    :param file_paths:
    :return:
    """

    for path in file_paths:
        try:
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write("TGAC")
        except Exception as e:
            log_general_error('Error touching file ' + path + ' ' + str(e))

    return True


def transfer_to_ena(webin_user, pass_word, remote_path, file_paths=list(), **kwargs):
    """
    function transfers files to ENA using Aspera CLI
    :param webin_user:
    :param pass_word:
    :param remote_path:
    :param file_paths:
    :param kwargs:
    :return:
    """

    submission_id = kwargs.get("submission_id", str())
    transfer_queue_id = kwargs.get("transfer_queue_id", str())  # set to True to enable status reporting
    report_status = kwargs.get("report_status", False)  # if status message should be sent via channels layer

    submission_collection_handle = get_submission_handle()
    transfer_collection_handle = get_filetransfer_queue_handle()

    if not file_paths:
        return True

    message = f'Commencing transfer of {len(file_paths)} data files to ENA. Progress will be reported.'
    logging_info(message, submission_id)

    resource_path = os.path.join(BASE_DIR, REPOSITORIES.get('ASPERA', dict()).get('resource_path', str()))
    os.chdir(resource_path)

    local_paths = ' '.join(file_paths)
    aspera_cmd = f'./ascp -d -QT -l700M -L- {local_paths} {webin_user}:{remote_path}'

    try:
        thread = pexpect.spawn(aspera_cmd, timeout=None)
        thread.expect(["assword:", pexpect.EOF])
        thread.sendline(pass_word)

        cpl = thread.compile_pattern_list([pexpect.EOF, '(.+)'])

        while True:
            i = thread.expect_list(cpl, timeout=None)
            if i == 0:  # signals end of transfer
                message = '[Submission: ' + submission_id + '] ' + "Updated remote path " + remote_path
                lg.log(message, level=Loglvl.INFO, type=Logtype.FILE)
                break
            elif i == 1:
                pexp_match = thread.match.group(1)
                tokens_to_match = ["LOG ======= end File Transfer statistics =======", "status=success"]

                if any(tm in pexp_match.decode("utf-8") for tm in tokens_to_match):
                    tokens = pexp_match.decode("utf-8")

                    # update transfer queue timestamp - useful for rescheduling of stalled transfers
                    if transfer_queue_id:
                        try:
                            transfer_record = transfer_collection_handle.find_one(
                                {'_id': ObjectId(transfer_queue_id)})
                        except Exception as e:
                            pass
                        else:
                            transfer_record['date_modified'] = d_utils.get_datetime()
                            transfer_collection_handle.update(
                                {"_id": ObjectId(str(transfer_record.pop('_id')))},
                                {'$set': transfer_record})

                    if 'status=success' in tokens and submission_id:  # per file success tracking
                        # update submission record
                        submission_record = submission_collection_handle.find_one(
                            {'_id': ObjectId(submission_id)}, {"bundle_meta": 1, "profile_id": 1})

                        profile_id = submission_record.get("profile_id", str())

                        target_files = [tk.split("=")[1].strip('"') for tk in tokens.split(" ") if
                                        tk[:5] == "file=" or tk[:7] == "source="]
                        target_files_meta = [x for x in submission_record['bundle_meta'] if
                                             x.get('file_path', str()) in target_files]

                        for file_meta in target_files_meta:
                            file_meta["upload_status"] = True

                        # push updates to client via to channels layer
                        if report_status:
                            total_files_in_bundle = len(submission_record['bundle_meta'])
                            total_transferred = [x for x in submission_record['bundle_meta'] if
                                                 x.get('upload_status', False) is True]

                            status_message = f"{len(total_transferred)}/{total_files_in_bundle}" \
                                             f" data files transferred..."
                            notify_transfer_status(profile_id=profile_id, submission_id=submission_id,
                                                   status_message=status_message)

                        submission_record = dict(bundle_meta=submission_record['bundle_meta'])
                        submission_collection_handle.update(
                            {"_id": ObjectId(submission_id)},
                            {'$set': submission_record})

                    if 'LOG ======= end File Transfer statistics =======' in tokens:
                        message = '[Submission: ' + submission_id + '] ' \
                                  + "Transfer to remote location " \
                                  + remote_path + " completed."
                        lg.log(message, level=Loglvl.INFO, type=Logtype.FILE)

        thread.close()
        return True
    except Exception as e:
        message = '[Submission: ' + submission_id + '] ' + 'File transfer error ' + str(e)
        lg.log(message, level=Loglvl.ERROR, type=Logtype.FILE)
        return False

    return True

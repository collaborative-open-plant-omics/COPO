__author__ = 'fshaw'

from dal.copo_da import ENAFileTransferObject, DataFile
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from datetime import datetime
from bson import ObjectId
from exceptions_and_logging.logger import Logger
import gzip
import hashlib
from submission.helpers.generic_helper import transfer_to_ena as to_ena
from tools import resolve_env
from datetime import datetime


def make_transfer_record(file_id, submission_id):
    # N.B. called from celery
    # make transfer object
    file = DataFile().get_record(file_id)
    tx = dict()
    tx["created"] = datetime.utcnow()
    tx["last_checked"] = datetime.utcnow()
    tx["remote_path"] = submission_id + "/reads/"
    tx["local_path"] = file["file_location"]
    tx["ecs_location"] = file["ecs_location"]
    tx["file_id"] = str(file["_id"])
    tx["profile_id"] = file["profile_id"]
    tx["status"] = "pending"
    tx["submission_id"] = submission_id
    # N.B. Transfer Status
    # 0 transfer complete
    # 1 check for presences of file on ecs
    # 2 transfer to COPO
    # 3 check for gzip
    # 4 check for md5
    # 5 transfer to ENA
    # 10 Error
    tx["transfer_status"] = 1
    print(tx)
    ENAFileTransferObject().ENAFileTransferObjectCollection.update_one({"local_path": file["file_location"]}, {"$set": tx}, upsert=True)


def check_for_stuck_transfers():
    # N.B. called from celery
    processing_tx = ENAFileTransferObject().get_processing_transfers()
    if processing_tx:
        for tx in processing_tx:
            '''
            check how long this has been processing. transfers can be allowed up to a day, but s3check, gzip and md5 should be quite quick, 
            so should be reset 
            to pending after a few minutes as they are probably stuck
            '''
            tx_status = tx["transfer_status"]
            chk = tx["last_checked"]
            delta = datetime.utcnow() - chk
            if tx_status in (1, 3, 4):
                # these are the processes which should be quick
                if delta.seconds > 60 / 1:
                    ENAFileTransferObject().set_pending(tx["_id"])
                    Logger().log("resetting to pending transfer: " + tx["local_path"])
            elif tx_status in (2, 5):
                # these are the processes which could take a long time so should have a much longer timeout
                if delta.seconds > 60 * 60 * 6:
                    ENAFileTransferObject().set_pending(tx["_id"])
                    Logger().log("resetting to pending transfer: " + tx["local_path"])


def process_pending_file_transfers():
    log = Logger()
    # get pending transfers
    docs = ENAFileTransferObject().get_pending_transfers()
    # N.B. Transfer Status
    # 0 transfer complete
    # 1 check for presences of file on ecs
    # 2 transfer to COPO
    # 3 check for gzip
    # 4 check for md5
    # 5 transfer to ENA
    if docs:
        for tx in docs:
            ENAFileTransferObject().set_processing(tx["_id"])

            tx_status = tx["transfer_status"]

            if tx_status == 1:
                # check if is on ECS
                chk = check_file_in_ecs(tx)
                if not chk:
                    # not much we can do here...this should not happen, just update last checked
                    record_error(tx, chk)
                    reset_status_counter(tx)
                else:
                    # no need to update last checked
                    increment_status_counter(tx)
                continue
            elif tx_status == 2:
                # transfer to COPO
                transfer_success = get_ecs_file(tx)
                try:
                    if transfer_success:
                        increment_status_counter(tx)
                    else:
                        record_error(tx, "error transfering file")
                        reset_status_counter(tx)
                except Exception as e:
                    record_error("error downloading from ecs: " + str(e))
                    reset_status_counter(tx)
            elif tx_status == 3:
                increment_status_counter(tx)
                pass
                '''
                if check_gzip(tx):
                    increment_status_counter(tx)
                else:
                    record_error(tx, "file not gzipped")
                    reset_status_counter(tx)
                '''
            elif tx_status == 4:
                if check_md5(tx):
                    increment_status_counter(tx)
                else:
                    reset_status_counter(tx)
            elif tx_status == 5:
                Logger().log("transfering to ENA: " + tx["local_path"])
                transfer_to_ena(tx)
                mark_complete(tx)


def record_error(tx, error):
    Logger().log(error)


def increment_status_counter(tx):
    tx["transfer_status"] = tx["transfer_status"] + 1
    tx["last_checked"] = datetime.utcnow()
    tx["status"] = "pending"
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def decrement_status_counter(tx):
    tx["transfer_status"] = tx["transfer_status"] - 1
    tx["last_checked"] = datetime.utcnow()
    tx["status"] = "pending"
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def mark_error(tx):
    tx["transfer_status"] = 10
    tx["last_checked"] = datetime.utcnow()
    tx["status"] = "error"
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def mark_complete(tx):
    tx["transfer_status"] = 0
    tx["last_checked"] = datetime.utcnow()
    tx["status"] = "complete"
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def reset_status_counter(tx):
    Logger().log("resetting: " + tx["local_path"])
    tx["transfer_status"] = 1
    tx["last_checked"] = datetime.utcnow()
    tx["status"] = "pending"
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def update_last_checked(tx):
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def get_ecs_file(tx):
    file = DataFile().get_collection_handle().find_one({"_id": ObjectId(tx["file_id"])})
    return s3().get_object(bucket=file["bucket_name"], key=file["file_name"], loc=tx["local_path"])


def check_file_in_ecs(tx):
    Logger().log("checking for file: " + tx["local_path"])
    file = DataFile().get_collection_handle().find_one({"_id": ObjectId(tx["file_id"])})
    return s3().check_s3_bucket_for_files(file["bucket_name"], [file["file_name"]])


def check_gzip(tx):
    Logger().log("checking gzip status: " + tx["local_path"])
    with gzip.open(tx["local_path"], 'r') as fh:
        try:
            fh.read(1)
            return True
        except OSError as e:
            return False


def check_md5(tx):
    Logger().log("checking md5: " + tx["local_path"])
    file = DataFile().get_collection_handle().find_one({"_id": ObjectId(tx["file_id"])})
    hash_md5 = hashlib.md5()
    with open(tx["local_path"], "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    calc = hash_md5.hexdigest()
    if calc == file["file_hash"]:
        return True
    else:
        Logger().log("md5 mismatch, should be: " + file["file_hash"] + ", but got: " + calc)
        return False


def transfer_to_ena(tx):
    # transfer_to_ena(webin_user, pass_word, remote_path, file_paths=list(), **kwargs):
    ena_service = resolve_env.get_env('ENA_SERVICE')
    pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
    user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
    webin_user = resolve_env.get_env('WEBIN_USER')
    webin_domain = resolve_env.get_env('WEBIN_USER').split("@")[1]
    # Logger().log("transfering file: " + tx["file_id"])
    kwargs = dict()
    try:
        to_ena(webin_user, pass_word, tx["remote_path"], [tx["local_path"]], **kwargs)
    except Exception as e:
        record_error("error transfering to ENA: " + str(e))
        reset_status_counter(tx)

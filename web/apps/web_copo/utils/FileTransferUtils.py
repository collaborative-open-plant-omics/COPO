__author__ = 'fshaw'

from dal.copo_da import ENAFileTransferObject, DataFile
from web.apps.web_copo.s3 import s3Connection as s3
from datetime import datetime


def make_transfer_record(file_id, submission_id):
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
    # N.B. Transfer Status
    # 0 transfer complete
    # 1 check for presences of file on ecs
    # 2 transfer to COPO
    # 3 check for gzip
    # 4 check for md5
    # 5 transfer to ENA
    tx["transfer_status"] = 1
    ENAFileTransferObject().ENAFileTransferObjectCollection.insert_one(tx)


def process_pending_file_transfers():
    # get pending transfers

    docs = ENAFileTransferObject().get_pending_transfers()
    # N.B. Transfer Status
    # 0 transfer complete
    # 1 check for presences of file on ecs
    # 2 transfer to COPO
    # 3 check for gzip
    # 4 check for md5
    # 5 transfer to ENA

    for tx in docs:
        ENAFileTransferObject().set_processing(tx["_id"])
        increment_status_counter(tx)
        tx_status = tx["transfer_status"]
        if tx_status == 1:
            # check if is on ECS
            if not check_file_in_ecs(tx):
                # not much we can do here...this should not happen, just update last checked
                decrement_status_counter(tx)
            else:
                # advanced status counter
                tx["transfer_status"] = tx_status + 1
                increment_status_counter(tx)
        if tx_status == 2:
    # transfer to COPO


def increment_status_counter(tx):
    tx["transfer_status"] = tx["transfer_status"] + 1
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update_one(tx)


def decrement_status_counter(tx):
    tx["transfer_status"] = tx["transfer_status"] - 1
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update_one(tx)


def update_last_checked(tx):
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update_one(tx)


def check_file_in_ecs(tx):
    file = DataFile().get_collection_handle().find({"_id": tx})
    return s3().check_s3_bucket_for_files(file["bucket_name"], [file["file_name"]])

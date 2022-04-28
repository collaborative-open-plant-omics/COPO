__author__ = 'fshaw'

from dal.copo_da import ENAFileTransferObject, DataFile
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from datetime import datetime
from bson import ObjectId

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
        tx_status = tx["transfer_status"]

        if tx_status == 1:
            # check if is on ECS
            if not check_file_in_ecs(tx):
                # not much we can do here...this should not happen, just update last checked
                update_last_checked(tx)
            else:
                # no need to update last checked
                increment_status_counter(tx)
            continue
        if tx_status == 2:
            # transfer to COPO
            transfer_success = get_object(tx)
            if transfer_success:
                increment_status_counter(tx)
            else:
                reset_status_counter(tx)

def increment_status_counter(tx):
    tx["transfer_status"] = tx["transfer_status"] + 1
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def decrement_status_counter(tx):
    tx["transfer_status"] = tx["transfer_status"] - 1
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def reset_status_counter(tx):
    tx["transfer_status"] = 1
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)

def update_last_checked(tx):
    tx["last_checked"] = datetime.utcnow()
    ENAFileTransferObject().ENAFileTransferObjectCollection.update({"_id": tx["_id"]}, tx)


def get_object(tx):
    file = DataFile().get_collection_handle().find_one({"_id": ObjectId(tx["file_id"])})
    return s3().get_object(bucket=file["bucket_name"], key=file["file_name"], loc=tx["local_path"])

def check_file_in_ecs(tx):
    file = DataFile().get_collection_handle().find_one({"_id": ObjectId(tx["file_id"])})
    return s3().check_s3_bucket_for_files(file["bucket_name"], [file["file_name"]])

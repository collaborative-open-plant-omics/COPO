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
    tx["status"] = "pending"
    tx["transfer_status"] = dict()
    tx["transfer_status"]["on_ecs"] = False
    tx["transfer_status"]["on_copo"] = False
    tx["transfer_status"]["on_ena"] = False
    tx["transfer_status"]["is_gzip"] = False
    tx["transfer_status"]["is_md5"] = False
    ENAFileTransferObject().ENAFileTransferObjectCollection.insert_one(tx)


def process_pending_file_transfers():
    # get pending transfers
    docs = ENAFileTransferObject().get_pending_transfers()
    for tx in docs:
        ENAFileTransferObject().set_processing(tx["_id"])
        tx_status = tx["transfer_status"]
        if not tx_status["on_ecs"]:
            # check if is on ECS
            if not check_file_in_ecs(tx):
                # not much we can do here...this should happen, just update last checked
                tx["status"] = "pending"
            else:
                tx["transfer_status"]["on_ecs"] = True
            tx["last_checked"] = datetime.utcnow()
            ENAFileTransferObject().ENAFileTransferObjectCollection.update_one(tx)


def check_file_in_ecs(tx):
    file = DataFile().get_collection_handle().find({"_id": tx})
    return s3().check_s3_bucket_for_files(file["bucket_name"], [file["file_name"]])

__author__ = 'fshaw'

from dal.copo_da import ENAFileTransferObject, DataFile


def make_transfer_record(file_id, submission_id):
    # make transfer object
    file = DataFile().get_record(file_id)
    tx = dict()
    tx["remote_path"] = submission_id + "/reads/"
    tx["local_path"] = file["file_location"]
    tx["file_id"] = str(file["_id"])
    tx["profile_id"] = file["profile_id"]
    tx["status"] = dict()
    tx["status"]["on_ecs"] = False
    tx["status"]["on_copo"] = False
    tx["status"]["on_ena"] = False
    tx["status"]["is_gzip"] = False
    ENAFileTransferObject().ENAFileTransferObjectCollection.insert_one(tx)

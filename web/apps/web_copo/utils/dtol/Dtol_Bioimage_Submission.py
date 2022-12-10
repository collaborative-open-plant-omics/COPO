from web.apps.web_copo.schemas.utils import data_utils
from exceptions_and_logging.logger import Logger
from pathlib import Path
from dal.copo_da import Submission, Source
from submission.helpers.generic_helper import notify_frontend
import subprocess
from bson import ObjectId
from web.apps.web_copo.lookup.copo_enums import Loglvl, Logtype
import os
from datetime import datetime, date
from django.conf import settings


def process_bioimage_pending_submission():
    # submit images
    submissions = Submission().get_bioimage_pending_submission()
    specimen_ids = []
    sub_ids = []
    now = data_utils.get_datetime()
    lastSubImageDt = {}
    imagePath = Path(settings.MEDIA_ROOT) / "sample_images"
    sentPath = imagePath / "sent"
    sentPath.mkdir(parents=True, exist_ok=True)

    if not submissions:
        return

    for sub in submissions:
        notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage submitting...", action="info",
                        html_id="dtol_sample_info")
        specimen_ids.extend(sub["dtol_specimen"])
        sub_ids.append(sub["_id"])

    sources = Source().get_sourcemap_by_specimens(specimen_ids)
    is_upload_needed = False
    for specimenId in specimen_ids:
        source = sources[specimenId]
        seqno = 0
        if "last_bioimage_submitted" in source and  source["last_bioimage_submitted"]:
            lastSubImageDt[specimenId] = source["last_bioimage_submitted"]
        if "bioimage_archive_seq_no" in source and source["bioimage_archive_seq_no"]:
            seqno = source["bioimage_archive_seq_no"]

        try:
            with os.scandir(imagePath) as ls:
                for imageFile in ls:
                    if imageFile.name.upper().startswith(specimenId + "-"):
                        # we have a match
                        if specimenId not in lastSubImageDt or os.path.getctime(imageFile) > datetime.timestamp(
                                lastSubImageDt[specimenId]):
                            newname = source["biosampleAccession"] + "_" + str(seqno+1) + os.path.splitext(imageFile)[1]
                            os.rename(imageFile.path, str(sentPath) + "/" + newname)
                            seqno = seqno + 1
                            if not is_upload_needed:
                                is_upload_needed = True
                            print(imageFile.name + " " + newname)
        finally:
            Source().add_fields({"last_bioimage_submitted": now,
                                     "bioimage_archive_seq_no": seqno,
                                     "date_modified": now}, source["_id"])

    curl_cmd = settings.BIOIMAGE_ASPERA_CMD
    Logger().log(curl_cmd)
    try:
        if len(os.listdir(sentPath)) > 0:
            output = subprocess.check_output(curl_cmd, shell=True)
            notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage submitted", action="info",
                            html_id="dtol_sample_info")
            Logger().log(output)
            # lg.log(output, level=Loglvl.INFO, type=Logtype.FILE)

    except subprocess.CalledProcessError as e:
        Logger().log(e.output, level=Loglvl.ERROR)
        notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage not submitted", action="error",
                        html_id="dtol_sample_info")
        # lg.log(e.output, level=Loglvl.ERROR, type=Logtype.FILE)
        print("error code", e.returncode, e.output)
        return

    #now = data_utils.get_datetime()
    Submission().get_collection_handle().update(
        {"_id" : {"$in": sub_ids}}, {"$set": {"dtol_specimen": [], "dtol_status":"complete", "date_modified": now}}
    )


from web.apps.web_copo.schemas.utils import data_utils
from exceptions_and_logging.logger import Logger
from pathlib import Path
from dal.copo_da import Submission, Source, DataFile
from submission.helpers.generic_helper import notify_frontend
import subprocess
from web.apps.web_copo.lookup.copo_enums import Loglvl, Logtype
import os
from datetime import datetime, timedelta
from django.conf import settings
from tools import resolve_env

BIOIMAGE_SERVER = resolve_env.get_env("BIOIMAGE_SERVER")  # "bsaspera_w@hx-fasp-1.ebi.ac.uk"
BIOIMAGE_UPLOAD_PATH = resolve_env.get_env("BIOIMAGE_PATH")  # "/.beta/91/31c15a-f0a0-4847-ab09-4135cefc03bd-a31912"
BIOIMAGE_LOCAL_ARCHIVE_PATH = f"{resolve_env.get_env('MEDIA_PATH')}sample_images/archive/sent"
BIOIMAGE_PATH = f"{settings.MEDIA_ROOT}sample_images"
BIOIMAGE_ARCHIVE = f"{BIOIMAGE_PATH}/archive"
BIOIMAGE_SENT = f"{BIOIMAGE_PATH}/sent"
BIOIMAGE_THUMBNAIL = f"{BIOIMAGE_PATH}/thumbnail"

ASCP_PATH = "/home/osboxes/.aspera/cli"
BIOIMAGE_ASPERA_CMD = f"{ASCP_PATH}/bin/ascp -P33001 -l700M --move-after-transfer  {BIOIMAGE_ARCHIVE} -i {ASCP_PATH}/etc/asperaweb_id_dsa.openssh -d {BIOIMAGE_SENT} {BIOIMAGE_SERVER}:{BIOIMAGE_UPLOAD_PATH}"


def housekeeping_bioimage_archive():
    housekeep_timestamp = datetime.timestamp(datetime.now() + timedelta(days=-30))
    with os.scandir(BIOIMAGE_ARCHIVE+"/sent") as ls:
        for file in ls:
            if os.path.getctime(file) < housekeep_timestamp:
                os.remove(file)

def process_bioimage_pending_submission():
    # submit images
    submissions = Submission().get_bioimage_pending_submission()
    specimen_ids = []
    sub_ids = []
    now = data_utils.get_datetime()
    lastSubImageDt = {}
    #imagePath = Path(settings.MEDIA_ROOT) / "sample_images"
    #sentPath = imagePath / "sent"

    Path(BIOIMAGE_SENT).mkdir(parents=True, exist_ok=True)

    if not submissions:
        return

    for sub in submissions:
        notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage submitting...", action="info",
                        html_id="dtol_sample_info")
        specimen_ids.extend(sub["dtol_specimen"])
        sub_ids.append(sub["_id"])

    sources = Source().get_sourcemap_by_specimens(specimen_ids)
    for specimenId in specimen_ids:
        source = sources[specimenId]
        seqno = 0
        #if "last_bioimage_submitted" in source and  source["last_bioimage_submitted"]:
        #    lastSubImageDt[specimenId] = source["last_bioimage_submitted"]
        if "bioimage_archive_seq_no" in source and source["bioimage_archive_seq_no"]:
            seqno = source["bioimage_archive_seq_no"]
        try:
            with os.scandir(BIOIMAGE_PATH) as ls:
                for imageFile in ls:
                    if imageFile.name.upper().startswith(specimenId + "-"):
                        # we have a match
                        ##if specimenId not in lastSubImageDt or os.path.getctime(imageFile) > datetime.timestamp(
                        ##        lastSubImageDt[specimenId]):
                        newname = source["biosampleAccession"] + "_" + str(seqno+1) + os.path.splitext(imageFile)[1]
                        DataFile().update_bioimage_name(imageFile.name, newname, f"{BIOIMAGE_LOCAL_ARCHIVE_PATH}/{newname}")
                        os.rename(imageFile.path, Path(BIOIMAGE_SENT) / newname)
                        try:
                            os.remove(f"{BIOIMAGE_THUMBNAIL}/{imageFile.name}")
                        except FileNotFoundError as e:
                            Logger().log(e, level=Loglvl.ERROR)
                        seqno = seqno + 1
                        print(imageFile.name + " " + newname)
        finally:
            Source().add_fields({"last_bioimage_submitted": now,
                                     "bioimage_archive_seq_no": seqno,
                                     "date_modified": now}, source["_id"])

    if len(os.listdir(BIOIMAGE_SENT)) > 0:
        try:
            Logger().log(BIOIMAGE_ASPERA_CMD, level=Loglvl.DEBUG)
            output = subprocess.check_output(BIOIMAGE_ASPERA_CMD, shell=True)
            notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage submitted", action="info",
                            html_id="dtol_sample_info")
            Logger().log(output)
        except subprocess.CalledProcessError as e:
            Logger().log(e.output, level=Loglvl.ERROR)
            Logger().log("bioimage not submitted", level=Loglvl.ERROR)
            notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage not submitted due to error",
                            action="error",
                            html_id="dtol_sample_info")
            print("error code", e.returncode, e.output)
            return
    else:
        notify_frontend(data={"profile_id": sub["profile_id"]}, msg="Bioimage not submitted", action="info",
                        html_id="dtol_sample_info")



    #now = data_utils.get_datetime()
    Submission().get_collection_handle().update(
        {"_id" : {"$in": sub_ids}}, {"$set": {"dtol_specimen": [], "dtol_status":"complete", "date_modified": now}}
    )


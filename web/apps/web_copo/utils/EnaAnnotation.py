import os
from shutil import rmtree
from pathlib import Path

from django.conf import settings
from django_tools.middlewares import ThreadLocal

from tools import resolve_env

from dal.copo_da import Sequnece_annotation, Submission, DataFile, ENAFileTransferObject
from exceptions_and_logging.logger import Logger
from django.contrib import messages
import glob
from submission.helpers import generic_helper as ghlper
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from django.http import HttpResponse
from os.path import join
from web.apps.web_copo.schemas.utils import data_utils
from pymongo import ReturnDocument
import web.apps.web_copo.utils.FileTransferUtils as tx
import xml.etree.ElementTree as ET
import requests
from exceptions_and_logging import logger
import json
from bson import ObjectId

l = logger.Logger("exceptions_and_logging/logs") 
pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
ena_v2_service_async = resolve_env.get_env("ENA_V2_SERVICE_ASYNC")


def validate_annotation(form_data,formset, profile_id):
    request = ThreadLocal.get_current_request()
    bucket_name = str(request.user.id) + "_" + request.user.username
    username = request.user.username

    form_data["profile_id"] = profile_id  
    s3obj = s3()
    dt = data_utils.get_datetime()
    files = []
    file_ids = []
    file_types = {}

    for f in formset:
        formset_data = f.cleaned_data
        f_name = formset_data.get("file","").strip()   
        if f_name:
            if f_name not in files:
                if formset_data["type"] == "gff":
                    if not f_name.endswith(".gff"):
                        return {"error": f'File {f_name} should be ended with .gff'}
                files.append( f_name)
                file_types[f_name] = formset_data["type"]
            else:
                return {"error": f'File {f_name} is duplicated, please make sure file names are unique'}
            
    if len(files) == 0:
        return {"error": 'At least one annotation file is required'}

    if s3obj.check_for_s3_bucket(bucket_name):
        # get filenames from manifest

        s3_file_etags = s3obj.check_s3_bucket_for_files(bucket_name=bucket_name, file_list=files)
        # check for files
        if not s3_file_etags:
            # error message has been sent to frontend by check_s3_bucket_for_files so return so prevent ena.collect() from running
            return {"error": 'Files not found, please upload files to COPO and try again'}

    else:
        # bucket is missing, therefore create bucket and notify user to upload files
        ghlper.notify_annotation_status(data={"profile_id": profile_id},
                msg="s3 bucket not found, creating it",
                action="info",
                html_id="annotation_info")
       
        s3obj.make_s3_bucket(bucket_name=bucket_name)
        msg='Files not found, please click "Upload Data into COPO" and follow the instructions',
        ghlper.notify_annotation_status(data={"profile_id": profile_id},
            msg= msg,
            action="info",
            html_id="annotation_info")
        return {"error": msg}


    sub = Submission().get_collection_handle().find_one({"profile_id": profile_id, "deleted": {"$ne": data_utils.get_deleted_flag()}})
 
    if not sub:
        sub = dict()
        sub["date_created"] = dt
        sub["date_modified"] = dt
        sub["repository"] = "ena"
        sub["accessions"] = dict()
        sub["profile_id"] = profile_id
        sub["deleted"] = data_utils.get_not_deleted_flag()
        sub_id = Submission().get_collection_handle().insert_one(sub).inserted_id
    else :
        sub_id = sub["_id"]   

    for f_name in files:
        df = dict()
        df["file_name"] = f_name
        df["ecs_location"] = str(request.user.id) + "_" + request.user.username + "/" + f_name
        file_location = join(settings.UPLOAD_PATH, username, f_name)
        df["file_location"] = file_location
        df["name"] = f_name
        df["file_id"] = "NA"
        df["file_hash"] = s3_file_etags[f_name]
        df["deleted"] = data_utils.get_not_deleted_flag()
        df["date_created"] = dt
        df["type"] = file_types[f_name]
        inserted = DataFile().get_collection_handle().find_one_and_update({"file_location": file_location},
                                                                            {"$set": df}, upsert=True,
                                                                            return_document=ReturnDocument.AFTER)        
        tx.make_transfer_record(file_id=str(inserted["_id"]), submission_id=str(sub_id))
        file_ids.append(str(inserted["_id"]))
    form_data["files"] = file_ids
    annotation_rec = Sequnece_annotation().save_record(auto_fields={},**form_data)    

    #schedule annotation submission in SubmisisonCollection

    Submission().make_seq_annotation_submission_uploading(sub_id, str(annotation_rec["_id"]))
    return {"success": "Annotation has been scheduled, you will be notified when it is complete"}

def build_submission_dom(seq_annotation):
    """
    <SUBMISSION_SET>
    <SUBMISSION>
   <ACTIONS>
      <ACTION>
         <ADD/>
      </ACTION>
    </ACTIONS>
    </SUBMISSION>
    </SUBMISSION_SET>
    """
    action_str = "ADD"
    if seq_annotation.get("accessions",""):
        action_str = "MODIFY"
    submission_set = ET.Element("SUBMISSION_SET")
    submission = ET.SubElement(submission_set, "SUBMISSION")
    actions = ET.SubElement(submission, "ACTIONS")
    action = ET.SubElement(actions, "ACTION")
    add = ET.SubElement(action, action_str)
    return submission_set

def build_analysis_dom(seq_annotation, sub):
    """
    <ANALYSIS_SET>
    <ANALYSIS alias="YF3059">
        <TITLE>Y chromosome sequence STR analysis using lobSTR</TITLE>
        <DESCRIPTION>Y chromosome sequence STR analysis using lobSTR</DESCRIPTION>
        <STUDY_REF accession="ERP011288"/>
        <SAMPLE_REF accession="ERS1023190"/>
        <RUN_REF accession="ERR1198112"/>
        <ANALYSIS_TYPE>
            <SEQUENCE_ANNOTATION/>
        </ANALYSIS_TYPE>
        <FILES>
            <FILE filename="STR_for_YF03059_20151228.tab.gz" filetype="tab" checksum_method="MD5"
                checksum="9f2976d079c10b111669b32590d1eb3e"/>
        </FILES>
    </ANALYSIS>
</ANALYSIS_SET>
    """
    if seq_annotation:
        analysis_set = ET.Element("ANALYSIS_SET")
        analysis = ET.SubElement(analysis_set, "ANALYSIS", alias=str(seq_annotation["_id"]))
        ET.SubElement(analysis, "TITLE").text = seq_annotation["title"]
        ET.SubElement(analysis, "DESCRIPTION").text = seq_annotation["description"]
        ET.SubElement(analysis, "STUDY_REF").set("accession", seq_annotation["study"])
        ET.SubElement(analysis, "SAMPLE_REF").set("accession", seq_annotation["sample"])
        for run in seq_annotation.get("runs", []):
            ET.SubElement(analysis, "RUN_REF").set("accession", run)
        for experiment in seq_annotation.get("experiments", []):
            ET.SubElement(analysis, "EXPERIMENT_REF").set("accession", experiment)            
        analysis_type = ET.SubElement(analysis, "ANALYSIS_TYPE")
        ET.SubElement(analysis_type, "SEQUENCE_ANNOTATION")
        files = ET.SubElement(analysis, "FILES")
        for f in seq_annotation["files"]:
            file = DataFile().get_record(f)
            if file:
                file_elm = ET.SubElement(files, "FILE")
                file_elm.set("filename", f'{str(sub["_id"])}/reads/{file["file_name"]}')
                file_elm.set("filetype", file["type"])
                file_elm.set("checksum_method","MD5")
                file_elm.set("checksum", file["file_hash"])

        return  analysis_set


def reset_seq_annotation_submission_status(sub_id):
    doc = Submission().get_collection_handle().find_one({"_id": sub_id})
    l = len(doc["seq_annotations"])
    if l > 0:
        status = "pending"
    else:
        status = "complete"
    Submission().get_collection_handle().update({"_id": sub_id}, {"$set": {"seq_annotation_status": status}})

def submit_ena_dtol_v2(submission_dom, analysis_dom, sub, seq_annotation):
    webin = ET.Element("WEBIN")
    webin.append(submission_dom)
    webin.append(analysis_dom)
    xml_str = ET.tostring(webin, encoding='utf8', method='xml')
    l.debug(xml_str)
    files = {'file': xml_str}

    with requests.Session() as session:    
        session.auth = (user_token, pass_word)    
        try:
            response = session.post(ena_v2_service_async, data={},files = files)
            receipt = response.text
            l.log("ENA RECEIPT " + receipt)
            print(receipt)
            if response.status_code == requests.codes.ok:
                #receipt = subprocess.check_output(curl_cmd, shell=True)
                return handle_async_receipt(receipt, sub, seq_annotation )
            else:
                l.log("General Error " + requests.status_codes)
                message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + ena_v2_service_async
                ghlper.notify_annotation_status(data={"profile_id": sub["profile_id"]}, msg=message, action="error",
                                html_id="annotation_info")
                reset_seq_annotation_submission_status(sub["_id"])
        except ET.ParseError as e:
            l.exception(e)
            message = " Unrecognized response from ENA - " + str(
                receipt) + " Please try again later, if it persists contact admins"
            ghlper.notify_annotation_status(data={"profile_id": sub["profile_id"]}, msg=message, action="error",
                            html_id="annotation_info")
            reset_seq_annotation_submission_status(sub["_id"])
            return False
        except Exception as e:
            l.exception(e)
            message = 'API call error ' + "Submitting project xml to ENA via CURL. href is: " + ena_v2_service_async
            ghlper.notify_annotation_status(data={"profile_id": sub["profile_id"]}, msg=message, action="error",
                            html_id="annotation_info")
            reset_seq_annotation_submission_status(sub["_id"])
            return False


def handle_async_receipt(receipt, sub, seq_annotation):
    result = json.loads(receipt)
    submission_id = result["submissionId"]
    href = result["_links"]["poll"]["href"]
    return Submission().update_seq_annotation_submission_async(sub["_id"], href, [str(seq_annotation["_id"])], submission_id)


def process_seq_annotation_pending_submission():
    # submit images
    submissions = Submission().get_seq_annotation_pending_submission()
   #sub_ids = []
    if not submissions:
        return

    for sub in submissions:
        ghlper.notify_annotation_status(data={"profile_id": sub["profile_id"]},
                msg="Sequence annotation submitting...",
                action="info",
                html_id="annotation_info")
        #sub_ids.append(sub["_id"])
        for seq_annotation_id in sub["seq_annotations"]:
            seq_annotation = Sequnece_annotation().get_record(seq_annotation_id)
            submission_dom = build_submission_dom(seq_annotation)
            analysis_dom = build_analysis_dom(seq_annotation, sub)
            submit_ena_dtol_v2(submission_dom,  analysis_dom, sub, seq_annotation)


def poll_asyn_seq_annotation_submission_receipt():
    submissions = Submission().get_async_seq_annotation_submission()

    with requests.Session() as session:
        session.auth = (user_token, pass_word)    
        for submission in submissions:
            for seq_annotation_sub in submission["seq_annotation_submission"]:
                accessions = ""
                response = session.get(seq_annotation_sub["href"])
                if response.status_code == requests.codes.accepted:
                    continue
                elif response.status_code == requests.codes.ok:
                    l.log("ENA RECEIPT " + response.text)
                    try:
                        tree = ET.fromstring(response.text)
                        accessions = handle_submit_receipt(  submission, tree, seq_annotation_sub["id"])
                    except ET.ParseError as e:
                        l.log("Unrecognized response from ENA " + str(e))
                        message = " Unrecognized response from ENA - " + str(
                            response.content) + " Please try again later, if it persists contact admins"
                        ghlper.notify_annotation_status(data={"profile_id": submission["profile_id"]}, msg=message, action="error",
                                        html_id="annotation_info")
                        continue
                    except Exception as e:
                        l.exception(e)
                        message = 'API call error ' + "Submitting project xml to ENA via CURL. href is: " + seq_annotation_sub["href"]
                        ghlper.notify_annotation_status(data={"profile_id": submission["profile_id"]}, msg=message, action="error",
                                        html_id="annotation_info")
                        continue

                    if not accessions:
                        ghlper.notify_annotation_status(data={"profile_id": submission["profile_id"]}, msg="Error creating sample - no accessions found",
                                        action="info",
                                        html_id="annotation_info")
                        continue
                    elif accessions["status"] == "ok":
                        msg = "Last Sequence Annotation Submitted:  - Seq Annotation Access: " + ','.join(str(x["accession"]) for x in accessions["accession"])   # + " - Biosample ID: " + accessions["biosample_accession"]
                        ghlper.notify_annotation_status(data={"profile_id": submission["profile_id"]}, msg=msg, action="info",
                                        html_id="annotation_info")


                    else:
                        msg = "Sequence Annotation Submission Rejected: <p>" + accessions["msg"] + "</p>"
                        ghlper.notify_annotation_status(data={"profile_id": submission["profile_id"]}, msg=msg, action="error",
                                        html_id="annotation_info")
                        Submission().update_seq_annotation_submission(sub_id=str(submission["_id"]), submission_id=seq_annotation_sub["id"])

                    #ghlper.notify_annotation_status(data={"profile_id": submission["profile_id"]}, msg="", action="hide_sub_spinner",
                    #            html_id="annotation_info")

def handle_submit_receipt( sub, tree, seq_annotation_sub_id):
    success_status = tree.get('success')
    if success_status == 'false':
        msg = ""
        error_blocks = tree.find('MESSAGES').findall('ERROR')
        for error in error_blocks:
            msg += error.text + "<br>"
        if not msg:
            msg = "Undefined error"
        status = {"status": "error", "msg": msg}
        # print(status)
        ghlper.notify_annotation_status(data={"profile_id": sub["profile_id"]}, msg=msg, action="error",
            html_id="annotation_info")
        Submission().update_seq_annotation_submission_error(str(sub["_id"]), seq_annotation_sub_id, msg)
        l.error(msg)
        return status
    else:
        # retrieve id and update record
        # return get_biosampleId(receipt, sample_id, collection_id)
        return get_accession(tree, sub["_id"], seq_annotation_sub_id)
    
def get_accession(tree, sub_id, submission_id):
    '''parsing ENA sample bundle accessions from receipt and
    storing in sample and submission collection object'''
    #tree = ET.fromstring(receipt)
    annotation_accession = Submission().get_collection_handle().find_one({"_id": ObjectId(sub_id)},{"accessions.seq_annotations.accession": 1})
    submission_accession = []

    for child in tree.iter():
        if child.tag == 'ANALYSIS':
            seq_annotation_id = child.get('alias')
            accession = child.get('accession')
                                  
            Sequnece_annotation().add_accession(seq_annotation_id, accession)
            if accession not in annotation_accession:
                submission_accession.append({"alias": seq_annotation_id, "accession": accession})
    if submission_accession:
        Submission().add_annotation_accessions(sub_id, submission_accession)
        Submission().update_seq_annotation_submission(sub_id, submission_id=submission_id)
 
    accessions = {"accession": submission_accession, "status": "ok"}
    return accessions

def update_seq_annotation_submission_pending():
    subs = Submission().get_seq_annotation_file_uploading()
    all_uploaded_sub_ids = []
    for sub in subs:
        all_file_uploaded = True
        for seq_annotation_id in sub["seq_annotations"]:
            seq_annotation = Sequnece_annotation().get_record(seq_annotation_id)
            for f in seq_annotation["files"]:
                enaFile = ENAFileTransferObject().get_collection_handle().find_one({"file_id": ObjectId(f), "profile_id": sub["profile_id"]})
                if enaFile:
                    if enaFile["status"] != "complete":
                        all_file_upload = False
                        break
                else:
                    """it should not happen"""    
                    l.error("file not found " + f )
        if all_file_uploaded:
            all_uploaded_sub_ids.append(sub["_id"])

    if all_uploaded_sub_ids:
        Submission().update_seq_annotation_submission_pending(all_uploaded_sub_ids)
import os
from shutil import rmtree
from pathlib import Path
from django.shortcuts import render
import subprocess
import re
from submission.helpers.generic_helper import notify_frontend
from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal

from tools import resolve_env

from dal.copo_da import Assembly, Submission, DataFile, EnaFileTransfer
from exceptions_and_logging.logger import Logger
from submission.helpers import generic_helper as ghlper
from bson import ObjectId
import web.apps.web_copo.templatetags.html_tags as htags
from os.path import join
from web.apps.web_copo.schemas.utils import data_utils
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from pymongo import ReturnDocument
import web.apps.web_copo.utils.FileTransferUtils as tx
from exceptions_and_logging.logger import Logger
import glob
l = Logger()

# other types of assemblies (not individualss or cultured isolates):
# Metagenome Assembly - Primary Metagenome Assemblies: the diff is the types of samples, an additional virtual sample
# needs to be registered, the rest of the submission is the same. Assembly type is  ‘primary metagenome’
# Metagenome Assembly - Binned Metagenome Assemblies: as above, Assembly type is ‘binned metagenome’
# Metagenome Assembly - A Metagenome-Assembled Genome (MAG): as above, Assembly type is ‘Metagenome-Assembled Genome
# (MAG)’
# Environmental Single-Cell Amplified Genomes: as above, Assembly type is  ‘Environmental Single-Cell Amplified Genome
# (SAG)’
# Transcriptome Assemblies: here the webin-cli command is different as -context transcriptome (instead of genome),
# assembly type is ‘isolate’, there are no fields [coverage, mingaplength, moleculetype] in the manifest, and the only
# file types allowed are FASTA and flatfile
# Metatranscriptome Assemblies: as transcriptome assembly

pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
ena_service = resolve_env.get_env('ENA_SERVICE')

def upload_assembly_files(files):
    assembly_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files"
    request = ThreadLocal.get_current_request()
    profile_id = request.session["profile_id"]
    these_assemblies = assembly_path / profile_id
    if os.path.isdir(these_assemblies):
        #todo maybe remove this depending on the decision if keeping the reports and about multiple assemblies per project
        rmtree(these_assemblies)
    these_assemblies.mkdir(parents=True)

    write_path = Path(these_assemblies)
    for f in files:
        file = files[f]

        file_path = write_path / file.name
        file_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files" / profile_id / file.name
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        filename = os.path.splitext(file.name)[0].upper()

    # save to session
    request = ThreadLocal.get_current_request()
    output = "done"
    return output

def validate_assembly(form, profile_id, assembly_id):
    #check assemblyname unique
    form["assemblyname"] = '_'.join(form["assemblyname"].split())
    conditions = {"assemblyname" : form["assemblyname"]}
    if assembly_id:
        conditions["_id"] = {"$ne" : ObjectId(assembly_id)}
    ass = Assembly(profile_id = profile_id).execute_query(conditions)

    if len(ass) > 0:
        msg = "AssemblyName " + form["assemblyname"] + " already exists "
        return {"error": msg}
    
    s3obj = s3()
    dt = data_utils.get_datetime()
    request = ThreadLocal.get_current_request()
    bucket_name = str(request.user.id) + "_" + request.user.username
    these_assemblies = join(settings.MEDIA_ROOT, "ena_assembly_files", profile_id)
    these_assemblies_url_path = f"{settings.MEDIA_URL}ena_assembly_files/{profile_id}"
    manifest_content =""
    file_fields = ["fasta", "flatfile", "agp", "chromosome_list", "unlocalised_list"]
    file_ids = []


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

    files = []
    for field in file_fields:
        if not form[field]:
            continue
        files.append(form[field])

    if not files:   
        return {"error": "At least one assembly file is required"}


    if s3obj.check_for_s3_bucket(bucket_name):
        # get filenames from manifest

        s3_file_etags = s3obj.check_s3_bucket_for_files(bucket_name=bucket_name, file_list=files)
        # check for files
        if not s3_file_etags:
            # error message has been sent to frontend by check_s3_bucket_for_files so return so prevent ena.collect() from running
            return {"error": 'Files not found, please upload files to COPO and try again'}


    for field in file_fields:
        if not form[field]:
            continue
        
        file_location = join(these_assemblies, form[field])
        df = DataFile().get_collection_handle().find_one({"file_location": file_location, "deleted": {"$ne": data_utils.get_deleted_flag()}})
        if df and df["file_hash"] == s3_file_etags[form[field]]:
            file_ids.append(str(df["_id"]))
            continue

        df = dict()
        df["file_name"] = form[field]
        df["ecs_location"] = ""
        df["bucket_name"] = bucket_name
        df["file_location"] = file_location
        df["name"] = form[field]
        df["file_id"] = "NA"
        df["file_hash"] = s3_file_etags[form[field]]
        df["deleted"] = data_utils.get_not_deleted_flag()
        df["date_created"] = dt
        df["type"] = field
        df["profile_id"] = profile_id
        inserted = DataFile().get_collection_handle().find_one_and_update({"file_location": file_location},
                                                                            {"$set": df}, upsert=True,
                                                                            return_document=ReturnDocument.AFTER)        
        tx.make_transfer_record(file_id=str(inserted["_id"]), submission_id=str(sub_id))
        file_ids.append(str(inserted["_id"]))

    form["files"] = file_ids
    form["profile_id"] = profile_id
    assembly_rec = Assembly().save_record(auto_fields={},**form, target_id=assembly_id)
    table_data = htags.generate_table_records(profile_id, "assembly", None)

    if not assembly_id or not assembly_rec["accession"]:
        result = Submission().make_assembly_submission_uploading(sub_id, [str(assembly_rec["_id"])])
        if result["status"] == "error":
            return {"success": "Assembly has been saved but not scheduled to submit as the submission is already in progress. <b>Please submit it later</b>", "table_data": table_data, "component": "assembly"}                 
        else:
            return {"success": "Assembly submission has been scheduled!", "table_data": table_data, "component": "assembly"}
    else:
        return {"success": "Assembly has been updated but no submission", "table_data": table_data, "component": "assembly"}                 



def _submit_assembly(file_path, profile_id):
    test = ""
    if "dev" in ena_service:
        test = " -test "
    webin_cmd = "java -Xmx6144m -jar webin-cli.jar -username " + user_token + " -password '" + pass_word + "'" + test + " -context genome -manifest " + str(
        file_path) + " -submit -ascp"
    Logger().debug(msg=webin_cmd)
    # print(webin_cmd)
    # try/except as it turns out this can fail even if validate is successfull
    try:
        Logger().log(msg="submitting assembly")
        ghlper.notify_assembly_status(data={"profile_id": profile_id},
                        msg="Submitting Assembly",
                        action="info",
                        html_id="assembly_info")
        output = subprocess.check_output(webin_cmd, shell=True)
        Logger().debug(output)
    except subprocess.CalledProcessError as cpe:
        output = cpe.stdout
    output = output.decode("ascii")
    Logger().debug(msg=output)

    #todo delete files after successfull submission
    #todo decide if keeping manifest.txt and store accession in assembly objec too
    return output

def update_assembly_submission_pending():
    subs = Submission().get_assembly_file_uploading()
    all_uploaded_sub_ids = []
    for sub in subs:
        all_file_uploaded = True
        for assembly_id in sub["assemblies"]:
            assembly = Assembly().get_record(assembly_id)
            if not assembly:
                Submission().update_assembly_submission(sub_id=str(sub["_id"]), assembly_id= assembly_id)
                continue
            for f in assembly["files"]:
                enaFile = EnaFileTransfer().get_collection_handle().find_one({"file_id": f, "profile_id": sub["profile_id"]})
                if enaFile:
                    if enaFile["status"] != "complete":
                        all_file_uploaded = False
                        break
                else:
                    """it should not happen"""    
                    Logger().error("file not found " + f )
        if all_file_uploaded:
            all_uploaded_sub_ids.append(sub["_id"])

    if all_uploaded_sub_ids:
        Submission().update_assembly_submission_pending(all_uploaded_sub_ids)

def process_assembly_pending_submission():
    # submit images
    submissions = Submission().get_assembly_pending_submission()
   #sub_ids = []
    if not submissions:
        return
    file_fields = ["fasta", "flatfile", "agp", "chromosome_list", "unlocalised_list"]
    ena_fields = []
    for x in Assembly().get_schema().get("schema_dict"):
        if x.get("ena_assembly_submisison", False):
            ena_fields.append(x["id"].split(".")[-1])

    for sub in submissions:
        ghlper.notify_assembly_status(data={"profile_id": sub["profile_id"]},
                msg="Assembly submitting...",
                action="info",
                html_id="assembly_info")
        these_assemblies = join(settings.MEDIA_ROOT, "ena_assembly_files", sub["profile_id"])
        these_assemblies_url_path = f"{settings.MEDIA_URL}ena_assembly_files/{sub['profile_id']}"

        for assembly_id in sub["assemblies"]:
            assembly = Assembly().get_record(assembly_id)
            if not assembly:
                l.log("Assembly not found " + assembly_id)
                message = " Assembly not found " + assembly_id
                ghlper.notify_assembly_status(data={"profile_id": sub["profile_id"]}, msg=message, action="error",
                                html_id="assembly_info")   
                Submission().update_assembly_submission(sub_id=str(sub["_id"]),  assembly_id=assembly_id)             
                continue
            
            manifest_content = ""


            for field in ena_fields:
                value = assembly.get(field, None)
                if value:
                    if field in file_fields:
                        manifest_content += field.upper() + "\t" + join(these_assemblies, value) + "\n"
                    else:
                        manifest_content += field.upper() + "\t" + str(value) + "\n"
                    
            manifest_path = join(these_assemblies, "manifest.txt")
            with open(manifest_path, "w") as destination:
                destination.write(manifest_content)
            #verify submission
            test = ""
            if "dev" in ena_service:
                test = " -test "
            #cli_path = "tools/reposit/ena_cli/webin-cli.jar"
            webin_cmd = "java -Xmx6144m -jar webin-cli.jar -username " + user_token + " -password '" + pass_word + "'" + test + " -context genome -manifest " + str(
                manifest_path) + " -validate -ascp"
            Logger().debug(msg=webin_cmd)
            #print(webin_cmd)
            try:
                Logger().log(msg='validating assembly submission')
                ghlper.notify_assembly_status(data={"profile_id": sub["profile_id"]},
                                msg="Validating Assembly Submission",
                                action="info",
                                html_id="assembly_info")
                output = subprocess.check_output(webin_cmd, shell=True)
                Logger().debug(output)
                output = output.decode("ascii")
            except subprocess.CalledProcessError as cpe:
                return_code = cpe.returncode
                output = cpe.stdout
                output = output.decode("ascii") + " ERROR return code " + str(return_code)

            Submission().update_assembly_submission(sub_id=str(sub["_id"]), assembly_id=assembly_id)
            Logger().debug(msg=output)
            #print(output)
            #todo decide if keeping or deleting these files
            #report is being stored in webin-cli.report and manifest.txt.report so we can get errors there
            if not "ERROR" in output:
                output = _submit_assembly(str(manifest_path), sub["profile_id"])
                if "ERROR" in output:
                    #handle possibility submission is not successfull
                    #this may happen for instance if the same assembly has already been submitted, which would not get caught
                    #by the validation step
                    return {"error": output}
                accession = re.search( "ERZ\d*\w" , output).group(0).strip()
                Assembly().add_accession(id=assembly_id, accession=accession)
                Submission().add_assembly_accession(sub["_id"], accession, "webin-genome-" + assembly["assemblyname"], assembly_id)

                table_data = htags.generate_table_records(sub["profile_id"], "assembly", None)
                ghlper.notify_assembly_status(data={"profile_id": sub["profile_id"],"table_data": table_data, "component": "assembly"}, msg="Assembly has been submitted", action="info",
                html_id="assembly_info")
            else:
                error = output
                if return_code == 2:
                    with open(join(these_assemblies,"manifest.txt.report")) as report_file:
                        error = output + " " + report_file.read()
                elif return_code == 3:
                    directories = sorted(glob.glob(f"{settings.MEDIA_ROOT}/ena_assembly_files/{sub['profile_id']}/genome/*"),key=os.path.getmtime)
                    with open(f"{directories[-1]}/validate/webin-cli.report") as report_file:
                        error = output + " " + report_file.read()
                    for file in os.scandir(f"{directories[-1]}/validate"):
                        if file.name != "webin-cli.report":
                            with open(file) as report_file:
                                error = error + f'<br/><a href="{these_assemblies_url_path}/genome/{os.path.basename(directories[0])}/validate/{file.name}">{file.name}</a>'                    
                Assembly().update_assembly_error( assembly_ids=[assembly_id], msg=error)                
                ghlper.notify_assembly_status(data={"profile_id": sub["profile_id"]}, msg=error, action="error", html_id="assembly_info")


def submit_assembly(profile_id, target_ids=list(),  target_id=str()):
    sub_id = None
    if profile_id:
        submissions = Submission().get_records_by_field("profile_id", profile_id)
        if submissions and len(submissions) > 0:
            sub_id = str(submissions[0]["_id"])
            if not target_ids:
                target_ids = list()
            if target_id:
                target_ids.append(target_id)
            target_obj_ids = [ObjectId(x) for x in target_ids]
            count = Assembly().get_collection_handle().find({"profile_id": profile_id, "accession": "", "_id" : {"$in": target_obj_ids}}).count()
            if count < len(target_ids):
                return dict(status='error', message="One or more Assembly has been submitted! Cannot submitted again.")        
            
            if target_ids:
                return Submission().make_assembly_submission_uploading(sub_id, target_ids)
            
    return dict(status='error', message="System error. Assembly submission has not been scheduled! Please contact system administrator.")        

    
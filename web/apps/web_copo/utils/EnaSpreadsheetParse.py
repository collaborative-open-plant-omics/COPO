import inspect
import math
import uuid
import json
import subprocess
import jsonpath_rw_ext as jp
import pandas
from django_tools.middlewares import ThreadLocal
from exceptions_and_logging import logger
from api.utils import map_to_dict
from dal.copo_da import Sample, DataFile, Profile, Source, Submission, EnaFileTransfer, SubmissionQueue, Sequnece_annotation, EnaChecklist
from submission.helpers.generic_helper import notify_read_status
from web.apps.web_copo.schema_versions.lookup import dtol_lookups as lookup
from web.apps.web_copo.lookup import lookup as lk
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype, get_datetime, get_not_deleted_flag
from django.http import HttpResponse, JsonResponse
from web.apps.web_copo.validators.validator import Validator
from web.apps.web_copo.validators.ena_validators import ena_seq_validators as required_validators
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from pymongo import ReturnDocument
import web.apps.web_copo.utils.FileTransferUtils as tx
from django.conf import settings
from os.path import join
from pathlib import Path
from bson import ObjectId
import web.apps.web_copo.templatetags.html_tags as htags
from dal import cursor_to_list
from django.contrib.auth.decorators import login_required
from web.apps.web_copo.utils.EnaChecklistHandler import EnaCheckListSpreedsheet

l = logger.Logger("exceptions_and_logging/logs")

@login_required()
def parse_ena_spreadsheet(request):
    username = request.user.username
    profile_id = request.session["profile_id"]
    notify_read_status(data={"profile_id": profile_id},
                       msg='', action="info",
                       html_id="sample_info")
    # method called by rest
    file = request.FILES["file"]
    checklist_id = request.POST["checklist_id"]
    name = file.name
    
    required_validators = []
    required = dict(globals().items())["required_validators"]
    for element_name in dir(required):
        element = getattr(required, element_name)
        if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
            required_validators.append(element)

    ena = EnaCheckListSpreedsheet(file=file, checklist_id=checklist_id, component="sample", validators=required_validators)
    s3obj = s3()
    if name.endswith("xlsx") or name.endswith("xls"):
        fmt = 'xls'
    else:
        return HttpResponse(status=415, content="Please make sure your manifest is in xlxs format")

    if ena.loadManifest(fmt):
        l.log("Dtol manifest loaded")
        if ena.validate():
            l.log("About to collect Dtol manifest")
            # check s3 for bucket and files files
            bucket_name = str(request.user.id) + "_" + request.user.username
            # bucket_name = request.user.username
            file_names = ena.get_filenames_from_manifest()

            if s3obj.check_for_s3_bucket(bucket_name):
                # get filenames from manifest
                # check for files
                if not s3obj.check_s3_bucket_for_files(bucket_name=bucket_name, file_list=file_names):
                    # error message has been sent to frontend by check_s3_bucket_for_files so return so prevent ena.collect() from running
                    return HttpResponse(status=400)
            else:
                # bucket is missing, therefore create bucket and notify user to upload files
                notify_read_status(data={"profile_id": profile_id},
                                   msg='s3 bucket not found, creating it', action="info",
                                   html_id="sample_info")
                s3obj.make_s3_bucket(bucket_name=bucket_name)
                notify_read_status(data={"profile_id": profile_id},
                                msg='Files not found, please click "Upload Data into COPO" and follow the '
                                    'instructions.', action="error",
                                html_id="sample_info")
                return HttpResponse(status=400)
            notify_read_status(data={"profile_id": profile_id},
                            msg='Spreadsheet is valid', action="info",
                            html_id="sample_info")
            ena.collect()
            return HttpResponse()
        return HttpResponse(status=400)
    return HttpResponse(status=400)

@login_required()
def save_ena_records(request):
    # create mongo sample objects from info parsed from manifest and saved to session variable
    sample_data = request.session.get("sample_data")
    profile_id = request.session["profile_id"]
    profile_name = Profile().get_name(profile_id)
    uid = str(request.user.id)
    username = request.user.username
    checklist = EnaChecklist().get_collection_handle().find_one({"primary_id": request.session["checklist_id"]})
    column_name_mapping = { field["name"].upper() : key  for key, field in checklist["fields"].items() if not field.get("read_field", False) }
    #checklist_read = EnaChecklist().get_collection_handle().find_one({"primary_id": "read"})
    column_name_mapping_read = { field["name"].upper() : key  for key, field in checklist["fields"].items() if field.get("read_field", False) }
    #bundle = list()
    #alias = str(uuid.uuid4())
    #bundle_meta = list()
    pairing = list()
    datafile_list = list()
    existing_bundle = list()
    existing_bundle_meta = list()
    sub = Submission().get_collection_handle().find_one(
        {"profile_id": profile_id, "deleted": get_not_deleted_flag()})
    # override the bundle files for every manifest upload
    # if sub:
    #    existing_bundle = sub["bundle"]
    #    existing_bundle_meta = sub["bundle_meta"]
    dt = get_datetime()
    project_release_date = None

    for line in range(1, len(sample_data)):
        # for each row in the manifest

        s = (map_to_dict(sample_data[0], sample_data[line]))

   
        #project_release_date = s["release_date"]
        df = dict()
        p = Profile().get_record(profile_id)
        attributes = dict()
        # attributes["datafiles_pairing"] = list()
        attributes["target_repository"] = {"deposition_context": "ena"}
        # attributes["project_details"] = {
        #    "project_name": p["title"],
        #    "project_title": p["title"],
        #    "project_description": p["description"],
        #    "project_release_date": s["release_date"]
        # }

        '''
        attributes["library_preparation"] = {
            "library_layout": s["library_layout"],
            "library_strategy": s["library_strategy"],
            "library_source": s["library_source"],
            "library_selection": s["library_selection"],
            "library_description": s["library_description"]
        }
        '''


        # check if sample already exists, if so, add new datafile
        sample = Sample().get_collection_handle().find_one({"name": s["Sample"], "profile_id": profile_id})
        insert_record = {}

        if not sample or sample.get("organism","") != s["Organism"]:
            if not sample:
                sample = dict()

            source = dict()
            curl_cmd = "curl " + \
                       "https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name/" + s["Organism"].replace(" ", "%20")
            receipt = subprocess.check_output(curl_cmd, shell=True)
            # ToDo - exit if species not found
            print(receipt)

            taxinfo = json.loads(receipt.decode("utf-8"))

            # create source from organism
            termAccession = "http://purl.obolibrary.org/obo/NCBITaxon_" + str(taxinfo[0]["taxId"])
            source["organism"] = \
                {"annotationValue": s["Organism"], "termSource": "NCBITAXON", "termAccession":
                    termAccession}
            # source["profile_id"] = request.session["profile_id"]
            source["date_modified"] = dt
            source["profile_id"] = profile_id
            source["deleted"] = "0"
            source["name"] = s["Sample"]
            insert_record["created_by"] = uid
            insert_record["time_created"] = get_datetime()
            insert_record["date_created"] = dt

            source_id = str(
                Source().get_collection_handle().find_one_and_update({"organism.termAccession": termAccession, "profile_id": profile_id},
                                                                     {"$set": source, "$setOnInsert": insert_record},
                                                                     upsert=True, return_document=ReturnDocument.AFTER)["_id"])
            sample["derivesFrom"] = source_id
            insert_record["status"] = "pending"


        # create associated sample
        sample["sample_type"] = "isasample"
        #sample["derivesFrom"] = source_id
        sample["profile_id"] = profile_id
        sample["name"] = s["Sample"]
        sample["date_modified"] = dt 
        sample["deleted"] = get_not_deleted_flag()
        #sample["read"] = {"file_name": [s["file_name"]] }
        sample["checklist_id"] = request.session["checklist_id"]
        sample["updated_by"] = uid
        sample.pop("created_by", None)
        sample.pop("time_created", None)
        sample.pop("date_created", None)
        sample.pop("status", None) 

        for key, value in s.items():
            header = key
            header = header.replace(" (optional)", "", -1)
            upper_key = header.upper()
            if upper_key in column_name_mapping:
                sample[column_name_mapping[upper_key]] = value

        sample = Sample().get_collection_handle().find_one_and_update({"profile_id": profile_id, "name":s["Sample"]},
                                                                    {"$set": sample, "$setOnInsert": insert_record},
                                                                    upsert=True,  return_document=ReturnDocument.AFTER)
        sample_id = str(sample["_id"])
       

        for key, value in s.items():
            header = key
            header = header.replace(" (optional)", "", -1)
            upper_key = header.upper()
            if upper_key in column_name_mapping_read:
                attributes[column_name_mapping_read[upper_key]] = value

        #attributes["library_preparation"] = {key: s[key] for key in s.keys() if key.startswith("library_")}
        #attributes["nucleic_acid_sequencing"] = {"sequencing_instrument": s["sequencing_instrument"]}
        attributes["study_samples"] = [sample_id] 

        df["description"] = {"attributes": attributes}
        df["title"] = p["title"]
        # df["date_created"] = dt
        df["profile_id"] = str(p["_id"])
        df["file_type"] = "TODO"
        df["type"] = "RAW DATA FILE"

        df["bucket_name"] = str(request.user.id) + "_" + request.user.username
        # df["bucket_name"] = username

        # create local location
        Path(join(settings.UPLOAD_PATH, username)).mkdir(parents=True, exist_ok=True)
        nserted = None
        f_meta = None
        # check if there are two files or one
        if s["Library layout"] == "SINGLE":
            # create single record
            f_name = s["File name"]
            df["ecs_location"] = uid + "_" + username + "/" + f_name
            # df["ecs_location"] = username + "/" + f_name   #temp-solution
            df["file_name"] = f_name
            file_location = join(settings.UPLOAD_PATH, username, f_name)
            df["file_location"] = file_location
            df["name"] = f_name
            df["file_id"] = "NA"
            df["file_hash"] = s["File checksum"].strip()
            df["deleted"] = get_not_deleted_flag()
            file_changed = True
            datafile = DataFile().get_collection_handle().find_one({"file_location": file_location})
            if datafile:
                if datafile["file_hash"] == df["file_hash"]:
                    file_changed = False
                file_id = str(datafile["_id"])

            result = DataFile().get_collection_handle().update_one({"file_location": file_location}, {"$set": df},
                                                                   upsert=True)
            if result.upserted_id:
                file_id = str(result.upserted_id)
            if file_changed:
                datafile_list.append(file_id)

            f_meta = {"file_id": file_id, "file_name": f_name, "status": "pending"}
            # Sample(profile_id=profile_id).get_collection_handle().update_one({"_id": ObjectId(sample_id)}, {"$addToSet": {"read": f_meta}})
        else:
            file_id1 = None
            file_id2 = None
            # create record for left
            tmp_pairing = dict()
            file_names = s["File name"].split(",")
            f_name = file_names[0].strip()
            df["file_name"] = f_name
            df["ecs_location"] = uid + "_" + username + "/" + f_name
            # df["ecs_location"] = username + "/" + f_name   #temp-solution
            file_location = join(settings.UPLOAD_PATH, username, f_name)
            df["file_location"] = file_location
            df["name"] = f_name
            df["file_id"] = "NA"
            df["file_hash"] = s["File checksum"].split(",")[0].strip()
            df["deleted"] = get_not_deleted_flag()
            file_changed = True
            datafile = DataFile().get_collection_handle().find_one({"file_location": file_location})
            if datafile:
                if datafile["file_hash"] == df["file_hash"]:
                    file_changed = False
                file_id = str(datafile["_id"])

            result = DataFile().get_collection_handle().update_one({"file_location": file_location}, {"$set": df},
                                                                   upsert=True)
            if result.upserted_id:
                file_id = str(result.upserted_id)
            if file_changed:
                datafile_list.append(file_id)
            file_id1 = file_id

            # create record for right
            tmp_pairing["_id"] = file_id
            # bundle_meta.append(f_meta)
            # df.pop("_id")
            f_name = file_names[1].strip()
            df["file_name"] = f_name
            df["ecs_location"] = uid + "_" + username + "/" + f_name
            # df["ecs_location"] = request.user.username + "/" + f_name
            file_location = join(settings.UPLOAD_PATH, username, f_name)
            df["file_location"] = file_location
            df["name"] = f_name
            df["file_id"] = "NA"
            df["file_hash"] = s["File checksum"].split(",")[1].strip()
            df["deleted"] = get_not_deleted_flag()
            file_changed = True
            datafile = DataFile().get_collection_handle().find_one({"file_location": file_location})
            if datafile:
                if datafile["file_hash"] == df["file_hash"]:
                    file_changed = False
                file_id = str(datafile["_id"])

            result = DataFile().get_collection_handle().update_one({"file_location": file_location}, {"$set": df},
                                                                   upsert=True)
            if result.upserted_id:
                file_id = str(result.upserted_id)
            if file_changed:
                datafile_list.append(file_id)

            file_id2 = file_id
            f_meta = {"file_id": f"{file_id1},{file_id2}", "file_name": s["File name"], "status": "pending"}
            tmp_pairing["_id2"] = file_id
            pairing.append(tmp_pairing)
            # Sample(profile_id=profile_id).get_collection_handle().update_one({"_id": ObjectId(sample_id)}, {"$addToSet": {"read": f_meta }} )

        is_found = False
        for read in sample.get("read", []):
            if set(read["file_name"].split(",")) == set(f_meta["file_name"].split(",")):
                is_found = True
                break
        if not is_found:
            Sample(profile_id=profile_id).get_collection_handle().update_one({"_id": ObjectId(sample_id)}, {"$set": {"read": [f_meta] }} )


    # attributes["datafiles_pairing"] = pairing

    # read_files = [x["file_location"] for x in bundle_meta]

    # if sub and sub["accessions"]:
    #    return HttpResponse(content="", status=400)

    if not sub:
        sub = dict()
        sub["date_created"] = dt
        sub["repository"] = "ena"
        sub["accessions"] = dict()
        sub["profile_id"] = profile_id

    sub["complete"] = "false"
    sub["user_id"] = uid
    # sub["bundle_meta"] = existing_bundle_meta
    # sub["bundle"] = existing_bundle
    sub["manifest_submission"] = 1
    sub["deleted"] = get_not_deleted_flag()
    sub["project_release_date"] = project_release_date

    # make description records and submissions record
    # dr = Description().create_description(attributes=attributes, profile_id=profile_id, component='datafile',
    #                                      name=profile_name)
    # sub["description_token"] = dr["_id"]

    if "_id" in sub:
        Submission().get_collection_handle().update_one({"_id": sub["_id"]}, {"$set": sub})
        sub_id = sub["_id"]
    else:
        sub_id = Submission().get_collection_handle().insert_one(sub).inserted_id

    for f in datafile_list:
        tx.make_transfer_record(file_id=str(f), submission_id=str(sub_id))

    table_data = htags.generate_read_record(profile_id=profile_id, checklist_id=request.session["checklist_id"])
    result = {"table_data": table_data, "component": "read"}
    return JsonResponse(status=200, data=result)

def submit_read(profile_id,  target_ids=list(), target_id=None, checklist_id=None):

    if target_id:
        target_ids = [target_id]

    if not target_ids:
        return dict(status='error', message="Please select one or more records to submit!")

    user = ThreadLocal.get_current_user()
    dt = get_datetime()
    file_ids = [file_id for id in target_ids for file_id in id.split("_")[1].split(",")]
    sample_obj_ids = [ObjectId(id.split("_")[0]) for id in target_ids]
    paired_file_ids = [id.split("_")[1] for id in target_ids]

    sub = Submission().get_collection_handle().find_one(
        {"profile_id": profile_id, "deleted": get_not_deleted_flag()})

    if not sub:
        return dict(status='error', message="Please contact System Support Error 10211!")

    doc = SubmissionQueue(profile_id=profile_id).execute_query({"submission_id": str(sub["_id"])})
    if doc and doc[0].get("processing_status", "pending") != 'pending':
        context = dict(status='error', message='Submission is already in the processing queue. Please try it later')
        return context

    Submission(profile_id=profile_id).get_collection_handle().update_one({"_id": sub["_id"]}, {
        "$addToSet": {"bundle": {"$each": paired_file_ids}},
        "$set": {"complete": "false", "date_modified": dt, "updated_by": str(user.id)}})

    for id in paired_file_ids:
        Sample(profile_id=profile_id).get_collection_handle().update_one(
            {"_id": {"$in": sample_obj_ids}, "read.file_id": id, "read.status": "pending"},
            {"$set": {"read.$.status": "processing", "date_modified": dt, "updated_by": str(user.id)}})

    if not doc:  # submission not in queue, add to queue
        fields = dict(
            submission_id=str(sub["_id"]),
            date_modified=dt,
            date_created=dt,
            repository=sub["repository"],
            processing_status='pending',
            profile_id=profile_id,
        )
        result = SubmissionQueue(profile_id=profile_id).get_collection_handle().insert_one(fields)
    return dict(status='success',
                message="Submission has been added to the processing queue. Status update will be provided.")


def delete_ena_records(profile_id, target_ids=list(), target_id=None):
    if target_id:
        target_ids = [target_id]

    if not target_ids:
        return dict(status='error', message="Please select one or more records to delete!")

    dt = get_datetime()
    existing_sample_with_file = []
    delete_samples = []
    delete_sources = []

    file_ids = [file_id for id in target_ids for file_id in id.split("_")[1].split(",")]
    sample_obj_ids = [ObjectId(id.split("_")[0]) for id in target_ids]
    file_regex_ids = "|".join([file_id for id in target_ids for file_id in id.split("_")[1].split(",")])

    # check if any of the selected file records have been submitted to ENA
    result = Sample(profile_id=profile_id).get_all_records_columns(
        filter_by={"_id": {"$in": sample_obj_ids}, "read.file_id": {"$regex": file_regex_ids}},
        projection={"status": 1, "biosampleAccession": 1, "read.$": 1, "derivesFrom": 1})
    for r in result:
        for file in r.get("read", []):
            interset = [file_id for file_id in file.get("file_id", "").split(",") if file_id in file_ids]
            if not interset:
                continue
            if file.get("status", "pending") == "accepted":
                return dict(status='error', message="one or more record/s have been submitted to ENA!")
            elif file.get("status", "pending") == "processing":
                return dict(status='error', message="one or more record/s have been scheduled to submit to ENA!")

    # check if any of the selected file records have been used by other samples

    # remove file_id from samples
    Sample().get_collection_handle().update_many({"_id": {"$in": sample_obj_ids}},
                                                 {"$pull": {"read": {"file_id": {"$regex": file_regex_ids}}}})

    # remove datafile records if no sample is using it
    other_samples_with_same_file = cursor_to_list(Sample(profile_id=profile_id).get_collection_handle().find(
        {"_id": {"$nin": sample_obj_ids}, "read.file_id": {"$regex": file_regex_ids}}, {"_id": 1, "read.$": 1}))
    other_annotation_with_same_file = cursor_to_list(
        Sequnece_annotation(profile_id=profile_id).get_collection_handle().find({"files": {"$in": file_ids}},
                                                                                {"_id": 1, "files": 1}))
    for s in other_samples_with_same_file:
        for f in s.get("read", []):
            for file_id in f["file_id"].split(","):
                file_ids.remove(file_id) if file_id in file_ids else None

    for a in other_annotation_with_same_file:
        for f in a.get("files", []):
            file_ids.remove(f) if f in file_ids else None

    if file_ids:
        DataFile(profile_id=profile_id).get_collection_handle().remove(
            {"_id": {"$in": [ObjectId(f) for f in file_ids]}}, multi=True)
        EnaFileTransfer(profile_id=profile_id).get_collection_handle().remove({"file_id": {"$in": file_ids}},
                                                                              multi=True)

    # remove sample records if no file inside

    samples = Sample(profile_id=profile_id).get_all_records_columns(filter_by={"_id": {"$in": sample_obj_ids}},
                                                                    projection={"biosampleAccession": 1, "read": 1,
                                                                                "derivesFrom": 1})

    for sample in samples:
        if not sample.get("read", []) and not sample.get("biosampleAccession", ""):
            delete_sources.append(sample["derivesFrom"])
            delete_samples.append(sample["_id"])

    if delete_sources:
        other_samples_with_same_source = cursor_to_list(Sample(profile_id=profile_id).get_collection_handle().find(
            {"_id": {"$nin": delete_samples}, "derivesFrom": {"$in": delete_sources}}, {"derivesFrom": 1}))
        for s in other_samples_with_same_source:
            delete_sources.remove(s["derivesFrom"]) if s["derivesFrom"] in delete_sources else None
        Source(profile_id=profile_id).get_collection_handle().remove(
            {"_id": {"$in": [ObjectId(s) for s in delete_sources]}})

    if delete_samples:
        Sample(profile_id=profile_id).get_collection_handle().remove({"_id": {"$in": delete_samples}})

    return dict(status='success', message="Read record/s have been deleted!")


@login_required()
def get_read_accessions(request, sample_accession): 
    samples = Sample().get_all_records_columns(filter_by={"sraAccession": sample_accession}, projection={"profile_id":1, "read":1})
    run_accessions = []
    experiment_accessions = []
    if samples:
        sample = samples[0]
        submission = Submission().get_all_records_columns(filter_by={"profile_id": sample["profile_id"]}, projection={"accessions":1})
        for read in sample.get("read", []):
            file_id_str = read.get("file_id", str())
            file_ids = file_id_str.split(",")
            if file_ids:
                if read.get("status", "pending") == "accepted":
                        for accession in submission[0].get("accessions", {}).get("run", []):
                            if set(accession.get("datafiles",[])) == set(file_ids):
                                run_accessions.append(accession.get("accession", str()))
                                alias = accession.get("alias", str())
                                break
                        for accession in submission[0].get("accessions", {}).get("experiment", []):
                            if accession.get("alias",[]) == alias:
                                experiment_accessions.append(accession.get("accession", str()))
                                break       
    result = dict(run_accessions=run_accessions, experiment_accessions=experiment_accessions)                                                     
    return JsonResponse(status=200,  data=result)


class ENASpreadsheet_old:

    def __init__(self, file):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        #self.channels_group_name = "s3_" + self.profile_id

        self.data = None
        self.fields = None
        self.required_validators = list()

        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated
        if file:
            self.file = file
        else:
            self.sample_data = self.req.session.get("sample_data", "")
            self.isupdate = self.req.session.get("isupdate", False)

        # get type of manifest
        t = Profile().get_type(self.profile_id)

        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.required_validators.append(element)

    def get_filenames_from_manifest(self):
        return list(self.data["file_name"])

    def loadManifest(self, m_format):

        if self.profile_id is not None:
            notify_read_status(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                               html_id="sample_info")

            try:
                # read excel and convert all to string
                if m_format == "xls":
                    self.data = pandas.read_excel(self.file, keep_default_na=False,
                                                  na_values=lookup.NA_VALS)
                elif m_format == "csv":
                    self.data = pandas.read_csv(self.file, keep_default_na=False,
                                                na_values=lookup.NA_VALS)
                else:
                    raise Exception("Unknown manifest format")
                self.data = self.data.loc[:, ~self.data.columns.str.contains('^Unnamed')]
                self.data = self.data.apply(lambda x: x.astype(str))
                self.data = self.data.apply(lambda x: x.str.strip())
                self.data.columns = self.data.columns.str.replace(" ", "")

                new_column_name = { name : name.replace(" (optional)", "",-1).upper() for name in self.data.columns.values.tolist() }
                self.new_data = self.data.rename(columns=new_column_name)    

                checklist = EnaChecklist().get_collection_handle().find_one({"primary_id": self.checklist_id})
                if checklist:
                   fields = checklist["fields"]
                   new_column_name = { value["name"].upper() : key for key, value in fields.items() }
                   self.new_data.rename(columns=new_column_name, inplace=True)    

            except Exception as e:
                # if error notify via web socket
                l.exception(e)
                l.exception(e)
                notify_read_status(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
                                   action="info",
                                   html_id="sample_info")
                return False
            return True

    def validate(self):
        flag = True
        errors = []
        warnings = []
        self.isupdate = False

        try:
            # get definitive list of mandatory DTOL fields from schema
            s = json_to_pytype(lk.WIZARD_FILES["ena_seq_manifest"], compatibility_mode=False)
            self.fields = jp.match(
                '$.properties[?(@.specifications[*] == "ena_seq" & @.required=="true")].versions[0]',
                s)

            # validate for required fields
            for v in self.required_validators:
                errors, warnings, flag, self.isupdate = v(profile_id=self.profile_id, fields=self.fields,
                                                          data=self.data,
                                                          errors=errors, warnings=warnings, flag=flag,
                                                          isupdate=self.isupdate).validate()

            # send warnings
            if warnings:
                notify_read_status(data={"profile_id": self.profile_id},
                                   msg="<br>".join(warnings),
                                   action="warning",
                                   html_id="warning_info2")
            # if flag is false, compile list of errors
            if not flag:
                errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                errors = "".join(errors)

                notify_read_status(data={"profile_id": self.profile_id},
                                   msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                                   action="error",
                                   html_id="sample_info")
                return False



        except Exception as e:
            l.exception(e)
            error_message = str(e).replace("<", "").replace(">", "")
            notify_read_status(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                               action="info",
                               html_id="sample_info")

            return False

        # if we get here we have a valid spreadsheet
        notify_read_status(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                           html_id="sample_info")
        notify_read_status(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls")
        notify_read_status(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id="sample_info")

        return True

    def collect(self):
        # create table data to show to the frontend from parsed manifest
        sample_data = []
        headers = list()
        for col in list(self.data.columns):
            headers.append(col)
        sample_data.append(headers)
        for index, row in self.data.iterrows():
            r = list(row)
            for idx, x in enumerate(r):
                if x is math.nan:
                    r[idx] = ""
            sample_data.append(r)
        # store sample data in the session to be used to create mongo objects
        self.req.session["sample_data"] = sample_data
        self.req.session["checklist_id"] = self.checklist_id

        notify_read_status(data={"profile_id": self.profile_id}, msg=sample_data, action="make_table",
                        html_id="sample_table")
        
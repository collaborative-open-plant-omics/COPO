import inspect
import math
from django.conf import settings
import uuid
import json
import subprocess
import jsonpath_rw_ext as jp
import pandas
from django_tools.middlewares import ThreadLocal
from exceptions_and_logging import logger
from api.utils import map_to_dict
from dal.copo_da import Sample, DataFile, Profile, Source, Submission, Description
from django.conf import settings
from submission.helpers.generic_helper import notify_frontend
# from web.apps.web_copo.lookup import dtol_lookups as lookup
from web.apps.web_copo.lookup import lookup as lk
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype
from django.http import HttpResponse
from web.apps.web_copo.validators.validator import Validator
from web.apps.web_copo.validators.ena_validators import ena_seq_validators as required_validators
import datetime
import importlib
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from dal.broker_da import BrokerDA
from pymongo import ReturnDocument
import web.apps.web_copo.utils.FileTransferUtils as tx

l = logger.Logger("exceptions_and_logging/logs")
schema_version_path_dtol_lookups = f'web.apps.web_copo.schema_versions.{settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
lookup = importlib.import_module(schema_version_path_dtol_lookups)

from django.conf import settings
from os.path import join
from pathlib import Path


def parse_ena_spreadsheet(request):
    profile_id = request.session["profile_id"]
    channels_group_name = "s3_" + profile_id

    # method called by rest
    file = request.FILES["file"]
    name = file.name
    ena = ENASpreadsheet(file=file)
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

            if s3obj.check_for_s3_bucket(bucket_name):
                # get filenames from manifest
                file_names = ena.get_filenames_from_manifest()
                # check for files
                if not s3obj.check_s3_bucket_for_files(bucket_name=bucket_name, file_list=file_names):
                    # error message has been sent to frontend by check_s3_bucket_for_files so return so prevent ena.collect() from running
                    return HttpResponse()

            else:
                # bucket is missing, therefore create bucket and notify user to upload files
                s3obj.make_s3_bucket(bucket_name=bucket_name)
                notify_frontend(data={"profile_id": profile_id},
                                msg='Files not found, please click "Upload Data into COPO" and follow the '
                                    'instructions.', action="info",
                                html_id="sample_info", group_name=channels_group_name)
                return HttpResponse()

            # iff all above have passed, then run collect
            ena.collect()

    return HttpResponse()


def save_ena_records(request):
    # create mongo sample objects from info parsed from manifest and saved to session variable
    sample_data = request.session.get("sample_data")
    profile_id = request.session["profile_id"]
    profile_name = Profile().get_name(profile_id)
    uid = request.user.id
    username = request.user.username
    alias = str(uuid.uuid4())
    bundle = list()
    bundle_meta = list()
    pairing = list()
    datafile_list = list()
    for p in range(1, len(sample_data)):
        # for each row in the manifest

        s = (map_to_dict(sample_data[0], sample_data[p]))

        # check if sample already exists, if so, add new datafile
        sample = Sample().get_collection_handle().find_one({"name": s["sample_name"]})
        if not sample:
            source = dict()
            curl_cmd = "curl " + \
                       "https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name/" + s["organism"].replace(" ", "%20")
            receipt = subprocess.check_output(curl_cmd, shell=True)
            # ToDo - exit if species not found
            print(receipt)

            taxinfo = json.loads(receipt.decode("utf-8"))

            # create source from organism
            termAccession = "http://purl.obolibrary.org/obo/NCBITaxon_" + str(taxinfo[0]["taxId"])
            source["organism"] = \
                {"annotationValue": s["organism"], "termSource": "NCBITAXON", "termAccession":
                    termAccession}
            source["profile_id"] = request.session["profile_id"]
            source["date_created"] = datetime.datetime.utcnow()
            source["profile_id"] = profile_id
            source["deleted"] = "0"
            source_id = str(
                Source().get_collection_handle().find_one_and_update({"organism.termAccession": termAccession},
                                                                     {"$set": source},
                                                                     upsert=True, return_document=ReturnDocument.AFTER)[
                    "_id"])

            # create associated sample
            sample = dict()
            sample["sample_type"] = "isasample"
            sample["profile_id"] = request.session["profile_id"]
            sample["derivesFrom"] = [source_id]
            sample["date_modified"] = datetime.datetime.utcnow()
            sample["profile_id"] = profile_id
            sample["name"] = s["sample_name"]
            sample["deleted"] = "0"
            sample_id = str(
                Sample().get_collection_handle().find_one_and_update({"name": sample["name"]}, {"$set": sample},
                                                                     upsert=True,
                                                                     return_document=ReturnDocument.AFTER)[
                    "_id"])
        else:
            sample_id = str(sample["_id"])

        df = dict()
        p = Profile().get_record(profile_id)
        attributes = dict()
        attributes["datafiles_pairing"] = list()
        attributes["target_repository"] = {"deposition_context": "ena"}
        attributes["project_details"] = {
            "project_name": p["title"],
            "project_title": p["title"],
            "project_description": p["description"],
            "project_release_date": s["release_date"]
        }
        attributes["library_preparation"] = {
            "library_layout": s["library_layout"],
            "library_strategy": s["library_strategy"],
            "library_source": s["library_source"],
            "library_selection": s["library_selection"],
            "library_description": s["library_description"]
        }
        attributes["attach_samples"] = {"study_samples": [sample_id]}
        attributes["nucleic_acid_sequencing"] = {"sequencing_instrument": s["sequencing_instrument"]}
        df["description"] = {"attributes": attributes}
        df["title"] = p["title"]
        df["date_created"] = datetime.datetime.utcnow()
        df["profile_id"] = str(p["_id"])
        df["file_type"] = "TODO"
        df["type"] = "RAW DATA FILE"
        df["bucket_name"] = str(request.user.id) + "_" + request.user.username

        # create local location
        Path(join(settings.UPLOAD_PATH, username)).mkdir(parents=True, exist_ok=True)

        # check if there are two files or one
        if s["library_layout"] == "SINGLE":
            # create single record
            f_name = s["file_name"]
            df["ecs_location"] = str(request.user.id) + "_" + request.user.username + "/" + f_name
            df["file_name"] = f_name
            file_location = join(settings.UPLOAD_PATH, username, f_name)
            df["file_location"] = file_location
            df["name"] = f_name
            df["file_id"] = "NA"
            df["file_hash"] = s["md5"].strip()
            inserted = DataFile().get_collection_handle().find_one_and_update({"file_location": file_location},
                                                                              {"$set": df}, upsert=True,
                                                                              return_document=ReturnDocument.AFTER)
            datafile_list.append(inserted)
            bundle.append(str(inserted["_id"]))
            f_meta = {"file_id": str(inserted["_id"]), "file_location": join(settings.UPLOAD_PATH, str(uid), f_name),
                      "upload_status": False}
            bundle_meta.append(f_meta)
        else:
            # create record for left
            tmp_pairing = dict()
            file_names = s["file_name"].split(",")
            f_name = file_names[0].strip()
            df["file_name"] = f_name
            df["ecs_location"] = str(request.user.id) + "_" + request.user.username + "/" + f_name
            file_location = join(settings.UPLOAD_PATH, username, f_name)
            df["file_location"] = file_location
            df["name"] = f_name
            df["file_id"] = "NA"
            df["file_hash"] = s["md5"].split(",")[0].strip()
            inserted = DataFile().get_collection_handle().find_one_and_update({"file_location": file_location},
                                                                              {"$set": df}, upsert=True,
                                                                              return_document=ReturnDocument.AFTER)
            datafile_list.append(inserted)
            bundle.append(str(inserted["_id"]))
            f_meta = {"file_id": str(inserted["_id"]), "file_location": join(settings.UPLOAD_PATH, str(uid),
                                                                             file_names[0]), "upload_status": False}
            # create record for right
            tmp_pairing["_id"] = str(inserted["_id"])
            bundle_meta.append(f_meta)
            # df.pop("_id")
            f_name = file_names[1].strip()
            df["file_name"] = f_name
            df["ecs_location"] = str(request.user.id) + "_" + request.user.username + "/" + f_name
            file_location = join(settings.UPLOAD_PATH, username, f_name)
            df["file_location"] = file_location
            df["name"] = f_name
            df["file_id"] = "NA"
            df["file_hash"] = s["md5"].split(",")[1].strip()
            inserted = DataFile().get_collection_handle().find_one_and_update({"file_location": file_location},
                                                                              {"$set": df}, upsert=True,
                                                                              return_document=ReturnDocument.AFTER)
            datafile_list.append(inserted)
            bundle.append(str(inserted["_id"]))
            f_meta = {"file_id": str(inserted["_id"]), "file_location": join(settings.UPLOAD_PATH, str(uid),
                                                                             file_names[1]), "upload_status": False}
            tmp_pairing["_id2"] = str(inserted["_id"])
            pairing.append(tmp_pairing)

            bundle_meta.append(f_meta)
    submission = dict()
    attributes["datafiles_pairing"] = pairing
    submission["repository"] = "ena"
    submission["date_created"] = datetime.datetime.utcnow()
    submission["complete"] = "false"
    submission["user_id"] = uid
    submission["accessions"] = dict()
    submission["bundle_meta"] = bundle_meta
    submission["bundle"] = bundle
    submission["profile_id"] = profile_id
    submission["manifest_submission"] = 1

    # make description records and submissions record
    dr = Description().create_description(attributes=attributes, profile_id=profile_id, component='datafile',
                                          name=profile_name)
    submission["description_token"] = dr["_id"]
    subs = Submission().get_collection_handle().find({"profile_id": profile_id})
    duplicates = list()
    update_ids = list()
    if subs:
        for s in subs:
            for s_bm in s.get("bundle_meta", ""):
                for bm in submission.get("bundle_meta", ""):
                    if s_bm.get("file_location") == bm.get("file_location", ""):
                        # we have an existing submission with at least one of these file locations so update existing submission record

                        duplicates.append(s_bm.get("file_location"))
                        update_ids.append(s["_id"])
        if len(duplicates) > 0:
            submission.pop("accessions")
            Submission().get_collection_handle().update_one({"_id": update_ids[0]}, {"$set": submission})
            sub_id = update_ids[0]
        else:
            sub_id = Submission().get_collection_handle().insert_one(submission)["_id"]
    else:
        sub = Submission().get_collection_handle().insert_one(submission)
        sub_id = str(sub.inserted_id)

    for f in datafile_list:
        tx.make_transfer_record(file_id=f["_id"], submission_id=str(sub_id))

    return HttpResponse()


class ENASpreadsheet:

    def __init__(self, file):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)

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
            notify_frontend(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                            html_id="sample_info")
            try:
                # read excel and convert all to string
                if m_format == "xls":
                    self.data = pandas.read_excel(self.file, keep_default_na=False,
                                                  na_values=lookup.NA_VALS)
                elif m_format == "csv":
                    self.data = pandas.read_csv(self.file, keep_default_na=False,
                                                na_values=lookup.NA_VALS)
                self.data = self.data.loc[:, ~self.data.columns.str.contains('^Unnamed')]
                self.data = self.data.apply(lambda x: x.astype(str))
                self.data = self.data.apply(lambda x: x.str.strip())
                self.data.columns = self.data.columns.str.replace(" ", "")
            except Exception as e:
                # if error notify via web socket
                notify_frontend(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
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
                notify_frontend(data={"profile_id": self.profile_id},
                                msg="<br>".join(warnings),
                                action="warning",
                                html_id="warning_info2")
            # if flag is false, compile list of errors
            if not flag:
                errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                errors = "".join(errors)

                notify_frontend(data={"profile_id": self.profile_id},
                                msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                                action="error",
                                html_id="sample_info")
                return False



        except Exception as e:
            error_message = str(e).replace("<", "").replace(">", "")
            notify_frontend(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                            action="info",
                            html_id="sample_info")
            return False

        # if we get here we have a valid spreadsheet
        notify_frontend(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                        html_id="sample_info")
        notify_frontend(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls")
        notify_frontend(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id="sample_info")

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

        notify_frontend(data={"profile_id": self.profile_id}, msg=sample_data, action="make_table",
                        html_id="sample_table")

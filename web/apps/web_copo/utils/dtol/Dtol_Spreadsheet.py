# Created by fshaw at 03/04/2020
import inspect
import math
import os
import uuid
import pickle
from os.path import join, isfile
from pathlib import Path
from shutil import rmtree
from urllib.error import HTTPError

import jsonpath_rw_ext as jp
import pandas
from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal

import web.apps.web_copo.schemas.utils.data_utils as d_utils
from api.utils import map_to_dict
from dal.copo_da import Sample, DataFile, Profile, ValidationQueue
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.copo_email import CopoEmail
from web.apps.web_copo.lookup import dtol_lookups as lookup
from web.apps.web_copo.lookup import lookup as lk
from web.apps.web_copo.lookup.lookup import SRA_SETTINGS
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype
from web.apps.web_copo.utils.dtol.Dtol_Helpers import query_public_name_service
from .Dtol_Helpers import make_tax_from_sample
from web.apps.web_copo.validators.tol_validators import optional_field_dtol_validators as optional_validators, \
    taxon_validators
from web.apps.web_copo.validators.tol_validators import required_field_dtol_validators as required_validators
from web.apps.web_copo.validators.validator import Validator
from dal import cursor_to_list
from exceptions_and_logging import logger

l = logger.Logger("exceptions_and_logging/logs")


def make_target_sample(sample):
    # need to pop taxon info, and add back into sample_list
    if not "species_list" in sample:
        sample["species_list"] = list()
    out = dict()
    symbiont = sample.pop("SYMBIONT")
    if symbiont.upper() not in ["SYMBIONT", "TARGET"]:
        if symbiont:
            out["SYMBIONT_SOP2dot2"] = symbiont
        symbiont = "TARGET"

    out["SYMBIONT"] = symbiont.upper()
    out["TAXON_ID"] = sample.pop("TAXON_ID")
    out["ORDER_OR_GROUP"] = sample.pop("ORDER_OR_GROUP")
    out["FAMILY"] = sample.pop("FAMILY")
    out["GENUS"] = sample.pop("GENUS")
    out["SCIENTIFIC_NAME"] = sample.pop("SCIENTIFIC_NAME")
    out["INFRASPECIFIC_EPITHET"] = sample.pop("INFRASPECIFIC_EPITHET")
    out["CULTURE_OR_STRAIN_ID"] = sample.pop("CULTURE_OR_STRAIN_ID")
    out["COMMON_NAME"] = sample.pop("COMMON_NAME")
    out["TAXON_REMARKS"] = sample.pop("TAXON_REMARKS")
    sample["species_list"].append(out)

    return sample


class DtolSpreadsheet:
    fields = ""
    sra_settings = d_utils.json_to_pytype(SRA_SETTINGS, compatibility_mode=False).get("properties", dict())

    def __init__(self, file=None, p_id="", validation_record_id=""):
        self.req = ThreadLocal.get_current_request()
        if p_id == "" and validation_record_id:
            self.vr = ValidationQueue().get_record(validation_record_id)
            p_id = self.vr.get("profile_id", "")
        if file:
            self.file = file
        else:
            self.sample_data = self.req.session.get("sample_data", "")
            if self.sample_data == "":
                self.sample_data = pickle.loads(self.vr["manifest_data"])
            self.isupdate = self.req.session.get("isupdate", False)

        self.profile_id = p_id

        sample_images = Path(settings.MEDIA_ROOT) / "sample_images"
        display_images = Path(settings.MEDIA_ROOT) / "img" / "sample_images"
        self.these_images = sample_images / self.profile_id
        self.display_images = display_images / self.profile_id
        self.data = None
        self.required_field_validators = list()
        self.optional_field_validators = list()
        self.optional_field_validators = list()
        self.taxon_field_validators = list()
        self.optional_validators = optional_validators
        self.required_validators = required_validators
        self.taxon_validators = taxon_validators
        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated

        self.public_name_list = list()
        # get type of manifest
        t = Profile().get_type(self.profile_id)
        if "ASG" in t:
            self.type = "ASG"
        elif "DTOL_EI" in t:
            self.type = "DTOL_EI"
        elif "ERGA" in t:
            self.type = "ERGA"
        else:
            self.type = "DTOL"

        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.required_field_validators.append(element)
        # create list of optional validators
        optional = dict(globals().items())["optional_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.optional_field_validators.append(element)
        # create list of taxon validators
        optional = dict(globals().items())["taxon_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.taxon_field_validators.append(element)

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
                '''
                for column in self.allowed_empty:
                    self.data[column] = self.data[column].fillna("")
                '''
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

    def save_records(self):
        # create mongo sample objects from info parsed from manifest and saved to session variable
        # sample_data = self.sample_data

        binary = pickle.loads(self.vr["manifest_data"])
        try:
            sample_data = pandas.read_excel(binary, keep_default_na=False,
                                            na_values=lookup.NA_VALS)
        except ValueError:
            sample_data = binary
        sample_data = sample_data.loc[:, ~sample_data.columns.str.contains('^Unnamed')]
        '''
        for column in self.allowed_empty:
            self.data[column] = self.data[column].fillna("")
        '''
        sample_data = sample_data.apply(lambda x: x.astype(str))
        sample_data = sample_data.apply(lambda x: x.str.strip())
        sample_data.columns = sample_data.columns.str.replace(" ", "")
        manifest_id = str(uuid.uuid4())
        request = ThreadLocal.get_current_request()
        image_data = []
        for p in range(0, len(sample_data)):
            s = (map_to_dict(sample_data.columns, sample_data.iloc[p, :]))
            # store manifest version for posterity. If unknown store as 0
            if "asg" in self.type.lower():
                s["manifest_version"] = settings.CURRENT_ASG_VERSION
            elif "dtol" in self.type.lower():
                s["manifest_version"] = settings.CURRENT_DTOL_VERSION
            elif "erga" in self.type.lower():
                s["manifest_version"] = settings.CURRENT_ERGA_VERSION
            else:
                s["manifest_version"] = 0

            s["sample_type"] = self.type.lower()
            s["tol_project"] = self.type
            s["biosample_accession"] = []
            s["manifest_id"] = manifest_id
            s["status"] = "pending_barcode"
            s["rack_tube"] = s.get("RACK_OR_PLATE_ID", "") + "/" + s["TUBE_OR_WELL_ID"]
            s["profile_id"] = self.profile_id
            s["deleted"] = '0'
            notify_frontend(data={"profile_id": self.profile_id},
                            msg="Creating Sample with ID: " + s.get("TUBE_OR_WELL_ID") + "/" + s["SPECIMEN_ID"],
                            action="info",
                            html_id="sample_info")

            # change fields for symbiont
            if s["SYMBIONT"] == "SYMBIONT":
                s["ORGANISM_PART"] = "WHOLE_ORGANISM"
                # if ASG change also sex to not collected
                if s["tol_project"] == "ASG":
                    s["SEX"] = "NOT_COLLECTED"
            s = make_target_sample(s)
            # check if sample with specimen id has already been created during barcoding upload
            preexisting_samples = cursor_to_list(Sample().get_sample_by_specimen_id(s["SPECIMEN_ID"]))
            if preexisting_samples:
                # we have existing samples with this specimen id
                racktube_list = []
                for ss in preexisting_samples:
                    # if there are samples with the same specimen_id, they may be symbionts in the same rack_tube,
                    # or another sample of the same organism in a different rack_tube
                    #use rack_tube to see if these are real samples or barcoding entries
                    if ss.get("rack_tube", ""):
                        racktube_list.append(ss.get("rack_tube", ""))

                if s.get("species_list", dict())[0].get("SYMBIONT", "").lower() == "symbiont":
                    # this is symbiont, just make a sample
                    self.make_pending_barcode_sample(s)

                elif racktube_list:
                    if s["rack_tube"] in racktube_list:
                        #check if the previously uploaded sample was a symbiont
                        existing = Sample().get_by_field("rack_tube", [s["rack_tube"]])
                        if all(x.get("species_list", dict())[0].get("SYMBIONT", "").lower() == "symbiont" for x in existing):
                            # we are dealing with another sample from the a same specimen
                            # so make new sample
                            smpl = Sample().get_collection_handle().insert(s)
                            # and copy over barcoding data

                            # N.B. function find_incorrectly_rejected_samples was setting these samples to accepted
                            # automatically, so I've commented it out. This may have knockon consequences
                            if preexisting_samples[0]["barcoding"] == "":
                                s_status = "pending_barcode"
                            else:
                                s_status = "pending"

                            Sample().get_collection_handle().update({"_id": smpl}, {"$set": {
                                "status": s_status, "barcoding": preexisting_samples[0][
                                    "barcoding"]}})
                        else:
                            # l.log("Dtol spreadsheet : 417 - duplicated tuberack in db and no symbiont ", type=Logtype.FILE)
                            pass
                    else:
                        # we are dealing with another sample from the a same specimen
                        # so make new sample
                        smpl = Sample().get_collection_handle().insert(s)
                        # and copy over barcoding data

                        # N.B. function find_incorrectly_rejected_samples was setting these samples to accepted
                        # automatically, so I've commented it out. This may have knockon consequences
                        if preexisting_samples[0]["barcoding"] == "":
                            s_status = "pending_barcode"
                        else:
                            s_status = "pending"

                        Sample().get_collection_handle().update({"_id": smpl}, {"$set": {
                            "status": s_status, "barcoding": preexisting_samples[0][
                                "barcoding"]}})
                else:
                    # else we are just updating an existing barcode with sample data
                    # here check if barcoding matches
                    # check bold reported scientific name with manifest reported and record any conflicts
                    if str(s["species_list"][0]["SCIENTIFIC_NAME"]).lower() == str(
                            preexisting_samples[0]["barcoding"]["taxonomy"]["species"]["taxon"]["name"]).lower():
                        s_status = "pending"
                    else:
                        s_status = "conflicting"
                    s["status"] = s_status
                    sampl = Sample().update_tol_by_specimen(specimen_id=ss["SPECIMEN_ID"], sample_data=s)
                    Sample().timestamp_dtol_sample_created(sampl["_id"])
                    # add updated sample to public_name_list
                    if not sampl["species_list"][0]["SYMBIONT"] or sampl["species_list"][0]["SYMBIONT"] == "TARGET":
                        self.public_name_list.append(
                            {"taxonomyId": int(sampl["species_list"][0]["TAXON_ID"]), "specimenId": sampl[
                                "SPECIMEN_ID"],
                             "sample_id": str(sampl["_id"])})
            else:
                self.make_pending_barcode_sample(s)

            for im in image_data:
                # create matching DataFile object for image is provided
                if s["SPECIMEN_ID"] in im["specimen_id"]:
                    fields = {"file_location": im["file_name"]}
                    df = DataFile().save_record({}, **fields)
                    DataFile().insert_sample_id(df["_id"], sampl["_id"])
                    break;

        uri = request.build_absolute_uri('/')
        # query public service service a first time now to trigger request for public names that don't exist
        public_names = query_public_name_service(self.public_name_list)
        for name in public_names:
            Sample().update_public_name(name)
        profile_id = request.session["profile_id"]
        profile = Profile().get_record(profile_id)
        title = profile["title"]
        description = profile["description"]
        CopoEmail().notify_new_manifest(uri + 'copo/accept_reject_sample/', title=title, description=description, project=self.type.upper())

    def make_pending_barcode_sample(self, s):
        s["status"] = "pending_barcode"
        s["barcoding"] = ""
        # create new sample
        sampl = Sample().get_collection_handle().insert(s)
        sampl = Sample().get_collection_handle().find_one({"_id": sampl})
        Sample().timestamp_dtol_sample_created(sampl["_id"])
        if not sampl["species_list"][0]["SYMBIONT"] or sampl["species_list"][0]["SYMBIONT"] == "TARGET":
            self.public_name_list.append(
                {"taxonomyId": int(sampl["species_list"][0]["TAXON_ID"]), "specimenId": sampl["SPECIMEN_ID"],
                 "sample_id": str(sampl["_id"])})
        return sampl

    def update_records(self):
        binary = pickle.loads(self.vr["manifest_data"])
        try:
            sample_data = pandas.read_excel(binary, keep_default_na=False,
                                            na_values=lookup.NA_VALS)
        except ValueError:
            sample_data = binary

        request = ThreadLocal.get_current_request()
        self.public_name_list = list()
        for p in range(0, len(sample_data)):
            s = map_to_dict(sample_data.columns, sample_data.iloc[p, :])
            notify_frontend(data={"profile_id": self.profile_id},
                            msg="Updating Sample with ID: " + s["TUBE_OR_WELL_ID"] + "/" + s["SPECIMEN_ID"],
                            action="info",
                            html_id="sample_info")
            rack_tube = s["RACK_OR_PLATE_ID"] + "/" + s["TUBE_OR_WELL_ID"]
            recorded_sample = Sample().get_target_by_field("rack_tube", rack_tube)[0]
            for field in s.keys():
                if s[field] != recorded_sample.get(field, "") and s[field].strip() != recorded_sample["species_list"][
                    0].get(field, ""):
                    if field in lookup.SPECIES_LIST_FIELDS:
                        # record change
                        Sample().record_user_update(field, recorded_sample["species_list"][0][field], s[field],
                                                    recorded_sample["_id"])
                        # update sample
                        Sample().add_field("species_list.0." + str(field), s[field], recorded_sample["_id"])
                    else:
                        # record change
                        Sample().record_user_update(field, recorded_sample[field], s[field], recorded_sample["_id"])
                        # update sample
                        Sample().add_field(field, s[field], recorded_sample["_id"])

            uri = request.build_absolute_uri('/')
            # query public service service a first time now to trigger request for public names that don't exist
            public_names = query_public_name_service(self.public_name_list)
            for name in public_names:
                Sample().update_public_name(name)
            profile_id = request.session["profile_id"]
            profile = Profile().get_record(profile_id)
            title = profile["title"]
            description = profile["description"]


    def delete_sample(self, sample_ids):
        # accept a list of ids, try to delete creating report
        report = list()
        for s in sample_ids:
            r = Sample().delete_sample(s)
            report.append(r)
        notify_frontend(data={"profile_id": self.profile_id}, msg=report,
                        action="info",
                        html_id="sample_info")

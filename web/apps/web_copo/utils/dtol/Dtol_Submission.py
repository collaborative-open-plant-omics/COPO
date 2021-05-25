import json
import os
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, date
from urllib.parse import urljoin
from exceptions_and_logging import logger
import requests
# from celery.utils.log import get_task_logger
from web.apps.web_copo.lookup.copo_enums import *
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from dal.copo_da import Submission, Sample, Profile, Source
from submission.helpers.generic_helper import notify_dtol_status
from tools import resolve_env
from web.apps.web_copo.lookup.dtol_lookups import DTOL_ENA_MAPPINGS, DTOL_UNITS
from web.apps.web_copo.lookup.lookup import SRA_SETTINGS as settings
from web.apps.web_copo.lookup.lookup import SRA_SUBMISSION_TEMPLATE, SRA_SAMPLE_TEMPLATE, SRA_PROJECT_TEMPLATE
from web.apps.web_copo.utils.dtol.Dtol_Helpers import query_public_name_service
from bson import ObjectId
from django_tools.middlewares.ThreadLocal import get_current_request

with open(settings, "r") as settings_stream:
    sra_settings = json.loads(settings_stream.read())["properties"]

# logger = get_task_logger(__name__)
l = logger.Logger("exceptions_and_logging/logs")
exclude_from_sample_xml = []  # todo list of keys that shouldn't end up in the sample.xml file
ena_service = resolve_env.get_env('ENA_SERVICE')

# public_name_service = resolve_env.get_env('PUBLIC_NAME_SERVICE')

pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]

submission_id = ""
profile_id = ""


def process_pending_dtol_samples():
    '''
    method called from celery to initiate transfers to ENA, see celery.py for timings
    :return:
    '''

    # get all pending dtol submissions
    sub_id_list = Submission().get_pending_dtol_samples()
    tolidflag = True
    # send each to ENA for Biosample ids
    for submission in sub_id_list:

        # check if study exist for this submission and/or create one
        profile_id = submission["profile_id"]
        type_submission = submission["type"]
        #removing study for general case, will be useful for subset of submissions
        '''if not Submission().get_study(submission['_id']):
            create_study(submission['profile_id'], collection_id=submission['_id'])'''
        file_subfix = str(uuid.uuid4())  # use this to recover bundle sample file
        build_bundle_sample_xml(file_subfix)
        s_ids = []
        # check for public name with Sanger Name Service
        public_name_list = list()
        for s_id in submission["dtol_samples"]:
            sam = Sample().get_record(s_id)
            issymbiont = sam["species_list"][0].get("SYMBIONT", "TARGET")
            if issymbiont == "SYMBIONT":
                targetsam = Sample().get_target_by_specimen_id(sam["SPECIMEN_ID"])
                assert targetsam
                #ASSERT ALL TAXON ID ARE THE SAME, they can only be associated to one specimen
                assert all(x["species_list"][0]["TAXON_ID"] == targetsam[0]["species_list"][0]["TAXON_ID"] for x in targetsam)
                targetsam = targetsam[0]
            else:
                #this is to speed up source public id call
                targetsam = sam
            print(type(sam['public_name']), sam['public_name'])

            if not sam["public_name"]:
                try:
                    if issymbiont == "TARGET":
                        public_name_list.append(
                            {"taxonomyId": int(sam["species_list"][0]["TAXON_ID"]), "specimenId": sam["SPECIMEN_ID"],
                            "sample_id": str(sam["_id"])})
                    else:
                        public_name_list.append(
                            {"taxonomyId": int(targetsam["species_list"][0]["TAXON_ID"]), "specimenId": targetsam["SPECIMEN_ID"],
                             "sample_id": str(sam["_id"])})
                except ValueError:
                    notify_dtol_status(data={"profile_id": profile_id}, msg="Invalid Taxon ID found", action="info",
                                       html_id="dtol_sample_info")
                    return False

            s_ids.append(s_id)

            # check if specimen ID biosample was already registered, if not do it
            specimen_sample = Source().get_specimen_biosample(sam["SPECIMEN_ID"])
            try:
                assert len(specimen_sample) <= 1
            except AssertionError:
                l.log("Multiple sources for SPECIMEN_ID " + sam["SPECIMEN_ID"], type=Logtype.FILE)
                return False
            specimen_accession = ""
            if specimen_sample:
                specimen_accession = specimen_sample[0].get("biosampleAccession", "")
            else:
                # create sample object and submit
                notify_dtol_status(data={"profile_id": profile_id},
                                   msg="Creating Sample for SPECIMEN_ID " + sam["RACK_OR_PLATE_ID"] + "/" + sam[
                                       "SPECIMEN_ID"],
                                   action="info",
                                   html_id="dtol_sample_info")
                if type_submission == "asg":
                    sample_type = "asg_specimen"
                else:
                    sample_type = "dtol_specimen"
                if issymbiont == "TARGET":
                    specimen_obj_fields = {"SPECIMEN_ID": sam["SPECIMEN_ID"],
                                           "TAXON_ID": sam["species_list"][0]["TAXON_ID"],
                                           "sample_type": sample_type, "profile_id": sam['profile_id']}
                    Source().save_record(auto_fields={}, **specimen_obj_fields)
                    specimen_obj_fields = populate_source_fields(sam)
                    sour = Source().get_by_specimen(sam["SPECIMEN_ID"])[0]
                    Source().add_fields(specimen_obj_fields, str(sour['_id']))
                else:
                    #look for sample with same specimen ID which is target
                    specimen_obj_fields = {"SPECIMEN_ID": targetsam["SPECIMEN_ID"],
                                           "TAXON_ID": targetsam["species_list"][0]["TAXON_ID"],
                                           "sample_type": sample_type, "profile_id": targetsam['profile_id']}
                    Source().save_record(auto_fields={}, **specimen_obj_fields)
                    specimen_obj_fields = populate_source_fields(targetsam)
                    sour = Source().get_by_specimen(sam["SPECIMEN_ID"])[0]
                    Source().add_fields(specimen_obj_fields, str(sour['_id']))
            #source exists but doesn't have accession/source didn't exist
            if not specimen_accession:
                sour = Source().get_by_specimen(sam["SPECIMEN_ID"])
                try:
                    assert len(sour) == 1, "more than one source for SPECIMEN_ID " + sam["SPECIMEN_ID"]
                except AssertionError:
                    l.log("AssertionError: more than one source for SPECIMEN_ID " + sam["SPECIMEN_ID"], type=Logtype.FILE)
                sour = sour[0]
                if not sour['public_name']:
                    #retrieve public name
                    spec_tolid = query_public_name_service([{"taxonomyId": int(targetsam["species_list"][0]["TAXON_ID"]),
                                                             "specimenId": targetsam["SPECIMEN_ID"],
                                                             "sample_id": str(sam["_id"])}])
                    assert len(spec_tolid) == 1
                    if not spec_tolid[0].get("tolId", ""):
                        # hadle failure to get public names and halt submission
                        # change dtol_status to "awaiting_tolids"
                        msg = "We couldn't retrieve one or more public names, a request for a new tolId has been sent, COPO will try again in 24 hours"
                        notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                                           html_id="dtol_sample_info")
                        Submission().make_dtol_status_awaiting_tolids(submission['_id'])
                        tolidflag = False
                        break
                    Source().update_public_name(spec_tolid[0])
                    sour = Source().get_by_specimen(sam["SPECIMEN_ID"])
                    assert len(sour) == 1
                    sour = sour[0]

                build_specimen_sample_xml(sour)
                build_submission_xml(str(sour['_id']), release=True)
                accessions = submit_biosample(str(sour['_id']), Source(), submission['_id'], type="source")
                print(accessions)
                if accessions.get("status", "") == "error":
                    msg = "Submission Rejected: specimen level " + sam["SPECIMEN_ID"] + "<p>" + accessions[
                        "msg"] + "</p>"
                    notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                                       html_id="dtol_sample_info")
                    break
                specimen_accession = Source().get_specimen_biosample(sam["SPECIMEN_ID"])[0].get("biosampleAccession",
                                                                                                "")

            if not specimen_accession:
                Submission().make_dtol_status_pending(submission['_id'])
                msg="Connection issue - please try resubmit later"
                notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                                   html_id="dtol_sample_info")
                Submission().make_dtol_status_pending(submission['_id'])
                break
            #set appropriate relationship to specimen level sample
            if issymbiont == "SYMBIONT":
                Sample().add_field("sampleSymbiontOf", specimen_accession, sam['_id'])
                sam["sampleSymbiontOf"] = specimen_accession
            elif sam.get('ORGANISM_PART', '')=="WHOLE_ORGANISM":
                Sample().add_field("sampleSameAs", specimen_accession, sam['_id'])
                sam["sampleSameAs"] = specimen_accession
            else:
                Sample().add_field("sampleDerivedFrom", specimen_accession, sam['_id'])
                sam["sampleDerivedFrom"] = specimen_accession

            #making sure relationship between sample and specimen level sample is set
            try:
                updated_sample = Sample().get_record(sam['_id'])
                assert any([updated_sample.get("sampleSymbiontOf", ""), updated_sample.get("sampleSameAs", ""), updated_sample.get("sampleDerivedFrom", "")])
            except AssertionError:
                l.log("Missing relationship to parent sample for sample " + sam["_id"], type=Logtype.FILE)
                Submission().make_dtol_status_pending(submission['_id'])
                return False

            notify_dtol_status(data={"profile_id": profile_id}, msg="Adding to Sample Batch: " + sam["SPECIMEN_ID"],
                               action="info",
                               html_id="dtol_sample_info")

        # query for public names and update
        notify_dtol_status(data={"profile_id": profile_id}, msg="Querying Public Naming Service", action="info",
                           html_id="dtol_sample_info")
        public_names = query_public_name_service(public_name_list)
        if any(not public_names[x].get("tolId", "") for x in range(len(public_names))):
            #hadle failure to get public names and halt submission
            #change dtol_status to "awaiting_tolids"
            msg = "We couldn't retrieve one or more public names, a request for a new tolId has been sent, COPO will try again in 24 hours"
            notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                               html_id="dtol_sample_info")
            Submission().make_dtol_status_awaiting_tolids(submission['_id'])
            tolidflag = False

        for name in public_names:
            if name.get("tolId", ""):
                Sample().update_public_name(name)

        #if tolid missing for specimen skip
        if not tolidflag:
            os.remove("bundle_" + file_subfix + ".xml")
            break

        update_bundle_sample_xml(s_ids, "bundle_" + file_subfix + ".xml")
        build_submission_xml(file_subfix, release=True)

        # store accessions, remove sample id from bundle and on last removal, set status of submission
        accessions = submit_biosample(file_subfix, Sample(), submission['_id'])

        # print(accessions)
        if not accessions:
            notify_dtol_status(data={"profile_id": profile_id}, msg="Error creating sample - no accessions found", action="info",
                               html_id="dtol_sample_info")
            continue
        elif accessions["status"] == "ok":
            msg = "Last Sample Submitted: " + sam["SPECIMEN_ID"] + " - ENA Submission ID: " + accessions[
                "submission_accession"]  # + " - Biosample ID: " + accessions["biosample_accession"]
            notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                               html_id="dtol_sample_info")
        else:
            msg = "Submission Rejected: " + sam["SPECIMEN_ID"] + "<p>" + accessions["msg"] + "</p>"
            notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                               html_id="dtol_sample_info")
        Submission().dtol_sample_processed(sub_id=submission["_id"], sam_ids=s_ids)

    notify_dtol_status(data={"profile_id": profile_id}, msg="", action="hide_sub_spinner",
                       html_id="dtol_sample_info")

def query_awaiting_tolids():
    #get all submission awaiting for tolids
    sub_id_list = Submission().get_awaiting_tolids()
    for submission in sub_id_list:
        public_name_list = list()
        samplelist = submission["dtol_samples"]
        for samid in samplelist:
            sam = Sample().get_record(samid)
            if not sam["public_name"]:
                try:
                    public_name_list.append(
                        {"taxonomyId": int(sam["species_list"][0]["TAXON_ID"]), "specimenId": sam["SPECIMEN_ID"],
                         "sample_id": str(sam["_id"])})
                except ValueError:
                    return False
            assert len(public_name_list)>0
            public_names = query_public_name_service(public_name_list)
            #still no response, do nothing
            #NOTE the query fails even if only one TAXON_ID can't be found
            if not public_names:
                return
            #update samples and set dtol_sattus to pending
            else:
                for name in public_names:
                    if name.get("tolId", ""):
                        Sample().update_public_name(name)
                    else:
                        return
        Submission().make_dtol_status_pending(submission["_id"])

def populate_source_fields(sampleobj):
    '''populate source in db to copy most of sample fields
    but change organism part and gal sample_id'''
    fields = {}
    project = sampleobj["tol_project"]
    for item in sampleobj.items():
        #print(item)
        try:
            if project == "DTOL":
                if item[0] == "PARTNER" or item[0] == "PARTNER_SAMPLE_ID":
                    continue
            elif project == "ASG":
                if item[0] == "GAL" or item[0] == "GAL_SAMPLE_ID":
                    continue
            print(item[0])
            if item[0]=="COLLECTION_LOCATION" or DTOL_ENA_MAPPINGS[item[0]]['ena']:
                if item[0]=="GAL_SAMPLE_ID" or item[0]=="PARTNER_SAMPLE_ID":
                    fields[item[0]] = "NOT_PROVIDED"
                elif item[0]=="ORGANISM_PART":
                    fields[item[0]] = "WHOLE_ORGANISM"
                else:
                    fields[item[0]]=item[1]
        except KeyError:
            pass
    return fields


def build_bundle_sample_xml(file_subfix):
    '''build structure and save to file bundle_file_subfix.xml'''
    shutil.copy(SRA_SAMPLE_TEMPLATE, "bundle_" + file_subfix + ".xml")


def update_bundle_sample_xml(sample_list, bundlefile):
    '''update the sample with submission alias adding a new sample'''
    # print("adding sample to bundle sample xml")
    tree = ET.parse(bundlefile)
    root = tree.getroot()
    project = Sample().get_record(sample_list[0])['tol_project']
    for sam in sample_list:
        sample = Sample().get_record(sam)

        sample_alias = ET.SubElement(root, 'SAMPLE')
        sample_alias.set('alias', str(sample['_id']))  # updated to copo id to retrieve it when getting accessions
        sample_alias.set('center_name', 'EarlhamInstitute')  # mandatory for broker account
        title = str(uuid.uuid4()) + "-" + project.lower()

        title_block = ET.SubElement(sample_alias, 'TITLE')
        title_block.text = title
        sample_name = ET.SubElement(sample_alias, 'SAMPLE_NAME')
        taxon_id = ET.SubElement(sample_name, 'TAXON_ID')
        taxon_id.text = sample.get("species_list", [])[0].get('TAXON_ID', "")
        sample_attributes = ET.SubElement(sample_alias, 'SAMPLE_ATTRIBUTES')
        # validating against TOL checklist
        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
        tag = ET.SubElement(sample_attribute, 'TAG')
        tag.text = 'ENA-CHECKLIST'
        value = ET.SubElement(sample_attribute, 'VALUE')
        value.text = 'ERC000053'

        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
        tag = ET.SubElement(sample_attribute, 'TAG')
        tag.text = 'project name'
        value = ET.SubElement(sample_attribute, 'VALUE')
        value.text = project
        #if project is ASG add symbiont
        if project == "ASG":
            sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
            tag = ET.SubElement(sample_attribute, 'TAG')
            tag.text = 'SYMBIONT'
            value = ET.SubElement(sample_attribute, 'VALUE')
            if sample.get("species_list", [])[0].get('SYMBIONT', "")=="symbiont":
                issymbiont = True
            else:
                issymbiont = False
            if issymbiont:
                value.text = "Y"
            else:
                value.text = "N"
        ##### for item in obj_id: if item in checklist (or similar according to some criteria).....
        for item in sample.items():
            if item[1]:
                try:
                    #exceptional handling of fields that should only be present for certain projects
                    if project == "DTOL":
                        if item[0] == "PARTNER" or item[0] == "PARTNER_SAMPLE_ID" or item[0]=="SYMBIONT": #TODO CHANGE IN SOP2.3
                            continue
                    elif project == "ASG":
                        if item[0] == "GAL" or item[0] == "GAL_SAMPLE_ID":
                            continue
                    # exceptional handling of COLLECTION_LOCATION
                    if item[0] == 'COLLECTION_LOCATION':
                        attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_1']['ena']
                        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                        tag = ET.SubElement(sample_attribute, 'TAG')
                        tag.text = attribute_name
                        value = ET.SubElement(sample_attribute, 'VALUE')
                        value.text = str(item[1]).split('|')[0]
                        attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_2']['ena']
                        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                        tag = ET.SubElement(sample_attribute, 'TAG')
                        tag.text = attribute_name
                        value = ET.SubElement(sample_attribute, 'VALUE')
                        value.text = '|'.join(str(item[1]).split('|')[1:])
                    elif item[0] in ["DATE_OF_COLLECTION", "DECIMAL_LATITUDE", "DECIMAL_LONGITUDE"]:
                        attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                        tag = ET.SubElement(sample_attribute, 'TAG')
                        tag.text = attribute_name
                        value = ET.SubElement(sample_attribute, 'VALUE')
                        value.text = str(item[1]).lower().replace("_", " ")
                    # handling annoying edge case below
                    elif item[0] == "LIFESTAGE" and item[1] == "SPORE_BEARING_STRUCTURE":
                        attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                        tag = ET.SubElement(sample_attribute, 'TAG')
                        tag.text = attribute_name
                        value = ET.SubElement(sample_attribute, 'VALUE')
                        value.text = "spore-bearing structure"
                    else:
                        attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                        sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                        tag = ET.SubElement(sample_attribute, 'TAG')
                        tag.text = attribute_name
                        value = ET.SubElement(sample_attribute, 'VALUE')
                        value.text = str(item[1]).replace("_", " ")
                    # add ena units where necessary
                    if DTOL_UNITS.get(item[0], ""):
                        if DTOL_UNITS[item[0]].get('ena_unit', ""):
                            unit = ET.SubElement(sample_attribute, 'UNITS')
                            unit.text = DTOL_UNITS[item[0]]['ena_unit']
                except KeyError:
                    # pass, item is not supposed to be submitted to ENA
                    pass

    ET.dump(tree)
    tree.write(open(bundlefile, 'w'),
               encoding='unicode')


def build_specimen_sample_xml(sample):
    # build specimen sample XML
    tree = ET.parse(SRA_SAMPLE_TEMPLATE)
    root = tree.getroot()
    project = sample['sample_type'].split("_")[0].upper()
    # from toni's code below
    # set sample attributes
    sample_alias = ET.SubElement(root, 'SAMPLE')
    sample_alias.set('alias', str(sample['_id']))  # updated to copo id to retrieve it when getting accessions
    sample_alias.set('center_name', 'EarlhamInstitute')  # mandatory for broker account
    title = str(uuid.uuid4()) + "-"+ project +"-specimen"

    title_block = ET.SubElement(sample_alias, 'TITLE')
    title_block.text = title
    sample_name = ET.SubElement(sample_alias, 'SAMPLE_NAME')
    taxon_id = ET.SubElement(sample_name, 'TAXON_ID')
    taxon_id.text = sample.get('TAXON_ID', "")



    sample_attributes = ET.SubElement(sample_alias, 'SAMPLE_ATTRIBUTES')
    # validating against DTOL checklist
    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
    tag = ET.SubElement(sample_attribute, 'TAG')
    tag.text = 'ENA-CHECKLIST'
    value = ET.SubElement(sample_attribute, 'VALUE')
    value.text = 'ERC000053'
    # adding project name field (ie copo profile name)
    # validating against DTOL checklist
    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
    tag = ET.SubElement(sample_attribute, 'TAG')
    tag.text = 'project name'
    value = ET.SubElement(sample_attribute, 'VALUE')
    value.text = project
    ##### for item in obj_id: if item in checklist (or similar according to some criteria).....
    for item in sample.items():
        if item[1]:
            try:
                #exceptional handling of fields that may be empty in different projects
                if project == "ASG":
                    if item[0] == 'GAL' or item[0] == "GAL_SAMPLE_ID":
                        continue
                elif project == "DTOL":
                    if item[0] == "PARTNER" or item[0] == "PARTNER_SAMPLE_ID":
                        continue
                # exceptional handling of COLLECTION_LOCATION
                if item[0] == 'COLLECTION_LOCATION':
                    attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_1']['ena']
                    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                    tag = ET.SubElement(sample_attribute, 'TAG')
                    tag.text = attribute_name
                    value = ET.SubElement(sample_attribute, 'VALUE')
                    value.text = str(item[1]).split('|')[0]
                    attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_2']['ena']
                    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                    tag = ET.SubElement(sample_attribute, 'TAG')
                    tag.text = attribute_name
                    value = ET.SubElement(sample_attribute, 'VALUE')
                    value.text = '|'.join(str(item[1]).split('|')[1:])
                elif item[0] in ["DATE_OF_COLLECTION", "DECIMAL_LATITUDE", "DECIMAL_LONGITUDE"]:
                    attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                    tag = ET.SubElement(sample_attribute, 'TAG')
                    tag.text = attribute_name
                    value = ET.SubElement(sample_attribute, 'VALUE')
                    value.text = str(item[1]).lower().replace("_", " ")
                # handling annoying edge case below
                elif item[0] == "LIFESTAGE" and item[1] == "SPORE_BEARING_STRUCTURE":
                    attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                    tag = ET.SubElement(sample_attribute, 'TAG')
                    tag.text = attribute_name
                    value = ET.SubElement(sample_attribute, 'VALUE')
                    value.text = "spore-bearing structure"
                else:
                    attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
                    tag = ET.SubElement(sample_attribute, 'TAG')
                    tag.text = attribute_name
                    value = ET.SubElement(sample_attribute, 'VALUE')
                    value.text = str(item[1]).replace("_", " ")
                # add ena units where necessary
                if DTOL_UNITS.get(item[0], ""):
                    if DTOL_UNITS[item[0]].get('ena_unit', ""):
                        unit = ET.SubElement(sample_attribute, 'UNITS')
                        unit.text = DTOL_UNITS[item[0]]['ena_unit']
            except KeyError:
                # pass, item is not supposed to be submitted to ENA
                pass

    ET.dump(tree)
    sample_id = str(sample['_id'])
    samplefile = "bundle_" + str(sample_id) + ".xml"
    tree.write(open(samplefile, 'w'),
               encoding='unicode')


def build_submission_xml(sample_id, hold="", release=False):
    # build submission XML
    tree = ET.parse(SRA_SUBMISSION_TEMPLATE)
    root = tree.getroot()
    # from toni's code below
    # set submission attributes
    root.set("submission_date", datetime.utcnow().replace(tzinfo=d_utils.simple_utc()).isoformat())

    # set SRA contacts
    contacts = root.find('CONTACTS')

    # set copo sra contacts
    copo_contact = ET.SubElement(contacts, 'CONTACT')
    copo_contact.set("name", sra_settings["sra_broker_contact_name"])
    copo_contact.set("inform_on_error", sra_settings["sra_broker_inform_on_error"])
    copo_contact.set("inform_on_status", sra_settings["sra_broker_inform_on_status"])
    if hold:
        actions = root.find('ACTIONS')
        action = ET.SubElement(actions, 'ACTION')
        hold_block = ET.SubElement(action, 'HOLD')
        hold_block.set("HoldUntilDate", hold)
    if release:
        actions = root.find('ACTIONS')
        action = ET.SubElement(actions, 'ACTION')
        release_block = ET.SubElement(action, 'RELEASE')
    ET.dump(tree)
    submissionfile = "submission_" + str(sample_id) + ".xml"
    tree.write(open(submissionfile, 'w'),
               encoding='unicode')  # overwriting at each run, i don't think we need to keep it


def build_validate_xml(sample_id):
    # TODO do we need this method at all? Its never actually used right?
    # build submission XML
    tree = ET.parse(SRA_SUBMISSION_TEMPLATE)
    root = tree.getroot()
    # set submission attributes
    root.set("submission_date", datetime.utcnow().replace(tzinfo=d_utils.simple_utc()).isoformat())
    # set SRA contacts
    contacts = root.find('CONTACTS')
    # set copo sra contacts
    copo_contact = ET.SubElement(contacts, 'CONTACT')
    copo_contact.set("name", sra_settings["sra_broker_contact_name"])
    copo_contact.set("inform_on_error", sra_settings["sra_broker_inform_on_error"])
    copo_contact.set("inform_on_status", sra_settings["sra_broker_inform_on_status"])
    # set user contacts
    sra_map = {"inform_on_error": "SRA Inform On Error", "inform_on_status": "SRA Inform On Status"}
    # change ADD to VALIDATE
    root.find('ACTIONS').find('ACTION').clear()
    action = root.find('ACTIONS').find('ACTION')
    ET.SubElement(action, 'VALIDATE')
    ET.dump(tree)
    submissionvalidatefile = "submission_validate_" + str(sample_id) + ".xml"
    tree.write(open(submissionvalidatefile, 'w'),
               encoding='unicode')


def submit_biosample(subfix, sampleobj, collection_id, type="sample"):
    # register project to the ENA service using XML files previously created

    submissionfile = "submission_" + str(subfix) + ".xml"
    samplefile = "bundle_" + str(subfix) + ".xml"
    curl_cmd = 'curl -m 300 -u ' + user_token + ':' + pass_word \
               + ' -F "SUBMISSION=@' \
               + submissionfile \
               + '" -F "SAMPLE=@' \
               + samplefile \
               + '" "' + ena_service \
               + '"'

    try:
        receipt = subprocess.check_output(curl_cmd, shell=True)

        l.log("ENA RECEIPT " + str(receipt), type=Logtype.FILE)
        print(receipt)
    except Exception as e:
        l.log("General Error " + str(e), type=Logtype.FILE)
        message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
            pass_word, "xxxxxx")
        notify_dtol_status(data={"profile_id": profile_id}, msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(samplefile)

        reset_submission_status(collection_id)
        return False
        # print(message)

    try:
        tree = ET.fromstring(receipt)
    except ET.ParseError as e:
        l.log("Unrecognized response from ENA " + str(e), type=Logtype.FILE)
        message = " Unrecognized response from ENA - " + str(
            receipt) + " Please try again later, if it persists contact admins"
        notify_dtol_status(data={"profile_id": profile_id}, msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(samplefile)
        reset_submission_status(collection_id)
        return False

    os.remove(submissionfile)
    os.remove(samplefile)
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
        for child in tree.iter():
            if child.tag == 'SAMPLE':
                sample_id = child.get('alias')
                sampleobj.add_rejected_status(status, sample_id)

        # print('error')
        l.log("Success False" + str(msg), type=Logtype.FILE)
        return status
    else:
        # retrieve id and update record
        # return get_biosampleId(receipt, sample_id, collection_id)
        return get_bundle_biosampleId(receipt, collection_id, type)


def get_bundle_biosampleId(receipt, collection_id, type="sample"):
    '''parsing ENA sample bundle accessions from receipt and
    storing in sample and submission collection object'''
    tree = ET.fromstring(receipt)
    submission_accession = tree.find('SUBMISSION').get('accession')
    for child in tree.iter():
        if child.tag == 'SAMPLE':
            sample_id = child.get('alias')
            sra_accession = child.get('accession')
            biosample_accession = child.find('EXT_ID').get('accession')
            if type == "sample":
                Sample().add_accession(biosample_accession, sra_accession, submission_accession, sample_id)
                Submission().add_accession(biosample_accession, sra_accession, submission_accession, sample_id,
                                           collection_id)
            elif type == "source":
                Source().add_accession(biosample_accession, sra_accession, submission_accession, sample_id)
    accessions = {"submission_accession": submission_accession, "status": "ok"}
    return accessions


def get_studyId(receipt, collection_id):
    # parsing ENA study accessions from receipt and storing in submission collection
    tree = ET.fromstring(receipt)
    project = tree.find('PROJECT')
    bioproject_accession = project.get('accession')
    ext_id = project.find('EXT_ID')
    sra_study_accession = ext_id.get('accession')
    submission = tree.find('SUBMISSION')
    study_accession = submission.get('accession')
    # print(bioproject_accession, sra_study_accession, study_accession) ######
    Submission().add_study_accession(bioproject_accession, sra_study_accession, study_accession, collection_id)
    accessions = {"bioproject_accession": bioproject_accession, "sra_study_accession": sra_study_accession,
                  "study_accession": study_accession, "status": "ok"}
    return accessions


def reset_submission_status(submission_id):
    doc = Submission().get_collection_handle().find_one({"_id": ObjectId(submission_id)})
    l = len(doc["dtol_samples"])
    if l > 0:
        status = "pending"
    else:
        status = "complete"
    Submission().get_collection_handle().update({"_id": ObjectId(submission_id)}, {"$set": {"dtol_status": status}})


def create_study(profile_id, collection_id):
    # build study XML
    profile = Profile().get_record(profile_id)
    tree = ET.parse(SRA_PROJECT_TEMPLATE)
    root = tree.getroot()
    # set study attributes
    project = root.find('PROJECT')
    project.set('alias', str(profile['copo_id']))
    project.set('center_name', 'EarlhamInstitute')
    title_block = ET.SubElement(project, 'TITLE')
    title_block.text = profile['title']
    project_description = ET.SubElement(project, 'DESCRIPTION')
    project_description.text = profile['description']
    submission_project = ET.SubElement(project, 'SUBMISSION_PROJECT')
    sequencing_project = ET.SubElement(submission_project, 'SEQUENCING_PROJECT')
    ET.dump(tree)
    studyfile = "study_" + profile_id + ".xml"
    # print(studyfile)
    tree.write(open(studyfile, 'w'),
               encoding='unicode')

    submissionfile = "submission_" + profile_id + ".xml"
    build_submission_xml(profile_id, hold=date.today().strftime("%Y-%m-%d"))

    curl_cmd = 'curl -u -m 300' + user_token + ':' + pass_word \
               + ' -F "SUBMISSION=@' \
               + submissionfile \
               + '" -F "PROJECT=@' \
               + studyfile \
               + '" "' + ena_service \
               + '"'
    try:
        receipt = subprocess.check_output(curl_cmd, shell=True)
        # print(receipt)
    except Exception as e:
        message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
            pass_word, "xxxxxx")
        notify_dtol_status(data={"profile_id": profile_id}, msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(studyfile)
        return False
    # print(receipt)
    try:
        tree = ET.fromstring(receipt)
    except ET.ParseError as e:
        message = " Unrecognized response from ENA - " + str(
            receipt) + " Please try again later, if it persists contact admins"
        notify_dtol_status(data={"profile_id": profile_id}, msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(studyfile)
        return False

    os.remove(submissionfile)
    os.remove(studyfile)
    success_status = tree.get('success')
    if success_status == 'false':
        msg = tree.find('MESSAGES').findtext('ERROR', default='Undefined error')
        status = {"status": "error", "msg": msg}
        return status
    else:
        # retrieve id and update record
        accessions = get_studyId(receipt, collection_id)

    if accessions["status"] == "ok":
        msg = "Study Submitted " + " - BioProject ID: " + accessions["bioproject_accession"] + " - SRA Study ID: " + \
              accessions["sra_study_accession"]
        notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                           html_id="dtol_sample_info")
    else:
        msg = "Submission Rejected: " + "<p>" + accessions["msg"] + "</p>"
        notify_dtol_status(data={"profile_id": profile_id}, msg=msg, action="info",
                           html_id="dtol_sample_info")


'''def query_public_name_service(sample_list):
    headers = {"api-key": API_KEY}
    url = urljoin(public_name_service, 'tol-ids')  # public-name
    try:
        r = requests.post(url=url, json=sample_list, headers=headers, verify=False)
        if r.status_code == 200:
            resp = json.loads(r.content)
        else:
            # in the case there is a network issue, just return an empty dict
            resp = {}
        return resp
    except Exception as e:
        print("PUBLIC NAME SERVER ERROR: " + str(e))
        return {}'''

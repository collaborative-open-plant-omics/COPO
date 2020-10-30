import json
import subprocess
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, date
import os
import shutil
import requests
from celery.utils.log import get_task_logger
from urllib.parse import urljoin
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from dal.copo_da import Submission, Sample, Profile, Source
from submission.helpers.generic_helper import notify_dtol_status
from tools import resolve_env
from web.apps.web_copo.lookup.lookup import SRA_SETTINGS as settings
from web.apps.web_copo.lookup.lookup import SRA_SUBMISSION_TEMPLATE, SRA_SAMPLE_TEMPLATE, SRA_PROJECT_TEMPLATE
from web.apps.web_copo.lookup.dtol_lookups import DTOL_ENA_MAPPINGS, DTOL_UNITS, PUBLIC_NAME_SERVICE, \
    API_KEY

with open(settings, "r") as settings_stream:
    sra_settings = json.loads(settings_stream.read())["properties"]

logger = get_task_logger(__name__)

exclude_from_sample_xml = []  # todo list of keys that shouldn't end up in the sample.xml file
ena_service = resolve_env.get_env('ENA_SERVICE')
#ena_service = resolve_env.get_env('ENA_TEST_SERVICE')
pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]

submission_id = ""


def process_pending_dtol_samples():
    '''
    method called from celery to initiate transfers to ENA, see celery.py for timings
    :return:
    '''

    # get all pending dtol submissions
    sample_id_list = Submission().get_pending_dtol_samples()
    # send each to ENA for Biosample ids
    for submission in sample_id_list:
        # check if study exist for this submission and/or create one
        if not Submission().get_study(submission['_id']):
            create_study(submission['profile_id'], collection_id=submission['_id'])
        file_subfix = str(uuid.uuid4())  # use this to recover bundle sample file
        build_bundle_sample_xml(file_subfix)
        s_ids = []
        # check for public name with Sanger Name Service
        public_name_list = list()
        for s_id in submission["dtol_samples"]:
            sam = Sample().get_record(s_id)
            try:
                public_name_list.append(
                    {"taxonomyId": int(sam["TAXON_ID"]), "specimenId": sam["SPECIMEN_ID"], "sample_id": str(sam["_id"])})
            except ValueError:
                notify_dtol_status(msg="Invalid Taxon ID found", action="info",
                                   html_id="dtol_sample_info")
                return False

            s_ids.append(s_id)

            #check if specimen ID biosample was already registered, if not do it
            specimen_sample = Source().get_specimen_biosample(sam["SPECIMEN_ID"])
            assert len(specimen_sample) <= 1
            if not specimen_sample:
                #create sample object and submit
                notify_dtol_status(msg="Creating Sample for SPECIMEN_ID "+ sam["SPECIMEN_ID"], action="info",
                                   html_id="dtol_sample_info")
                specimen_obj_fields = { "SPECIMEN_ID" : sam["SPECIMEN_ID"], "TAXON_ID" : sam["TAXON_ID"],
                                        "sample_type" : "dtol_specimen", "profile_id" : sam['profile_id']}
                Source().save_record(auto_fields={},**specimen_obj_fields)
                sour = Source().get_by_specimen(sam["SPECIMEN_ID"])
                assert len(sour) == 1
                sour = sour[0]
                build_specimen_sample_xml(sour)
                build_submission_xml(str(sour['_id']), release=True)
                accessions = submit_biosample(str(sour['_id']), Source(), submission['_id'], type="source")
                print(accessions)
                specimen_accession = Source().get_specimen_biosample(sam["SPECIMEN_ID"])[0].get("biosampleAccession", "")

            else:
                specimen_accession = specimen_sample[0].get("biosampleAccession", "")

            Sample().add_field("sampleDerivedFrom", specimen_accession, sam['_id'])
            sam["sampleDerivedFrom"] = specimen_accession
            notify_dtol_status(msg="Adding to Sample Batch: " + sam["SPECIMEN_ID"], action="info",
                               html_id="dtol_sample_info")
            update_bundle_sample_xml(sam, "bundle_" + file_subfix + ".xml")

        # query for public names and update
        notify_dtol_status(msg="Querying Public Naming Service", action="info",
                           html_id="dtol_sample_info")
        public_names = query_public_name_service(public_name_list)
        for name in public_names:
            Sample().update_public_name(name)

        build_submission_xml(file_subfix, release=True)

        # store accessions, remove sample id from bundle and on last removal, set status of submission
        accessions = submit_biosample(file_subfix, Sample(), submission['_id'])
        #print(accessions)
        if not accessions:
            continue
        elif accessions["status"] == "ok":
            msg = "Last Sample Submitted: " + sam["SPECIMEN_ID"] + " - ENA Submission ID: " + accessions[
                "submission_accession"]  # + " - Biosample ID: " + accessions["biosample_accession"]
            notify_dtol_status(msg=msg, action="info",
                               html_id="dtol_sample_info")
        else:
            msg = "Submission Rejected: " + sam["SPECIMEN_ID"] + "<p>" + accessions["msg"] + "</p>"
            notify_dtol_status(msg=msg, action="info",
                               html_id="dtol_sample_info")
        Submission().dtol_sample_processed(sub_id=submission["_id"], sam_ids=s_ids)


def build_bundle_sample_xml(file_subfix):
    '''build structure and save to file bundle_file_subfix.xml'''
    shutil.copy(SRA_SAMPLE_TEMPLATE, "bundle_" + file_subfix + ".xml")


def update_bundle_sample_xml(sample, bundlefile):
    '''update the sample with submission alias alias adding a new sample'''
    #print("adding sample to bundle sample xml")
    tree = ET.parse(bundlefile)
    root = tree.getroot()
    sample_alias = ET.SubElement(root, 'SAMPLE')
    sample_alias.set('alias', str(sample['_id']))  # updated to copo id to retrieve it when getting accessions
    sample_alias.set('center_name', 'EarlhamInstitute')  # mandatory for broker account
    title = str(uuid.uuid4())+"-dtol"

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
    #adding reference to parent specimen biosample
    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
    tag = ET.SubElement(sample_attribute, 'TAG')
    tag.text = 'sample derived from'
    value = ET.SubElement(sample_attribute, 'VALUE')
    value.text = sample.get("sampleDerivedFrom", "")
    #adding project name field (ie copo profile name)
    # validating against DTOL checklist
    sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
    tag = ET.SubElement(sample_attribute, 'TAG')
    tag.text = 'project name'
    value = ET.SubElement(sample_attribute, 'VALUE')
    value.text = 'DTOL'#Profile().get_record(sample["profile_id"])["title"]
    ##### for item in obj_id: if item in checklist (or similar according to some criteria).....
    for item in sample.items():
        if item[1]:
            try:
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
                #handling annoying edge case below
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
    # from toni's code below
    # set sample attributes
    sample_alias = ET.SubElement(root, 'SAMPLE')
    sample_alias.set('alias', str(sample['_id']))  # updated to copo id to retrieve it when getting accessions
    sample_alias.set('center_name', 'EarlhamInstitute')  # mandatory for broker account
    title = str(uuid.uuid4())+"-dtol-specimen"

    title_block = ET.SubElement(sample_alias, 'TITLE')
    title_block.text = title
    sample_name = ET.SubElement(sample_alias, 'SAMPLE_NAME')
    taxon_id = ET.SubElement(sample_name, 'TAXON_ID')
    taxon_id.text = sample.get('TAXON_ID', "")
    ET.dump(tree)
    sample_id = str(sample['_id'])
    samplefile = "bundle_" + str(sample_id) + ".xml"
    tree.write(open(samplefile, 'w'),
               encoding='unicode')


def build_xml(sample, sub_id, p_id, collection_id, file_subfix):
    notify_dtol_status(msg="Creating Sample: " + sample.get("SPECIMEN_ID", ""), action="info",
                       html_id="dtol_sample_info")
    # build_sample_xml(sample)
    update_bundle_sample_xml(sample, "bundle_" + file_subfix + ".xml")
    sample_id = str(sample['_id'])
    # build_validate_xml(sample_id)
    build_submission_xml(sample_id, release=True)
    notify_dtol_status(msg="Communicating with ENA", action="info",
                       html_id="dtol_sample_info")
    accessions = submit_biosample(sample_id, Sample(), collection_id)
    # print(accessions)
    if accessions["status"] == "ok":
        msg = "Last Sample Submitted: " + sample["SPECIMEN_ID"] + " - ENA ID: " + accessions[
            "submission_accession"] + " - Biosample ID: " + accessions["biosample_accession"]
        notify_dtol_status(msg=msg, action="info",
                           html_id="dtol_sample_info")
    else:
        msg = "Submission Rejected: " + sample["SPECIMEN_ID"] + "<p>" + accessions["msg"] + "</p>"
        notify_dtol_status(msg=msg, action="info",
                           html_id="dtol_sample_info")


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
               encoding='unicode')  # overwriting at each run, i don't think we need to keep it - todo again I think these should have unique id attached, and then file deleted after submission


def submit_biosample(subfix, sampleobj, collection_id, type="sample"):
    # register project to the ENA service using XML files previously created
    submissionfile = "submission_" + str(subfix) + ".xml"
    samplefile = "bundle_" + str(subfix) + ".xml"
    curl_cmd = 'curl -u ' + user_token + ':' + pass_word \
               + ' -F "SUBMISSION=@' \
               + submissionfile \
               + '" -F "SAMPLE=@' \
               + samplefile \
               + '" "' + ena_service \
               + '"'

    try:
        receipt = subprocess.check_output(curl_cmd, shell=True)
        print(receipt)
    except Exception as e:
        message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
            pass_word, "xxxxxx")
        notify_dtol_status(msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(samplefile)
        return False
        # print(message)

    try:
        tree = ET.fromstring(receipt)
    except ET.ParseError as e:
        message = " Unrecognized response from ENA - " + str(receipt) + " Please try again later, if it persists contact admins"
        notify_dtol_status(msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(samplefile)
        return False

    os.remove(submissionfile)
    os.remove(samplefile)
    success_status = tree.get('success')
    if success_status == 'false':  ####todo

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
        return status
    else:
        # retrieve id and update record
        #return get_biosampleId(receipt, sample_id, collection_id)
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
            if type=="sample":
                Sample().add_accession(biosample_accession, sra_accession, submission_accession, sample_id)
                Submission().add_accession(biosample_accession, sra_accession, submission_accession, sample_id,
                                       collection_id)
            elif type=="source":
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

    curl_cmd = 'curl -u ' + user_token + ':' + pass_word \
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
        notify_dtol_status(msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(studyfile)
        return False
    # print(receipt)
    try:
        tree = ET.fromstring(receipt)
    except ET.ParseError as e:
        message = " Unrecognized response from ENA - " + str(receipt) + " Please try again later, if it persists contact admins"
        notify_dtol_status(msg=message, action="error",
                           html_id="dtol_sample_info")
        os.remove(submissionfile)
        os.remove(studyfile)
        return False
    os.remove(submissionfile)
    os.remove(studyfile)
    success_status = tree.get('success')
    if success_status == 'false':  ####todo
        msg = tree.find('MESSAGES').findtext('ERROR', default='Undefined error')
        status = {"status": "error", "msg": msg}
        return status
    else:
        # retrieve id and update record
        accessions = get_studyId(receipt, collection_id)

    if accessions["status"] == "ok":
        msg = "Study Submitted " + " - BioProject ID: " + accessions["bioproject_accession"] + " - SRA Study ID: " + \
              accessions["sra_study_accession"]
        notify_dtol_status(msg=msg, action="info",
                           html_id="dtol_sample_info")
    else:
        msg = "Submission Rejected: " + "<p>" + accessions["msg"] + "</p>"
        notify_dtol_status(msg=msg, action="info",
                           html_id="dtol_sample_info")


def query_public_name_service(sample_list):
    return {}
    '''headers = {"api-key":API_KEY}
    url = urljoin(PUBLIC_NAME_SERVICE, 'public-name')
    r = requests.post(url=url, json=sample_list, headers=headers, verify=False)
    if r.status_code == 200:
        resp = json.loads(r.content)

    else:

        resp = {}
    return resp'''
import requests
from lxml import etree as ET
from tools import resolve_env
from dal.copo_da import TaggedSequenceChecklist, TaggedSequence, Submission
from exceptions_and_logging import logger
from web.apps.web_copo.validators.ena_validators import ena_tagged_seq_validators  as required_validators
from django_tools.middlewares import ThreadLocal
import inspect
from web.apps.web_copo.validators.validator import Validator
from submission.helpers.generic_helper import notify_tagged_seq_status
import pandas 
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype, get_datetime, get_not_deleted_flag
from web.apps.web_copo.schema_versions.lookup import dtol_lookups as lookup
import math
from web.apps.web_copo.schemas.utils import data_utils
from django.http import HttpResponse, JsonResponse
from api.utils import map_to_dict
import web.apps.web_copo.templatetags.html_tags as htags
from submission.helpers.ena_helper import SubmissionHelper
from datetime import datetime
import os
from web.apps.web_copo.lookup.resolver import RESOLVER
from web.apps.web_copo.lookup.lookup import SRA_SUBMISSION_TEMPLATE, SRA_PROJECT_TEMPLATE, \
    SRA_SUBMISSION_MODIFY_TEMPLATE, ENA_CLI
import subprocess
from django.conf import settings
from bson import ObjectId
from pathlib import Path
import pandas as pd
import gzip
import shutil
import re
import glob
from web.apps.web_copo.lookup.lookup import SRA_SETTINGS
l = logger.Logger()
import uuid

class EnaTaggedSequence:
    pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
    user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
    ena_service = resolve_env.get_env('ENA_SERVICE')
    headers = {'Accept': 'application/xml' }
    sra_settings = data_utils.json_to_pytype(SRA_SETTINGS).get("properties", dict())
    submission_helper = None
    submission_path = os.path.join(Path(settings.MEDIA_ROOT), "ena_tagged_seq_files")
    the_submission= None

    def loadCheckList(self):
        url = "https://www.ebi.ac.uk/ena/submit/report/checklists/xml/*?type=sequence"
        with requests.Session() as session:    
            session.auth = (self.user_token, self.pass_word) 
            try:
                response = session.get(url,headers=self.headers)
                return response.text
            except Exception as e:
                l.exception(e)
                return False            
    
    '''
    <CHECKLIST_SET>
    <CHECKLIST accession="ERT000028" checklistType="Sequence">
    <IDENTIFIERS>
        <PRIMARY_ID>ERT000028</PRIMARY_ID>
    </IDENTIFIERS>
    <DESCRIPTOR>
        <LABEL>Single Viral CDS</LABEL>
        <NAME>Single Viral CDS</NAME>
        <DESCRIPTION>For complete or partial single coding sequence (CDS) from a viral gene. Please do not use for peptides processed from polyproteins or proviral sequences, as these are all annotated differently.</DESCRIPTION>
        <AUTHORITY>ENA</AUTHORITY>
        <FIELD_GROUP restrictionType="Any number or none of the fields">
            <NAME>Mandatory Fields and Questions</NAME>
            <FIELD>
                <LABEL>VMOLTYPE</LABEL>
                <NAME>Molecule Type</NAME>
                <DESCRIPTION>Type of in vivo molecule sequenced. Taken from the INSDC controlled vocabulary. Example: Genomic DNA, Genomic RNA, viral cRNA.</DESCRIPTION>
                <FIELD_TYPE>
                <TEXT_CHOICE_FIELD>
                    <TEXT_VALUE>
                        <VALUE>genomic DNA</VALUE>
                    </TEXT_VALUE>
                    <TEXT_VALUE>
                        <VALUE>genomic RNA</VALUE>
                    </TEXT_VALUE>
                    <TEXT_VALUE>
                        <VALUE>viral cRNA</VALUE>
                    </TEXT_VALUE>
                </TEXT_CHOICE_FIELD>
                </FIELD_TYPE>
                <MANDATORY>mandatory</MANDATORY>
                <MULTIPLICITY>single</MULTIPLICITY>
            </FIELD>
            <FIELD>
                <LABEL>ORGANISM</LABEL>
                <NAME>Organism</NAME>
                <DESCRIPTION>Full name of virus (ICTV-approved or otherwise), NCBI taxid, BioSample accession, SRA sample accession, or sample alias. Influenza, Norovirus, Sapovirus and HIV have special nomenclature. Please contact us if you are unsure. Example: Raspberry bushy dwarf virus, Influenza A virus (A/chicken/Germany/1949(H10N7)), HIV-1 M:F_CHU51.</DESCRIPTION>
                <FIELD_TYPE>
                <TAXON_FIELD/>
                </FIELD_TYPE>
                <MANDATORY>mandatory</MANDATORY>
                <MULTIPLICITY>single</MULTIPLICITY>
            </FIELD>
            <FIELD>
                <LABEL>GENE</LABEL>
                <NAME>Gene</NAME>
                <DESCRIPTION>Symbol of the gene corresponding to a sequence region. Example: RdRp, CP, ORF1.</DESCRIPTION>
                <FIELD_TYPE>
                <TEXT_FIELD/>
                </FIELD_TYPE>
                <MANDATORY>mandatory</MANDATORY>
                <MULTIPLICITY>single</MULTIPLICITY>
            </FIELD>
            <FIELD>
                <LABEL>SVCGRTABLE</LABEL>
                <NAME>Translation table</NAME>
                <DESCRIPTION>Translation table for this virus. Chose between standard (table 1) and mitovirus codes (table 4.). Example: 1, 4.</DESCRIPTION>
                <FIELD_TYPE>
                <TEXT_FIELD/>
                </FIELD_TYPE>
                <MANDATORY>mandatory</MANDATORY>
                <MULTIPLICITY>single</MULTIPLICITY>
            </FIELD>
            <FIELD>
                <LABEL>5PARTIAL</LABEL>
                <NAME>Partial at 5' ? (yes/no)</NAME>
                <DESCRIPTION>For an incomplete CDS with the start codon upstream of the submitted sequence.</DESCRIPTION>
                <FIELD_TYPE>
                <TEXT_CHOICE_FIELD>
                    <TEXT_VALUE>
                        <VALUE>yes</VALUE>
                    </TEXT_VALUE>
                    <TEXT_VALUE>
                        <VALUE>no</VALUE>
                    </TEXT_VALUE>
                </TEXT_CHOICE_FIELD>
                </FIELD_TYPE>
                <MANDATORY>mandatory</MANDATORY>
                <MULTIPLICITY>single</MULTIPLICITY>
            </FIELD>
            <FIELD>
                <LABEL>5CDS</LABEL>
                <NAME>5' CDS location</NAME>
                <DESCRIPTION>Start of the coding region relative to the submitted sequence. For a full length CDS this is the position of the first base of the start codon.</DESCRIPTION>
                <FIELD_TYPE>
                <TEXT_FIELD>
                    <REGEX_VALUE>\d+</REGEX_VALUE>
                </TEXT_FIELD> 
                </FIELD_TYPE>
                <MANDATORY>mandatory</MANDATORY>
                <MULTIPLICITY>single</MULTIPLICITY>
            </FIELD> 
            </FIELD_GROUP>
        </DESCRIPTOR>
        </CHECKLIST>
        </CHECKLIST_SET>
    '''

    def _parseCheckList(self, xmlstr):
        xml = xmlstr.encode('utf-8')
        parser = ET.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        checklist_set = []
        dt = get_datetime()
        root = ET.fromstring(xml, parser=parser)
        checklist_ids = ["ERT000002", "ERT000020"]
        for checklist_elm in root.findall("./CHECKLIST"):
            primary_id = checklist_elm.find("./IDENTIFIERS/PRIMARY_ID").text.strip() 
            if primary_id not in checklist_ids:
                continue
            checklist_ids.remove(primary_id)
            checklist = {}
            checklist['primary_id'] = primary_id
            checklist['name'] = checklist_elm.find("./DESCRIPTOR/NAME").text.strip()
            checklist['description'] = checklist_elm.find("./DESCRIPTOR/DESCRIPTION").text.strip()
            checklist['fields'] = {}
            for field_elm in checklist_elm.findall("./DESCRIPTOR/FIELD_GROUP/FIELD"):
                field = {}
                key = field_elm.find("./LABEL").text.strip()
                field['name'] = field_elm.find("./NAME").text.strip()
                field['description'] = field_elm.find("./DESCRIPTION").text.strip()
                field['mandatory'] = field_elm.find("./MANDATORY").text.strip()
                field['multiplicity'] = field_elm.find("./MULTIPLICITY").text.strip()
                field['type'] = field_elm.find("./FIELD_TYPE")[0].tag
                choice = field_elm.find("./FIELD_TYPE/TEXT_CHOICE_FIELD")
                if choice is not None:
                    field['choice'] = []
                    for choice_elm in choice.findall("./TEXT_VALUE"):
                        field['choice'].append(choice_elm.find("./VALUE").text.strip())

                regex = field_elm.find("./FIELD_TYPE/TEXT_FIELD/REGEX_VALUE")
                if regex is not None:
                    field['regex'] = regex.text.strip()
                checklist['fields'][key] = field

            #add SPECIMEN_ID
            field = {}
            field['name'] = "SPECIMEN_ID"
            field['description'] = "SPECIMENT_ID"
            field['mandatory'] = "mandatory"
            field['multiplicity'] = "single"
            field['type'] = "TEXT_FIELD"
            checklist['fields']["SPECIMEN_ID"] = field

            checklist["modified_date"] =  dt
            checklist["deleted"] = data_utils.get_not_deleted_flag()
            checklist_set.append(checklist)
            if len(checklist_ids) == 0:
                break
        return checklist_set

    def updateCheckList(self):
        xmlstr = self.loadCheckList()
        checklist_set = self._parseCheckList(xmlstr)
        for checklist in checklist_set:
            TaggedSequenceChecklist().get_collection_handle().find_one_and_update({"primary_id": checklist["primary_id"]},
                                                                            {"$set": checklist},
                                                                            upsert=True)
            
    def get_mandatory_field(self, checklist):
        mandatory_fields = []
        for field in checklist["fields"]:
            if field["mandatory"] == "mandatory":
                mandatory_fields.append(field["label"])
        return mandatory_fields


    def parse_ena_taggedseq_spreadsheet(self, request):
        profile_id = request.session["profile_id"]
        notify_tagged_seq_status(data={"profile_id": profile_id},
                        msg='', action="info",
                        html_id="tagged_seq_info")
        # method called by rest
        file = request.FILES["file"]
        checklist_id = request.POST["checklist_id"]
        name = file.name
        ena = TaggedSequenceSpreedsheet(file=file, checklist_id=checklist_id)
        if name.endswith("xlsx") or name.endswith("xls"):
            fmt = 'xls'
        else:
            return HttpResponse(status=415, content="Please make sure your manifest is in xlxs format")

        if ena.loadManifest(fmt):
            l.log("Dtol manifest loaded")
            if ena.validate():
                ena.collect()
                return HttpResponse()
            return HttpResponse(status=400)
        return HttpResponse(status=400)

    def save_ena_taggedseq_records(self, request):
        tagged_seq_data = request.session.get("tagged_seq_data")
        profile_id = request.session["profile_id"]
        uid = str(request.user.id)
        checklist = TaggedSequenceChecklist().get_collection_handle().find_one({"primary_id": request.session["checklist_id"]})
        column_name_mapping = { field["name"].upper() : key  for key, field in checklist["fields"].items()  }
        fields = checklist["fields"]
        if tagged_seq_data:
            for p in range(1, len(tagged_seq_data)):
                # for each row in the manifest
                s = (map_to_dict(tagged_seq_data[0], tagged_seq_data[p]))

                record = {}
                record["profile_id"] = profile_id
                record["updated_by"] = uid
                record["modified_date"] = get_datetime()
                record["deleted"] = get_not_deleted_flag()
                record["checklist_id"] = request.session["checklist_id"]

                for key, value in s.items():
                    upper_key = key.upper()
                    if upper_key in column_name_mapping:
                        record[column_name_mapping[upper_key]] = value

                insert_record = {}
                insert_record["created_by"] = uid
                insert_record["created_date"] = get_datetime()
                insert_record["status"] = "pending"

                TaggedSequence().get_collection_handle().find_one_and_update({"profile_id": profile_id, column_name_mapping["ORGANISM"]:s["Organism"]},
                                                                            {"$set": record, "$setOnInsert": insert_record},
                                                                            upsert=True)
        
        table_data = htags.generate_taggedseq_record(profile_id=profile_id, checklist_id=request.session["checklist_id"])
        result = {"table_data": table_data, "component": "taggedseq"}
        return JsonResponse(status=200, data=result)

    def submit_tagged_seq(self, profile_id, checklist_id=None, target_ids=[], target_id=str()):
        if profile_id:
            submissions = Submission().get_records_by_field("profile_id", profile_id)
            if submissions and len(submissions) > 0:
                sub_id = str(submissions[0]["_id"])
                if not target_ids:
                    target_ids = []
                if target_id:
                    target_ids.append(target_id)

                tagged_seq_obj_ids = [ ObjectId(x) for x in target_ids]
                count = TaggedSequence().get_collection_handle().find({"_id": {"$in": tagged_seq_obj_ids},"profile_id": profile_id,  "accession":{"$exists": False}} ).count()
                if count != len(target_ids):
                    return dict(status='error', message="One of the tagged sequences have been accessed. Cannot submit again!")        

                submission_status = submissions[0].get("tagged_seq_status","complete")
                if submission_status in [ "pending", "complete" ]:
                    TaggedSequence().update_tagged_seq_processing(profile_id=profile_id, tagged_seq_ids=target_ids)
                    Submission().make_tagged_seq_submission_pending(sub_id=str(submissions[0]["_id"]), target_ids=target_ids)
                    return dict(status='success', message="Tagged sequence submission has been scheduled!")        
                else:
                    return dict(status='error', message="Tagged sequence submission is processing. Please wait for the current submission to complete before submitting another.")        

        return dict(status='error', message="System error. Tagged sequence submission has NOT been scheduled! Please contact system administrator.")        

    def _get_submission_xml(self):
        """
        function creates and return submission xml path
        :return:
        """

        # create submission xml
        l.log("Creating submission xml...")

        parser = ET.XMLParser(remove_blank_text=True)
        root = ET.parse(SRA_SUBMISSION_TEMPLATE, parser).getroot()

        # set submission attributes
        root.set("broker_name", self.sra_settings["sra_broker"])
        root.set("center_name", self.sra_settings["sra_center"])
        root.set("submission_date", datetime.utcnow().replace(tzinfo=data_utils.simple_utc()).isoformat())

        # set SRA contacts
        contacts = root.find('CONTACTS')

        # set copo sra contacts
        copo_contact = ET.SubElement(contacts, 'CONTACT')
        copo_contact.set("name", self.sra_settings["sra_broker_contact_name"])
        copo_contact.set("inform_on_error", self.sra_settings["sra_broker_inform_on_error"])
        copo_contact.set("inform_on_status", self.sra_settings["sra_broker_inform_on_status"])

        # set user contacts
        sra_map = {"inform_on_error": "SRA Inform On Error", "inform_on_status": "SRA Inform On Status"}
        user_contacts = self.submission_helper.get_sra_contacts()
        for k, v in user_contacts.items():
            user_sra_roles = [x for x in sra_map.keys() if sra_map[x].lower() in v]
            if user_sra_roles:
                user_contact = ET.SubElement(contacts, 'CONTACT')
                user_contact.set("name", ' '.join(k[1:]))
                for role in user_sra_roles:
                    user_contact.set(role, k[0])

        # todo: add study publications

        # set release action
        release_date = self.submission_helper.get_study_release()

        # only set release info if in the past, instant release should be handled upon submission completion
        if release_date and release_date["in_the_past"] is False:
            actions = root.find('ACTIONS')
            action = ET.SubElement(actions, 'ACTION')

            action_type = ET.SubElement(action, 'HOLD')
            action_type.set("HoldUntilDate", release_date["release_date"])

        return self._write_xml_file(xml_object=root, file_name="submission.xml")



    def _get_edit_submission_xml(self,submission_xml_path=str()):
        """
        function creates and return submission xml path
        :return:
        """
        # create submission xml
        l.log("Creating submission xml for edit....")

        parser = ET.XMLParser(remove_blank_text=True)
        root = ET.parse(submission_xml_path, parser).getroot()
        actions = root.find('ACTIONS')
        action = actions.find('ACTION')
        add = action.find("ADD")
        if add != None:
            action.remove(add)
        modify = ET.SubElement(action, 'MODIFY')
        
        return self._write_xml_file(xml_object=root, file_name="submission_edit.xml")

    def _write_xml_file(self, location=str(), xml_object=None, file_name=str()):
            """
            function writes xml to the specified location or to a default one
            :param location:
            :param xml_object:
            :param file_name:
            :return:
            """

            result = dict(status=True, value='')

            output_location = self.the_submission
            if location:
                output_location = location

            xml_file_path = os.path.join(output_location, file_name)
            tree = ET.ElementTree(xml_object)

            try:
                tree.write(xml_file_path, encoding="utf8", xml_declaration=True, pretty_print=True)
            except Exception as e:
                message = 'Error writing xml file ' + file_name + ": " + str(e)
                l.error(message)
                raise

            message = file_name + ' successfully written to  ' + xml_file_path
            l.log(message)

            result['value'] = xml_file_path

            return result




    def processing_pending_tagged_seq_submission(self):

        # submit images
        submissions = Submission().get_tagged_seq_pending_submission()
        #sub_ids = []
        if not submissions:
            return

        for sub in submissions:
            notify_tagged_seq_status(data={"profile_id": sub["profile_id"]},
                    msg="Sequence annotation submitting...",
                    action="info",
                    html_id="tagged_seq_info")
            
            self.submission_helper = SubmissionHelper(submission_id=str(sub["_id"]))
            self.the_submission = os.path.join(self.submission_path, sub["profile_id"]) 
            try:
                if not os.path.exists(self.the_submission ):
                    os.makedirs(self.the_submission )

                context = self._get_submission_xml()
                submission_xml_path = context['value']

                context = self._get_edit_submission_xml(submission_xml_path) 
                modify_submission_xml_path = context['value']

 
                # register project
                if not self.submission_helper.get_study_accessions():
                    xml = submission_xml_path
                #do the modifiction
                else:
                    xml = modify_submission_xml_path
                tagged_seqs = TaggedSequence().get_records(sub["tagged_seqs"])
                context = self._register_project(sub["profile_id"], str(sub["_id"]), submission_xml_path=xml)
                if context['status'] is False:
                    self._reject_submission(sub["_id"], tagged_seqs, context.get("message", str()))
                    notify_tagged_seq_status(data={"profile_id": sub["profile_id"]}, msg=context.get("message", str()), action="error", html_id="tagged_seq_info")
                    continue

                project_accession = context['value']
                notify_tagged_seq_status(data={"profile_id": sub["profile_id"]}, msg="Project registered with accession: " + project_accession["accession"], action="info", html_id="tagged_seq_info")

                tagged_seqs_map = dict()
                accessed_tagged_seqs = []
                if tagged_seqs:
                    for tagged_seq in tagged_seqs:
                        if tagged_seq.get("accession", ""):
                            accessed_tagged_seqs.append(tagged_seq)
                            continue
                        checklist_id = tagged_seq["checklist_id"]
                        if checklist_id not in tagged_seqs_map:
                            tagged_seqs_map[checklist_id] = []
                        tagged_seqs_map[checklist_id].append(tagged_seq)
                            
                self._remove_accessed_tagged_seqs(sub["_id"], accessed_tagged_seqs)

                for checklist_id, tagged_seqs_per_checklist in tagged_seqs_map.items():
                    # validate tagged seqs                    
                    notify_tagged_seq_status(data={"profile_id": sub["profile_id"]}, msg="Validating barcoding sequence......" , action="info", html_id="tagged_seq_info")
                    context = self._validate_tagged_seq(sub["profile_id"], str(sub["_id"]), project_accession["accession"], checklist_id, tagged_seqs_per_checklist)
                    table_data = htags.generate_taggedseq_record(profile_id=sub["profile_id"], checklist_id=checklist_id)
                    action="info"
                    message=context.get("success", str())
                    if context.get('error',str()) :
                        self._reject_submission(sub["_id"], tagged_seqs_per_checklist, context.get("error", str()))
                        action="error"
                        message=context.get("error", str())
                    notify_tagged_seq_status(data={"profile_id": sub["profile_id"], "table_data": table_data, "component": "taggedseq"}, msg=message, action=action, html_id="tagged_seq_info")

            except Exception as e:
                l.exception(e)
                message = "Submission processing failed due to exception! Retry again : " + str(e)
                notify_tagged_seq_status(data={"profile_id": sub["profile_id"]}, msg=message , action="error", html_id="tagged_seq_info")
                # reset sample status to pending & remove bundle / bundle samples
                Submission().get_collection_handle().update(
                    {"_id": sub["_id"]},
                    {'$set': {'tagged_seq_status': 'pending'}})

    def _remove_accessed_tagged_seqs(self, submission_id, accessed_tagged_seqs):
        dt = get_datetime()
        submission = Submission().get_collection_handle().find_one({"_id": submission_id})
        accessed_tagged_seqs_ids = [x["_id"] for x in accessed_tagged_seqs]
        TaggedSequence().get_collection_handle().update_many({"_id" : {"$in":  accessed_tagged_seqs_ids}}, {'$set': {'status': 'accepted', "modified_date": dt , "error": str()}})
        submission["tagged_seqs"] = [ x for x in submission["tagged_seqs"] if ObjectId(x) not in accessed_tagged_seqs_ids]
        if len(submission["tagged_seqs"]) == 0:
            submission["tagged_seq_status"] = "complete"
        Submission().get_collection_handle().update_one({"_id": submission_id}, {"$set": submission})

    def _add_tagged_seq_accession(self, submission_id, accession, alias, tagged_seqs):
        dt = get_datetime()
        submission = Submission().get_collection_handle().find_one({"_id": submission_id})
        tagged_seq_ids = [x["_id"] for x in tagged_seqs]
        TaggedSequence().get_collection_handle().update_many({"_id" : {"$in":  tagged_seq_ids}}, {'$set': {'status': 'accepted', 'accession': accession, "modified_date": dt , "error": str(), "submission_alias": alias}})
        submission["tagged_seqs"] = [ x for x in submission["tagged_seqs"] if ObjectId(x) not in tagged_seq_ids]
        if len(submission["tagged_seqs"]) == 0:
            submission["tagged_seq_status"] = "complete"
        Submission().get_collection_handle().update_one({"_id": submission_id}, {"$set": {"tagged_seq_status": submission["tagged_seq_status"], "tagged_seqs": submission["tagged_seqs"] }, "$addToSet": {"accessions.tagged_seq_accessions": {"accession": accession, "alias": alias}}})


    def _reject_submission(self, submission_id, tagged_seqs, message=str()):
        dt = get_datetime()
        submission = Submission().get_collection_handle().find_one({"_id": submission_id})
        tagged_seq_object_ids = [x["_id"] for x in tagged_seqs]
        TaggedSequence().get_collection_handle().update_many({"_id" : {"$in":  tagged_seq_object_ids}}, {'$set': {'status': 'pending', 'error': message}})
        submission["tagged_seqs"] = [ x for x in submission["tagged_seqs"] if ObjectId(x) not in tagged_seq_object_ids]
        if len(submission["tagged_seqs"]) == 0:
            submission["tagged_seq_status"] = "complete"
        Submission().get_collection_handle().update({"_id": submission_id}, {'$set': {"tagged_seqs" : submission["tagged_seqs"] , 'tagged_seq_status': submission["tagged_seq_status"], "modified_date": dt}})

    def _register_project(self, profile_id, submission_id, submission_xml_path=str()):
        """
        function creates and submits project (study) xml
        :return:
        """

        # create project xml
        log_message = "Registering project..."
        l.log(log_message)
        notify_tagged_seq_status(data={"profile_id": profile_id}, msg=log_message, action="info", html_id="tagged_seq_info")

        parser = ET.XMLParser(remove_blank_text=True)
        root = ET.parse(SRA_PROJECT_TEMPLATE, parser).getroot()

        # set SRA contacts
        project = root.find('PROJECT')

        # set project descriptors
        project.set("alias", submission_id)
        project.set("center_name", self.sra_settings["sra_center"])

        study_attributes = self.submission_helper.get_study_descriptors()

        if study_attributes.get("name", str()):
            ET.SubElement(project, 'NAME').text = study_attributes.get("name", str())

        if study_attributes.get("title", str()):
            ET.SubElement(project, 'TITLE').text = study_attributes.get("title", str())

        if study_attributes.get("description", str()):
            ET.SubElement(project, 'DESCRIPTION').text = study_attributes.get("description", str())

        # set project type - sequencing project
        submission_project = ET.SubElement(project, 'SUBMISSION_PROJECT')
        ET.SubElement(submission_project, 'SEQUENCING_PROJECT')

        # write project xml
        result = self._write_xml_file(xml_object=root, file_name="project.xml")
        if result['status'] is False:
            return result

        project_xml_path = result['value']


        # register project to the ENA service
        curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                    + '" -F "SUBMISSION=@' \
                    + submission_xml_path \
                    + '" -F "PROJECT=@' \
                    + project_xml_path \
                    + '" "' + self.ena_service \
                    + '"'

        l.log("Submitting project xml to ENA via CURL. CURL command is: " + curl_cmd.replace(self.pass_word, "xxxxxx"))

        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
        except Exception as e:
            if settings.DEBUG:
                l.exception(e)
            message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + \
                        curl_cmd.replace(
                            self.pass_word, "xxxxxx")
            raise e


        root = ET.fromstring(receipt)

        if root.get('success') == 'false':
            result['status'] = False
            result['message'] = "Couldn't register STUDY due to the following errors: "
            errors = root.findall('.//ERROR')
            if errors:
                error_text = str()
                for e in errors:
                    error_text = error_text + " \n" + e.text

                result['message'] = result['message'] + error_text

            # log error
            l.error(result['message'])

            return result

        # save project accession
        self._write_xml_file(xml_object=root, file_name="project_receipt.xml")
        l.log("Saving project accessions to the database")
        project_accessions = list()
        accession = root.find('PROJECT')
        if accession is None:
            return dict(status=False, value='NO_PROJECT_ACCESSION_FOUND')
        project_accessions.append(
            dict(
                accession=accession.get('accession', default=str()),
                alias=accession.get('alias', default=str()),
                status=accession.get('status', default=str()),
                release_date=accession.get('holdUntilDate', default=str())
            )
        )

        collection_handle = Submission().get_collection_handle()
        doc = collection_handle.find_one({"_id": ObjectId(submission_id)}, {"accessions": 1})

        if doc:
            submission_record = doc
            accessions = submission_record.get("accessions", dict())
            accessions['project'] = project_accessions
            submission_record['accessions'] = accessions

            collection_handle.update(
                {"_id": ObjectId(str(submission_record.pop('_id')))},
                {'$set': submission_record})

            # update submission status
            status_message = "Project successfully registered, and accessions saved."
            l.log(status_message)
        return dict(status=True, value=project_accessions[0])


    def _validate_tagged_seq(self, profile_id, submission_id, accession=str(), checklist_id=None, tagged_seqs=list()):
        dt = get_datetime()
        request = ThreadLocal.get_current_request()
        self.the_submission = os.path.join(self.submission_path, profile_id) 
        the_submission_url_path = f"{settings.MEDIA_URL}ena_tagged_seq_files/{profile_id}"
        tsv_file = os.path.join(self.the_submission, f"{submission_id}_{checklist_id}.tsv" )
        manifest_path = os.path.join(self.the_submission, "manifest.txt")

        #tagged_seq_obj_ids = [ObjectId(x) for x in tagged_seq_ids]

        #tagged_seqs = TaggedSequence().execute_query({"_id": {"$in": tagged_seq_obj_ids}, "profile_id": profile_id, "checklist_id": checklist_id})

        #if len(tagged_seqs) != len(tagged_seq_ids):
        #    return dict(status=False, value="Tagged sequence checklist id mismatch")

        checklists = TaggedSequenceChecklist().execute_query({"primary_id": checklist_id})
        
        if not checklists:
            return dict(status=False, value="Tagged sequence checklist not found")
        checklist = checklists[0]

        fields = checklist["fields"]
        new_column_name = { key: value["name"] for key, value in fields.items() }

        df = pd.DataFrame(tagged_seqs)      

        df.drop(['SPECIMEN_ID'], axis=1, inplace=True)
        df.drop([x for x in df.columns if x not in fields.keys()], axis=1, inplace=True)
        df.rename(columns=new_column_name, inplace=True) 

        with open(tsv_file, "w") as destination:
            destination.write("Checklist"+"\t" + checklist_id + "\t" + checklist["name"] + "\n")
            df.to_csv(destination, sep="\t", index=False, mode="a")

        with open(tsv_file, 'rb') as f_in:
            with gzip.open(tsv_file + ".gz", "w") as f_out:
                shutil.copyfileobj(f_in, f_out)
        

        manifest_name = submission_id + "_" + uuid.uuid4().hex + "_" + checklist_id
        manifest_content = "STUDY" + "\t" + accession + "\n"
        manifest_content += "NAME" + "\t" + manifest_name +  "\n"   
        manifest_content += "TAB" + "\t" +  tsv_file + ".gz" +  "\n"

    
        with open(manifest_path, "w") as destination:
            destination.write(manifest_content)

        test = ""
        if "dev" in self.ena_service:
            test = " -test "
        #cli_path = "tools/reposit/ena_cli/webin-cli.jar"
        webin_cmd = "java -jar webin-cli.jar -username " + self.user_token + " -password '" + self.pass_word + "'" + test + " -context sequence -manifest " + str(
            manifest_path) + " -validate -ascp"
        l.debug(msg=webin_cmd)
        #print(webin_cmd)
        try:
            l.log(msg='validating assembly submission')
            notify_tagged_seq_status(data={"profile_id": profile_id},
                            msg="Validating Assembly Submission",
                            action="info",
                            html_id="assembly_info")
            output = subprocess.check_output(webin_cmd, shell=True)
            l.debug(output)
        except subprocess.CalledProcessError as cpe:
            return_code = cpe.returncode
            output = cpe.stdout
        output = output.decode("ascii")
        l.debug(msg=output)
        #print(output)
        #todo decide if keeping or deleting these files
        #report is being stored in webin-cli.report and manifest.txt.report so we can get errors there
        if not "ERROR" in output:
            notify_tagged_seq_status(data={"profile_id": profile_id}, msg="Submitting barcoding sequence......" , action="info", html_id="tagged_seq_info")
            output = self._submit_tagged_seq( profile_id)
            if "ERROR" in output:
                #handle possibility submission is not successfull
                #this may happen for instance if the same assembly has already been submitted, which would not get caught
                #by the validation step
                return {"error": output}
    
            accession = re.search( "ERZ\d*\w" , output).group(0).strip()
            self._add_tagged_seq_accession(ObjectId(submission_id), accession, "webin-sequence-" + manifest_name, tagged_seqs)        
            table_data = htags.generate_taggedseq_record(profile_id, checklist_id)
            return {"success": f"Tagged Sequence has been submitted with accession {accession}", "table_data": table_data, "component": "taggedseq" }
        else:
            if return_code == 2:
                with open(self.the_submission / "manifest.txt.report") as report_file:
                    return {"error": (report_file.read())}
            elif return_code == 3:

                directories = sorted(glob.glob(f"{self.the_submission}/sequence/*"), key=os.path.getmtime)
                with open(f"{directories[-1]}/validate/webin-cli.report") as report_file:
                    error = report_file.read()
                
                for file in os.scandir(f"{directories[-1]}/validate"):
                    if file.name != "webin-cli.report":
                        with open(file) as report_file:
                            error = error + f'<br/><a href="{the_submission_url_path}/sequence/{os.path.basename(directories[-1])}/validate/{file.name}"/>{file.name}</a>'                    
                return {"error": error}
            else:
                return {"error": output}    
    

    def _submit_tagged_seq(self, profile_id):
        manifest_path = os.path.join(self.the_submission ,"manifest.txt")

        test = ""
        if "dev" in self.ena_service:
            test = " -test "
        webin_cmd = "java -jar webin-cli.jar -username " + self.user_token + " -password '" + self.pass_word + "'" + test + " -context sequence -manifest " + manifest_path + " -submit"
        l.debug(msg=webin_cmd)
        # print(webin_cmd)
        # try/except as it turns out this can fail even if validate is successfull
        try:
            l.log(msg="submitting assembly")
            notify_tagged_seq_status(data={"profile_id": profile_id},
                            msg="Submitting Tagged Sequence",
                            action="info",
                            html_id="tagged_seq_info")
            output = subprocess.check_output(webin_cmd, shell=True)
            l.debug(output)
        except subprocess.CalledProcessError as cpe:
            output = cpe.stdout
        output = output.decode("ascii")
        l.debug(msg=output)

        #todo delete files after successfull submission
        #todo decide if keeping manifest.txt and store accession in assembly objec too
        return output


class TaggedSequenceSpreedsheet:
   def __init__(self, file, checklist_id):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        self.checklist_id = checklist_id
        self.data = None
        self.new_data = None
        self.required_validators = list()

        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated
        if file:
            self.file = file
        else:
            self.sample_data = self.req.session.get("tagged_seq_data", "")
            self.isupdate = self.req.session.get("isupdate", False)


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
            notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                            html_id="tagged_seq_info")

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
                #self.data.columns = self.data.columns.str.replace(" ", "")
                   
                new_column_name = { name : name.upper() for name in self.data.columns.values.tolist() }
                self.new_data = self.data.rename(columns=new_column_name)    

                checklist = TaggedSequenceChecklist().get_collection_handle().find_one({"primary_id": self.checklist_id})
                if checklist:
                   fields = checklist["fields"]
                   new_column_name = { value["name"].upper() : key for key, value in fields.items() }
                   self.new_data.rename(columns=new_column_name, inplace=True)    

            except Exception as e:
                # if error notify via web socket
                notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
                                action="info",
                                html_id="tagged_seq_info")
                return False
            return True

   def validate(self):
        flag = True
        errors = []
        warnings = []
        self.isupdate = False

        try:

            checklist = TaggedSequenceChecklist().get_collection_handle().find_one({"primary_id": self.checklist_id})

            # validate for required fields
            for v in self.required_validators:
                errors, warnings, flag, self.isupdate = v(profile_id=self.profile_id, checklist=checklist,
                                                          data=self.new_data, fields=None,
                                                          errors=errors, warnings=warnings, flag=flag,
                                                          isupdate=self.isupdate).validate()

            # send warnings
            if warnings:
                l.log(",".join(warnings))
                notify_tagged_seq_status(data={"profile_id": self.profile_id},
                                msg="<br>".join(warnings),
                                action="warning",
                                html_id="warning_info2")
            # if flag is false, compile list of errors
            if not flag:
                errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                errors = "".join(errors)
                l.log(errors)
                notify_tagged_seq_status(data={"profile_id": self.profile_id},
                                msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                                action="error",
                                html_id="tagged_seq_info")
                return False



        except Exception as e:
            l.exception(e)
            error_message = str(e).replace("<", "").replace(">", "")
            notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                            action="info",
                            html_id="tagged_seq_info")

            return False

        # if we get here we have a valid spreadsheet
        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                        html_id="tagged_seq_info")
        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls")
        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id="tagged_seq_info")

        return True

   def collect(self):
        # create table data to show to the frontend from parsed manifest
        tagged_seq_data = []
        headers = list()
        for col in list(self.data.columns):
            headers.append(col)
        tagged_seq_data.append(headers)
        for index, row in self.data.iterrows():
            r = list(row)
            for idx, x in enumerate(r):
                if x is math.nan:
                    r[idx] = ""
            tagged_seq_data.append(r)
        # store sample data in the session to be used to create mongo objects
        self.req.session["tagged_seq_data"] = tagged_seq_data
        self.req.session["checklist_id"] = self.checklist_id

        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg=tagged_seq_data, action="make_table",
                        html_id="tagged_seq_parse_table")
             


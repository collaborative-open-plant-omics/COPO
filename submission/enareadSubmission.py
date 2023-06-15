__author__ = 'etuka'
__date__ = '27 March 2019'

import os
import glob
import time
import shutil
import ftplib
import ntpath
import pexpect
import subprocess
import pandas as pd
from lxml import etree
from bson import ObjectId
from datetime import datetime
from tools import resolve_env
from dal import cursor_to_list
import dal.mongo_util as mutil
from contextlib import closing
from django.conf import settings
from submission.helpers import generic_helper as ghlper
from dal.copo_da import Submission, Sample
from web.apps.web_copo.lookup.lookup import SRA_SETTINGS
from submission.helpers.ena_helper import SubmissionHelper
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from web.apps.web_copo.lookup.copo_lookup_service import COPOLookup
from web.apps.web_copo.lookup.lookup import SRA_SUBMISSION_TEMPLATE, SRA_EXPERIMENT_TEMPLATE, SRA_RUN_TEMPLATE, \
    SRA_PROJECT_TEMPLATE, SRA_SAMPLE_TEMPLATE, \
    SRA_SUBMISSION_MODIFY_TEMPLATE, ENA_CLI
import web.apps.web_copo.utils.FileTransferUtils as tx
from submission.helpers.generic_helper import notify_read_status
from web.apps.web_copo.schema_versions.lookup import dtol_lookups
import web.apps.web_copo.templatetags.html_tags as htags


REPOSITORIES = settings.REPOSITORIES
BASE_DIR = settings.BASE_DIR
ENA_TYPES = settings.ENA_TYPES
"""
class handles read data submissions to the ENA - see: https://ena-docs.readthedocs.io/en/latest/cli_06.html
"""

REFRESH_THRESHOLD = 5 * 3600  # in hours, time to reset a potentially staled task to pending
TRANSFER_REFRESH_THRESHOLD = 10 * 3600


class EnaReads:
    def __init__(self, submission_id=str()):
        self.submission_id = submission_id
        self.project_alias = self.submission_id

        self.ena_service = resolve_env.get_env('ENA_SERVICE')
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.webin_user = resolve_env.get_env('WEBIN_USER')
        self.webin_domain = resolve_env.get_env('WEBIN_USER').split("@")[1]

        self.submission_helper = None
        self.sra_settings = None
        self.datafiles_dir = None
        self.submission_context = None
        self.tmp_folder = None
        self.remote_location = None
        self.project_id = None

    def process_queue(self):
        """
        function picks a submission from the queue to process
        :return:
        """
        collection_handle = ghlper.get_submission_queue_handle()
        dt = d_utils.get_datetime()
        # check and update status for long running tasks
        records = list(
            collection_handle.find({'repository': {'$in': ENA_TYPES}, 'processing_status': 'running'}))

        for rec in records:
            recorded_time = rec.get("date_modified", None)

            if not recorded_time:
                rec['date_modified'] = dt
                collection_handle.update(
                    {"_id": ObjectId(str(rec.pop('_id')))},
                    {'$set': rec})

                continue

            current_time = dt
            time_difference = current_time - recorded_time
            if time_difference.seconds >= (REFRESH_THRESHOLD):  # time submission is perceived to have been running

                # refresh task to be rescheduled
                rec['date_modified'] = dt
                rec['processing_status'] = 'pending'
                collection_handle.update(
                    {"_id": ObjectId(str(rec.pop('_id')))},
                    {'$set': rec})

        # obtain pending submission for processing
        records = list(
            collection_handle.find({'repository': {'$in': ENA_TYPES}, 'processing_status': 'pending'}).sort(
                [['date_modified', 1]]))

        if not records:
            return True

        # pick top of the list, update status and timestamp
        queued_record = records[0]
        queued_record['processing_status'] = 'running'
        queued_record['date_modified'] = dt

        queued_record_id = queued_record.pop('_id', '')

        self.submission_id = queued_record.get("submission_id", str())
        message = "Now processing submission..."

        ghlper.logging_info(message, self.submission_id)
        ghlper.update_submission_status(status='info', message=message, submission_id=self.submission_id)

        collection_handle.update(
            {"_id": ObjectId(str(queued_record_id))},
            {'$set': queued_record})

        result = self._submit()
        if not result.get("status", False):
            message = "Submission processing failed!"
            ghlper.logging_info(message, self.submission_id)
            # reset sample status to pending & remove bundle / bundle samples
            Submission(profile_id=self.profile_id).reset_read_submisison_bundle(self.submission_id, is_success=False)


        # remove from queue - this supposes that submissions that returned error will have
        # to be re-scheduled for processing, upon addressing the error, by the user
        collection_handle.remove({"_id": queued_record_id})
        table_data = htags.generate_read_record(profile_id=self.profile_id)
        result = {"table_data": table_data, "component": "read"}
        notify_read_status(data={"profile_id": self.profile_id, "table_data":table_data, "component": "read"}, action="refresh_table", html_id="read_table"  )
        return True

    def _submit(self):
        """
        function acts as a controller for the submission process
        :return:
        """

        self.project_alias = self.submission_id
        self.remote_location = os.path.join(self.project_alias, 'reads')  # ENA-Dropbox upload path

        collection_handle = ghlper.get_submission_handle()

        if not self.submission_id:
            return dict(status=False, message='Submission identifier not found!')

        # check status of submission record
        submission_record = collection_handle.find_one({"_id": ObjectId(self.submission_id)},
                                                       {"profile_id": 1, "complete": 1, "manifest_submission": 1})

        if not submission_record:
            return dict(status=False, message='Submission record not found!')

        if str(submission_record.get("complete", False)).lower() == 'true':
            message = 'Submission is marked as completed.'
            ghlper.logging_info(message, self.submission_id)

            return dict(status=True, message=message)
        
        self.profile_id = submission_record.get("profile_id", str())

        notify_read_status(data={"profile_id": self.profile_id},
                        msg='Initiating Read submission......', action="info", html_id="sample_info")

        # instantiate helper object - performs most auxiliary tasks associated with the submission
        self.submission_helper = SubmissionHelper(submission_id=self.submission_id)

        ghlper.logging_info('Initiating submission...', self.submission_id)

        # clear any existing submission transcript - error or info alike
        ghlper.update_submission_status(submission_id=self.submission_id)

        # submission location
        self.submission_location = self.create_submission_location()
        self.datafiles_dir = os.path.join(self.submission_location, "files")
        self.submission_context = os.path.join(self.submission_location, "reads")
        self.tmp_folder = os.path.join(self.submission_location, "tmp")

        # retrieve sra settings
        self.sra_settings = d_utils.json_to_pytype(SRA_SETTINGS).get("properties", dict())
        print("create self")
        # get submission xml
        context = self._get_submission_xml()

        if context['status'] is False:
            notify_read_status(data={"profile_id": self.profile_id}, msg=context.get("message", str()), action="error", html_id="sample_info")
            ghlper.update_submission_status(status='error', message=context.get("message", str()),
                                            submission_id=self.submission_id)
            return context

        submission_xml_path = context['value']

        context = self._get_edit_submission_xml(submission_xml_path) 
        modify_submission_xml_path = context['value']

        # register project
        if not self.submission_helper.get_study_accessions():
            xml = submission_xml_path
        #do the modifiction
        else:
            xml = modify_submission_xml_path
        context = self._register_project(submission_xml_path=xml)

        if context['status'] is False:
            notify_read_status(data={"profile_id": self.profile_id}, msg=context.get("message", str()), action="error", html_id="sample_info")
            ghlper.update_submission_status(status='error', message=context.get("message", str()),
                                            submission_id=self.submission_id)
            return context

        # register samples
        context = self._register_samples(submission_xml_path=submission_xml_path, modify_submission_xml_path=modify_submission_xml_path)
        if context['status'] is False:
            notify_read_status(data={"profile_id": self.profile_id}, msg=context.get("message", str()), action="error", html_id="sample_info")
            ghlper.update_submission_status(status='error', message=context.get("message", str()),
                                            submission_id=self.submission_id)
            return context

        # submit datafiles via the CLI pathway
        # todo: uncomment the following line to use the CLI submission pathway,
        #  and comment out _submit_datafiles_rest below
        # context = self._submit_datafiles_cli(submission_xml_path=submission_xml_path)

        # submit datafiles via the RESTful pathway

        context = self._submit_datafiles_rest(submission_xml_path=submission_xml_path, is_new=False)
        if context['status'] is False:
            notify_read_status(data={"profile_id": self.profile_id}, msg=context.get("message", str()), action="error", html_id="sample_info") 
            ghlper.update_submission_status(status='error', message=context.get("message", str()),
                                            submission_id=self.submission_id)
            return context

        context = self._submit_datafiles_rest(submission_xml_path=submission_xml_path, is_new=True)
        if context['status'] is False:
            notify_read_status(data={"profile_id": self.profile_id}, msg=context.get("message", str()), action="error", html_id="sample_info")
            ghlper.update_submission_status(status='error', message=context.get("message", str()),
                                            submission_id=self.submission_id)
            return context
        

        #delete bundle as submission complete
        ghlper.delete_submisison_bundle(submission_id=self.submission_id)

        # todo branch here for manifest submissions, as we will be handling datafiles differently

        # process study release
        self.process_study_release()

        # depending on the release status of the study, process emabargo message
        self.set_embargo_message()

        # report on file upload status
        context = self.get_upload_status()
        if context['status'] is True and context['message']:
            notify_read_status(data={"profile_id": self.profile_id}, msg=context.get("message", str()), action="info", html_id="sample_info")
            ghlper.notify_transfer_status(profile_id=submission_record['profile_id'], submission_id=self.submission_id,
                                          status_message=context['message'])

        return context

    def create_submission_location(self):
        """
        function creates the location for storing submission files
        :return:
        """

        conv_dir = os.path.join(os.path.join(os.path.dirname(__file__), "data"), self.submission_id)

        try:
            if not os.path.exists(conv_dir):
                os.makedirs(conv_dir)
        except Exception as e:
            message = 'Error creating submission location ' + conv_dir + ": " + str(e)
            notify_read_status(data={"profile_id": self.profile_id}, msg=message, action="error", html_id="sample_info")
            ghlper.logging_error(message, self.submission_id)
            raise

        ghlper.logging_info('Created submission location: ' + conv_dir, self.submission_id)

        return conv_dir

    def _get_submission_xml(self):
        """
        function creates and return submission xml path
        :return:
        """

        # create submission xml
        ghlper.logging_info("Creating submission xml...", self.submission_id)

        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(SRA_SUBMISSION_TEMPLATE, parser).getroot()

        # set submission attributes
        root.set("broker_name", self.sra_settings["sra_broker"])
        root.set("center_name", self.sra_settings["sra_center"])
        root.set("submission_date", datetime.utcnow().replace(tzinfo=d_utils.simple_utc()).isoformat())

        # set SRA contacts
        contacts = root.find('CONTACTS')

        # set copo sra contacts
        copo_contact = etree.SubElement(contacts, 'CONTACT')
        copo_contact.set("name", self.sra_settings["sra_broker_contact_name"])
        copo_contact.set("inform_on_error", self.sra_settings["sra_broker_inform_on_error"])
        copo_contact.set("inform_on_status", self.sra_settings["sra_broker_inform_on_status"])

        # set user contacts
        sra_map = {"inform_on_error": "SRA Inform On Error", "inform_on_status": "SRA Inform On Status"}
        user_contacts = self.submission_helper.get_sra_contacts()
        for k, v in user_contacts.items():
            user_sra_roles = [x for x in sra_map.keys() if sra_map[x].lower() in v]
            if user_sra_roles:
                user_contact = etree.SubElement(contacts, 'CONTACT')
                user_contact.set("name", ' '.join(k[1:]))
                for role in user_sra_roles:
                    user_contact.set(role, k[0])

        # todo: add study publications

        # set release action
        release_date = self.submission_helper.get_study_release()

        # only set release info if in the past, instant release should be handled upon submission completion
        if release_date and release_date["in_the_past"] is False:
            actions = root.find('ACTIONS')
            action = etree.SubElement(actions, 'ACTION')

            action_type = etree.SubElement(action, 'HOLD')
            action_type.set("HoldUntilDate", release_date["release_date"])

        return self.write_xml_file(xml_object=root, file_name="submission.xml")


    def _get_edit_submission_xml(self,submission_xml_path=str()):
        """
        function creates and return submission xml path
        :return:
        """
        # create submission xml
        ghlper.logging_info("Creating submission xml for edit....", self.submission_id)

        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(submission_xml_path, parser).getroot()
        actions = root.find('ACTIONS')
        action = actions.find('ACTION')
        add = action.find("ADD")
        if add != None:
            action.remove(add)
        modify = etree.SubElement(action, 'MODIFY')
        
        return self.write_xml_file(xml_object=root, file_name="submission_edit.xml")

    def _register_project(self, submission_xml_path=str()):
        """
        function creates and submits project (study) xml
        :return:
        """

        # create project xml
        log_message = "Registering project..."
        ghlper.logging_info(log_message, self.submission_id)
        ghlper.update_submission_status(status='info', message=log_message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id}, msg=log_message, action="info", html_id="sample_info")

        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(SRA_PROJECT_TEMPLATE, parser).getroot()

        # set SRA contacts
        project = root.find('PROJECT')

        # set project descriptors
        project.set("alias", self.project_alias)
        project.set("center_name", self.sra_settings["sra_center"])

        study_attributes = self.submission_helper.get_study_descriptors()

        if study_attributes.get("name", str()):
            etree.SubElement(project, 'NAME').text = study_attributes.get("name", str())

        if study_attributes.get("title", str()):
            etree.SubElement(project, 'TITLE').text = study_attributes.get("title", str())

        if study_attributes.get("description", str()):
            etree.SubElement(project, 'DESCRIPTION').text = study_attributes.get("description", str())

        # set project type - sequencing project
        submission_project = etree.SubElement(project, 'SUBMISSION_PROJECT')
        etree.SubElement(submission_project, 'SEQUENCING_PROJECT')

        # write project xml
        result = self.write_xml_file(xml_object=root, file_name="project.xml")
        if result['status'] is False:
            return result

        project_xml_path = result['value']

        result = dict(status=True, value='')

        # register project to the ENA service
        curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                   + '" -F "SUBMISSION=@' \
                   + submission_xml_path \
                   + '" -F "PROJECT=@' \
                   + project_xml_path \
                   + '" "' + self.ena_service \
                   + '"'

        ghlper.logging_info(
            "Submitting project xml to ENA via CURL. CURL command is: " + curl_cmd.replace(self.pass_word, "xxxxxx"),
            self.submission_id)

        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
        except Exception as e:
            message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + \
                      curl_cmd.replace(
                          self.pass_word, "xxxxxx")
            
            ghlper.logging_error(message, self.submission_id)
            result['message'] = message
            result['status'] = False

            return result

        root = etree.fromstring(receipt)

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
            ghlper.logging_error(result['message'], self.submission_id)

            return result

        # save project accession
        self.write_xml_file(xml_object=root, file_name="project_receipt.xml")
        ghlper.logging_info("Saving project accessions to the database", self.submission_id)
        project_accessions = list()
        for accession in root.findall('PROJECT'):
            project_accessions.append(
                dict(
                    accession=accession.get('accession', default=str()),
                    alias=accession.get('alias', default=str()),
                    status=accession.get('status', default=str()),
                    release_date=accession.get('holdUntilDate', default=str())
                )
            )

        collection_handle = ghlper.get_submission_handle()
        doc = collection_handle.find_one({"_id": ObjectId(self.submission_id)}, {"accessions": 1})

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
            ghlper.update_submission_status(status='info', message=status_message, submission_id=self.submission_id)
            notify_read_status(data={"profile_id": self.profile_id},
                        msg=status_message, action="info", html_id="sample_info")
        return dict(status=True, value='')

    def _register_samples(self, submission_xml_path=str(), modify_submission_xml_path=str()):
        """
        function creates and submits sample xml
        :return:
        """

        result = dict(status=True, value='')
        dt = d_utils.get_datetime()

        # create sample xml
        message = "Registering samples..."
        ghlper.logging_info(message, self.submission_id)
        ghlper.update_submission_status(status='info', message=message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id}, msg=message, action="info", html_id="sample_info")

        # reset error object
        self.submission_helper.flush_converter_errors()

        parser = etree.XMLParser(remove_blank_text=True)

        # root element is  SAMPLE_SET
        root = None
        root_add = etree.parse(SRA_SAMPLE_TEMPLATE, parser).getroot()
        root_modify = etree.parse(SRA_SAMPLE_TEMPLATE, parser).getroot()

        # get samples and create sample nodes
        samples = self.submission_helper.get_sra_samples(submission_location=self.submission_location)

        # get errors
        converter_errors = self.submission_helper.get_converter_errors()

        if converter_errors:
            result['status'] = False
            result['message'] = converter_errors

            return result

        # filter out already submitted samples
        sample_accession_list = self.submission_helper.get_sample_accessions()
        submitted_samples_id = [x['sample_id'] for x in sample_accession_list]
        new_samples = [x['sample_id'] for x in samples if x['sample_id'] not in submitted_samples_id]       

        # modify samples



        # add samples
        sra_samples = list()
        for sample in samples:
            sample_alias = self.project_alias + ":sample:" + sample.get("name", str())
            root = root_add
            if sample['sample_id'] in submitted_samples_id:
                root = root_modify

            sra_samples.append(dict(sample_id=sample['sample_id'], sample_alias=sample_alias))
            sample_node = etree.SubElement(root, 'SAMPLE')
            sample_node.set("alias", sample_alias)
            sample_node.set("center_name", self.sra_settings["sra_center"])
            sample_node.set("broker_name", self.sra_settings["sra_broker"])

            etree.SubElement(sample_node, 'TITLE').text = sample_alias
            sample_name_node = etree.SubElement(sample_node, 'SAMPLE_NAME')
            etree.SubElement(sample_name_node, 'TAXON_ID').text = sample.get("taxon_id", str())
            etree.SubElement(sample_name_node, 'SCIENTIFIC_NAME').text = sample.get("scientific_name", str())

            # add sample attributes
            sample_attributes_node = etree.SubElement(sample_node, 'SAMPLE_ATTRIBUTES')
            for atr in sample.get("attributes", list()):
                sample_attribute_node = etree.SubElement(sample_attributes_node, 'SAMPLE_ATTRIBUTE')
                etree.SubElement(sample_attribute_node, 'TAG').text = atr.get("tag", str())
                etree.SubElement(sample_attribute_node, 'VALUE').text = atr.get("value", str())

                if atr.get("unit", str()):
                    etree.SubElement(sample_attribute_node, 'UNITS').text = atr.get("unit", str())

            # add sample collection date & collection location TODO

            for key in sample.keys():
                if key[0].isupper():
                    ena_names = [ena_key for ena_key in dtol_lookups.DTOL_ENA_MAPPINGS.keys() if ena_key == key or (ena_key.startswith(key + "_" ) and dtol_lookups.DTOL_ENA_MAPPINGS[ena_key].get('ena', ""))]
                    for ena_name in ena_names:
                        sample_attribute_node = etree.SubElement(sample_attributes_node, 'SAMPLE_ATTRIBUTE')
                        etree.SubElement(sample_attribute_node, 'TAG').text =  dtol_lookups.DTOL_ENA_MAPPINGS[ena_name]['ena']
                        function =  dtol_lookups.DTOL_ENA_MAPPINGS[ena_name].get('ena_data_function', dtol_lookups.get_default_data_function)
                        etree.SubElement(sample_attribute_node, 'VALUE').text =  function(sample.get(key, str()))

        if not sra_samples:  # no samples to submit
            log_message = "No new samples to register!"
            ghlper.logging_info(log_message, self.submission_id)
            ghlper.update_submission_status(status='info', message=log_message, submission_id=self.submission_id)
            notify_read_status(data={"profile_id": self.profile_id},
                        msg=log_message, action="info", html_id="sample_info")
            return dict(status=True, value='')

        sra_df = pd.DataFrame(sra_samples)
        sra_df.index = sra_df['sample_alias']


        #do it for modify
        if submitted_samples_id:
            self.process_sample(root_modify, modify_submission_xml_path, sra_df, is_new=False)

        #do it for add
        else:
            self.process_sample(root_add, submission_xml_path, sra_df, is_new=True)

    
        '''
        # write sample xml
        result = self.write_xml_file(xml_object=root_add, file_name="sample.xml")
        if result['status'] is False:
            return result

        sample_xml_path = result['value']

        result = dict(status=True, value='')

        # register samples to the ENA service
        curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                   + '" -F "SUBMISSION=@' \
                   + submission_xml_path \
                   + '" -F "SAMPLE=@' \
                   + sample_xml_path \
                   + '" "' + self.ena_service \
                   + '"'

        ghlper.logging_info(
            "Submitting samples xml to ENA via CURL. CURL command is: " + curl_cmd.replace(self.pass_word, "xxxxxx"),
            self.submission_id)

        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
        except Exception as e:
            message = 'API call error ' + str(e)
            ghlper.logging_error(message, self.submission_id)
            result['message'] = message
            result['status'] = False

            return result

        root = etree.fromstring(receipt)

        if root.get('success') == 'false':
            result['status'] = False
            result['message'] = "Couldn't register SAMPLES due to the following errors: "
            errors = root.findall('.//ERROR')
            if errors:
                error_text = str()
                for e in errors:
                    error_text = error_text + " \n" + e.text

                result['message'] = result['message'] + error_text

            # log error
            ghlper.logging_error(result['message'], self.submission_id)

            return result

        # save sample accession
        self.write_xml_file(xml_object=root, file_name="samples_receipt.xml")
        ghlper.logging_info("Saving samples accessions to the database", self.submission_id)
        sample_accessions = list()
        for accession in root.findall('SAMPLE'):
            biosample = accession.find('EXT_ID')
            sample_alias = accession.get('alias', default=str())
            sample_id = sra_df.loc[sample_alias]['sample_id']
            sample_accessions.append(
                dict(
                    sample_accession=accession.get('accession', default=str()),
                    sample_alias=sample_alias,
                    biosample_accession=biosample.get('accession', default=str()),
                    sample_id=sample_id
                )
            )

        collection_handle = ghlper.get_submission_handle()
        doc = collection_handle.find_one({"_id": ObjectId(self.submission_id)}, {"accessions": 1})

        if doc:
            submission_record = doc
            accessions = submission_record.get("accessions", dict())
            previous = accessions.get('sample', list())
            previous.extend(sample_accessions)
            accessions['sample'] = previous
            submission_record['accessions'] = accessions
            submission_record['date_modified'] = dt

            collection_handle.update(
                {"_id": ObjectId(str(submission_record.pop('_id')))},
                {'$set': submission_record})

            # update submission status
            status_message = "Samples successfully registered, accessions saved."
            ghlper.update_submission_status(status='info', message=status_message, submission_id=self.submission_id)
            notify_read_status(data={"profile_id": self.profile_id},
                        msg=status_message, action="info", html_id="sample_info")
        #update sample status
        Sample(profile_id=self.profile_id).update_read_accession(sample_accessions)
        '''

        return dict(status=True, value='')

    def process_sample(self, root, submission_xml_path, sra_df, is_new=True)  :
        dt = d_utils.get_datetime()

        result = self.write_xml_file(xml_object=root, file_name="sample.xml")
        if result['status'] is False:
            return result

        sample_xml_path = result['value']

        result = dict(status=True, value='')

        # register samples to the ENA service
        curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                   + '" -F "SUBMISSION=@' \
                   + submission_xml_path \
                   + '" -F "SAMPLE=@' \
                   + sample_xml_path \
                   + '" "' + self.ena_service \
                   + '"'

        ghlper.logging_info(
            "Submitting samples xml to ENA via CURL. CURL command is: " + curl_cmd.replace(self.pass_word, "xxxxxx"),
            self.submission_id)

        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
        except Exception as e:
            message = 'API call error ' + str(e).replace(self.pass_word, "xxxxxx"),
            ghlper.logging_error(message, self.submission_id)
            result['message'] = message
            result['status'] = False

            return result

        root = etree.fromstring(receipt)

        if root.get('success') == 'false':
            result['status'] = False
            result['message'] = "Couldn't register SAMPLES due to the following errors: "
            errors = root.findall('.//ERROR')
            if errors:
                error_text = str()
                for e in errors:
                    error_text = error_text + " \n" + e.text

                result['message'] = result['message'] + error_text

            # log error
            ghlper.logging_error(result['message'], self.submission_id)

            return result

        # save sample accession for new sample only
        if is_new:
            self.write_xml_file(xml_object=root, file_name="samples_receipt.xml")
            ghlper.logging_info("Saving samples accessions to the database", self.submission_id)
            sample_accessions = list()
            for accession in root.findall('SAMPLE'):
                biosample = accession.find('EXT_ID')
                sample_alias = accession.get('alias', default=str())
                sample_id = sra_df.loc[sample_alias]['sample_id']
                sample_accessions.append(
                    dict(
                        sample_accession=accession.get('accession', default=str()),
                        sample_alias=sample_alias,
                        biosample_accession=biosample.get('accession', default=str()),
                        sample_id=sample_id
                    )
                )

            collection_handle = ghlper.get_submission_handle()
            doc = collection_handle.find_one({"_id": ObjectId(self.submission_id)}, {"accessions": 1})

            if doc:
                submission_record = doc
                accessions = submission_record.get("accessions", dict())
                previous = accessions.get('sample', list())
                previous.extend(sample_accessions)
                accessions['sample'] = previous
                submission_record['accessions'] = accessions
                submission_record['date_modified'] = dt

                collection_handle.update(
                    {"_id": ObjectId(str(submission_record.pop('_id')))},
                    {'$set': submission_record})

                # update submission status
                status_message = "Samples successfully registered, accessions saved."
                ghlper.update_submission_status(status='info', message=status_message, submission_id=self.submission_id)
                notify_read_status(data={"profile_id": self.profile_id},
                            msg=status_message, action="info", html_id="sample_info")
            #update sample status
            Sample(profile_id=self.profile_id).update_read_accession(sample_accessions)
        return dict(status=True, value='')



    def process_study_release(self, force_release=False):
        """
        function manages release of a study
        :param force_release: if True, study will be released even if still on embargo
        :return:
        """
        dt = d_utils.get_datetime()

        self.submission_helper = SubmissionHelper(submission_id=self.submission_id)

        context = dict(status=True, value='', message='')

        # get study accession
        prj = self.submission_helper.get_study_accessions()

        if not prj:
            message = 'Project accession not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)

            return result

        project_accession = prj[0].get('accession', str())

        # get study status from API
        project_status = ghlper.get_study_status(user_token=self.user_token, pass_word=self.pass_word,
                                                 project_accession=project_accession)

        if not project_status:
            message = 'Cannot determine project release status!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)

            return result

        release_status = project_status[0].get('report', dict()).get('releaseStatus', str())

        if release_status.upper() == 'PUBLIC':
            # study already released, update the information in the db

            first_public = project_status[0].get('report', dict()).get('firstPublic', str())

            try:
                first_public = datetime.strptime(first_public, "%Y-%m-%dT%H:%M:%S")
            except Exception as e:
                first_public = dt

            collection_handle = self.submission_helper.collection_handle
            submission_record = collection_handle.find_one({"_id": ObjectId(self.submission_id)}, {"accessions": 1})
            prj = submission_record.get('accessions', dict()).get('project', [{}])
            prj[0]['status'] = 'PUBLIC'
            prj[0]['release_date'] = first_public

            collection_handle.update(
                {"_id": ObjectId(str(submission_record.pop('_id')))},
                {'$set': submission_record})

            self.set_embargo_message()

            return dict(status=True, value='', message='Project is already public.')

        # release study
        release_date = self.submission_helper.get_study_release()

        if (release_date and release_date["in_the_past"] is True) or force_release is True:
            # clear any existing submission error
            ghlper.update_submission_status(submission_id=self.submission_id)

            self.submission_location = self.create_submission_location()
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.parse(SRA_SUBMISSION_MODIFY_TEMPLATE, parser).getroot()
            actions = root.find('ACTIONS')
            action = etree.SubElement(actions, 'ACTION')

            ghlper.logging_info('Releasing project with accession: ' + project_accession, self.submission_id)

            action_type = etree.SubElement(action, 'RELEASE')
            action_type.set("target", project_accession)

            context = self.write_xml_file(xml_object=root, file_name="submission_modify.xml")

            if context['status'] is False:
                message = context.get("message", str())
                ghlper.update_submission_status(status='error', message=message,
                                                submission_id=self.submission_id)
                notify_read_status(data={"profile_id": self.profile_id},
                        msg=message, action="error", html_id="sample_info")
                return context

            submission_xml_path = context['value']

            result = dict(status=True, value='')

            # compose curl command for study release
            curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                       + '" -F "SUBMISSION=@' \
                       + submission_xml_path \
                       + '" "' + self.ena_service \
                       + '"'

            ghlper.logging_info(
                "Releasing study via CURL. CURL command is: " + curl_cmd.replace(self.pass_word, "xxxxxx"),
                self.submission_id)

            try:
                receipt = subprocess.check_output(curl_cmd, shell=True)
            except Exception as e:
                message = 'API call error ' + str(e).replace(self.pass_word, "xxxxxx"),
                ghlper.logging_error(message, self.submission_id)
                result['message'] = message
                result['status'] = False

                return result

            root = etree.fromstring(receipt)

            if root.get('success') == 'false':
                result['status'] = False
                result['message'] = "Couldn't release project due to the following errors: "
                errors = root.findall('.//ERROR')
                if errors:
                    error_text = str()
                    for e in errors:
                        error_text = error_text + " \n" + e.text

                    result['message'] = result['message'] + error_text

                # log error
                ghlper.logging_error(result['message'], self.submission_id)

                return result

            # update submission record with study status
            self.write_xml_file(xml_object=root, file_name="submission_receipt.xml")
            ghlper.logging_info("Project successfully released. Updating status in the database",
                                self.submission_id)

            collection_handle = self.submission_helper.collection_handle
            submission_record = collection_handle.find_one({"_id": ObjectId(self.submission_id)}, {"accessions": 1})
            prj = submission_record.get('accessions', dict()).get('project', [{}])
            prj[0]['status'] = 'PUBLIC'
            prj[0]['release_date'] = dt

            collection_handle.update(
                {"_id": ObjectId(str(submission_record.pop('_id')))},
                {'$set': submission_record})

            # set embargo message
            self.set_embargo_message()

            return dict(status=True, value='', message="Project release successful.")

        return context

    def _submit_datafiles_rest(self, submission_xml_path=str(), is_new=True):
        """
        function submits run xmls using ENA RESTfulness API,
        and also schedules the transfer of datafiles to ENA Dropbox
        :param submission_xml_path:
        :return:
        """

        message = "Preparing datafiles for submission..."
        ghlper.logging_info(message, self.submission_id)
        ghlper.update_submission_status(status='info', message=message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id}, msg=message, action="info", html_id="sample_info")

        collection_handle = ghlper.get_submission_handle()

        result = dict(status=True, value='')
        xml_parser = etree.XMLParser(remove_blank_text=True)

        # read in datafiles
        try:
            datafiles_df = pd.read_csv(os.path.join(self.submission_location, "datafiles.csv"))
        except Exception as e:
            message = "Couldn't retrieve data files information " + str(e)
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        if not len(datafiles_df):
            # no further datafiles to submit, finalise submission
            self.finalise_submission(is_new)
            return dict(status=True, value='')

        # set default for nans
        datafile_columns = datafiles_df.columns
        for k in datafile_columns:
            datafiles_df[k].fillna('', inplace=True)

        # get run accessions - to provide info on datafiles submission status
        run_accessions = self.submission_helper.get_run_accessions()

        submitted_files = [x for y in run_accessions for x in y.get('datafiles', list())]

        # filter out submitted files from datafiles_df
        if is_new:
            datafiles_df = datafiles_df[~datafiles_df.datafile_id.isin(submitted_files)]
        else:
            datafiles_df = datafiles_df[datafiles_df.datafile_id.isin(submitted_files)]

        if not len(datafiles_df):
            # no further datafiles to submit, finalise submission
            self.finalise_submission(is_new)
            return dict(status=True, value='')

        # get pairing info
        datafiles_pairs = pd.DataFrame(self.submission_helper.get_pairing_info(), columns=['_id', '_id2'])

        # filter datafiles_pairs based on submitted_files and datafiles_df
        # i.e. if any file in a pair has been submitted, then remove the paired record
        if len(datafiles_pairs):
            if is_new:
                datafiles_pairs = datafiles_pairs[
                    ~((datafiles_pairs['_id'].isin(submitted_files)) | (datafiles_pairs['_id2'].isin(submitted_files)))]
            else:
                datafiles_pairs = datafiles_pairs[((datafiles_pairs['_id'].isin(submitted_files)) | (datafiles_pairs['_id2'].isin(submitted_files)))]

        datafile_ids = list(datafiles_df.datafile_id)

        # ...also, it's a valid pair if paired files are in datafiles_df
        if len(datafiles_pairs):
            datafiles_pairs = datafiles_pairs[
                (datafiles_pairs['_id'].isin(datafile_ids)) & (datafiles_pairs['_id2'].isin(datafile_ids))]

        # information found in 'datafiles_pairs' is used to match datafiles in the course of this submission

        left_right_pair = list(datafiles_pairs['_id']) + list(datafiles_pairs['_id2'])
        unpaired_datafiles = [[x, ''] for x in datafile_ids if x not in left_right_pair]

        if unpaired_datafiles:
            frames = [datafiles_pairs, pd.DataFrame(unpaired_datafiles, columns=['_id', '_id2'])]
            datafiles_pairs = pd.concat(frames, ignore_index=True)

        datafiles_df.index = datafiles_df.datafile_id

        # get study accession
        prj = self.submission_helper.get_study_accessions()
        if not prj:
            message = 'Project accession not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        project_accession = prj[0].get('accession', str())

        # get sample accessions
        sample_accessions = self.submission_helper.get_sample_accessions()
        if not sample_accessions:
            message = 'Sample accessions not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        # store file submission error
        submission_errors = list()

        # create submission context - holds xmls for the different reads
        try:
            if not os.path.exists(self.submission_context):
                os.makedirs(self.submission_context)
        except Exception as e:
            message = 'Error creating submission context ' + self.submission_context + ": " + str(e)
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        # create tmp folder to hold mock files
        try:
            if not os.path.exists(self.tmp_folder):
                os.makedirs(self.tmp_folder)
        except Exception as e:
            message = 'Error creating temporary directory ' + self.tmp_folder + ": " + str(e)
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        # retrieve already uploaded files
        files_in_remote = [x.get('report', dict()).get('fileName', str()) for x in
                           ghlper.get_ena_remote_files(user_token=self.user_token, pass_word=self.pass_word)]

        files_not_in_remote = [x for x in list(datafiles_df.datafile_name) if
                               os.path.join(self.remote_location, x) not in files_in_remote]

        mock_file_names = [os.path.join(self.tmp_folder, x) for x in files_not_in_remote]

        # create and upload datafile 'placeholders' to facilitate submission; actual datafiles uploaded separately
        ghlper.touch_files(file_paths=mock_file_names)

        kwargs = dict(submission_id=self.submission_id)
        ghlper.transfer_to_ena(webin_user=self.webin_user, pass_word=self.pass_word, remote_path=
        self.remote_location, file_paths=mock_file_names, **kwargs)
        # branch for manifest submissions
        if Submission().is_manifest_submission(self.submission_id):
            pass
            # self._setup_files_transfer(self.submission_id)
        else:
            # schedule the transfer of actual datafiles to ENA Dropbox
            ghlper.schedule_file_transfer(submission_id=self.submission_id, remote_location=self.remote_location)

        # get sequencing instruments
        instruments = COPOLookup(data_source='sequencing_instrument').broker_data_source()

        for indx in range(len(datafiles_pairs)):
            file1_id = datafiles_pairs.iloc[indx]['_id']
            file2_id = datafiles_pairs.iloc[indx]['_id2']

            files_pair = list()

            if file1_id:
                files_pair.append(datafiles_df.loc[file1_id, :])

            if file2_id:
                files_pair.append(datafiles_df.loc[file2_id, :])

            if not files_pair:
                continue

            # collate submission metadata

            # set sample accession
            s_accession = [x['sample_accession'] for x in sample_accessions if
                           x['sample_id'] == files_pair[0]['study_samples']]

            if not s_accession:
                accession_error = 'Sample accession not found for data files: ' + str(
                    [file_meta['datafile_name'] for file_meta in files_pair])
                ghlper.logging_error(accession_error, self.submission_id)
                submission_errors.append(accession_error)
                continue

            sample_accession = s_accession[0]

            # get submission name
            submission_name = self.project_alias + "_reads_" + files_pair[0].datafile_id

            # get sequencing instrument
            sequencing_instrument = files_pair[
                0].sequencing_instrument if 'sequencing_instrument' in datafile_columns else ''

            # get library source
            library_source = files_pair[0].library_source if 'library_source' in datafile_columns else ''

            # get library selection
            library_selection = files_pair[0].library_selection if 'library_selection' in datafile_columns else ''

            # get library_strategy
            library_strategy = files_pair[0].library_strategy if 'library_strategy' in datafile_columns else ''

            # get description
            library_description = files_pair[0].library_description if 'library_description' in datafile_columns else ''

            submission_file_names = list()
            file_paths = list()
            submitted_files_id = list()
            file = files_pair[0]
            file_paths.append(file.datafile_location)
            submission_file_names.append(file.datafile_name)
            submitted_files_id.append(file.datafile_id)
            if len(files_pair) > 1:
                file = files_pair[1]
                file_paths.append(file.datafile_location)
                submission_file_names.append(file.datafile_name)
                submitted_files_id.append(file.datafile_id)

            # create manifest
            submission_location = os.path.join(self.submission_context, submission_name)
            try:
                if not os.path.exists(submission_location):
                    os.makedirs(submission_location)
            except Exception as e:
                message = 'Error creating submission location ' + ": " + str(e)
                ghlper.logging_error(message, self.submission_id)
                submission_errors.append(message)
                continue

            submission_message = f'Submitting {str(submission_file_names)} ...'
            ghlper.logging_info(submission_message, self.submission_id)
            ghlper.update_submission_status(status='info', message=submission_message, submission_id=self.submission_id)
            notify_read_status(data={"profile_id": self.profile_id},
                        msg=submission_message, action="info", html_id="sample_info")
            # construct experiment xml
            experiment_root = etree.parse(SRA_EXPERIMENT_TEMPLATE, xml_parser).getroot()

            # add experiment node to experiment set
            experiment_node = etree.SubElement(experiment_root, 'EXPERIMENT')
            experiment_alias = "copo-reads-" + submission_name
            experiment_node.set("alias", experiment_alias)
            experiment_node.set("center_name", self.sra_settings["sra_center"])

            study_attributes = self.submission_helper.get_study_descriptors()
            etree.SubElement(experiment_node, 'TITLE').text = study_attributes.get("title", submission_name)
            etree.SubElement(experiment_node, 'STUDY_REF').set("accession", project_accession)

            # design
            experiment_design_node = etree.SubElement(experiment_node, 'DESIGN')
            etree.SubElement(experiment_design_node, 'DESIGN_DESCRIPTION').text = library_description
            etree.SubElement(experiment_design_node, 'SAMPLE_DESCRIPTOR').set("accession", sample_accession)

            # descriptor
            experiment_library_descriptor_node = etree.SubElement(experiment_design_node, 'LIBRARY_DESCRIPTOR')
            etree.SubElement(experiment_library_descriptor_node, 'LIBRARY_STRATEGY').text = library_strategy
            etree.SubElement(experiment_library_descriptor_node, 'LIBRARY_SOURCE').text = library_source
            etree.SubElement(experiment_library_descriptor_node, 'LIBRARY_SELECTION').text = library_selection

            experiment_library_layout_node = etree.SubElement(experiment_library_descriptor_node, 'LIBRARY_LAYOUT')
            if len(files_pair) == 1:
                etree.SubElement(experiment_library_layout_node, 'SINGLE')
            else:
                etree.SubElement(experiment_library_layout_node, 'PAIRED')

            # platform
            inst_plat = [inst['platform'] for inst in instruments if inst['value'] == sequencing_instrument]

            if len(inst_plat):
                experiment_platform_node = etree.SubElement(experiment_node, 'PLATFORM')
                experiment_platform_type_node = etree.SubElement(experiment_platform_node, inst_plat[0])
                etree.SubElement(experiment_platform_type_node, 'INSTRUMENT_MODEL').text = sequencing_instrument

            # write experiement xml
            result = self.write_xml_file(location=submission_location, xml_object=experiment_root,
                                         file_name="experiment.xml")

            if result['status'] is False:
                submission_errors.append(result['message'])
                continue

            experiement_xml_path = result['value']

            # construct run xml
            run_root = etree.parse(SRA_RUN_TEMPLATE, xml_parser).getroot()

            # add run to run set
            run_node = etree.SubElement(run_root, 'RUN')
            run_node.set("alias", experiment_alias)
            run_node.set("center_name", self.sra_settings["sra_center"])
            etree.SubElement(run_node, 'TITLE').text = study_attributes.get("title", submission_name)
            etree.SubElement(run_node, 'EXPERIMENT_REF').set("refname", experiment_alias)

            run_data_block_node = etree.SubElement(run_node, 'DATA_BLOCK')
            run_files_node = etree.SubElement(run_data_block_node, 'FILES')

            for file in files_pair:
                run_file_node = etree.SubElement(run_files_node, 'FILE')
                run_file_node.set("filename", os.path.join(self.remote_location, file.datafile_name))
                run_file_node.set("filetype", "fastq")  # todo: what about BAM, CRAM files?
                run_file_node.set("checksum", file.datafile_hash)  # todo: is this correct as submission time?
                run_file_node.set("checksum_method", "MD5")

            # write run xml
            result = self.write_xml_file(location=submission_location, xml_object=run_root,
                                         file_name="run.xml")

            if result['status'] is False:
                submission_errors.append(result['message'])
                continue

            run_xml_path = result['value']

            final_submission_xml_path = submission_xml_path
            if not is_new:
                result = self._get_edit_submission_xml(submission_xml_path) 
                final_submission_xml_path = result['value']

            # submit xmls to ENA service
            curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                       + '" -F "SUBMISSION=@' \
                       + final_submission_xml_path \
                       + '" -F "EXPERIMENT=@' \
                       + experiement_xml_path \
                       + '" -F "RUN=@' \
                       + run_xml_path \
                       + '" "' + self.ena_service \
                       + '"'

            ghlper.logging_info(
                "Submitting EXPERIMENT and RUN XMLs for " + str(
                    submission_file_names) + " using CURL. CURL command is: " + curl_cmd.replace(self.pass_word,
                                                                                                 "xxxxxx"),
                self.submission_id)

            try:
                receipt = subprocess.check_output(curl_cmd, shell=True)
            except Exception as e:
                message = 'API call error ' + str(e).replace(self.pass_word,"xxxxxx"),
                ghlper.logging_error(message, self.submission_id)
                submission_errors.append(message)
                continue

            receipt_root = etree.fromstring(receipt)

            if receipt_root.get('success') == 'false':
                result['status'] = False
                result['message'] = "Submission error for datafiles: " + str(submission_file_names)
                errors = receipt_root.findall('.//ERROR')
                if errors:
                    error_text = str()
                    for e in errors:
                        error_text = error_text + " \n" + e.text

                    result['message'] = result['message'] + error_text

                # log error
                ghlper.logging_error(result['message'], self.submission_id)

                submission_errors.append(result['message'])
                continue

            # retrieve and save accessions
            self.write_xml_file(location=submission_location, xml_object=receipt_root, file_name="receipt.xml")
            ghlper.logging_info("Saving EXPERIMENT and RUN accessions to the database", self.submission_id)
            run_dict = dict(
                accession=receipt_root.find('RUN').get('accession', default=str()),
                alias=receipt_root.find('RUN').get('alias', default=str()),
                datafiles=submitted_files_id
            )

            experiment_dict = dict(
                accession=receipt_root.find('EXPERIMENT').get('accession', default=str()),
                alias=receipt_root.find('EXPERIMENT').get('alias', default=str()),
            )

            submission_record = collection_handle.find_one({"_id": ObjectId(self.submission_id)},
                                                           {"accessions": 1})
            if submission_record:
                accessions = submission_record.get("accessions", dict())

                #previous_run = accessions.get('run', list())
                #accessions['run'] = previous_run
                #previous_run.append(run_dict)

                #previous_exp = accessions.get('experiment', list())
                #accessions['experiment'] = previous_exp
                #previous_exp.append(experiment_dict)

                previous_run = accessions.get('run', list())
                is_found = False
                for access in previous_run: 
                    if run_dict["accession"] == access["accession"]:
                        is_found = True
                        break
                if not is_found:
                    previous_run.append(run_dict)
                    accessions['run'] = previous_run

                previous_exp = accessions.get('experiment', list())                                                        
                is_found = False
                for access in previous_exp: 
                    if experiment_dict["accession"] == access["accession"]:
                        is_found = True
                        break
                if not is_found:    
                    previous_exp.append(experiment_dict)
                    accessions['experiment'] = previous_exp



                submission_record['accessions'] = accessions

                collection_handle.update(
                    {"_id": ObjectId(self.submission_id)},
                    {'$set': submission_record})

        # completion formalities
        if submission_errors:
            result['status'] = False
            result['message'] = submission_errors
        else:
            # do post submission clean-up

            # get updated run accessions
            run_accessions = self.submission_helper.get_run_accessions()

            submitted_files = [x for y in run_accessions for x in y.get('datafiles', list())]

            # filter out submitted files from datafiles_df
            datafiles_df = datafiles_df[~datafiles_df.datafile_id.isin(submitted_files)]

            # update datafile status
            Sample(profile_id=self.profile_id).update_datafile_status(datafile_ids=submitted_files, status="accepted")

            if  not len(datafiles_df):
                # all files have been successfully submitted, finalise submission
                self.finalise_submission(is_new)

        return result

    '''
    def _submit_datafiles_cli(self, submission_xml_path=str()):
        """
        function handles the submission of datafiles using ENA CLI
        :param submission_xml_path:
        :return:
        """

        collection_handle = ghlper.get_submission_handle()
        log_message = "Preparing datafiles for submission..."
        ghlper.logging_info(log_message, self.submission_id)
        ghlper.update_submission_status(status='info', message=log_message, submission_id=self.submission_id)

        result = dict(status=True, value='')
        xml_parser = etree.XMLParser(remove_blank_text=True)

        # read in datafiles
        try:
            datafiles_df = pd.read_csv(os.path.join(self.submission_location, "datafiles.csv"))
        except Exception as e:
            message = 'Data files information not found ' + str(e)
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        if not len(datafiles_df):
            # no further datafiles to submit, finalise submission
            self.finalise_submission()
            return dict(status=True, value='')

        # set default for nans
        datafile_columns = datafiles_df.columns
        for k in datafile_columns:
            datafiles_df[k].fillna('', inplace=True)

        # create location for submission files -  ena-cli only accepts a single file path
        try:
            if not os.path.exists(self.datafiles_dir):
                os.makedirs(self.datafiles_dir)
        except Exception as e:
            message = 'Error creating file location ' + self.datafiles_dir + ": " + str(e)
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        # compose the cli command to use
        manifest_location = os.path.join(self.submission_location, "manifest.txt")
        cli_cmd = self.get_cli_command(manifest_location=manifest_location)
        ghlper.logging_info("CURL command is: " + cli_cmd.replace(self.pass_word, "xxxxxx"),
                            self.submission_id)

        # get run accessions - these provide info on already submitted datafiles
        run_accessions = self.submission_helper.get_run_accessions()

        submitted_files = [x for y in run_accessions for x in y.get('datafiles', list())]

        # filter out submitted files from datafiles_df
        datafiles_df = datafiles_df[~datafiles_df.datafile_id.isin(submitted_files)]

        if not len(datafiles_df):
            # no further datafiles to submit, finalise submission
            self.finalise_submission()
            return dict(status=True, value='')

        # get pairing info
        datafiles_pairs = pd.DataFrame(self.submission_helper.get_pairing_info(), columns=['_id', '_id2'])

        # filter datafiles_pairs based on submitted_files and datafiles_df
        # i.e. if any of the paired files has been submitted, then remove the paired record
        if len(datafiles_pairs):
            datafiles_pairs = datafiles_pairs[
                ~((datafiles_pairs['_id'].isin(submitted_files)) | (datafiles_pairs['_id2'].isin(submitted_files)))]

        datafile_ids = list(datafiles_df.datafile_id)

        # ...also, it's a valid pair if both files in a pair are in datafiles_df
        if len(datafiles_pairs):
            datafiles_pairs = datafiles_pairs[
                (datafiles_pairs['_id'].isin(datafile_ids)) & (datafiles_pairs['_id2'].isin(datafile_ids))]

        # datafiles will be submitted on the following guideline:
        # if a datafile is marked as paired, but no pairing information is found (in datafiles_pairs),
        # the datafile will be submitted as a single file

        left_right_pair = list(datafiles_pairs['_id']) + list(datafiles_pairs['_id2'])
        unpaired_datafiles = [x for x in datafile_ids if x not in left_right_pair]

        if unpaired_datafiles:
            unpaired_datafiles = [[x, ''] for x in unpaired_datafiles]
            frames = [datafiles_pairs, pd.DataFrame(unpaired_datafiles, columns=['_id', '_id2'])]
            datafiles_pairs = pd.concat(frames, ignore_index=True)

        datafiles_df.index = datafiles_df.datafile_id

        # get study accession
        prj = self.submission_helper.get_study_accessions()
        if not prj:
            message = 'Project accession not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        project_accession = ['STUDY', prj[0]['accession']]

        # get sample accessions
        sample_accessions = self.submission_helper.get_sample_accessions()
        if not sample_accessions:
            message = 'Sample accessions not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        # store file submission error
        submission_errors = list()

        for indx in range(len(datafiles_pairs)):
            file1_id = datafiles_pairs.iloc[indx]['_id']
            file2_id = datafiles_pairs.iloc[indx]['_id2']

            files_pair = list()

            if file1_id:
                files_pair.append(datafiles_df.loc[file1_id, :])

            if file2_id:
                files_pair.append(datafiles_df.loc[file2_id, :])

            if not files_pair:
                continue

            # collate submission metadata
            reads_metadata = list()

            # set study accession
            reads_metadata.append(project_accession)

            # set sample accession
            s_accession = [x['sample_accession'] for x in sample_accessions if
                           x['sample_id'] == files_pair[0]['study_samples']]

            if not s_accession:
                accession_error = 'Sample accession not found for datafiles: ' + str(
                    [file_meta['datafile_name'] for file_meta in files_pair])
                ghlper.logging_error(accession_error, self.submission_id)
                submission_errors.append(accession_error)
                continue

            reads_metadata.append(['SAMPLE', s_accession[0]])

            # set submission name
            submission_name = self.project_alias + "_reads_" + files_pair[0].datafile_id
            reads_metadata.append(['NAME', submission_name])

            # set sequencing instrument
            if 'sequencing_instrument' in datafile_columns:
                reads_metadata.append(['INSTRUMENT', files_pair[0].sequencing_instrument])

            # set library source
            if 'library_source' in datafile_columns:
                reads_metadata.append(['LIBRARY_SOURCE', files_pair[0].library_source])

            # set library selection
            if 'library_selection' in datafile_columns:
                reads_metadata.append(['LIBRARY_SELECTION', files_pair[0].library_selection])

            # set library_strategy
            if 'library_strategy' in datafile_columns:
                reads_metadata.append(['LIBRARY_STRATEGY', files_pair[0].library_strategy])

            # set description
            if 'library_description' in datafile_columns:
                reads_metadata.append(['DESCRIPTION', files_pair[0].library_description])

            # set file name - The following file name fields are supported in the manifest file:
            #
            #     BAM: Single BAM file
            #     CRAM: Single CRAM file
            #     FASTQ: Single fastq file
            # reads_metadata.append(['FASTQ', ntpath.basename(files_pair[0].datafile_location)])
            # if len(files_pair) > 1:
            #     reads_metadata.append(['FASTQ', ntpath.basename(files_pair[1].datafile_location)])

            submission_file_names = list()
            submitted_files_id = list()
            file = files_pair[0]
            reads_metadata.append(['FASTQ', file.datafile_location])
            submission_file_names.append(file.datafile_name)
            submitted_files_id.append(file.datafile_id)
            if len(files_pair) > 1:
                file = files_pair[1]
                reads_metadata.append(['FASTQ', file.datafile_location])
                submission_file_names.append(file.datafile_name)
                submitted_files_id.append(file.datafile_id)

            # generate manifest file
            manifest = pd.DataFrame(reads_metadata)
            manifest.to_csv(manifest_location, sep='\t', header=False, index=False)

            # copy target datafile(s) to submission location
            # existing_files = [ntpath.basename(name) for name in glob.glob(os.path.join(self.datafiles_dir, "*.*"))]
            # copy_errors = list()
            # submission_file_names = list()
            # submitted_files_id = list()
            # for file_meta in files_pair:
            #     submission_file_names.append(file_meta.datafile_name)
            #     submitted_files_id.append(file_meta.datafile_id)
            #     if ntpath.basename(file_meta.datafile_location) not in existing_files:
            #         try:
            #             shutil.copy(file_meta.datafile_location, self.datafiles_dir)
            #         except Exception as e:
            #             message = "Error copying datafile " + file_meta.datafile_name + " " + str(e)
            #             copy_errors.append(message)
            #
            # if len(copy_errors):
            #     ghlper.logging_error(str(copy_errors))
            #     submission_errors.extend(copy_errors)
            #     continue

            submission_message = "Submitting: " + str(submission_file_names)
            ghlper.logging_info(submission_message, self.submission_id)
            ghlper.update_submission_status(status='info', message=submission_message, submission_id=self.submission_id)

            try:
                thread = pexpect.spawn(cli_cmd, timeout=None)
                cpl = thread.compile_pattern_list([pexpect.EOF, '(.+)'])

                while True:
                    i = thread.expect_list(cpl, timeout=None)
                    if i == 0:  # signals end of transfer
                        # retrieve submission receipt
                        output_path = os.path.join(self.submission_location, 'reads', submission_name, 'submit',
                                                   'receipt.xml')
                        receipt_xml = [x for x in glob.glob(output_path)]

                        if receipt_xml:
                            receipt_root = etree.parse(receipt_xml[0], xml_parser).getroot()

                            if receipt_root.get('success') == 'true':
                                run_dict = dict(
                                    accession=receipt_root.find('RUN').get('accession', default=str()),
                                    alias=receipt_root.find('RUN').get('alias', default=str()),
                                    datafiles=submitted_files_id
                                )

                                experiment_dict = dict(
                                    accession=receipt_root.find('EXPERIMENT').get('accession', default=str()),
                                    alias=receipt_root.find('EXPERIMENT').get('alias', default=str()),
                                )

                                doc = collection_handle.find_one({"_id": ObjectId(self.submission_id)},
                                                                 {"accessions": 1})
                                if doc:
                                    submission_record = doc
                                    accessions = submission_record.get("accessions", dict())

                                    previous_run = accessions.get('run', list())
                                    is_found = False
                                    for access in previous_run: 
                                        if run_dict["accession"] == access["accession"]:
                                            is_found = True
                                            break
                                    if not is_found:
                                        previous_run.append(run_dict)
                                        accessions['run'] = previous_run

                                    previous_exp = accessions.get('experiment', list())                                                        
                                    is_found = False
                                    for access in previous_exp: 
                                        if experiment_dict["accession"] == access["accession"]:
                                            is_found = True
                                            break
                                    if not is_found:    
                                        previous_exp.append(experiment_dict)
                                        accessions['experiment'] = previous_exp

                                    submission_record['accessions'] = accessions
                                    submission_record['target_id'] = str(submission_record.pop('_id'))

                                    collection_handle.update(
                                        {"_id": ObjectId(str(submission_record.pop('_id')))},
                                        {'$set': submission_record})
                            else:
                                datafile_error = "Submission error for datafiles: " + str(submission_file_names)
                                errors = receipt_root.findall('.//ERROR')
                                if errors:
                                    for e in errors:
                                        datafile_error = datafile_error + " \n" + e.text

                                # log error
                                ghlper.logging_error(datafile_error, self.submission_id)
                                submission_errors.append(datafile_error)
                        break
                    elif i == 1:
                        pexp_match = thread.match.group(1)
                        tokens_to_match = ["INFO", "ERROR"]

                        if any(tm in pexp_match.decode("utf-8") for tm in tokens_to_match):
                            tokens = pexp_match.decode("utf-8")

                            if tokens.startswith("INFO :"):
                                ghlper.logging_info(tokens[7:], self.submission_id)
                            elif tokens.startswith("ERROR:"):
                                t_message = tokens[7:]
                                ghlper.logging_error(t_message, self.submission_id)
                                submission_errors.append(t_message)
                            else:
                                ghlper.logging_info(tokens, self.submission_id)
                thread.close()
            except Exception as e:
                message = 'API call error ' + str(e)
                ghlper.logging_error(message, self.submission_id)
                submission_errors.append(message)

        if submission_errors:
            result['status'] = False
            result['message'] = submission_errors
        else:
            # do post submission clean-up

            # get updated run accessions
            run_accessions = self.submission_helper.get_run_accessions()

            submitted_files = [x for y in run_accessions for x in y.get('datafiles', list())]

            # filter out submitted files from datafiles_df
            datafiles_df = datafiles_df[~datafiles_df.datafile_id.isin(submitted_files)]

            if not len(datafiles_df):
                # all files have been successfully submitted, finalise submission
                self.finalise_submission()

        return result
    
    def get_cli_command(self, manifest_location=str()):
        """
        function composes the command line interface command to use for datafiles submission
        :param manifest_location:
        :return:
        """

        test_service = ''
        if 'wwwdev' in self.ena_service:  # using ena's test service
            test_service = ' -test '
            ghlper.logging_info("This is a test submission", self.submission_id)

        # todo with -inputdir set - ENA currently claims we don't need this, but doesn't work otherwise
        # cli_cmd = 'java -Xmx2048m -jar ' + ENA_CLI + ' -context reads -userName ' + self.user_token + \
        #           ' -password ' + self.pass_word + ' -manifest ' + manifest_location + test_service + ' -submit
        #           -centerName ' + \
        #           self.sra_settings["sra_center"] + ' -inputDir ' + self.datafiles_dir + ' -ascp '

        cli_cmd = 'java -Xmx2048m -jar ' + ENA_CLI + ' -context reads -userName ' + self.user_token + \
                  ' -password "' + self.pass_word + '" -manifest ' + manifest_location + test_service + ' -submit ' \
                                                                                                      '-centerName ' + \
                  self.sra_settings["sra_center"] + ' -ascp '

        return cli_cmd
    '''

    def finalise_submission(self, is_new=True):
        """
        function runs final steps to complete the submission
        :return:
        """
        if not is_new:
            return

        dt = d_utils.get_datetime()
        # all metadata have been successfully submitted
        log_message = "Finalising submission..."
        ghlper.logging_info(log_message, self.submission_id)
        ghlper.update_submission_status(status='info', message=log_message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id},
                        msg=log_message, action="info", html_id="sample_info")
        # remove submission auxiliary folders

        if os.path.exists(self.datafiles_dir):
            try:
                shutil.rmtree(self.datafiles_dir)
            except Exception as e:
                message = "Error removing files folder: " + str(e)
                ghlper.logging_error(message, self.submission_id)

        if os.path.exists(self.tmp_folder):
            try:
                shutil.rmtree(self.tmp_folder)
            except Exception as e:
                message = "Error removing temporary folder: " + str(e)
                ghlper.logging_error(message, self.submission_id)

        # mark submission as complete
        collection_handle = ghlper.get_submission_handle()
        submission_record = dict(complete=True, completed_on=dt)
        collection_handle.update(
            {"_id": ObjectId(self.submission_id)},
            {'$set': submission_record})

        # update submission status
        status_message = "Submission is marked as complete!"
        ghlper.logging_info(status_message, self.submission_id)
        ghlper.update_submission_status(status='success', message=status_message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id},
                        msg=status_message, action="info", html_id="sample_info")
        return True

    def write_xml_file(self, location=str(), xml_object=None, file_name=str()):
        """
        function writes xml to the specified location or to a default one
        :param location:
        :param xml_object:
        :param file_name:
        :return:
        """

        result = dict(status=True, value='')

        output_location = self.submission_location
        if location:
            output_location = location

        xml_file_path = os.path.join(output_location, file_name)
        tree = etree.ElementTree(xml_object)

        try:
            tree.write(xml_file_path, encoding="utf8", xml_declaration=True, pretty_print=True)
        except Exception as e:
            message = 'Error writing xml file ' + file_name + ": " + str(e)
            ghlper.logging_error(message, self.submission_id)
            result['message'] = message
            result['status'] = False

            return result

        message = file_name + ' successfully written to  ' + xml_file_path
        ghlper.logging_info(message, self.submission_id)

        result['value'] = xml_file_path

        return result

    def release_study(self):
        """
        function makes the study public
        :return:
        """
        dt = d_utils.get_datetime()
        # instantiate helper object - performs most auxiliary tasks associated with the submission
        self.submission_helper = SubmissionHelper(submission_id=self.submission_id)

        # clear any existing submission error
        ghlper.update_submission_status(submission_id=self.submission_id)

        # submission location
        self.submission_location = self.create_submission_location()

        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(SRA_SUBMISSION_MODIFY_TEMPLATE, parser).getroot()
        actions = root.find('ACTIONS')
        action = etree.SubElement(actions, 'ACTION')

        # get study accession
        prj_accession = str()
        collection_handle = self.submission_helper.collection_handle
        doc = collection_handle.find_one({"_id": ObjectId(self.submission_id)}, {"accessions": 1})

        if doc:
            submission_record = doc
            prj = submission_record.get('accessions', dict()).get('project', [{}])
            prj_accession = prj[0].get("accession", str())

        if not prj_accession:
            message = 'Project accession not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        ghlper.logging_info('Releasing study with accession: ' + prj_accession, self.submission_id)

        action_type = etree.SubElement(action, 'RELEASE')
        action_type.set("target", prj_accession)

        context = self.write_xml_file(xml_object=root, file_name="submission_modify.xml")

        if context['status'] is False:
            ghlper.update_submission_status(status='error', message=context.get("message", str()),
                                            submission_id=self.submission_id)
            return context

        submission_xml_path = context['value']

        result = dict(status=True, value='')

        # compose curl command for study release
        curl_cmd = 'curl -u "' + self.user_token + ':' + self.pass_word \
                   + '" -F "SUBMISSION=@' \
                   + submission_xml_path \
                   + '" "' + self.ena_service \
                   + '"'

        ghlper.logging_info(
            "Modifying study via CURL. CURL command is: " + curl_cmd.replace(self.pass_word, "xxxxxx"),
            self.submission_id)

        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
        except Exception as e:
            message = 'API call error ' + str(e).replace(self.pass_word, "xxxxxx"),
            ghlper.logging_error(message, self.submission_id)
            result['message'] = message
            result['status'] = False

            return result

        root = etree.fromstring(receipt)

        if root.get('success') == 'false':
            result['status'] = False
            result['message'] = "Couldn't release STUDY due to the following errors: "
            errors = root.findall('.//ERROR')
            if errors:
                error_text = str()
                for e in errors:
                    error_text = error_text + " \n" + e.text

                result['message'] = result['message'] + error_text

            # log error
            ghlper.logging_error(result['message'], self.submission_id)

            return result

        # update submission record with study status
        self.write_xml_file(xml_object=root, file_name="submission_receipt.xml")
        ghlper.logging_info("Study successfully released. Updating status in the database",
                            self.submission_id)
        prj[0]['status'] = 'PUBLIC'
        prj[0]['release_date'] = dt

        collection_handle.update(
            {"_id": ObjectId(str(submission_record.pop('_id')))},
            {'$set': submission_record})

        # update submission status
        status_message = "Study release successful."
        ghlper.update_submission_status(status='info', message=status_message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id},
                        msg=status_message, action="info", html_id="sample_info")
        result = dict(status=True, value='', message=status_message)
        return result

    def update_study_status(self):
        """
        function updates the embargo status of studies
        :return:
        """

        # this manages its own mongodb connection as it will be accessed by a celery worker subprocess
        mongo_client = mutil.get_mongo_client()
        collection_handle = mongo_client['SubmissionCollection']

        records = cursor_to_list(collection_handle.find({"$and": [
            {"repository": "ena", "complete": True, 'deleted': d_utils.get_not_deleted_flag()},
            {'accessions.project.0': {"$exists": True}}]},
            {'accessions.project': 1}))

        status_message = "Checking for ENA Study status updates " + str(len(records))
        ghlper.log_general_info(status_message)
        #
        # if submissions:
        #     pass

        result = dict(status=True, value='')

        return result

    def set_embargo_message(self):
        """
        function sets embargo status message for submission
        :return:
        """

        self.submission_helper = SubmissionHelper(submission_id=self.submission_id)

        # get study accession
        prj = self.submission_helper.get_study_accessions()
        if not prj:
            message = 'Project accession not found!'
            ghlper.logging_error(message, self.submission_id)
            result = dict(status=False, value='', message=message)
            return result

        status = prj[0].get('status', "Unknown")
        release_date = prj[0].get("release_date", str())

        extra_info = ''

        if status.upper() == "PRIVATE":
            if len(release_date) >= 10:  # e.g. '2019-08-30'
                try:
                    datetime_object = datetime.strptime(release_date[:10], '%Y-%m-%d')
                    release_date = time.strftime('%a, %d %b %Y %H:%M', datetime_object.timetuple())
                except Exception as e:
                    ghlper.logging_error("Could not resolve submission release date" + str(e), self.submission_id)

            extra_info = "<li>An embargo is placed on this submission. Embargo will be automatically lifted on: " + \
                         release_date + \
                         "</li><li>" \
                         "To release this study now, select " \
                         "<strong>Lift Embargo</strong> from the menu</li>"
        elif status.upper() == "PUBLIC":
            extra_info = "<li>" \
                         "To view this study on the ENA browser, select <strong>" \
                         "View in Remote</strong> from the menu (<span style='font-size:10px;'>Recently " \
                         "completed submissions can take up to 24 hours to appear on ENA</span>)</li>"

        # add transfer status
        transfer_status_message = ''
        transfer_status = self.get_upload_status()
        if transfer_status['status'] is True and transfer_status['message']:
            transfer_status_message = "<li>" + transfer_status['message'] + "</li>"

        status_message = f'<div>Submission completed.</div><ul>{transfer_status_message}<li>To view accessions, ' \
                         f'select <strong>View Accessions</strong> from the menu</li>{extra_info}</ul>'

        ghlper.update_submission_status(status='success', message=status_message, submission_id=self.submission_id)
        notify_read_status(data={"profile_id": self.profile_id},
                        msg=status_message, action="info", html_id="sample_info")

        return dict(status=True, value='', message='')

    def get_upload_status(self):
        """
        function reports on the upload status of files to ENA
        :return:
        """

        result = dict(status=True, value='', message='')
        transfer_collection_handle = ghlper.get_filetransfer_queue_handle()

        transfer_record = transfer_collection_handle.find_one({"submission_id": self.submission_id})

        if not transfer_record:
            # transfer probably done
            return result

        status_message = "Currently uploading data files. Progress report will be provided."
        if transfer_record.get("processing_status", str()) == "pending":
            status_message = "Data files upload pending. Progress will be reported."

        result['message'] = status_message

        return result

    def process_file_transfer(self):
        """
        function processes the file transfer queue and initiates transfer to ENA Dropbox
        :return:
        """
        dt = d_utils.get_datetime()
        transfer_collection_handle = ghlper.get_filetransfer_queue_handle()

        # check and update status for long running transfers - possibly stalled
        records = cursor_to_list(
            transfer_collection_handle.find({'processing_status': 'running'}))

        for rec in records:
            recorded_time = rec.get("date_modified", None)

            if not recorded_time:
                rec['date_modified'] = dt
                transfer_collection_handle.update(
                    {"_id": ObjectId(str(rec.pop('_id')))},
                    {'$set': rec})

                continue

            current_time = dt
            time_difference = current_time - recorded_time
            if time_difference.seconds >= (TRANSFER_REFRESH_THRESHOLD):  # time transfer has been running
                # refresh task to be rescheduled
                rec['date_modified'] = dt
                rec['processing_status'] = 'pending'
                transfer_collection_handle.update(
                    {"_id": ObjectId(str(rec.pop('_id')))},
                    {'$set': rec})

        # obtain pending submission for processing
        records = cursor_to_list(
            transfer_collection_handle.find({'processing_status': 'pending'}).sort([['date_modified', 1]]))

        if not records:
            return True

        # pick top of the list, update status and timestamp
        queued_record = records[0]
        queued_record['processing_status'] = 'running'
        queued_record['date_modified'] = dt

        queued_record_id = queued_record.pop('_id', '')

        transfer_collection_handle.update(
            {"_id": ObjectId(str(queued_record_id))},
            {'$set': queued_record})

        self.submission_id = str(queued_record['submission_id'])
        self.remote_location = str(queued_record['remote_location'])

        # get submission record
        submission_collection_handle = ghlper.get_submission_handle()
        submission_record = submission_collection_handle.find_one(
            {'_id': ObjectId(self.submission_id)}, {"bundle_meta": 1, "profile_id": 1})

        local_paths = [x['file_path'] for x in submission_record['bundle_meta'] if
                       x.get('upload_status', False) is False]

        if not local_paths:
            message = "File transfer request: There are files to transfer."
            ghlper.logging_info(message, self.submission_id)
            return True

        # push updates to client via to channels layer
        status_message = f'Commencing transfer of {len(local_paths)} data files to ENA. Progress will be reported.'
        ghlper.notify_transfer_status(profile_id=submission_record['profile_id'], submission_id=self.submission_id,
                                      status_message=status_message)

        kwargs = dict(submission_id=self.submission_id, transfer_queue_id=queued_record_id, report_status=True)
        ghlper.transfer_to_ena(webin_user=self.webin_user, pass_word=self.pass_word, remote_path=self.remote_location,
                               file_paths=local_paths, **kwargs)

        # another sanity check...this time for transfer completion
        submission_record = submission_collection_handle.find_one(
            {'_id': ObjectId(self.submission_id)}, {"bundle_meta": 1, "profile_id": 1})

        local_paths = [x['file_path'] for x in submission_record['bundle_meta'] if
                       x.get('upload_status', False) is False]

        if not local_paths:
            message = "All data files successfully transferred to ENA."
            ghlper.logging_info(message, self.submission_id)
            transfer_collection_handle.remove({"_id": queued_record_id})
            self.set_embargo_message()

            ghlper.notify_transfer_status(profile_id=submission_record['profile_id'], submission_id=self.submission_id,
                                          status_message=message)

        return True

    def _setup_files_transfer(self, submission_record_id):
        submission = Submission().get_record(submission_record_id)
        for file_id in submission["bundle"]:
            tx.make_transfer_record(file_id=file_id, submission_id=submission_record_id)

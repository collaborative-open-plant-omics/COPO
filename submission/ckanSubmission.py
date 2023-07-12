# Created by fshaw at 21/11/2018

import datetime
import traceback
import subprocess
import os, json, uuid
from collections import namedtuple

import requests
from dal import cursor_to_list
from dal.copo_da import Submission
from dal.copo_da import Profile
from exceptions_and_logging.logger import Logger
from bson import ObjectId
from submission.helpers import generic_helper as ghlper
from web.apps.web_copo.schemas.utils.cg_core.cg_schema_generator import CgCoreSchemas
from web.apps.web_copo.schemas.utils.data_utils import get_base_url
from urllib.parse import urljoin
import web.apps.web_copo.schemas.utils.data_utils as d_utils


class CkanSubmit:
    def __init__(self, submission_id=str()):
        self.submission_id = submission_id

        self.host = None
        self.api_token = None
        self.headers = None
        self.api_url = None
        self.profile_id = None

    def submit(self):
        """
        function manages the submission of objects to ckan
        :return:
        """

        if not self.submission_id:
            return dict(status=False, message='Submission identifier not found!')

            # retrieve submssion record from db

        # specify filtering
        filter_by = dict(_id=ObjectId(str(self.submission_id)))

        # specify projection
        query_projection = {
            "_id": 1,
            "repository_docs.apikey": 1,
            "repository_docs.url": 1,
            "profile_id": 1,
            "meta.type": 1,
            "meta.params": 1,
            "complete": 1

        }

        doc = Submission().get_collection_handle().aggregate(
            [
                {"$addFields": {
                    "destination_repo_converted": {
                        "$convert": {
                            "input": "$destination_repo",
                            "to": "objectId",
                            "onError": 0
                        }
                    }
                }
                },
                {
                    "$lookup":
                        {
                            "from": "RepositoryCollection",
                            "localField": "destination_repo_converted",
                            "foreignField": "_id",
                            "as": "repository_docs"
                        }
                },
                {
                    "$project": query_projection
                },
                {
                    "$match": filter_by
                }
            ])

        records = cursor_to_list(doc)

        # get submission record
        try:
            submission_record = records[0]
        except Exception as e:
            ghlper.logging_error(traceback.format_exc(), self.submission_id)
            message = "Submission record not found. Please try resubmitting."
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            Logger().exception(e)
            return dict(status='error', message=message)

        try:
            repository_info = submission_record['repository_docs'][0]
        except Exception as ex:
            ghlper.logging_error(traceback.format_exc(), self.submission_id)
            error_type = type(ex).__name__
            message = f"Couldn't retrieve repository information due to the following error: '{error_type}'"
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            return dict(status='error', message=message)

        if str(submission_record.get("complete", False)).lower() == 'true':
            message = 'Submission is marked as complete!'
            ghlper.logging_info(message, self.submission_id)
            ghlper.update_submission_status(status='success', message=message, submission_id=self.submission_id)

            return dict(status=True, message=message)

        # set submission parameters
        self.profile_id = submission_record.get("profile_id", str())
        self.host = repository_info.get("url", str())
        self.api_token = repository_info.get("apikey", str())
        self.headers = {'X-CKAN-API-Key': self.api_token}
        self.api_url = self.host
        if self.host.endswith(".org"):
            self.api_url = urljoin(self.host, '/api/3/action/')

        # check submission context and select submission pathway
        type = submission_record.get("meta", dict()).get("type", str())
        params = submission_record.get("meta", dict()).get("params", dict())

        if type == "new":  # create a dataset to submit
            return self._do_dataset_create_submit()

        if type == "existing":  # a dataset specified proceed to submit
            return self._do_dataset_submit(**params)

        return dict(status=True, message="No status message provided!")

    def _do_dataset_submit(self, **params):
        """
        function submits to a selected dataset
        :param params:
        :return:
        """

        dataset_id = params.get("id", str()).strip()
        dataset_name = params.get("name", str()).strip()
        dataset_title = params.get("title", str())

        if not all((dataset_id, dataset_name)):
            message = f"Error submitting to CKAN. Missing dataset identifier and/or name!"
            ghlper.logging_error(message, self.submission_id)
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            return dict(status='error', message=message)

        # accessions to db
        acc = dict()
        acc['dataset_id'] = dataset_id
        acc['dataset_title'] = dataset_title
        acc['dataset_name'] = dataset_name
        acc['repo_url'] = self.api_url
        acc['url'] = self.host

        # update submission record with accessions
        submission_record = dict(accessions=acc)
        Submission().get_collection_handle().update(
            {"_id": ObjectId(self.submission_id)},
            {'$set': submission_record})

        return self._submit_datafiles(dataset_id=dataset_id)

    def _do_dataset_create_submit(self):
        """
        function creates a new dataset to fulfill submission
        :return:
        """

        submission_record = Submission().get_collection_handle().find_one({'_id': ObjectId(self.submission_id)},
                                                                          {"accessions": 1})

        dataset_id = submission_record.get("accessions", dict()).get("dataset_id", str())

        # there's an existing dataset associated with this submission
        if dataset_id:
            return self._submit_datafiles(dataset_id=dataset_id)

        # convert to CKAN metadata
        try:
            submission_metadata = self._get_submission_metadata()
        except Exception as ex:
            ghlper.logging_error(traceback.format_exc(), self.submission_id)
            message = f"Error converting from CG Core to CKAN: '{str(ex)}'"
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            return dict(status='error', message=message)

        dataset_result = dict()
        call_url = urljoin(self.api_url, 'package_create')

        try:
            response = requests.post(call_url, json=submission_metadata, headers=self.headers)
            response_status_code = response.status_code
            response_data = response.json()
        except Exception as ex:
            ghlper.logging_error(traceback.format_exc(), self.submission_id)
            message = f"Dataset creation error: '{str(ex)}'"
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            return dict(status='error', message=message)

        if response_status_code == 200:
            # check for error
            if str(response_data.get('success', str())).lower() == "false":
                message = response_data.get('error', dict()).get('message', str())
                message = f"Dataset creation error: '{message}'"
                ghlper.logging_error(message, self.submission_id)

                ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
                return dict(status='error', message=message)

            dataset_result = response_data.get("result", dict())

        elif response_status_code == 400:
            # likely bad request due to protocol used
            if call_url.startswith('http://'):
                call_url = call_url.replace("http", "https")

            try:
                response = requests.post(call_url, json=submission_metadata, headers=self.headers)
                response_status_code = response.status_code
                response_data = response.json()
            except Exception as ex:
                ghlper.logging_error(traceback.format_exc(), self.submission_id)
                message = f"Dataset creation error: '{str(ex)}'"
                ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
                return dict(status='error', message=message)

            if response_status_code == 200:
                # check for error
                if str(response_data.get('success', str())).lower() == "false":
                    message = response_data.get('error', dict()).get('message', str())
                    message = f"Dataset creation error: '{message}'"
                    ghlper.logging_error(message, self.submission_id)

                    ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
                    return dict(status='error', message=message)

                dataset_result = response_data.get("result", dict())
        elif response_status_code == 409:
            # check for error
            if str(response_data.get('success', str())).lower() == "false":
                message = response_data.get('error', dict()).get('message', str())
                message = f"Dataset creation error: '{message}'"
                ghlper.logging_error(message, self.submission_id)

                ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
                return dict(status='error', message=message)

        else:
            message = f"Dataset creation error: '{response.reason} - {response.text}'"
            ghlper.logging_error(message, self.submission_id)
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            return dict(status='error', message=message)

        if not dataset_result:
            message = f"Dataset creation error. No status message provided!"
            ghlper.logging_error(message, self.submission_id)
            ghlper.update_submission_status(status='error', message=message, submission_id=self.submission_id)
            return dict(status='error', message=message)

        # retrieve and store accessions to db
        acc = dict()
        acc['dataset_id'] = dataset_result.get("id", str())
        acc['dataset_title'] = dataset_result.get("title", str())
        acc['dataset_name'] = dataset_result.get("name", str())
        acc['repo_url'] = self.api_url
        acc['url'] = self.host

        # update submission record with accessions
        submission_record = dict(accessions=acc)
        Submission().get_collection_handle().update(
            {"_id": ObjectId(self.submission_id)},
            {'$set': submission_record})

        return self._submit_datafiles(dataset_id=dataset_result.get("id", str()))

    def _submit_datafiles(self, dataset_id=str()):
        """
        function submits datafiles in the submission bundle given the dataset id
        :param dataset_id:
        :return:
        """

        submission_record = Submission().get_collection_handle().find_one({'_id': ObjectId(self.submission_id)},
                                                                          {"bundle_meta": 1})

        # get files to upload
        datafiles = submission_record.get("bundle_meta", list())
        call_url = urljoin(self.api_url, 'resource_create')
        api_token = self.api_token

        upload_error = list()

        for df in datafiles:
            # check for already uploaded file
            if str(df.get("upload_status", False)).lower() == 'true':
                continue

            file_basename = os.path.basename(df.get("file_path", str()))
            filename, file_extension = os.path.splitext(file_basename)
            file_extension = file_extension.lstrip(".")
            file_mimetype = self.get_media_type_from_file_ext(file_extension)
            date_created = str(datetime.date.today())

            file_path = df.get("file_path", str())
            api_call = f'curl -H "Authorization:{api_token}" "{call_url}" ' \
                       f'--form upload=@{file_path} ' \
                       f'--form package_id={dataset_id} ' \
                       f'--form name={file_basename} ' \
                       f'--form mimetype={file_mimetype} ' \
                       f'--form created={date_created}'

            try:
                receipt = subprocess.check_output(api_call, shell=True)
                receipt = json.loads(receipt.decode('utf-8'))

                if str(receipt.get('success', str())).lower() == "false":
                    message = receipt.get('error', dict()).get('message', str())
                    message = f"Error uploading file: '{message}'"
                    ghlper.logging_error(message, self.submission_id)
                    upload_error.append(message)
                else:
                    df["upload_status"] = True
            except Exception as e:
                exception_message = "Error uploading file " + df.get("file_path", str()) + " : " + str(e)
                ghlper.logging_error(exception_message, self.submission_id)
                upload_error.append(exception_message)

        if upload_error:
            # save status of uploaded files
            submission_record = dict(bundle_meta=datafiles)
            Submission().get_collection_handle().update(
                {"_id": ObjectId(self.submission_id)},
                {'$set': submission_record})

            ghlper.logging_error(str(upload_error), self.submission_id)
            ghlper.update_submission_status(status='error', message=str(upload_error), submission_id=self.submission_id)

            return dict(status='error', message=str(upload_error))

        # update status, marking submission as complete
        submission_record = dict(complete=True, completed_on=d_utils.get_datetime(), bundle_meta=datafiles)
        Submission().get_collection_handle().update(
            {"_id": ObjectId(self.submission_id)},
            {'$set': submission_record})

        status_message = "Submission is marked as complete!"
        ghlper.logging_info(status_message, self.submission_id)
        ghlper.update_submission_status(status='success', message=status_message, submission_id=self.submission_id)

        return dict(status='success', message=status_message)

    def _get_submission_metadata(self):
        """
        function composes the metadata for a new dataset creation
        :return:
        """

        submission_metadata = dict()

        # submission metadata will be derived from a number of sources including description metadata,
        # Profile, and Persons

        # get user data
        description_metadata = Submission().get_submission_metadata(submission_id=self.submission_id)["meta"]

        # profile info
        profile = Profile().get_record(self.profile_id)

        # get person info
        person = ghlper.get_person_handle().find_one({'profile_id': self.profile_id},
                                                     {"email": 1, "firstName": 1, "lastName": 1})

        # set some initial values, these coould be replaced later with actual user data from CG Core
        submission_metadata['title'] = profile.get('title', str())

        person_name = person.get('firstName', str()) + " " + person.get('lastName', str())
        person_email = person.get('email', str())
        submission_metadata["author"] = person_name
        submission_metadata["maintainer"] = person_name
        submission_metadata["author_email"] = person_email
        submission_metadata["maintainer_email"] = person_email

        submission_metadata["state"] = "active"
        submission_metadata["tags"] = list()
        submission_metadata["private"] = False
        submission_metadata['extras'] = list()
        submission_metadata["type"] = "dataset"

        try:
            url = get_base_url()
            submission_metadata["url"] = urljoin(url, 'copo/resolve/' + self.submission_id)
            submission_metadata["extras"].append(dict(key="relation", value=submission_metadata["url"]))
        except Exception as ex:
            ghlper.logging_error(traceback.format_exc(), self.submission_id)

        # define a mapping from cgcore to ckan fields
        MetaMap = namedtuple('MetaMap', ['repo', 'cgcore'])

        schema_mappings = [
            MetaMap(repo="title", cgcore="dc.title"),
            MetaMap(repo="notes", cgcore="dc.description"),
            MetaMap(repo="author", cgcore="dc.creator"),
            MetaMap(repo="publisher", cgcore="dc.publisher"),
            MetaMap(repo="", cgcore="dc.type"),  # doing this penalises the cgcore field
        ]

        # map defined fields first
        for mapping in schema_mappings:
            target_val = [x for x in description_metadata if x.get("dc", str()) == mapping.cgcore]

            if not target_val:
                continue

            target_dict = target_val[0]
            target_val = target_dict.get("vals", str())

            # remove mapped entry from list
            description_metadata.remove(target_dict)

            # can't map unspecified ckan field
            if not mapping.repo:
                continue

            if isinstance(target_val, str) and target_val.strip() != "":
                submission_metadata[mapping.repo] = target_val

            elif isinstance(target_val, list):
                value_set = False

                for idx, val in enumerate(target_val):
                    if str(val).strip() == "":
                        continue

                    if not value_set:
                        submission_metadata[mapping.repo] = str(val).strip()
                        value_set = True
                        continue

                    extra_value_key = target_dict['label'] + "[" + str(idx + 1) + "]"
                    extra_value_value = val
                    submission_metadata["extras"].append(dict(key=extra_value_key, value=extra_value_value))

        # set submission name based on title
        submission_metadata['name'] = submission_metadata['title'].replace(" ", "_").lower()

        # now map non-predefined entries
        for target_dict in description_metadata:
            target_val = target_dict['vals']

            if isinstance(target_val, str) and target_val.strip() != "":
                submission_metadata["extras"].append(dict(key=target_dict['label'], value=target_val))

            elif isinstance(target_val, list):
                for idx, val in enumerate(target_val):
                    if str(val).strip() == "":
                        continue

                    extra_value_key = target_dict['label'] + " [" + str(idx + 1) + "]"
                    extra_value_value = val
                    submission_metadata["extras"].append(dict(key=extra_value_key, value=extra_value_value))

        return submission_metadata

    def _update_and_complete_submission(self, details, sub_id):
        if details["success"] == False:
            return False
        Submission(ObjectId(sub_id)).insert_ckan_accession(sub_id, details)

        return True

    def _get_all_datasets(self):
        fullurl = self.host['url'] + "package_list?"
        resp = requests.get(fullurl)
        if resp.status_code == 200:
            return resp.content.decode('utf-8')
        else:
            return json.dumps({"status": resp.status_code, "message": "error getting datasets"})

    def dc_dict_to_dc(self, sub_id):
        # get file metadata, call converter to strip out dc fields
        s = Submission().get_record(ObjectId(sub_id))
        f_id = s["bundle"][0]
        items = CgCoreSchemas().extract_repo_fields(str(f_id), "ckan")

        Submission().update_meta(sub_id, json.dumps(items))

    def get_media_type_from_file_ext(self, ext):
        """
        function returns the mimetype matching an extension
        :param ext:
        :return:
        """
        mime_type = dict(
            pdf="application/pdf",
            ai="application/postscript",
            eps="application/postscript",
            ps="application/postscript",
            xls="application/vnd.ms-excel",
            xlsx="application/vnd.ms-excel",
            ppt="application/vnd.ms-powerpoint",
            gif="image/gif",
            jpg="image/jpeg",
            jpeg="image/jpeg",
            png="image/png",
            tif="image/tiff",
            tiff="image/tiff",
            bmp="image/x-ms-bmp",
            html="text/html",
            htm="text/html",
            asc="text/plain",
            txt="text/plain",
            xml="text/xml",
            doc="application/msword",
            docx="application/msword",
        )

        return mime_type.get(ext.lower(), str())

    def get_submitted_package_details(self, package_id):
        fullurl = urljoin(self.host["url"], "package_show?id=" + package_id)
        resp = requests.get(fullurl)
        return resp.content.decode('utf-8')

from dal.copo_da import ValidationQueue, Profile
from web.apps.web_copo.validators.tol_validators import optional_field_dtol_validators as optional_validators, taxon_validators
from web.apps.web_copo.validators.tol_validators import required_field_dtol_validators as required_validators
from web.apps.web_copo.validators.validator import Validator
import pandas
import inspect
import pickle
import math
from web.apps.web_copo.lookup import dtol_lookups as lookup
from submission.helpers.generic_helper import notify_frontend
from urllib.error import HTTPError
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype
from web.apps.web_copo.lookup import lookup as lk
import jsonpath_rw_ext as jp


class ProcessValidationQueue:

    def __init__(self):
        self.required_field_validators = list()
        self.optional_field_validators = list()
        self.taxon_field_validators = list()
        self.optional_validators = optional_validators
        self.required_validators = required_validators
        self.taxon_validators = taxon_validators
        self.symbiont_list = []
        self.validator_list = []
        self.sample_data = None
        self.profile_id = None
        self.fields = []
        self.file_name = None
        self.data = None
        self.isupdate = None
        self.type = None

    def process_validation_queue(self):
        """This method is called from celery and looks in the validationqueue collection in mongo for manifests which need validation
        once found, these are processed here"""

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

        # get all manifests queued for validation
        queued_manifests = ValidationQueue().get_queued_manifests()

        for qm in queued_manifests:
            self.sample_data = pickle.loads(qm["manifest_data"])
            self.profile_id = qm["profile_id"]
            self.file_name = qm["file_name"]
            t = Profile().get_type(self.profile_id)
            if "ASG" in t:
                self.type = "ASG"
            elif "DTOL_EI" in t:
                self.type = "DTOL_EI"
            elif "ERGA" in t:
                self.type = "ERGA"
            else:
                self.type = "DTOL"
            try:
                self.data = pandas.read_excel(self.sample_data, keep_default_na=False, na_values=lookup.NA_VALS)
            except:
                notify_frontend(data={"profile_id": self.profile_id}, msg="Failed to load manifest", action="info",
                                html_id="sample_info")
                return False

            notify_frontend(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                            html_id="sample_info")
            try:

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

            """
            TAXONOMY VALIDATION
            check if provided scientific name, TAXON ID,
            family and order are consistent with each other in known taxonomy
            """

            errors = []
            warnings = []
            flag = True
            try:
                # validate for optional dtol fields
                for v in self.taxon_field_validators:
                    errors, warnings, flag = v(profile_id=self.profile_id, fields=self.fields, data=self.data,
                                               errors=errors, warnings=warnings, flag=flag).validate()

                # send warnings
                if warnings:
                    notify_frontend(data={"profile_id": self.profile_id},
                                    msg="<br>".join(warnings),
                                    action="warning",
                                    html_id="warning_info")

                if not flag:
                    errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                    errors = "".join(errors)
                    msg = "<h4>" + self.file_name + "</h4><ol>" + errors + "</ol>"
                    notify_frontend(data={"profile_id": self.profile_id},
                                    msg=msg,
                                    action="error",
                                    html_id="sample_info")
                    ValidationQueue().set_taxon_validation_error(qm["_id"], err=msg)

                else:
                    # set validation queue taxon flag to complete
                    ValidationQueue().set_taxon_validation_complete(qm["_id"])

            except HTTPError as e:

                error_message = str(e).replace("<", "").replace(">", "")
                msg = "Service Error - The NCBI Taxonomy service may be down, please try again later."
                notify_frontend(data={"profile_id": self.profile_id},
                                msg=msg,
                                action="error",
                                html_id="sample_info")
                ValidationQueue().set_taxon_validation_error(qm["_id"], err=msg)
                return False
            except Exception as e:
                error_message = str(e).replace("<", "").replace(">", "")
                msg = "Server Error - " + error_message
                notify_frontend(data={"profile_id": self.profile_id}, msg=msg,
                                action="error",
                                html_id="sample_info")
                ValidationQueue().set_taxon_validation_error(qm["_id"], err=msg)
                return False

            """
            SCHEMA VALIDATION
            checks to make sure the manifest conforms to the TOL SOPs
            """
            flag = True
            errors = []
            warnings = []
            self.isupdate = False

            try:
                # get definitive list of mandatory DTOL fields from schema
                s = json_to_pytype(lk.WIZARD_FILES["sample_details"], compatibility_mode=False)
                self.fields = jp.match(
                    '$.properties[?(@.specifications[*] == "' + self.type.lower() + '" & @.required=="true")].versions[0]',
                    s)

                # validate for required fields
                for v in self.required_field_validators:
                    errors, warnings, flag, self.isupdate = v(profile_id=self.profile_id, fields=self.fields,
                                                              data=self.data,
                                                              errors=errors, warnings=warnings, flag=flag,
                                                              isupdate=self.isupdate).validate()

                # get list of all DTOL fields from schemas
                self.fields = jp.match(
                    '$.properties[?(@.specifications[*] == ' + self.type.lower() + ')].versions[0]', s)

                # validate for optional dtol fields
                for v in self.optional_field_validators:
                    errors, warnings, flag = v(profile_id=self.profile_id, fields=self.fields, data=self.data,
                                               errors=errors, warnings=warnings, flag=flag).validate()

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
                    msg = "<h4>" + self.file_name + "</h4><ol>" + errors + "</ol>"
                    notify_frontend(data={"profile_id": self.profile_id},
                                    msg=msg,
                                    action="error",
                                    html_id="sample_info")
                    ValidationQueue().set_schema_validation_error(qm["_id"], err=msg)
                    return False

            except Exception as e:
                error_message = str(e).replace("<", "").replace(">", "")
                msg = "Server Error - " + error_message,
                notify_frontend(data={"profile_id": self.profile_id}, msg=msg,
                                action="info",
                                html_id="sample_info")
                ValidationQueue().set_schema_validation_error(qm["_id"], err=msg)
                return False

            # if we get here we have a valid spreadsheet
            # so set validation queue taxon flag to complete
            ValidationQueue().set_schema_validation_complete(qm["_id"])
            notify_frontend(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                            html_id="sample_info")
            notify_frontend(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls")
            notify_frontend(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id="sample_info")

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
            # self.req.session["sample_data"] = sample_data
            # self.req.session["isupdate"] = self.isupdate
            # if self.isupdate:
            #    DtolSpreadsheet().detect_updates()

            # else:
            notify_frontend(data={"profile_id": self.profile_id}, msg=sample_data, action="make_table",
                            html_id="sample_table")

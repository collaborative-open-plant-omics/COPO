from dal.copo_da import ValidationQueue
from web.apps.web_copo.validators.tol_validators import optional_field_dtol_validators as optional_validators, \
    taxon_validators
from web.apps.web_copo.validators.tol_validators import required_field_dtol_validators as required_validators
from web.apps.web_copo.validators.validator import Validator
import pandas
import inspect
import pickle
from web.apps.web_copo.lookup import dtol_lookups as lookup
from submission.helpers.generic_helper import notify_frontend
from urllib.error import HTTPError


class ProcessValidationQueue:

    def __init__(self):
        self.required_field_validators = list()
        self.optional_field_validators = list()
        self.optional_field_validators = list()
        self.taxon_field_validators = list()
        self.optional_validators = optional_validators
        self.required_validators = required_validators
        self.taxon_validators = taxon_validators
        self.symbiont_list = []
        self.validator_list = []
        self.sample_data = None
        self.profile_id = None

    def process_validation_queue(self):
        # get all manifests queued for validation
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

        queued_manifests = ValidationQueue().get_queued_manifests()

        for qm in queued_manifests:
            self.sample_data = pickle.loads(qm["manifest_data"])
            self.profile_id = qm["profile_id"]
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

            # --------------------------------*TAXONOMY VALIDATION*----------------------------------#
            ''' 
            check if provided scientific name, TAXON ID,
            family and order are consistent with each other in known taxonomy
            '''

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
                    notify_frontend(data={"profile_id": self.profile_id},
                                    msg="<h4>" + self.file_name + "</h4><ol>" + errors + "</ol>",
                                    action="error",
                                    html_id="sample_info")
                    return False

                else:
                    return True

            except HTTPError as e:

                error_message = str(e).replace("<", "").replace(">", "")
                notify_frontend(data={"profile_id": self.profile_id},
                                msg="Service Error - The NCBI Taxonomy service may be down, please try again later.",
                                action="error",
                                html_id="sample_info")
                return False
            except Exception as e:
                error_message = str(e).replace("<", "").replace(">", "")
                notify_frontend(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                                action="error",
                                html_id="sample_info")
                return False

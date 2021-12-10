import inspect
import math
import os
import uuid
from os.path import join, isfile
from pathlib import Path
from shutil import rmtree
from urllib.error import HTTPError

import jsonpath_rw_ext as jp
import pandas
from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal
from exceptions_and_logging import logger
from web.apps.web_copo.lookup import dtol_lookups as lkup
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from api.utils import map_to_dict
from dal.copo_da import Sample, DataFile, Profile
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.copo_email import CopoEmail
from web.apps.web_copo.lookup import dtol_lookups as lookup
from web.apps.web_copo.lookup import lookup as lk
from web.apps.web_copo.lookup.lookup import SRA_SETTINGS
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype
from web.apps.web_copo.utils.dtol.Dtol_Helpers import query_public_name_service
from django.http import HttpResponse
from web.apps.web_copo.validators.tol_validators import optional_field_dtol_validators as optional_validators, \
    taxon_validators
from web.apps.web_copo.validators.ena_validators import ena_seq_validators as required_validators
from web.apps.web_copo.validators.validator import Validator

l = logger.Logger("exceptions_and_logging/logs")


def parse_ena_spreadsheet(request):
    # method called by rest
    file = request.FILES["file"]
    name = file.name
    ena = ENASpreadsheet(file=file)
    if name.endswith("xlsx") or name.endswith("xls"):
        fmt = 'xls'
    else:
        return HttpResponse(status=415, content="Please make sure your manifest is in xlxs format")

    if ena.loadManifest(fmt):
        l.log("Dtol manifest loaded")
        if ena.validate():
            l.log("About to collect Dtol manifest")
            ena.collect()

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
        if "ASG" in t:
            self.type = "ASG"
        elif "DTOL_EI" in t:
            self.type = "DTOL_EI"
        else:
            self.type = "DTOL"

        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.required_validators.append(element)

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

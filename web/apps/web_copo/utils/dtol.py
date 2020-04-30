# Created by fshaw at 03/04/2020
from django.http import HttpResponse
import pandas, json
from web.apps.web_copo.lookup import lookup
import jsonpath_rw_ext as jp
from submission.helpers.generic_helper import notify_sample_status
from django_tools.middlewares import ThreadLocal
from asgiref.sync import async_to_sync
import math
import time


class DtolSpreadsheet:
    # list of strings in spreadsheet to be considered NaN by Pandas....N.B. "NA" is allowed
    na_vals = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A',
               'NULL', 'NaN', 'n/a', 'nan', 'null']

    validation_msg_missing_data = "Missing data detected in column <strong>%s</strong>. All required fields must have a value. There must be no empty rows. Values of 'NA' and 'none' are allowed."

    def __init__(self, file):
        self.file = file
        req = ThreadLocal.get_current_request()
        self.profile_id = req.session.get("profile_id", None)

    def loadCsv(file):
        raise NotImplementedError

    def loadExcel(self):

        if self.profile_id is not None:
            notify_sample_status(profile_id=self.profile_id, msg="Loading..", action="info", html_id="sample_info")
            try:
                self.data = pandas.read_excel(self.file, keep_default_na=False, na_values=self.na_vals)
            except pandas.XLRDError as e:
                notify_sample_status(profile_id=self.profile_id, msg="Unable to load file.", action="info",
                                     html_id="sample_info")
                return False

    def validate(self):
        # need to load validation field set
        with open(lookup.WIZARD_FILES["sample_details"]) as json_data:
            fields = ""
            try:
                # get definitive list of DTOL fields
                s = json.load(json_data)
                fields = jp.match('$.properties[?(@.specifications[*] == "dtol" & @.required=="true")].versions', s)
                columns = list(self.data.columns)
                # check required fields are present in spreadsheet
                for item in fields:
                    notify_sample_status(profile_id=self.profile_id, msg="Checking - " + item[0],
                                         action="info",
                                         html_id="sample_info")
                    time.sleep(0.1)
                    if item[0] not in columns:
                        # invalid or missing field, inform user and return false
                        notify_sample_status(profile_id=self.profile_id, msg="Field not found - " + item[0],
                                             action="info",
                                             html_id="sample_info")
                        return False
                    # if we have a required field and it has null data
                    if self.data[item[0]].isnull().values.any():
                        # we have missing data in required cells
                        notify_sample_status(profile_id=self.profile_id,
                                             msg=(self.validation_msg_missing_data % item[0]),
                                             action="info",
                                             html_id="sample_info")
                        return False


            except:
                notify_sample_status(profile_id=self.profile_id, msg="Server Error - Try Again", action="info",
                                     html_id="sample_info")
                return False
            # if we get here we have a valid spreadsheet
            notify_sample_status(profile_id=self.profile_id, msg="Spreadsheet is Valid", action="info",
                                 html_id="sample_info")
            notify_sample_status(profile_id=self.profile_id, msg="", action="close", html_id="upload_controls")
            return True

    def parse(self):
        for index, row in self.data.iterrows():
            notify_sample_status(profile_id=self.profile_id, msg=row[3], action="info",
                                 html_id="sample_info")

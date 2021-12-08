from web.apps.web_copo.validators.validator import Validator
from dal.copo_da import Sample, Profile
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg


class ColumnValidator(Validator):
    def validate(self):
        p_type = Profile().get_type(profile_id=self.profile_id)
        columns = list(self.data.columns)
        # check required fields are present in spreadsheet
        for item in self.fields:
            notify_frontend(data={"profile_id": self.profile_id}, msg="Validating Column- " + item,
                            action="info",
                            html_id="sample_info")
            if item not in columns:
                # invalid or missing field, inform user and return false
                self.errors.append("Field not found - " + item)
                self.flag = False
                # if we have a required fields, check that there are no missing values
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class MissingValuesValidator(Validator):
    def validate(self):
        p_type = Profile().get_type(profile_id=self.profile_id)
        for header, cells in self.data.iteritems():
            # here we need to check if there are not missing values in its cells
            if header in self.fields:
                cellcount = 0
                for c in cells:
                    cellcount += 1
                    if c.strip() == "":
                        # we have missing data in required cells
                        self.errors.append(msg["validation_msg_missing_data_ena_seq"] % (
                            header, str(cellcount + 1)))
                        self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class SinglePairedValuesValidator(Validator):
    def validate(self):
        row_count = 1
        for row in self.data.iterrows():
            row_count = row_count + 1
            layout = row[1]["library_layout"]
            files = row[1]["file_name"]
            if layout == "PAIRED":
                if len(files.split(",")) != 2:
                    self.errors.append(msg["validation_msg_paired_file_error"] % (str(row_count)))
                    self.flag = False
            elif layout == "SINGLE":
                if len(files.split(",")) != 1:
                    self.errors.append(msg["validation_msg_single_file_error"] % (str(row_count)))
                    self.flag = False

        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")

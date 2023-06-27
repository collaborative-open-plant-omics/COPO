from web.apps.web_copo.validators.validator import Validator
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg
import re

#check mandatory fields are present in spreadsheet
#check mandatory fields are not empty
#check values are valid: enum, regex

 
class MandatoryValuesValidator(Validator):
    def validate(self):
        for key, field in self.checklist.fields.items():
            if field.get("mandatory","") == "Mandatory":                
                if key not in self.data.columns:
                    self.errors.append("Mandatory field " + key + " is missing")
                    self.flag = False
                else:
                    null_rows = self.data[self.data[field.get("label")].isnull()]
                    null_rows = null_rows.extend(self.data[self.data[field.get("label")] == ""])
                    null_rows = null_rows.extend(self.data[self.data[field.get("label")].isna()])
                    for row in null_rows.index:
                        if row:
                            self.errors.append(msg["validation_msg_missing_data_ena_seq"] % (
                                field.get("label"), str(row.index)))
                            self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class IncorrectValueValidator(Validator):
    def validate(self):
        for column in self.data:
            for row in self.data[column]:
                if row:
                    if column in self.checklist.fields.keys():
                        field = self.checklist.fields[column]
                        type = field.get("type","")
                        if type == "TEXT_CHOICE_FIELD":
                            if row not in field.get("choice"):
                                self.errors.append("Invalid value " + row + " in column " + column)
                                self.flag = False
                        elif type == "TEXT_FIELD":
                            regex = field.get("regex","")
                            if regex:
                                if not re.match(regex, row):
                                    self.errors.append("Invalid value " + row + " in column " + column)
                                    self.flag = False
                    else:
                        self.errors.append("Invalid column " + column)
                        self.flag = False
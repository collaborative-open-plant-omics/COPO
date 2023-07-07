from web.apps.web_copo.validators.validator import Validator
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg
from dal.copo_da import Sample 
import re

#check mandatory fields are present in spreadsheet
#check mandatory fields are not empty
#check values are valid: enum, regex

 
class MandatoryValuesValidator(Validator):
    def validate(self):
        checklist = self.kwargs.get("checklist", {})
        for key, field in checklist["fields"].items():
            if field.get("mandatory","") == "mandatory":               
                if key not in self.data.columns:
                    self.errors.append("Mandatory column: '" + field["name"] + "' is missing")
                    self.flag = False
                else:
                    null_rows=[]
                    null_rows.extend(self.data[self.data[key].isnull()].index.tolist())
                    null_rows.extend(self.data[self.data[key] == ""].index.tolist())
                    null_rows.extend(self.data[self.data[key].isna()].index.tolist())
                    for row in null_rows:
                        self.errors.append(msg["validation_msg_missing_data_ena_seq"] % (
                            field["name"], str(row + 1)))
                        self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class IncorrectValueValidator(Validator):
    def validate(self):
        checklist = self.kwargs.get("checklist", {})
        biosampleAccessions = Sample(profile_id=self.profile_id).get_all_records_columns(filter_by= {"biosampleAccession": {"$exists":True, "$ne": ""}}, projection={"biosampleAccession":1, "SPECIMEN_ID":1})
        biosampleAccessionsMap = {}
        if biosampleAccessions:
            biosampleAccessionsMap = {row["biosampleAccession"]:row["SPECIMEN_ID"] for row in biosampleAccessions} 

        for column in self.data.columns:
            if column in checklist["fields"].keys():
                field = checklist["fields"][column]
                type = field.get("type","")
                i = 1
                for row in self.data[column]:
                    i += 1
                    if row:
                        if type == "TEXT_CHOICE_FIELD":
                            if row not in field.get("choice"):
                                self.errors.append("Invalid value '" + row + "' in column : '" + field["name"] + "' at row " + str(i) + ". Valid values are: " + str(field.get("choice")))
                                self.flag = False
                        elif type == "TEXT_FIELD":
                            regex = field.get("regex","")
                            if regex:
                                if not re.match(regex, row):
                                    self.errors.append("Invalid value '" + row + "' in column : '" + field["name"] + "' at row " + str(i))
                                    self.flag = False
                        elif type == "TAXON_FIELD":
                            if row not in biosampleAccessionsMap.keys():
                                self.errors.append("Invalid value " + row + " in column:'" + field["name"] + "'")
                                self.flag = False
                            else:
                                if biosampleAccessionsMap[row] != self.data.iloc[i-2]["SPECIMEN_ID"]:
                                    self.errors.append("Invalid value " + self.data.iloc[i-2]["SPECIMEN_ID"] + " not match with " + biosampleAccessionsMap[row] + " in column: 'SPECIMEN_ID' at row " + str(i)) 
                                    self.flag = False

            else:
                self.errors.append("Invalid column : '" + column +"'")
                self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")

'''
class CheckBiosampleAccession(Validator):
    def validate(self):
        checklist = self.kwargs.get("checklist", {})

        #find biosampleAccession from SimpleCollection
        biosampleAccessions = Sample(profile_id=self.profile_id).get_all_records_columns(filter_by= {"biosampleAccession": {"$exists":True, "$ne": ""}}, projection={"biosampleAccession":1, "SPECIMEN_ID":1})
        biosampleAccessionsMap = {}
        if biosampleAccessions:
            biosampleAccessionsMap = {row["biosampleAccession"]:row["SPECIMEN_ID"] for row in biosampleAccessions} 

        for index, row in self.data.iterrows():
            if row["ORGANISM_NAME"]:
                if row["ORGANISM_NAME"] not in biosampleAccessionsMap.keys():
                    self.errors.append("Invalid value " + row["ORGANISM_NAME"] + " in column: 'Organism'")
                    self.flag = False
                else:
                    if biosampleAccessionsMap[row["ORGANISM_NAME"]] != row.get("SPECIMEN_ID",""):
                        self.errors.append("Invalid value " + row["SPECIMEN_ID"] + " not match with " + biosampleAccessionsMap[row["ORGANISM_NAME"]] + " in column: 'SPECIMEN_ID'")
                        self.flag = False

        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")
 '''   

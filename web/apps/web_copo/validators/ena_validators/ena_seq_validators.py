from web.apps.web_copo.validators.validator import Validator
from dal.copo_da import Sample, Profile
from web.apps.web_copo.schema_versions.lookup import dtol_lookups as lookup
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg
from web.apps.web_copo.utils.dtol.Dtol_Helpers import check_taxon_ena_submittable
from Bio import Entrez
import pandas as pd
from web.apps.web_copo.utils.dtol.Dtol_Helpers import validate_date


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
                    if c.strip() == "" :
                        # we have missing data in required cells
                        self.errors.append(msg["validation_msg_missing_data_ena_seq"] % (
                            header, str(cellcount + 1)))
                        self.flag = False

                    if header in lookup.DATE_FIELDS and c.strip() not in lookup.BLANK_VALS:
                        try:
                            validate_date(c)
                        except ValueError as e:
                            self.errors.append(
                                msg["validation_msg_invalid_date"] % (c, str(cellcount + 1), header))
                            self.flag = False
                        except AssertionError as e:
                            self.errors.append(
                                msg["validation_msg_future_date"] % (c, str(cellcount + 1), header)
                            )
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


class TaxonValidator(Validator):

    def validate(self):
        Entrez.api_key = lookup.NIH_API_KEY
        # build dictioanry of species in this manifest  max 200 IDs per query
        taxon_id_set = set([x for x in self.data['organism'].tolist() if x])
        notify_frontend(data={"profile_id": self.profile_id},
                        msg="Querying NCBI for TAXON_IDs in manifest ",
                        action="info",
                        html_id="sample_info")
        taxon_id_list = list(taxon_id_set)
        if any(x for x in taxon_id_list):
            for taxon in taxon_id_list:
                # check if taxon is submittable
                ena_taxon_errors = check_taxon_ena_submittable(taxon, by="binomial")
                if ena_taxon_errors:
                    self.errors += ena_taxon_errors
                    self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class GzipValidator(Validator):

    def validate(self):
        for row in self.data.iterrows():
            file_names = row[1]["file_name"]
            for f in file_names.split(","):
                if not f.strip().endswith(".gz"):
                    error_str = f + ": File not gzipped. All files must be gzipped and end in '.gz'"
                    self.errors.append(error_str)
                    self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class ReadNotInSubmissionQueueValidator(Validator):
    def validate(self):
        sample_names = list(self.data["sample_name"])
        samples = Sample(profile_id=self.profile_id).get_all_records_columns(projection=dict(read=1,name=1), filter_by=dict(profile_id=self.profile_id, name={"$in": sample_names}))
        sampleMap = {}
        for sample in samples:
            sampleMap[sample["name"]] = sample.get("read",[])
            
        for index, row in self.data.iterrows():
            file_names = row["file_name"]
            sample_name = row["sample_name"]
            reads = sampleMap.get(sample_name, None)
            if reads:
                for read in reads:
                    if set(read.get("file_name", str()).split(",")) == set(file_names.split(",")) and read.get("status","pending") == "processing":
                        self.errors.append("File " + file_names + " already in submission queue for sample " + sample_name)
                        self.flag = False 
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")
    
class DuplicatedDataFile(Validator):
    def validate(self):
        file_names = list(self.data["file_name"])
        samples = Sample(profile_id=self.profile_id).get_all_records_columns(projection={"read":1,"name":1}, filter_by=dict(profile_id=self.profile_id))
        fileMap = {}
        for sample in samples:
            for read in sample.get("read", []):
                files = read.get("file_name", str()).split(",")
                for f in files:
                    fileMap[f] = sample["name"]

        file_name_list = [ file_name  for paried_names in file_names for file_name in paried_names.split(",")]
        file = [ x for x in file_name_list if file_name_list.count(x) > 1]

        for f in set(file):
            self.errors.append("File " + f + " is duplicated in manifest")
            self.flag = False               

        for index, row in self.data.iterrows():
            file_names = row["file_name"]
            sample_name = row["sample_name"]
            files = file_names.split(",")
            for f in files:
                sample = fileMap.get(f, None)
                if sample and sample != sample_name:
                    self.errors.append(f"File {f} for sample {sample_name} already attached sample {sample}")
                    self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")

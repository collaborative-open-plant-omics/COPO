from web.apps.web_copo.validators.validator import Validator
from dal.copo_da import Sample, Profile
from django.conf import settings
# from web.apps.web_copo.lookup import dtol_lookups as lookup
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg
from web.apps.web_copo.utils.dtol.Dtol_Helpers import check_taxon_ena_submittable
from Bio import Entrez

import importlib

schema_version_path_dtol_lookups = f'web.apps.web_copo.schema_versions.{settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
lookup = importlib.import_module(schema_version_path_dtol_lookups)


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

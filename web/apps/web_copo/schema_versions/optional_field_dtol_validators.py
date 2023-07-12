from dal.copo_da import Profile, Sample
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.schema_versions.lookup import dtol_lookups as lookup
from web.apps.web_copo.utils.dtol.Dtol_Helpers import validate_date
from web.apps.web_copo.validators.validator import Validator
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg

import pandas as pd
import re
import validators


class PermitColumnsValidator(Validator):
    def check_permit_filename_value(self, permit_filename_column_name, permit_required_column_name, index, row):
        header_rules = lookup.DTOL_RULES.get(permit_filename_column_name, "")
        optional_regex = header_rules.get("optional_regex", "")
        regex_human_readable = header_rules.get("human_readable", "")

        if row.get(permit_required_column_name, "").strip() == "Y" \
                and row.get(permit_filename_column_name, "").strip().replace(" ", "_").upper() == "NOT_APPLICABLE":
            self.errors.append(msg["validation_msg_invalid_permit_filename"] % (
                row.get(permit_filename_column_name, ""), permit_filename_column_name, str(index + 1),
                regex_human_readable))
            self.flag = False

        if row.get(permit_required_column_name, "").strip() == "Y" \
                and row.get(permit_filename_column_name, "") \
                and not re.match(
            optional_regex, row.get(permit_filename_column_name, "").strip().replace(" ", "_"), re.IGNORECASE):
            self.errors.append(msg["validation_msg_invalid_permit_filename"] % (
                row.get(permit_filename_column_name, ""), permit_filename_column_name, str(index + 1),
                regex_human_readable))
            self.flag = False

        if row.get(permit_required_column_name, "").strip() == "N" and row.get(permit_filename_column_name,
                                                                               "").strip().replace(" ",
                                                                                                   "_").upper() != "NOT_APPLICABLE":
            self.errors.append(msg["validation_msg_invalid_permit_filename"] % (
                row.get(permit_filename_column_name, ""), permit_filename_column_name, str(index + 1),
                regex_human_readable))
            self.flag = False

    def check_multiple_permit_filenames_with_same_specimen_id(self, data, permit_column_prefix):
        for specimen_id, permit_filename in data.items():
            permit_filename_lst = list(permit_filename)  # Convert numpy array to list
            if len(permit_filename_lst) > 1:
                # Display an error message for each row that has the same SPECIMEN_ID but different filename
                for filename in permit_filename_lst:
                    self.errors.append(msg["validation_msg_multiple_permit_filenames_with_same_specimen_id"] % (
                        filename, f"{permit_column_prefix}_REQUIRED", f"{permit_column_prefix}_FILENAME", specimen_id))
                    self.flag = False

            # If there is only 1 filename, check if it is valid in relation to the value in the REQUIRED permit column
            if len(permit_filename_lst) == 1:
                if permit_filename_lst[0] == "N|NOT_APPLICABLE":
                    pass
                elif permit_filename_lst[0].startswith("Y|") and permit_filename_lst[0].endswith(".pdf"):
                    pass
                else:
                    self.errors.append(msg["validation_msg_multiple_permit_filenames_with_same_specimen_id"] % (
                        permit_filename_lst[0], f"{permit_column_prefix}_REQUIRED", f"{permit_column_prefix}_FILENAME",
                        specimen_id))
                    self.flag = False

    def validate(self):
        p_type = Profile().get_type(profile_id=self.profile_id)

        # Only ERGA manifests have permit files
        if "ERGA" in p_type:
            permit_filename_column_names = lookup.PERMIT_FILENAME_COLUMN_NAMES
            permit_required_column_names = lookup.PERMIT_REQUIRED_COLUMN_NAMES
            permit_column_names = lookup.PERMIT_COLUMN_NAMES_PREFIX

            # Check if permit file name is valid
            for index, row in self.data.iterrows():
                for i, item in enumerate(permit_filename_column_names):
                    self.check_permit_filename_value(item, permit_required_column_names[i], index, row)

            # Check if more than 1 specimenID is the same and check if the permit file name is also the same
            for prefix in permit_column_names:
                # Create a new column that combines the permit column name prefix with "_REQUIRED" and
                # "_FILENAME" columns each
                self.data[f"{prefix}"] = self.data[f"{prefix}_REQUIRED"] + "|" + self.data[f"{prefix}_FILENAME"]

                # Group the data by SPECIMEN_ID and combine the values in the new column into a numpy array
                result = self.data.groupby('SPECIMEN_ID')[f"{prefix}"].unique()

                self.check_multiple_permit_filenames_with_same_specimen_id(result, prefix)
                # Drop the column created
                self.data.drop(columns=[f"{prefix}"], inplace=True)

        return self.errors, self.warnings, self.flag


class DtolEnumerationValidator(Validator):

    def validate(self):
        whole_used_specimens = set()
        manifest_specimen_taxon_pairs = {}
        regex_human_readable = ""
        flag_symbiont = False
        p_type = Profile().get_type(profile_id=self.profile_id)
        if "ERGA" in p_type:
            p_type = "ERGA"
        elif "DTOL_ENV" in p_type:
            p_type = "DTOL_ENV"
        elif "DTOL" in p_type:
            p_type = "DTOL"
        elif "ASG" in p_type:
            p_type = "ASG"
        barcoding_fields = ["PLATE_ID_FOR_BARCODING", "TUBE_OR_WELL_ID_FOR_BARCODING",
                            "TISSUE_FOR_BARCODING", "BARCODE_PLATE_PRESERVATIVE"]
        # erga manifest doesn't have plate_id_for_barcoding
        if p_type == "ERGA":
            barcoding_fields.pop(0)
        for header, cells in self.data.iteritems():

            notify_frontend(data={"profile_id": self.profile_id}, msg="Validating Header- " + header,
                            action="info",
                            html_id="sample_info")
            if header in self.fields:

                # check if there is an enum for this header specific to the project
                lookup_entry = lookup.DTOL_ENUMS.get(header, "")
                if type(lookup_entry) is dict:
                    allowed_vals = lookup_entry.get(p_type, "")
                else:
                    # check if there is a general enum for this header, else ""
                    allowed_vals = lookup_entry

                # check if there's a regex rule for the header and exceptional handling
                header_rules = lookup.DTOL_RULES.get(f'{header}_{p_type}', "")

                # Check if header does not contain the profile type at the end
                if not header_rules:
                    header_rules = lookup.DTOL_RULES.get(header, "")

                # Check if header contains the profile type at the end
                if header_rules:
                    # control for when ENA regex is too permissive
                    if header_rules.get("strict_regex", ""):
                        regex_rule = header_rules.get("strict_regex", "")
                    else:
                        regex_rule = header_rules.get("ena_regex", "")

                    regex_human_readable = header_rules.get("human_readable", "")
                    optional_regex = header_rules.get("optional_regex", "")
                else:
                    regex_rule = ""
                    optional_regex = ""
                cellcount = 0
                for c in cells:
                    cellcount += 1

                    c_value = c

                    # reformat time of collection to handle excel format
                    if header == "TIME_OF_COLLECTION":
                        csplit = c.split(":")
                        if len(csplit) == 3 and csplit[2] == "00":
                            c = ":".join(csplit[0:2])
                            self.data.at[cellcount - 1, "TIME_OF_COLLECTION"] = c

                    if allowed_vals:
                        # extra handling of barcode hubs for ASG
                        # todo move this in lookups and re-structure, this is in interest of time
                        if header == "BARCODE_HUB" and "ASG" in p_type:
                            allowed_vals = lookup.DTOL_ENUMS.get("PARTNER", "") + ["NOT_PROVIDED"]
                        if header == "COLLECTION_LOCATION" or header == "ORIGINAL_FIELD_COLLECTION_LOCATION":
                            # special check for COLLETION_LOCATION as this needs invalid list error for feedback
                            c_value = str(c).split('|')[0].strip()
                            location_2part = str(c).split('|')[1:]
                            if c_value.upper() not in allowed_vals or not location_2part:
                                self.errors.append(msg["validation_msg_invalid_list"] % (
                                    c_value, header, str(cellcount + 1)))
                                self.flag = False
                        elif header == "ORGANISM_PART":
                            # special check for piped values
                            for part in str(c).split('|'):
                                if part.strip() not in allowed_vals:
                                    self.errors.append(msg["validation_msg_invalid_data"] % (
                                        part, header, str(cellcount + 1), allowed_vals
                                    ))
                                    self.flag = False
                        elif c_value.strip() not in allowed_vals:
                            # extra handling for empty SYMBIONT ind DTOL and ERGA manifest, which means TARGET
                            if not c_value.strip() and header == "SYMBIONT" and any(
                                    x in p_type for x in ["DTOL", "ERGA"]):
                                self.data.at[cellcount - 1, "SYMBIONT"] = "TARGET"
                            # check value is in allowed enum
                            else:
                                self.errors.append(msg["validation_msg_invalid_data"] % (
                                    c_value, header, str(cellcount + 1), allowed_vals))
                                self.flag = False
                        if header == "ORGANISM_PART" and c_value.strip() == "WHOLE_ORGANISM":
                            # send specimen in used whole specimens set
                            current_specimen = self.data.at[cellcount - 1, "SPECIMEN_ID"]
                            if current_specimen in whole_used_specimens:
                                self.errors.append(msg["validation_msg_used_whole_organism"] % current_specimen)
                                self.flag = False
                            else:
                                whole_used_specimens.add(current_specimen)
                    if regex_rule:
                        # handle any regular expressions provided for validation
                        if c and not re.match(regex_rule, c.replace("_", " "), re.IGNORECASE):
                            self.errors.append(msg["validation_msg_invalid_data"] % (
                                c, header, str(cellcount + 1), regex_human_readable))
                            self.flag = False
                    if optional_regex:
                        # handle regular expression that will only trigger a warning exclude ERGA from this warning
                        # ignore if 'NOT_APPLICABLE' is set as a value for the PERMIT_FILENAME_COLUMN_NAMES
                        # for ERGA manifests
                        if c and not re.match(optional_regex, c.replace("_", " "), re.IGNORECASE) \
                                and header not in lookup.PERMIT_FILENAME_COLUMN_NAMES:
                            if header in ['RACK_OR_PLATE_ID', 'TUBE_OR_WELL_ID'] and p_type == "ERGA":
                                self.warnings.append(msg["validation_msg_warning_racktube_format"] % (
                                    c, header, str(cellcount + 1)))
                            else:  # not in use atm, here in case we add more optional validations
                                self.warnings.append(msg["validation_msg_warning_racktube_format"] % (
                                    c, header, str(cellcount + 1)))

                    # validate link fields
                    if header.endswith('_LINK') or header == "VOUCHER_INSTITUTION":
                        if c.strip() and not validators.url(c.strip()):
                            self.errors.append(msg["validation_msg_invalid_link"] % (
                                c, header, str(cellcount + 1)
                            ))
                            self.flag = False

                    # validation checks for SERIES
                    if header == "SERIES":
                        try:
                            int(c)
                        except ValueError:
                            self.errors.append(msg["validation_msg_invalid_data"] % (
                                c, header, str(cellcount + 1), "integers"))
                            self.flag = False
                    elif header == "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION":
                        # check this is either a NOT_* or an integer
                        if c_value.strip() not in lookup.BLANK_VALS:
                            try:
                                float(c_value)
                            except ValueError:
                                self.errors.append(msg["validation_msg_invalid_data"] % (
                                    c_value, header, str(cellcount + 1),
                                    "integer or " + ", ".join(lookup.BLANK_VALS)
                                ))
                                self.flag = False
                    # check SPECIMEN_ID has the right prefix
                    elif header == "SPECIMEN_ID":
                        # both DTOL and DTOL_ENV
                        if "DTOL" in p_type:
                            current_gal = self.data.at[cellcount - 1, "GAL"]
                            specimen_regex = re.compile(lookup.SPECIMEN_PREFIX["GAL"][p_type.lower()].get(current_gal,
                                                                                                          "") +
                                                        lookup.SPECIMEN_SUFFIX["GAL"][p_type.lower()].get(current_gal,
                                                                                                          ''))
                            if not re.match(specimen_regex, c.strip()):
                                self.errors.append(msg["validation_msg_error_specimen_regex_dtol"] % (
                                    c, header, str(cellcount + 1), "GAL", current_gal,
                                    lookup.SPECIMEN_PREFIX["GAL"][p_type.lower()].get(current_gal, "XXX"),
                                    lookup.SPECIMEN_SUFFIX["GAL"][p_type.lower()].get(current_gal, "XXX")
                                ))
                                self.flag = False
                        elif "ERGA" in p_type:
                            specimen_regex = re.compile(lookup.SPECIMEN_PREFIX["GAL"][p_type.lower()].get("default",
                                                                                                          "") +
                                                        lookup.SPECIMEN_SUFFIX["GAL"][p_type.lower()].get("default",
                                                                                                          ''))
                            if not re.match(specimen_regex, c.strip()):
                                self.errors.append(msg["validation_msg_error_specimen_regex_dtol"] % (
                                    c, header, str(cellcount + 1), "GAL", "XXX",
                                    lookup.SPECIMEN_PREFIX["GAL"][p_type.lower()].get("default", "XXX"),
                                    lookup.SPECIMEN_SUFFIX["GAL"][p_type.lower()].get("default", "XXX")
                                ))
                                self.flag = False
                        elif "ASG" in p_type:
                            current_partner = self.data.at[cellcount - 1, "PARTNER"]
                            specimen_regex = re.compile(
                                lookup.SPECIMEN_PREFIX["PARTNER"].get(current_partner, "") + '\d{7}')
                            if not re.match(specimen_regex, c.strip()):
                                self.errors.append(msg["validation_msg_error_specimen_regex"] % (
                                    c, header, str(cellcount + 1), "PARTNER", current_partner,
                                    lookup.SPECIMEN_PREFIX["PARTNER"].get(current_partner, "XXX")
                                ))
                                self.flag = False
                        # only do this if this is target
                        if self.data.at[cellcount - 1, "SYMBIONT"].strip().upper() != "SYMBIONT":
                            # check if SPECIMEN_ID in db, if it is check it refers to the same TAXON_ID if target
                            existing_samples = Sample().get_target_by_specimen_id(c.strip())
                            if existing_samples:
                                for exsam in existing_samples:
                                    if exsam["species_list"][0]["TAXON_ID"] != self.data.at[cellcount - 1, "TAXON_ID"]:
                                        self.errors.append(msg["validation_message_wrong_specimen_taxon_pair"] % (
                                            str(cellcount + 1), c.strip(), exsam["species_list"][0]["TAXON_ID"]
                                        ))
                                        self.flag = False
                                        break
                            # check the same in spreadsheet
                            if c.strip() in manifest_specimen_taxon_pairs:
                                if manifest_specimen_taxon_pairs[c.strip()] != self.data.at[cellcount - 1, "TAXON_ID"]:
                                    self.errors.append(msg["validation_message_wrong_specimen_taxon_pair"] % (
                                        str(cellcount + 1), c.strip(), manifest_specimen_taxon_pairs[c.strip()] +
                                        " in this manifest"
                                    ))
                                    self.flag = False
                            else:
                                manifest_specimen_taxon_pairs[c.strip()] = self.data.at[cellcount - 1, "TAXON_ID"]
                        else:
                            flag_symbiont = True

                    # if TISSUE_REMOVED_FOR_BARCODING is not YES, the barcoding columns will be overwritten
                    elif header == "TISSUE_REMOVED_FOR_BARCODING" and c.strip() != "Y":
                        barcoding_flag = True
                        for barfield in barcoding_fields:
                            if self.data.at[cellcount - 1, barfield] != "NOT_APPLICABLE":
                                self.data.at[cellcount - 1, barfield] = "NOT_APPLICABLE"
                                barcoding_flag = False
                        if barcoding_flag == False:
                            self.warnings.append(msg["validation_msg_warning_barcoding"] % (
                                str(cellcount + 1), c
                            ))
                    # if tissue removed for biobanking warning that voucher should be present
                    elif header == "TISSUE_REMOVED_FOR_BIOBANKING" and c.strip() == "Y":
                        if self.data.at[cellcount - 1, "TISSUE_VOUCHER_ID_FOR_BIOBANKING"].strip() in lookup.BLANK_VALS:
                            self.warnings.append(msg["validation_msg_warning_na_value_voucher"] % (
                                self.data.at[cellcount - 1, "TISSUE_VOUCHER_ID_FOR_BIOBANKING"].strip(),
                                "TISSUE_VOUCHER_ID_FOR_BIOBANKING", str(cellcount + 1),
                                "TISSUE_VOUCHER_ID_FOR_BIOBANKING"
                            ))
                    # if dna removed for biobanking warning that voucher should be present
                    elif header == "DNA_REMOVED_FOR_BIOBANKING" and c.strip() == "Y":
                        if self.data.at[cellcount - 1, "DNA_VOUCHER_ID_FOR_BIOBANKING"].strip() in lookup.BLANK_VALS:
                            self.warnings.append(msg["validation_msg_warning_na_value_voucher"] % (
                                self.data.at[cellcount - 1, "DNA_VOUCHER_ID_FOR_BIOBANKING"].strip(),
                                "DNA_VOUCHER_ID_FOR_BIOBANKING", str(cellcount + 1), "DNA_VOUCHER_ID_FOR_BIOBANKING"
                            ))
                    # if original collection date is provided so must be the orginal geographic collection
                    elif header == "ORIGINAL_COLLECTION_DATE" and c.strip():
                        if not self.data.at[cellcount - 1, "ORIGINAL_GEOGRAPHIC_LOCATION"]:
                            self.errors.append(msg["validation_msg_original_field_missing"] % (
                                str(cellcount + 1)
                            ))
                            self.flag = False
                    # validation checks for date types
                    if header in lookup.DATE_FIELDS and c_value.strip() not in lookup.BLANK_VALS:
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
        if flag_symbiont:
            self.warnings.insert(0, msg["validation_msg_overwrite_symbionts"])
        return self.errors, self.warnings, self.flag

import re

from dal.copo_da import Profile, Sample
from submission.helpers.generic_helper import notify_dtol_status
from web.apps.web_copo.lookup import dtol_lookups as lookup
from web.apps.web_copo.utils.dtol.Dtol_Helpers import validate_date
from .tol_validator import TolValidtor
from .validation_messages import MESSAGES as msg


class DtolEnumerationValidator(TolValidtor):

    def validate(self):
        whole_used_specimens = set()
        manifest_specimen_taxon_pairs = {}
        regex_human_readable = ""
        p_type = Profile().get_type(profile_id=self.profile_id)
        barcoding_fields = ["PLATE_ID_FOR_BARCODING", "TUBE_OR_WELL_ID_FOR_BARCODING",
                            "TISSUE_FOR_BARCODING", "BARCODE_PLATE_PRESERVATIVE"]
        for header, cells in self.data.iteritems():

            notify_dtol_status(data={"profile_id": self.profile_id}, msg="Validating Header- " + header,
                               action="info",
                               html_id="sample_info")
            if header in self.fields:

                # check if there is an enum for this header
                allowed_vals = lookup.DTOL_ENUMS.get(header, "")

                # check if there's a regex rule for the header and exceptional handling
                if lookup.DTOL_RULES.get(header, ""):
                    # control for when ENA regex is too permissive
                    if lookup.DTOL_RULES[header].get("strict_regex", ""):
                        regex_rule = lookup.DTOL_RULES[header].get("strict_regex", "")
                    else:
                        regex_rule = lookup.DTOL_RULES[header].get("ena_regex", "")
                    regex_human_readable = lookup.DTOL_RULES[header].get("human_readable", "")
                    optional_regex = lookup.DTOL_RULES[header].get("optional_regex", "")
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
                        if header == "COLLECTION_LOCATION" or header=="ORIGINAL_FIELD_COLLECTION_LOCATION":
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
                            #extra handling for empty SYMBIONT ind DTOL manifest, which means TARGET
                            if not c_value.strip() and header == "SYMBIONT" and "DTOL" in p_type:
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
                        # handle regular expression that will only trigger a warning
                        if c and not re.match(optional_regex, c.replace("_", " "), re.IGNORECASE):
                            if header in ['RACK_OR_PLATE_ID', 'TUBE_OR_WELL_ID']:
                                self.warnings.append(msg["validation_msg_warning_racktube_format"] % (
                                    c, header, str(cellcount + 1)))
                            else:  # not in use atm, here in case we add more optional validations
                                self.warnings.append(msg["validation_msg_warning_racktube_format"] % (
                                    c, header, str(cellcount + 1)))

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
                        if c_value.strip() not in lookup.blank_vals:
                            try:
                                float(c_value)
                            except ValueError:
                                self.errors.append(msg["validation_msg_invalid_data"] % (
                                    c_value, header, str(cellcount + 1),
                                    "integer or " + ", ".join(lookup.blank_vals)
                                ))
                                self.flag = False
                    #check SPECIMEN_ID has the right prefix
                    elif header == "SPECIMEN_ID":
                        if "DTOL" in p_type:
                            current_gal = self.data.at[cellcount - 1, "GAL"]
                            specimen_regex = re.compile(lookup.SPECIMEN_PREFIX["GAL"].get(current_gal,
                                                                                              "") + '[\d\-_]')
                            if not re.match(specimen_regex, c.strip()):
                                self.errors.append(msg["validation_msg_error_specimen_regex_dtol"] % (
                                    c, header, str(cellcount + 1), "GAL", current_gal,
                                    lookup.SPECIMEN_PREFIX["GAL"].get(current_gal, "XXX"),
                                        lookup.SPECIMEN_SUFFIX["GAL"].get(current_gal, "XXX")
                                ))
                                self.flag = False
                        elif "ASG" in p_type:
                            current_partner = self.data.at[cellcount - 1, "PARTNER"]
                            specimen_regex = re.compile(lookup.SPECIMEN_PREFIX["PARTNER"].get(current_partner, "") + '\d{7}')
                            if not re.match(specimen_regex, c.strip()):
                                self.errors.append(msg["validation_msg_error_specimen_regex"] % (
                                    c, header, str(cellcount + 1), "PARTNER", current_partner,
                                    lookup.SPECIMEN_PREFIX["PARTNER"].get(current_partner, "XXX")
                                ))
                                self.flag = False
                    #only do this if this is target
                            if self.data.at[cellcount - 1, "SYMBIONT"].strip().upper() != "SYMBIONT":
                                #check if SPECIMEN_ID in db, if it is check it refers to the same TAXON_ID if target
                                existing_samples = Sample().get_target_by_specimen_id(c.strip())
                                if existing_samples:
                                    for exsam in existing_samples:
                                        if exsam["species_list"][0]["TAXON_ID"] != self.data.at[cellcount -1, "TAXON_ID"]:
                                            self.errors.append(msg["validation_message_wrong_specimen_taxon_pair"] % (
                                                str(cellcount + 1), c.strip(), exsam["species_list"][0]["TAXON_ID"]
                                            ))
                                            self.flag = False
                                            break
                                #check the same in spreadsheet
                                if c.strip() in manifest_specimen_taxon_pairs:
                                    if manifest_specimen_taxon_pairs[c.strip()] != self.data.at[cellcount -1, "TAXON_ID"]:
                                        self.errors.append(msg["validation_message_wrong_specimen_taxon_pair"] % (
                                                str(cellcount + 1), c.strip(), manifest_specimen_taxon_pairs[c.strip()]+
                                                " in this manifest"
                                            ))
                                        self.flag = False
                                else:
                                    manifest_specimen_taxon_pairs[c.strip()] = self.data.at[cellcount -1, "TAXON_ID"]

                        #if TISSUE_REMOVED_FOR_BARCODING is not YES, the barcoding columns will be overwritten
                    elif header == "TISSUE_REMOVED_FOR_BARCODING" and c.strip() != "Y":
                        barcoding_flag = True
                        for barfield in barcoding_fields:
                            if self.data.at[cellcount-1, barfield] != "NOT_APPLICABLE":
                                self.data.at[cellcount - 1, barfield] = "NOT_APPLICABLE"
                                barcoding_flag = False
                        if barcoding_flag == False:
                            self.warnings.append(msg["validation_msg_warning_barcoding"] % (
                                str(cellcount+1), c
                            ))
                    #if original collection date is provided so must be the orginal geographic collection
                    elif header == "ORIGINAL_COLLECTION_DATE" and c.strip():
                        if not self.data.at[cellcount-1, "ORIGINAL_GEOGRAPHIC_LOCATION"]:
                            self.errors.append(msg["validation_msg_original_field_missing"] % (
                                str(cellcount+1)
                            ))
                            self.flag = False
                    # validation checks for date types
                    if header in lookup.date_fields and c_value.strip() not in lookup.blank_vals:
                        try:
                            validate_date(c)
                        except ValueError as e:
                            self.errors.append(
                                msg["validation_msg_invalid_date"] % (c, str(cellcount + 1), header))
                            self.flag = False
        return self.errors, self.warnings, self.flag

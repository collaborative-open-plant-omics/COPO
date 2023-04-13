from dal.copo_da import Sample, Profile
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.validators.validator import Validator
from web.apps.web_copo.validators.validation_messages import MESSAGES as msg
from collections import Counter

blank_vals = ["NOT_COLLECTED", "NOT_PROVIDED", "NOT_APPLICABLE"]


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


class CellMissingDataValidator(Validator):
    def validate(self):
        p_type = Profile().get_type(profile_id=self.profile_id)
        for header, cells in self.data.iteritems():
            # here we need to check if there are not missing values in its cells
            if header in self.fields:
                if header == "SYMBIONT" and "DTOL" in p_type:
                    # dtol manifests are allowed to have blank field in SYMBIONT
                    pass
                else:
                    cellcount = 0
                    for c in cells:
                        cellcount += 1
                        if not c.strip():
                            # we have missing data in required cells
                            if header == "SYMBIONT":
                                self.errors.append(msg["validation_msg_missing_symbiont"] % (
                                    header, str(cellcount + 1), "TARGET and SYMBIONT"))
                            else:
                                self.errors.append(msg["validation_msg_missing_data"] % (
                                    header, str(cellcount + 1), blank_vals))
                            self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class RackTubeNotNullValidator(Validator):
    def validate(self):
        for index, row in self.data.iterrows():
            if row.get("RACK_OR_PLATE_ID", "") in blank_vals and row["TUBE_OR_WELL_ID"] in blank_vals:
                self.errors.append(msg["validation_msg_rack_tube_both_na"] % (str(index + 1)))
                self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class OrphanedSymbiontValidator(Validator):
    def validate(self):
        # check that if sample is a symbiont, there is a target with matching RACK_OR_PLATE_ID and TUBE_OR_WELL_ID
        syms = self.data.loc[(self.data["SYMBIONT"] == "SYMBIONT")]
        tid = syms["TUBE_OR_WELL_ID"]
        for el in list(tid):
            target = self.data.loc[(self.data["SYMBIONT"] == "TARGET") & (self.data["TUBE_OR_WELL_ID"] == el)]
            if len(target) == 0:
                self.errors.append(msg["validation_msg_orphaned_symbiont"] % el)
                self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class RackPlateUniquenessValidator(Validator):
    def validate(self):
        # check for uniqueness of RACK_OR_PLATE_ID and TUBE_OR_WELL_ID in this manifest
        rack_tube = self.data.get("RACK_OR_PLATE_ID", "") + "/" + self.data["TUBE_OR_WELL_ID"]
        # now check for uniqueness across all Samples
        p_type = Profile().get_type(profile_id=self.profile_id)
        dup = Sample().check_dtol_unique(rack_tube)
        # duplicated returns a boolean array, false for not duplicate, true for duplicate
        u = list(rack_tube[rack_tube.duplicated()])

        if len(dup) > 0:
            # errors = list(map(lambda x: "<li>" + x + "</li>", errors))
            err = list(map(lambda x: x.get("RACK_OR_PLATE_ID", "") + "/" + x["TUBE_OR_WELL_ID"], dup))


            #check if rack_tube present we are in the same profile
            existingsam = Sample().get_by_field("rack_tube", err) #[str(rack_tube[0])])
            for exsam in existingsam:
                if exsam["profile_id"] == self.profile_id:
                    # todo check SYMBIONT value in species list is the same too
                    # check accessions do not exist yet and status is pending
                    if not exsam["biosampleAccession"]:
                        if "ERGA" in p_type and exsam["status"] in ["pending", "rejected"]:
                            self.warnings.append(msg["validation_msg_isupdate"] % exsam["rack_tube"])
                            self.kwargs["isupdate"] = True
                        elif exsam["status"] == "pending":
                            self.warnings.append(msg["validation_msg_isupdate"] % exsam["rack_tube"])
                            self.kwargs["isupdate"] = True
                    else:     #allow for update after approval in the same profile
                         self.kwargs["isupdate"] = True
                         self.warnings.append(msg["validation_msg_warning_update_submitted_sample"] % (
                                    exsam["rack_tube"], exsam["biosampleAccession"]))
                    #    #rack_tube has already been approved by sample manager and can't be updated any more
                    #    self.errors.append(msg["validation_msg_duplicate_tube_or_well_id_in_copo"] % (err))
                    #    self.flag = False
                else:
                    #rack_tube exist in another profile, can't be updated
                    self.errors.append(msg["validation_msg_duplicate_tube_or_well_id_in_copo"] % exsam["rack_tube"])
                    self.flag = False

        # duplicates are allowed for asg (and possibily dtol) but one element of duplicate set must have one
        # and only one target in
        # sybiont fields
        for i in u:
            rack, tube = i.split('/')
            rows = self.data.loc[
                (self.data.get("RACK_OR_PLATE_ID", "") == rack) & (self.data["TUBE_OR_WELL_ID"] == tube)]
            counts = Counter([x.upper() for x in list(rows["SYMBIONT"].values)])
            if "TARGET" not in counts:
                self.errors.append(msg["validation_msg_duplicate_without_target"] % (
                    str(rows.get("RACK_OR_PLATE_ID", "") + "/" + rows["TUBE_OR_WELL_ID"])))
                self.flag = False
            if counts["TARGET"] > 1:
                self.errors.append(msg["validation_msg_multiple_targets_with_same_id"] % (i))
                self.flag = False
            # TODO this can go at version 2.3 of DTOL
            if counts["TARGET"] + counts["SYMBIONT"] < len(list(rows["SYMBIONT"].values)):
                self.errors.append(msg["validation_msg_multiple_targets_with_same_id"] % (i))
                self.flag = False
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")


class DecimalLatitudeLongitudeValidator(Validator):
    def validate(self):
        """
            Check if sample has an ERGA manifest type and validate the fields - DECIMAL_LATITUDE, DECIMAL_LONGITUDE,
            LATITUDE_START, LATITUDE_END, LONGITUDE_START and LONGITUDE_END based on the following scenarios:

            1) If any of the aforementioned fields is empty, then the valdiation should fail
               because if there is no value, 'NOT_COLLECTED' should be the value

            2) All of the aforementioned fields cannot be 'NOT_COLLECTED'. The validation should fail if that occurs.

            3) If LATITUDE_START, LATITUDE_END, LONGITUDE_START and LONGITUDE_END have a decimal value then,
               DECIMAL_LATITUDE and DECIMAL_LONGITUDE must have the value 'NOT_COLLECTED'

            4) If DECIMAL_LATITUDE and DECIMAL_LONGITUDE have a decimal value then, LATITUDE_START, LATITUDE_END,
               LONGITUDE_START and LONGITUDE_END must have the value 'NOT_COLLECTED'
        """

        p_type = Profile().get_type(profile_id=self.profile_id)

        if "ERGA" in p_type:
            for index, row in self.data.iterrows():
                decimal_latlong_lst = [row.get("DECIMAL_LATITUDE", ""), row.get("DECIMAL_LONGITUDE", "")]
                latlong_start_end_lst = [row.get("LATITUDE_START", ""), row.get("LATITUDE_END", ""),
                                         row.get("LONGITUDE_START", ""), row.get("LONGITUDE_END", "")]

                if any(i == "" for i in decimal_latlong_lst) or any(i == "" for i in latlong_start_end_lst):
                    self.errors.append(
                        msg["validation_msg_error_decimal_latlong_or_latlong_start_end_missing_value"] % str(index + 2))
                    self.flag = False

                elif any(i == "NOT_COLLECTED" for i in decimal_latlong_lst) and any(
                        i != "NOT_COLLECTED" for i in decimal_latlong_lst) or any(
                    i == "NOT_COLLECTED" for i in latlong_start_end_lst) and any(
                    i != "NOT_COLLECTED" for i in latlong_start_end_lst):
                    self.errors.append(
                        msg["validation_msg_error_decimal_latlong_or_latlong_start_end_mixed_value"] % str(index + 2))
                    self.flag = False

                elif all(i == "NOT_COLLECTED" for i in decimal_latlong_lst) and all(
                        i == "NOT_COLLECTED" for i in latlong_start_end_lst):
                    self.errors.append(
                        msg["validation_msg_error_decimal_latlong_or_latlong_start_end_all_not_collected"] % str(
                            index + 2))
                    self.flag = False


                elif all(i == "NOT_COLLECTED" for i in decimal_latlong_lst) and any(
                        i == "NOT_COLLECTED" for i in latlong_start_end_lst):
                    self.errors.append(
                        msg["validation_msg_error_decimal_latlong_or_latlong_start_end_missing_start_end"] % str(
                            index + 2))
                    self.flag = False


                elif all(i == "NOT_COLLECTED" for i in latlong_start_end_lst) and any(
                        i == "NOT_COLLECTED" for i in decimal_latlong_lst):
                    self.errors.append(
                        msg["validation_msg_error_decimal_latlong_or_latlong_start_end_missing_decimal_latlong"] % str(
                            index + 2))
                    self.flag = False


                elif any(i == "NOT_COLLECTED" for i in decimal_latlong_lst) and any(
                        i == "NOT_COLLECTED" for i in latlong_start_end_lst):
                    self.errors.append(msg[
                                           "validation_msg_error_decimal_latlong_or_latlong_start_end_not_collected_mixed_value"] % str(
                        index + 2))
                    self.flag = False

                elif all(i != "NOT_COLLECTED" for i in decimal_latlong_lst) and all(
                        i != "NOT_COLLECTED" for i in latlong_start_end_lst):
                    self.errors.append(
                        msg["validation_msg_error_decimal_latlong_or_latlong_start_end_all_contains_a_value"] % str(
                            index + 2))
                    self.flag = False

                else:
                    print('success')

        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")

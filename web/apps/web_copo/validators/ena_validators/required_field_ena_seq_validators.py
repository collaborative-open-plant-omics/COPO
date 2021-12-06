from web.apps.web_copo.validators.validator import Validator
from dal.copo_da import Sample, Profile


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
                # TODO remove once all 2.2 manifests are gone!!!!
                if item == "BARCODE_HUB":
                    self.data["BARCODE_HUB"] = ["NOT_PROVIDED" for x in range(self.data.shape[0])]
                    continue
                # invalid or missing field, inform user and return false
                self.errors.append("Field not found - " + item)
                self.flag = False
                # if we have a required fields, check that there are no missing values
        return self.errors, self.warnings, self.flag, self.kwargs.get("isupdate")

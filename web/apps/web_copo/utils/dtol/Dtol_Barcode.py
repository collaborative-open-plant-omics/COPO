import uuid
import xml.etree.ElementTree as ET
import requests
import pandas
import xmljson
from django_tools.middlewares import ThreadLocal
from collections import OrderedDict
from dal.copo_da import Sample
from submission.helpers.generic_helper import notify_dtol_status
from .tol_validators.validation_messages import MESSAGES as msg


class Barcoding:

    def __init__(self, file):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        self.file = file
        self.data = None
        self.name = self.file.name

    def load_manifest(self):
        if self.name.endswith("xlsx") or self.name.endswith("xls"):
            self.data = pandas.read_excel(self.file)
        elif self.name.endswith("csv"):
            self.data = pandas.read_csv(self.file)
        flag = True
        required_columns = ["SPECIMEN_ID", "BOLD_ID"]
        actual_columns = list(self.data.columns)
        for r in required_columns:
            if r not in actual_columns:
                notify_dtol_status(data={"profile_id": self.profile_id}, msg="Error - column not found: " + str(r),
                                   action="error",
                                   html_id="barcode_notify")
                flag = False
        return flag

    def check_specimen_ids(self):
        # method to check if specimen ids already exist in COPO, i.e. has manifest been uploaded and accepted
        # these specimen ids will be used for matching to barcoding information
        flag = True
        errors = []

        for ids in self.data["SPECIMEN_ID"]:
            for s_id in ids.split(","):
                s_id = s_id.strip()
                notify_dtol_status(data={"profile_id": self.profile_id}, msg="Checking for specimen" + s_id,
                                   action="info",
                                   html_id="barcode_notify")
                num = Sample().count_samples_by_specimen_id_for_barcoding(s_id)
                if int(num) < 1:
                    flag = False
                    errors.append(msg["barcode_msg_missing_specimen"] % (s_id))

        # if flag is false, compile list of errors
        if not flag:
            errors = list(map(lambda x: "<li>" + x + "</li>", errors))
            errors = "".join(errors)

            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                               action="error",
                               html_id="barcode_notify")
            return False
        return flag

    def query_bold_and_store_in_session(self):

        notify_dtol_status(data={"profile_id": self.profile_id}, msg="Querying Bold...",
                           action="info",
                           html_id="barcode_notify")
        bold_ids = self.data["BOLD_ID"]
        bold_url_param = ""
        for bid in bold_ids:
            # concatenate bold ids
            bold_url_param = bold_url_param + bid + '|'
        url = "http://www.boldsystems.org/index.php/API_Public/combined?ids=" + bold_url_param
        bold_xml = requests.get(url)
        resp = bold_xml.content
        try:
            xml = ET.fromstring(resp)
            # with open('/home/fshaw/Downloads/bold_data.xml') as f:
            #    xml = ET.fromstring(f.read())
            d = xmljson.parker.data(xml)["record"]
            x = list()
            if type(d) == OrderedDict:
                x.append(d)
                d = x
            output = list()
            full_records = list()

            for record in d:
                r = dict()
                full_records.append(record)
                r["bold_sample_id"] = record["specimen_identifiers"]["sampleid"]

                # properly associate bold_ids from returned results, with specimen_ids from the barcoding manifest
                # this step is becuase bold api does not return results in order
                row = self.data.loc[self.data["BOLD_ID"] == r["bold_sample_id"]]
                r["specimen_id"] = row["SPECIMEN_ID"].to_string(index=False)

                # phylum
                taxid = record.get("taxonomy", dict()).get("phylum", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("phylum", dict()).get("taxon", dict()).get("name", "")
                r["phylum"] = {"taxid": taxid, "name": name}
                # class
                taxid = record.get("taxonomy", dict()).get("class", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("class", dict()).get("taxon", dict()).get("name", "")
                r["class"] = {"taxid": taxid, "name": name}
                # order
                taxid = record.get("taxonomy", dict()).get("order", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("order", dict()).get("taxon", dict()).get("name", "")
                r["order"] = {"taxid": taxid, "name": name}
                # family
                taxid = record.get("taxonomy", dict()).get("family", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("family", dict()).get("taxon", dict()).get("name", "")
                r["family"] = {"taxid": taxid, "name": name}
                # subfamily
                taxid = record.get("taxonomy", dict()).get("subfamily", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("subfamily", dict()).get("taxon", dict()).get("name", "")
                r["subfamily"] = {"taxid": taxid, "name": name}
                # genus
                taxid = record.get("taxonomy", dict()).get("genus", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("genus", dict()).get("taxon", dict()).get("name", "")
                r["genus"] = {"taxid": taxid, "name": name}
                # species
                taxid = record.get("taxonomy", dict()).get("species", dict()).get("taxon", dict()).get("taxID", "")
                name = record.get("taxonomy", dict()).get("species", dict()).get("taxon", dict()).get("name", "")
                r["species"] = {"taxid": taxid, "name": name}

                output.append(r)

            df = pandas.DataFrame.from_dict(output)
            b_id = str(uuid.uuid4())
            retval = {"uid": b_id, "full_records": full_records, "data": df.to_json(), "num_records": len(output)}
            # store this object in the session to calling later by uuid
            req = ThreadLocal.get_current_request()
            req.session[b_id] = retval
            return retval
        except KeyError as e:
            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="KeyError Encountered: " + str(e),
                               action="info",
                               html_id="barcode_notify")
            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="",
                               action="hide_sub_spinner",
                               html_id="")
        except Exception as e:
            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="Samples not found in Bold. Please try again Later.",
                               action="info",
                               html_id="barcode_notify")
            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="",
                               action="hide_sub_spinner",
                               html_id="")

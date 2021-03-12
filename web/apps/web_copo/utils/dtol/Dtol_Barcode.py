import uuid
import xml.etree.ElementTree as ET

import pandas
import xmljson
from django_tools.middlewares import ThreadLocal


class Barcoding:

    def __init__(self, file):

        self.file = file
        self.data = None
        name = self.file.name
        if name.endswith("xlsx") or name.endswith("xls"):
            self.data = pandas.read_excel(self.file)
        elif name.endswith("csv"):
            self.data = pandas.read_csv(self.file)

        required_columns = ["SPECIMEN_ID", "BOLD_ID"]
        actual_columns = list(self.data.columns)
        for r in required_columns:
            if r not in actual_columns:
                raise AssertionError(r + " not Found in Barcoding Manifest")

    def query_bold(self):
        bold_ids = self.data["BOLD_ID"].unique()
        bold_url_param = ""
        for bid in bold_ids:
            # concatenate bold ids
            bold_url_param = bold_url_param + bid + '|'
        url = "http://www.boldsystems.org/index.php/API_Public/combined?ids=" + bold_url_param
        # bold_xml = requests.get(url)
        # resp = bold_xml.content
        with open('/home/fshaw/Downloads/bold_data.xml') as f:
            xml = ET.fromstring(f.read())
            d = xmljson.badgerfish.data(xml)["bold_records"]["record"]

        output = list()
        for record in d:
            r = dict()
            r["bold_sample_id"] = record["specimen_identifiers"]["sampleid"]["$"]
            # phylum
            taxid = record["taxonomy"]["phylum"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["phylum"]["taxon"]["name"]["$"]
            r["phylum"] = {"taxid": taxid, "name": name}
            # class
            taxid = record["taxonomy"]["class"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["class"]["taxon"]["name"]["$"]
            r["class"] = {"taxid": taxid, "name": name}
            # order
            taxid = record["taxonomy"]["order"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["order"]["taxon"]["name"]["$"]
            r["order"] = {"taxid": taxid, "name": name}
            # family
            taxid = record["taxonomy"]["family"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["family"]["taxon"]["name"]["$"]
            r["family"] = {"taxid": taxid, "name": name}
            # subfamily
            taxid = record["taxonomy"]["subfamily"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["subfamily"]["taxon"]["name"]["$"]
            r["subfamily"] = {"taxid": taxid, "name": name}
            # genus
            taxid = record["taxonomy"]["genus"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["genus"]["taxon"]["name"]["$"]
            r["genus"] = {"taxid": taxid, "name": name}
            # species
            taxid = record["taxonomy"]["species"]["taxon"]["taxID"]["$"]
            name = record["taxonomy"]["species"]["taxon"]["name"]["$"]
            r["species"] = {"taxid": taxid, "name": name}
            # sequences
            sequence_id = record["sequences"]["sequence"]["sequenceID"]["$"]
            markercode = record["sequences"]["sequence"]["markercode"]["$"]
            nucleotides = record["sequences"]["sequence"]["nucleotides"]["$"]
            r["sequence"] = {"sequence_id": sequence_id, "markercode": markercode, "nucleotides": nucleotides}
            output.append(r)

        df = pandas.DataFrame.from_dict(output)
        b_id = str(uuid.uuid4())
        retval = {"uid": b_id, "data": df.to_json()}
        # store this object in the session to calling later by uuid
        req = ThreadLocal.get_current_request()
        req.session[b_id] = retval
        return retval

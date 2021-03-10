import xml.etree.ElementTree as ET

import pandas


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

    def do_bold(self):
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
        # xml = ET.fromstring(resp)
        for child in xml:
            print(child)

import requests
import os
from django.conf import settings
import xmltodict, json
from dal.copo_da import EnaChecklist


def download_ena_checklists():
    # the sample checklist filenames are in the format: ERC0000XX (where XX varies between 10 and 60)
    for x in range(0, 100):

        resp = requests.get("https://www.ebi.ac.uk/ena/browser/api/xml/ERC0000" + str(
            x) + "?download=false&gzip=false&includeLinks=false")
        print(resp.status_code)
        if resp.status_code == 200:
            filepath = os.path.join(settings.BASE_DIR, "web", "apps", "web_copo", "utils", "ena_sample_checklists",
                                    "ERC0000" + str(x) + ".json")
            with open(filepath, "w+") as f:
                o = xmltodict.parse(resp.content)
                f.write(json.dumps(o))
                o_db = {
                    "path": filepath,
                    "name": o["CHECKLIST_SET"]["CHECKLIST"]["DESCRIPTOR"]["NAME"],
                    "description": o["CHECKLIST_SET"]["CHECKLIST"]["DESCRIPTOR"]["DESCRIPTION"],
                    "accession": o["CHECKLIST_SET"]["CHECKLIST"]["@accession"]
                }
                EnaChecklist().get_collection_handle().update_one({"accession": o_db["accession"]},
                                                                  {"$set": o_db}, upsert=True)


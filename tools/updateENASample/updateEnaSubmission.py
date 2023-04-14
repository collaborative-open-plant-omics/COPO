import requests
from requests.auth import HTTPBasicAuth
import json
import xml.etree.ElementTree as ET
import copy

f = open("./data.json")
config = json.load(f)
session = requests.Session()
session.auth = (config["username"], config["password"])
submit_url = config["submit_url"]
retrive_url = config["retrive_url"]

webin = ET.Element("WEBIN")
submission_set = ET.SubElement(webin, "SUBMISSION_SET")
submission = ET.SubElement(submission_set, "SUBMISSION")
actions = ET.SubElement(submission, "ACTIONS")
action = ET.SubElement(actions, "ACTION")
modify = ET.SubElement(action, "MODIFY")

def update_xml(data):
 print("\nDoing Sample Accession:", data["sample_accession"])
 response = session.get(f'{retrive_url}{data["sample_accession"]}')
 not_found = False
 if response.status_code == requests.codes.ok:
    root = ET.fromstring(response.text)
    for i in data.keys():
        if i == "sample_accession":
           continue
        element = root.find(f".//*[TAG='{i}']")
        if element != None:   
             value = element.find('VALUE')
             value.text = data[i]
        else:
             element = root.find(f".//{i}")
             if element != None:
                  element.text = data[i]
             else:
                 print('element:', i, "not found")
                 not_found = True

    if not not_found:
      new_root = copy.copy(webin)
      new_root.append(root)
      tree = ET.ElementTree(new_root)
      tree.write("/tmp/sample.xml")
      response = session.post(submit_url, data={},files = {'file':open("/tmp/sample.xml")})
      print(response.text)
 else:
    print(response.status_code, response.text)

for sample in config["data"]:
 update_xml(sample)

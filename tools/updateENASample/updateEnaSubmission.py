import requests
from requests.auth import HTTPBasicAuth
import json
import xml.etree.ElementTree as ET
import copy

f = open("./data.json")
config = json.load(f)
session = None
submit_url = config["submit_url"]
retrive_url = config["retrive_url"]
add_new_attribute = config.get("add_new_attribute",False)

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
    sampleAttributes = root.find(".//SAMPLE_ATTRIBUTES")

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
        if not_found and add_new_attribute:
             element = ET.SubElement(sampleAttributes, "SAMPLE_ATTRIBUTE")
             tag = ET.SubElement(element, "TAG")
             tag.text = i
             value = ET.SubElement(element, "VALUE")
             value.text = data[i]
             not_found = False
    if not not_found:
      new_root = copy.copy(webin)
      new_root.append(root)
      tree = ET.ElementTree(new_root)
      tree.write("/tmp/sample.xml")
      response = session.post(submit_url, data={},files = {'file':open("/tmp/sample.xml")})
      print(response.text)
 else:
    print(response.status_code, response.text)

with requests.Session() as session:
  session.auth = (config["username"], config["password"])
  for sample in config["data"]:
     update_xml(sample)

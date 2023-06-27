import requests
import xml.etree.ElementTree as ET
from tools import resolve_env
from dal.copo_da import TagSequenceChecklist 
from web.apps.web_copo.schemas.utils.data_utils import get_datetime
from exceptions_and_logging import logger
from web.apps.web_copo.validators.ena_validators import ena_tagged_seq_validators  as required_validators
from django_tools.middlewares import ThreadLocal
import inspect
from web.apps.web_copo.validators.validator import Validator
from submission.helpers.generic_helper import notify_tagged_seq_status
import pandas 
from web.apps.web_copo.schemas.utils.data_utils import json_to_pytype, get_datetime, get_not_deleted_flag
from web.apps.web_copo.schema_versions.lookup import dtol_lookups as lookup
import math
from web.apps.web_copo.schemas.utils import data_utils

pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
l = logger.Logger()
headers = {'Accept': 'application/xml' }

def loadCheckList():
    url = "https://www.ebi.ac.uk/ena/submit/report/checklists/xml/*?type=sequence"
    with requests.Session() as session:    
        session.auth = (user_token, pass_word) 
        try:
            response = session.get(url,headers=headers)
            return response.text
        except Exception as e:
            l.exception(e)
            return False            
   
'''
<CHECKLIST_SET>
<CHECKLIST accession="ERT000028" checklistType="Sequence">
   <IDENTIFIERS>
      <PRIMARY_ID>ERT000028</PRIMARY_ID>
   </IDENTIFIERS>
   <DESCRIPTOR>
      <LABEL>Single Viral CDS</LABEL>
      <NAME>Single Viral CDS</NAME>
      <DESCRIPTION>For complete or partial single coding sequence (CDS) from a viral gene. Please do not use for peptides processed from polyproteins or proviral sequences, as these are all annotated differently.</DESCRIPTION>
      <AUTHORITY>ENA</AUTHORITY>
      <FIELD_GROUP restrictionType="Any number or none of the fields">
         <NAME>Mandatory Fields and Questions</NAME>
         <FIELD>
            <LABEL>VMOLTYPE</LABEL>
            <NAME>Molecule Type</NAME>
            <DESCRIPTION>Type of in vivo molecule sequenced. Taken from the INSDC controlled vocabulary. Example: Genomic DNA, Genomic RNA, viral cRNA.</DESCRIPTION>
            <FIELD_TYPE>
               <TEXT_CHOICE_FIELD>
                  <TEXT_VALUE>
                     <VALUE>genomic DNA</VALUE>
                  </TEXT_VALUE>
                  <TEXT_VALUE>
                     <VALUE>genomic RNA</VALUE>
                  </TEXT_VALUE>
                  <TEXT_VALUE>
                     <VALUE>viral cRNA</VALUE>
                  </TEXT_VALUE>
               </TEXT_CHOICE_FIELD>
            </FIELD_TYPE>
            <MANDATORY>mandatory</MANDATORY>
            <MULTIPLICITY>single</MULTIPLICITY>
         </FIELD>
         <FIELD>
            <LABEL>ORGANISM</LABEL>
            <NAME>Organism</NAME>
            <DESCRIPTION>Full name of virus (ICTV-approved or otherwise), NCBI taxid, BioSample accession, SRA sample accession, or sample alias. Influenza, Norovirus, Sapovirus and HIV have special nomenclature. Please contact us if you are unsure. Example: Raspberry bushy dwarf virus, Influenza A virus (A/chicken/Germany/1949(H10N7)), HIV-1 M:F_CHU51.</DESCRIPTION>
            <FIELD_TYPE>
               <TAXON_FIELD/>
            </FIELD_TYPE>
            <MANDATORY>mandatory</MANDATORY>
            <MULTIPLICITY>single</MULTIPLICITY>
         </FIELD>
         <FIELD>
            <LABEL>GENE</LABEL>
            <NAME>Gene</NAME>
            <DESCRIPTION>Symbol of the gene corresponding to a sequence region. Example: RdRp, CP, ORF1.</DESCRIPTION>
            <FIELD_TYPE>
               <TEXT_FIELD/>
            </FIELD_TYPE>
            <MANDATORY>mandatory</MANDATORY>
            <MULTIPLICITY>single</MULTIPLICITY>
         </FIELD>
         <FIELD>
            <LABEL>SVCGRTABLE</LABEL>
            <NAME>Translation table</NAME>
            <DESCRIPTION>Translation table for this virus. Chose between standard (table 1) and mitovirus codes (table 4.). Example: 1, 4.</DESCRIPTION>
            <FIELD_TYPE>
               <TEXT_FIELD/>
            </FIELD_TYPE>
            <MANDATORY>mandatory</MANDATORY>
            <MULTIPLICITY>single</MULTIPLICITY>
         </FIELD>
         <FIELD>
            <LABEL>5PARTIAL</LABEL>
            <NAME>Partial at 5' ? (yes/no)</NAME>
            <DESCRIPTION>For an incomplete CDS with the start codon upstream of the submitted sequence.</DESCRIPTION>
            <FIELD_TYPE>
               <TEXT_CHOICE_FIELD>
                  <TEXT_VALUE>
                     <VALUE>yes</VALUE>
                  </TEXT_VALUE>
                  <TEXT_VALUE>
                     <VALUE>no</VALUE>
                  </TEXT_VALUE>
               </TEXT_CHOICE_FIELD>
            </FIELD_TYPE>
            <MANDATORY>mandatory</MANDATORY>
            <MULTIPLICITY>single</MULTIPLICITY>
         </FIELD>
         <FIELD>
            <LABEL>5CDS</LABEL>
            <NAME>5' CDS location</NAME>
            <DESCRIPTION>Start of the coding region relative to the submitted sequence. For a full length CDS this is the position of the first base of the start codon.</DESCRIPTION>
            <FIELD_TYPE>
               <TEXT_FIELD>
                  <REGEX_VALUE>\d+</REGEX_VALUE>
               </TEXT_FIELD> 
            </FIELD_TYPE>
            <MANDATORY>mandatory</MANDATORY>
            <MULTIPLICITY>single</MULTIPLICITY>
         </FIELD> 
        </FIELD_GROUP>
    </DESCRIPTOR>
    </CHECKLIST>
    </CHECKLIST_SET>
'''

def parseCheckList(xmlstr):
    checklist_set = []
    dt = get_datetime()
    root = ET.fromstring(xmlstr)
    for checklist_elm in root.findall('./CHECKLIST'):
        checklist = {}
        checklist['primary_id'] = checklist_elm.find("./IDENTIFIERS/PRIMARY_ID").text.strip()
        checklist['name'] = checklist_elm.find("./DESCRIPTOR/NAME").text.strip()
        checklist['description'] = checklist_elm.find("./DESCRIPTOR/DESCRIPTION").text.strip()
        checklist['fields'] = {}
        for field_elm in checklist_elm.findall("./DESCRIPTOR/FIELD_GROUP/FIELD"):
            field = {}
            key = field_elm.find("./LABEL").text.strip()
            field['name'] = field_elm.find("./NAME").text.strip()
            field['description'] = field_elm.find("./DESCRIPTION").text.strip()
            field['mandatory'] = field_elm.find("./MANDATORY").text.strip()
            field['multiplicity'] = field_elm.find("./MULTIPLICITY").text.strip()
            field['type'] = field_elm.find("./FIELD_TYPE")[0].tag
            choice = field_elm.find("./FIELD_TYPE/TEXT_CHOICE_FIELD")
            if choice is not None:
                field['choice'] = []
                for choice_elm in choice.findall("./TEXT_VALUE"):
                    field['choice'].append(choice_elm.find("./VALUE").text.strip())

            regex = field_elm.find("./FIELD_TYPE/TEXT_FIELD/REGEX_VALUE")
            if regex is not None:
                field['regex'] = regex.text.strip()
            checklist['fields'][key] = field
        checklist["modified_date"] =  dt
        checklist["deleted"] = data_utils.get_not_deleted_flag()
        checklist_set.append(checklist)
    return checklist_set

def updateCheckList():
    xmlstr = loadCheckList()
    checklist_set = parseCheckList(xmlstr)
    for checklist in checklist_set:
        TagSequenceChecklist().get_collection_handle().find_one_and_update({"primary_id": checklist["primary_id"]},
                                                                        {"$set": checklist},
                                                                        upsert=True)
        
def get_mandatory_field(checklist):
    mandatory_fields = []
    for field in checklist["fields"]:
        if field["mandatory"] == "mandatory":
            mandatory_fields.append(field["label"])
    return mandatory_fields


class TaggedSequenceSpreedsheet:
   def __init__(self, file):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        self.checklist_id = self.req.session.get("checklist_id", None)
        self.data = None
        self.required_validators = list()

        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated
        if file:
            self.file = file
        else:
            self.sample_data = self.req.session.get("tagged_seq_data", "")
            self.isupdate = self.req.session.get("isupdate", False)


        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.required_validators.append(element)

   def get_filenames_from_manifest(self):
        return list(self.data["file_name"])

   def loadManifest(self, m_format):

        if self.profile_id is not None:
            notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                            html_id="sample_info")

            try:
                # read excel and convert all to string
                if m_format == "xls":
                    self.data = pandas.read_excel(self.file, keep_default_na=False,
                                                  na_values=lookup.NA_VALS)
                elif m_format == "csv":
                    self.data = pandas.read_csv(self.file, keep_default_na=False,
                                                na_values=lookup.NA_VALS)
                self.data = self.data.loc[:, ~self.data.columns.str.contains('^Unnamed')]
                self.data = self.data.apply(lambda x: x.astype(str))
                self.data = self.data.apply(lambda x: x.str.strip())
                self.data.columns = self.data.columns.str.replace(" ", "")
            except Exception as e:
                # if error notify via web socket
                notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
                                action="info",
                                html_id="tagged_seq_info")
                return False
            return True

   def validate(self):
        flag = True
        errors = []
        warnings = []
        self.isupdate = False

        try:

            checklist = TagSequenceChecklist().get_collection_handle().find_one({"primary_id": self.checklist_id})

            # validate for required fields
            for v in self.required_validators:
                errors, warnings, flag, self.isupdate = v(profile_id=self.profile_id, checklist=checklist,
                                                          data=self.data,
                                                          errors=errors, warnings=warnings, flag=flag,
                                                          isupdate=self.isupdate).validate()

            # send warnings
            if warnings:
                notify_tagged_seq_status(data={"profile_id": self.profile_id},
                                msg="<br>".join(warnings),
                                action="warning",
                                html_id="warning_info2")
            # if flag is false, compile list of errors
            if not flag:
                errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                errors = "".join(errors)

                notify_tagged_seq_status(data={"profile_id": self.profile_id},
                                msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                                action="error",
                                html_id="sample_info")
                return False



        except Exception as e:
            l.exception(e)
            error_message = str(e).replace("<", "").replace(">", "")
            notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                            action="info",
                            html_id="sample_info")

            return False

        # if we get here we have a valid spreadsheet
        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                        html_id="sample_info")
        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls")
        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id="sample_info")

        return True

   def collect(self):
        # create table data to show to the frontend from parsed manifest
        tagged_seq_data = []
        headers = list()
        for col in list(self.data.columns):
            headers.append(col)
        tagged_seq_data.append(headers)
        for index, row in self.data.iterrows():
            r = list(row)
            for idx, x in enumerate(r):
                if x is math.nan:
                    r[idx] = ""
            tagged_seq_data.append(r)
        # store sample data in the session to be used to create mongo objects
        self.req.session["tagged_seq_data"] = tagged_seq_data

        notify_tagged_seq_status(data={"profile_id": self.profile_id}, msg=tagged_seq_data, action="make_table",
                        html_id="sample_table")
             
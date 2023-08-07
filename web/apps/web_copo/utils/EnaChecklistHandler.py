import requests
from lxml import etree as ET
from tools import resolve_env
from dal.copo_da import EnaChecklist
from exceptions_and_logging import logger
import pandas as pd
import os
from django.conf import settings
from openpyxl.utils.cell import get_column_letter
from web.apps.web_copo.schemas.utils.data_utils import get_datetime, get_not_deleted_flag
from django_tools.middlewares import ThreadLocal
import inspect
import math
from web.apps.web_copo.schema_versions.lookup import dtol_lookups as lookup
from web.apps.web_copo.validators.ena_validators import ena_checklist_validators  as required_validators
from web.apps.web_copo.validators.validator import Validator
from submission.helpers.generic_helper import notify_ena_object_status
import json

l = logger.Logger()

class ChecklistHandler:
    def __init__(self):
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.headers = {'Accept': 'application/xml' }

    def _loadCheckList(self, url):
        with requests.Session() as session:    
            session.auth = (self.user_token, self.pass_word) 
            try:
                response = session.get(url,headers=self.headers)
                return response.text
            except Exception as e:
                l.exception(e)
                return ""            
    
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
                <UNITS>
                  <UNIT>DD</UNIT>
                </UNITS>
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

    def _parseCheckList(self, xmlstr):
        xml = xmlstr.encode('utf-8')
        parser = ET.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        checklist_set = []
        dt = get_datetime()
        root = ET.fromstring(xml, parser=parser)
        #checklist_ids = settings.BARCODING_CHECKLIST
        for checklist_elm in root.findall("./CHECKLIST"):
            primary_id = checklist_elm.find("./IDENTIFIERS/PRIMARY_ID").text.strip() 
            skip = settings.ENA_CHECKLIST_CONFIG.get(primary_id, dict()).get( "skip", list() )
            #if primary_id not in checklist_ids:
            #    continue
            #checklist_ids.remove(primary_id)
            checklist = {}
            checklist['primary_id'] = primary_id
            checklist['name'] = checklist_elm.find("./DESCRIPTOR/NAME").text.strip()
            checklist['description'] = checklist_elm.find("./DESCRIPTOR/DESCRIPTION").text.strip()
            checklist['fields'] = {}
            for field_elm in checklist_elm.findall("./DESCRIPTOR/FIELD_GROUP/FIELD"):
                field = {}
                key = field_elm.find("./LABEL").text.strip()
                if key in skip:
                    continue
                field['name'] = field_elm.find("./NAME").text.strip()
                desc = field_elm.find("./DESCRIPTION")
                if desc is not None:
                    field['description'] = desc.text.strip()
                field['mandatory'] = field_elm.find("./MANDATORY").text.strip()
                field['multiplicity'] = field_elm.find("./MULTIPLICITY").text.strip()
                synonym = field_elm.find("./SYNONYM")
                if synonym is not None:
                    field['synonym'] = synonym.text.strip()

                unit = field_elm.find("./UNITS/UNIT")
                if unit is not None:
                    field['unit'] = unit.text.strip()
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

            if checklist['primary_id'].startswith("ERT"):
                #add SPECIMEN_ID
                field = {}
                field['name'] = "SPECIMEN_ID"
                field['description'] = "SPECIMENT_ID"
                field['mandatory'] = "mandatory"
                field['multiplicity'] = "single"
                field['type'] = "TEXT_FIELD"
                checklist['fields']["SPECIMEN_ID"] = field
                #add TAXON_ID
                field = {}
                field['name'] = "TAXON_ID"
                field['description'] = "TAXON_ID"
                field['mandatory'] = "mandatory"
                field['multiplicity'] = "single"
                field['type'] = "TEXT_FIELD"
                checklist['fields']["TAXON_ID"] = field

            checklist["modified_date"] =  dt
            checklist["deleted"] = get_not_deleted_flag()
            checklist_set.append(checklist)
            #if len(checklist_ids) == 0:
            #    break
        return checklist_set

    def updateCheckList(self):
        urls = settings.ENA_CHECKLIST_URL
        checklist_set = []

        for url in urls:
            xmlstr = self._loadCheckList(url)
            checklist_set.extend(self._parseCheckList(xmlstr))

        reads = EnaChecklist().execute_query({"primary_id": "read", "deleted": get_not_deleted_flag()})
        read = None
        if reads:
            read = reads[0]

        for checklist in checklist_set:
            if checklist["primary_id"].startswith("ERC"):
                for key, value in read["fields"].items():
                    value.update({"read_field": True})   
                checklist["fields"].update(read["fields"])
            EnaChecklist().get_collection_handle().find_one_and_update({"primary_id": checklist["primary_id"]},
                                                                            {"$set": checklist},
                                                                            upsert=True)
            df = pd.DataFrame.from_dict(list(checklist["fields"].values()), orient='columns')
            df1 = df
            df.sort_values(by=['mandatory','name'], inplace=True)
            df.loc[df["mandatory"] == "mandatory" , "name"] = df["name"]
            df.loc[df["mandatory"] != "mandatory", "name"] = df["name"] + " (optional)"

            df1 = df.transpose()

            version = settings.MANIFEST_VERSION.get(checklist["primary_id"], str())
            if version:
                version = "_v" + version
            checklist_filename = os.path.join(settings.MANIFEST_PATH, settings.MANIFEST_FILE_NAME.format(checklist["primary_id"], version)  )
            with pd.ExcelWriter(path=checklist_filename, engine='xlsxwriter' ) as writer:  
                sheet_name = checklist["primary_id"] + " " + checklist["name"]
                sheet_name = sheet_name[:31]
                df1.loc[["name"]].to_excel(writer, sheet_name=sheet_name, index=False, header=False)

                df1.columns = df1.iloc[0] 
                data_validation_column_index = 0
                for field in checklist["fields"].values():
                    name = field["name"] if field["mandatory"] == "mandatory"  else field["name"] + " (optional)"
                    column_index = df1.columns.get_loc(name)
                    column_length = len(name)
                    writer.sheets[sheet_name].set_column(column_index, column_index, column_length)
                    if "choice" in field:
                        choice = field["choice"]
                        column_letter = get_column_letter(column_index + 1)
                        cell_start_end = '%s2:%s1048576' % (column_letter, column_letter)

                        if len(choice) > 0:
                            source = ""
                            number_of_char_for_choice = sum([len(x) for x in choice])
                            if number_of_char_for_choice <= 255:
                                source = choice
                            else:
                                s = pd.Series(choice, name=field["name"])
                                s.to_frame().to_excel(writer, sheet_name="data_values", index=False, header=True, startrow=0, startcol=data_validation_column_index)
                                column_letter = get_column_letter(data_validation_column_index + 1)
                                column_length = max(s.astype(str).map(len).max(), len(field["name"]))
                                writer.sheets["data_values"].set_column(data_validation_column_index, data_validation_column_index, column_length)
                                source = "=%s!$%s$2:$%s$%s" % ("data_values", column_letter, column_letter, str(len(choice) + 1))
                                data_validation_column_index = data_validation_column_index + 1
                            writer.sheets[sheet_name].data_validation(cell_start_end,
                                                                 {'validate': 'list',
                                                                 'source': source})

                sheet_name = 'field_descriptions'           
                df.to_excel(writer, sheet_name=sheet_name)

                for column in df.columns:
                    column_length = max(df[column].astype(str).map(len).max(), len(column))
                    column_index = df.columns.get_loc(column)+1
                    writer.sheets[sheet_name].set_column(column_index, column_index, column_length)    

'''
    def parse_ena_taggedseq_spreadsheet(self, request):
        profile_id = request.session["profile_id"]
        notify_ena_object_status(data={"profile_id": profile_id},
                        msg='', action="info",
                        html_id="tagged_seq_info")
        # method called by rest
        file = request.FILES["file"]
        checklist_id = request.POST["checklist_id"]
        name = file.name
        ena = EnaCheckListSpreedsheet(file=file, checklist_id=checklist_id)
        if name.endswith("xlsx") or name.endswith("xls"):
            fmt = 'xls'
        else:
            return HttpResponse(status=415, content="Please make sure your manifest is in xlxs format")

        if ena.loadManifest(fmt):
            l.log("Dtol manifest loaded")
            if ena.validate():
                ena.collect()
                return HttpResponse()
            return HttpResponse(status=400)
        return HttpResponse(status=400)

    def save_checklist_manifest_records(self, request):
        tagged_seq_data = request.session.get("tagged_seq_data")
        profile_id = request.session["profile_id"]
        uid = str(request.user.id)
        checklist = EnaChecklist().get_collection_handle().find_one({"primary_id": request.session["checklist_id"]})
        column_name_mapping = { field["name"].upper() : key  for key, field in checklist["fields"].items()  }
        fields = checklist["fields"]
        if tagged_seq_data:
            for p in range(1, len(tagged_seq_data)):
                # for each row in the manifest
                s = (map_to_dict(tagged_seq_data[0], tagged_seq_data[p]))

                record = {}
                record["profile_id"] = profile_id
                record["updated_by"] = uid
                record["modified_date"] = get_datetime()
                record["deleted"] = get_not_deleted_flag()
                record["checklist_id"] = request.session["checklist_id"]

                for key, value in s.items():
                    header = key
                    header = header.replace(" (optional)", "", -1)
                    upper_key = header.upper()
                    if upper_key in column_name_mapping:
                        record[column_name_mapping[upper_key]] = value

                insert_record = {}
                insert_record["created_by"] = uid
                insert_record["created_date"] = get_datetime()
                insert_record["status"] = "pending"

                EnaObject().get_collection_handle().find_one_and_update({"profile_id": profile_id, column_name_mapping["ORGANISM"]:s["Organism"]},
                                                                            {"$set": record, "$setOnInsert": insert_record},
                                                                            upsert=True)
        
        table_data = htags.generate_taggedseq_record(profile_id=profile_id, checklist_id=request.session["checklist_id"])
        result = {"table_data": table_data, "component": "taggedseq"}
        return JsonResponse(status=200, data=result)                    
'''
    
class EnaCheckListSpreedsheet:
   def __init__(self, file, checklist_id, component, validators=[]):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        self.checklist_id = checklist_id
        self.data = None
        self.new_data = None
        self.component = component
        self.component_info = f"{self.component}_info"
        self.component_table = f"{self.component}_table"
        self.required_validators = []    
        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated
        if file:
            self.file = file
        #else:
        #    self.sample_data = self.req.session.get( self.component_table, "")
        #    self.isupdate = self.req.session.get("isupdate", False)


        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.required_validators.append(element)

        self.required_validators.extend(validators)

   def get_filenames_from_manifest(self):
        return list(self.data["File name"])

   def loadManifest(self, m_format):

        if self.profile_id is not None:
            notify_ena_object_status(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                            html_id=self.component_info, checklist_id=self.checklist_id)

            try:
                # read excel and convert all to string
                if m_format == "xls":
                    self.data = pd.read_excel(self.file, keep_default_na=False,
                                                  na_values=lookup.NA_VALS)
                elif m_format == "csv":
                    self.data = pd.read_csv(self.file, keep_default_na=False,
                                                na_values=lookup.NA_VALS)
                else:
                    raise Exception("Unknown file format")
                if self.data.empty:
                    raise Exception("Empty file")
                self.data = self.data.loc[:, ~self.data.columns.str.contains('^Unnamed')]
                self.data = self.data.apply(lambda x: x.astype(str))
                self.data = self.data.apply(lambda x: x.str.strip())
                #self.data.columns = self.data.columns.str.replace(" ", "")
                   
                new_column_name = { name : name.replace(" (optional)", "",-1).upper() for name in self.data.columns.values.tolist() }
                self.new_data = self.data.rename(columns=new_column_name)    

                checklist = EnaChecklist().get_collection_handle().find_one({"primary_id": self.checklist_id})
                if checklist:
                   fields = checklist["fields"]
                   new_column_name = { value["name"].upper() : key for key, value in fields.items() }
                   self.new_data.rename(columns=new_column_name, inplace=True)    

            except Exception as e:
                # if error notify via web socket
                l.exception(e)
                notify_ena_object_status(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
                                action="error",
                                html_id=self.component_info, checklist_id=self.checklist_id)
                return False
            return True

   def validate(self):
        flag = True
        errors = []
        warnings = []
        self.isupdate = False
 
        checklist = EnaChecklist().get_collection_handle().find_one({"primary_id": self.checklist_id})

        # validate for required fields
        for v in self.required_validators:
            try:
                errors, warnings, flag, self.isupdate = v(profile_id=self.profile_id, checklist=checklist,
                                                        data=self.new_data, fields=None,
                                                        errors=errors, warnings=warnings, flag=flag,
                                                        isupdate=self.isupdate).validate()
            except Exception as e:
                l.exception(e)
                error_message = str(e).replace("<", "").replace(">", "")

                flag = False
                errors.append(error_message)
                                    
                #notify_ena_object_status(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                #                action="info",
                #                html_id=self.component_info, checklist_id=self.checklist_id)
                
        # send warnings
        if warnings:
            l.log(",".join(warnings))
            notify_ena_object_status(data={"profile_id": self.profile_id},
                            msg="<br>".join(warnings),
                            action="warning",
                            html_id="warning_info2", checklist_id=self.checklist_id)
        # if flag is false, compile list of errors
        if not flag:
            errors = list(map(lambda x: "<li>" + x + "</li>", errors))
            errors = "".join(errors)
            l.log(errors)
            notify_ena_object_status(data={"profile_id": self.profile_id},
                            msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                            action="error",
                            html_id=self.component_info, checklist_id=self.checklist_id)
            return False
 
        # if we get here we have a valid spreadsheet
        notify_ena_object_status(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                        html_id=self.component_info)
        notify_ena_object_status(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls", checklist_id=self.checklist_id)
        notify_ena_object_status(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id=self.component_info, checklist_id=self.checklist_id)

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
        self.req.session[f"{self.component}_data"] = tagged_seq_data
        self.req.session["checklist_id"] = self.checklist_id

        notify_ena_object_status(data={"profile_id": self.profile_id}, msg=tagged_seq_data, action="make_table",
                        html_id=f"{self.component}_parse_table", checklist_id=self.checklist_id)
        

class ReadChecklistHandler:
    def __init__(self ):
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.headers = {'Accept': 'application/xml' }

    def _loadCheckList(self, url):
        with requests.Session() as session:    
            session.auth = (self.user_token, self.pass_word) 
            try:
                response = session.get(url,headers=self.headers)
                return response.text
            except Exception as e:
                l.exception(e)
                return ""         

    def _parseCheckList(self, jsonstr):
            dt = get_datetime()
            try:
                checklists_elm = json.loads(jsonstr)
                checklists = list()
                for checklist_elm in checklists_elm.get("fieldTypes",[]):
                    name = checklist_elm["name"]
                    if name == "fastq1":
                        checklist = dict()
                        checklist["primary_id"] = "read"
                        checklist["name"] = "read checklist"
                        checklist["description"] = checklist_elm["description"]
                        checklist["fields"] = {}
                        checklist["modified_date"] =  dt
                        checklist["deleted"] = get_not_deleted_flag()
                        for field_elm in checklist_elm["fields"]:

                            field = dict()
                            name = field_elm["label"]
                            if name.lower() in ["study"]:
                                continue

                            field["name"] = name
                            field["description"] = field_elm["description"]
                            field["mandatory"] =  "mandatory" if field_elm.get("mandatory", False) else "optional"
                            field["type"] = "TEXT_FIELD"
                            if "value_choice" in field_elm:
                                field["type"] = "TEXT_CHOICE_FIELD"
                                field["choice"] = field_elm["value_choice"]
                            checklist["fields"][field_elm["name"]] = field


                        field = {}
                        field['name'] = "Organism"
                        field['description'] = "Organism name"
                        field['mandatory'] = "mandatory"
                        field['multiplicity'] = "single"
                        field['type'] = "TEXT_FIELD"
                        checklist['fields']["organism"] = field

                        checklists.append(checklist)
                        break

                return checklists
            except Exception as e:
                l.exception(e)
                return []

    def updateCheckList(self):
        urls = [
            "https://www.ebi.ac.uk/ena/submit/report/checklists/getReadFields?format=xml"
        ]
        checklist_set = []
        for url in urls:
            jsonstr = self._loadCheckList(url)
            checklist_set.extend(self._parseCheckList(jsonstr))

        for checklist in checklist_set:

            EnaChecklist().get_collection_handle().find_one_and_update({"primary_id": checklist["primary_id"]},
                                                                            {"$set": checklist},
                                                                            upsert=True)        
from bson import json_util
from dal import cursor_to_list
from dal.copo_da import Sample
from datetime import datetime, timezone
from django.conf import settings as settings
from django.core.management import BaseCommand
from xlrd import open_workbook, XLRDError
import ast
import dal.copo_da as da
import importlib
import json
import pandas as pd
import re

'''
Extract "SPECIMEN_ID" value from a Excel spreadsheet then, retrieve the sample metadata 
from the COPO database using the "SPECIMEN_ID"

Output the result in a .json file

e.g. python3 manage.py parse_xlsx_to_json "/usr/users/EI_ga012/providen/Downloads/nhmdump.xlsx"
'''

schema_version_path_dtol_lookups = f'web.apps.web_copo.schema_versions.{settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
dtol_lookups_data = importlib.import_module(schema_version_path_dtol_lookups)
DTOL_ENA_MAPPINGS = dtol_lookups_data.DTOL_ENA_MAPPINGS
TOL_PROFILE_TYPES = dtol_lookups_data.TOL_PROFILE_TYPES


class Command(BaseCommand):
    # The following information is shown when a user types "help"
    help = "Extract/parse data from an .xlsx file then, retrieve metadata from COPO database based on the data and " \
           "output the result in  a .json format "

    def __init__(self):
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument("xlsx", type=str)

    def parse_db_data_to_json(self, data_in_db, json_filename):
        datetime_fields = ["date_modified", "time_created"]
        new_fields = []
        data = json.loads(json_util.dumps(data_in_db))
        # print("List of data found in COPO db: ", data[0])

        for sample in data[0]:
            print("\n\nSample 1: ", sample)
            ''' 
                Remove nested dicitonaries from the sample dictionary by retrieving
                the value of the nested dictionary and assigning it to the key of the outer dictionary
                if a dictionary is present within the list of values
            '''

            for key, value in sample.items():
                if type(value) is dict and key == "_id":
                    field_value = value.get('$oid')
                    sample[key] = field_value

                if type(value) is dict and key in datetime_fields:
                    field_value = value.get('$date')

                    # Convert datetime in milliseconds to timestamp
                    field_value = datetime.fromtimestamp(field_value / 1000.0, tz=timezone.utc).strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    sample[key] = field_value

            sample_fields1 = list(sample.keys())
            sample_values1 = list(sample.values())
            print("Sample 2: ", sample)
            print("Sample items: ", sample.items())
            print("Sample fields count 1: ", len(sample_fields1))
            print("Sample field values count 1: ", len(sample_values1))
            print("Sample fields 1: ", sample_fields1)
            print("Sample field values 1: ", sample_values1)

            # Get the ENA field name that corresponds to COPO field name based on the 'ena' key
            # in the "DTOL_ENA_MAPPINGS" dictionary

            print("field now: ", sample_fields1[sample_fields1.index('_id')])
            # new_sample_fields = [value['ena'] if key in list(sample.keys()) else sample_fields[sample_fields.index(key)]
            #                      for key, value in DTOL_ENA_MAPPINGS.items()]

            for key, value in DTOL_ENA_MAPPINGS.items():
                if key in list(sample.keys()):
                    sample_df = pd.DataFrame([sample])
                    sample_df.rename(columns={key: value['ena']}, inplace=True)
                    sample = sample_df.to_dict('records')[0]
                    sample.update(sample_df.to_dict('records')[0])

            print("Sample 3: ", sample)

            # sample_fields = list(sample.keys())
            # sample_values = list(sample.values())
            print("Sample fields count 2: ", len(list(sample.keys())))
            print("Sample field values count 2: ", len(list(sample.values())))
            print("Sample fields 2: ", list(sample.keys()))
            print("Sample field values 2: ", list(sample.values()))
            print("Missing fields from current sample dictionary: ",
                  [field for field in list(sample.keys()) if field not in sample_fields1])

            # new_fields = [value['ena'] if field in fields else fields[fields.index(field)] for field, value in
            #               DTOL_ENA_MAPPINGS.items()]

            # for field, value in DTOL_ENA_MAPPINGS.items():
            #     if field in fields:
            #         new_fields.append(value['ena'])
            #         # index = fields.index(field)
            #         # fields[index] = value['ena']  # Update field name with ENA mapping field name
            #     else:
            #         #     fields[index] = element
            #         new_fields.append(field)

            # # list(map(lambda x: a if condition1 else b, filter(lambda x, y: condition2, DTOL_ENA_MAPPINGS.items())))
            # field_values = list(sample.values())  # Contains dictionary in the list of values
            # print("\n\nKeys (ENA field names and COPO field names): ", new_fields)

            # Remove dictionary in the list of values by retrieving the value of a dictionary
            # if a dictionary is present within the list of values
            # new_field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
            # print("\n\nValues: ", new_field_values)
            # samples_only_df = pd.DataFrame(data=[new_field_values], columns=new_fields)
            # samples_only_df.to_json(json_filename)

    # A command must define handle()
    def handle(self, *args, **options):
        file_path_dict = ast.literal_eval(str(options))  # '/usr/users/EI_ga012/providen/Downloads/nhmdump.xlsx'
        excel_file_path = file_path_dict.get("xlsx")
        try:
            open_workbook(excel_file_path)
            df = pd.read_excel(excel_file_path)  # Convert excel file to  a Pandas dataframe
            rows_list = df.to_dict('records')  # Get all rows from the excel spreadsheet
            pattern_without_prefix = "EMu/\d{9}"
            pattern_with_prefix = "EMu/NHMUK\d{9}"  # SPECIMEN_ID begins with the prefix - "NHMUK"
            pattern_with_Emu_only = "EMu/"

            # Iterate through each row in the spreadsheet to retrieve the "SPECIMEN_ID"
            specimen_id_list = []
            for row in rows_list:
                search_query_without_prefix = re.search(pattern_without_prefix, str(row))
                search_query_with_prefix = re.search(pattern_with_prefix, str(row))
                if search_query_without_prefix:
                    specimen_id = search_query_without_prefix.group(0)
                    # Remove the substring, "EMu/" then, add the string, "NHMUK", to get the "SPECIMEN_ID"
                    specimen_id = "NHMUK".join(specimen_id.split(pattern_with_Emu_only))
                    specimen_id_list.append(specimen_id)

                if search_query_with_prefix:
                    specimen_id = search_query_with_prefix.group(0)
                    # Remove the substring, "EMu/", to retain the "SPECIMEN_ID" only
                    specimen_id = "".join(specimen_id.split(pattern_with_Emu_only))
                    specimen_id_list.append(specimen_id)

            assert 2138 == len(specimen_id_list)  # Number of SPECIMEN_IDs is equal to 2138

            specimen_ids_not_in_db = []
            samples_only_in_db = []
            sources_only_in_db = []
            samples_and_sources_in_db = []
            specimen_id_list = ["MBA-190930-001A", "MBA-190930-001B"]

            for specimen in specimen_id_list:
                sample_in_db = cursor_to_list(Sample().get_sample_by_specimen_id(specimen))
                source_in_db = cursor_to_list(da.Source().get_by_specimen(specimen))

                if sample_in_db == [] and source_in_db == []:
                    specimen_ids_not_in_db.append(specimen)
                elif sample_in_db != [] and source_in_db == []:
                    samples_only_in_db.append(sample_in_db)
                elif sample_in_db == [] and source_in_db != []:
                    sources_only_in_db.append(source_in_db)
                else:
                    # if sample_in_db and source_in_db
                    samples_and_sources_in_db.append(sample_in_db)
                    samples_and_sources_in_db.append(source_in_db)

            # Convert list of "SPECIMEN_ID" not present in COPO to json format
            if specimen_ids_not_in_db:
                print("List of specimens not found in COPO db: ", specimen_ids_not_in_db)
                specimen_ids_df = pd.DataFrame(data=[specimen_ids_not_in_db], columns=["SPECIMEN_ID"])
                specimen_ids_df.to_json('specimen_ids_not_present_in_copo.json')

            # Convert db list of dictionary data to json
            # Samples only
            if samples_only_in_db and not sources_only_in_db:
                # Samples only
                self.parse_db_data_to_json(samples_only_in_db, 'copo_samples_only.json')

                # print("List of samples found in COPO db: ", samples_only_in_db)
                # samples_only_in_db = json.loads(json_util.dumps(samples_only_in_db))
                # fields = list(samples_only_in_db[0][0].keys())
                #
                # # Get the ENA field name that corresponds to COPO field name based on the 'ena' key
                # # in the "DTOL_ENA_MAPPINGS" dictionary
                # new_fields = [value['ena'] for field, value in DTOL_ENA_MAPPINGS.items() for item in fields if
                #               field == item]
                # field_values = list(samples_only_in_db[0][0].values())
                # print("Keys: ", new_fields)
                # print("\n\n")
                # print("Values: ", field_values)
                # # Get value of a dictionary if a dictionary is present within the list
                # field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
                # print("Values 2: ", field_values)
                # samples_only_df = pd.DataFrame(data=[field_values], columns=new_fields)
                # samples_only_df.to_json('copo_samples_only.json')
            elif sources_only_in_db and not samples_only_in_db:
                # Sources only
                self.parse_db_data_to_json(sources_only_in_db, 'copo_sources_only.json')

                # print("List of sources found in COPO db: ", sources_only_in_db)
                # sources_only_in_db = json.loads(json_util.dumps(sources_only_in_db))
                # fields = list(sources_only_in_db[0][0].keys())
                # # Get the ENA field name that corresponds to COPO field name based on the 'ena' key
                # # in the "DTOL_ENA_MAPPINGS" dictionary
                # new_fields = [value['ena'] for field, value in DTOL_ENA_MAPPINGS.items() for item in fields if
                #               field == item]
                # field_values = list(sources_only_in_db[0][0].values())
                # print("Keys: ", fields)
                # print("\n\n")
                # print("Values: ", field_values)
                # # Get value of a dictionary if a dictionary is present within the list
                # field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
                # print("Values 2: ", field_values)
                # sources_only_df = pd.DataFrame(data=[field_values], columns=new_fields)
                # sources_only_df.to_json('copo_sources_only.json')
            else:
                # Samples and sources....if sample_in_db and source_in_db
                self.parse_db_data_to_json(samples_and_sources_in_db, 'copo_samples_and_sources.json')

                # print("List of samples and sources found in COPO db: ", samples_and_sources_in_db)
                # samples_and_sources_in_db = json.loads(json_util.dumps(samples_and_sources_in_db))
                # fields = list(samples_and_sources_in_db[0][0].keys())
                # # Get the ENA field name that corresponds to COPO field name based on the 'ena' key
                # # in the "DTOL_ENA_MAPPINGS" dictionary
                # new_fields = [value['ena'] for field, value in DTOL_ENA_MAPPINGS.items() for item in fields if
                #               field == item]
                # field_values = list(samples_and_sources_in_db[0][0].values())
                # # Get value of a dictionary if a dictionary is present within the list
                # field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
                # samples_and_sources_only_df = pd.DataFrame(data=[field_values], columns=new_fields)
                # samples_and_sources_only_df.to_json('copo_samples_and_sources.json')

        except XLRDError as error:
            # File format is unsupported or file is corrupt
            print("Error: ", error)

        # Parse xml file
        # try:
        #     field_values = []
        #     tree = ET.parse(excel_file_path)
        #     root = tree.getroot()
        #
        #     accession_list = [accession.text for accession in root.iter('PRIMARY_ID')]
        #     sample_alias_list = [accession.text for accession in root.iter('SUBMITTER_ID')]  # or SUBMITTER_ID
        #     title_list = [accession.text for accession in root.iter('TITLE')]
        #     taxon_ID_list = [accession.text for accession in root.iter('TAXON_ID')]
        #     scientific_name_list = [accession.text for accession in root.iter('SCIENTIFIC_NAME')]
        #
        #     # SAMPLE_ATTRIBUTE within <SAMPLE_ATTRIBUTES></SAMPLE_ATTRIBUTES> tag
        #     for sampleAttribute in root.findall('SAMPLE_ATTRIBUTE'):
        #         field = sampleAttribute.find('TAG')
        #         value = sampleAttribute.find('VALUE')
        #         if field is None and value is None:
        #             print("Field and its value does not exist for the sample attribute")
        #         else:
        #             # Get the database field name based on the 'ena' key in the "DTOL_ENA_MAPPINGS" dictionary
        #             fields = [field for field, field_value in DTOL_ENA_MAPPINGS.items() if
        #                       field_value['ena'] == field.text]
        #             field_values.append(value.text)
        #
        # except ET.ParseError:
        #     # If xml file is empty
        #     print(ET.ParseError.msg)

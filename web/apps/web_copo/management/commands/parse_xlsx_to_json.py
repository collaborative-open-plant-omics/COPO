from bson import json_util
from dal import cursor_to_list
from dal.copo_da import Sample, DAComponent
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
                    # sample_in_db != [] and source_in_db != []
                    samples_and_sources_in_db.append(sample_in_db)
                    samples_and_sources_in_db.append(source_in_db)

            print("List of specimens not found in db: ", specimen_ids_not_in_db)
            print("List of samples found in db: ", samples_only_in_db)
            print("List of sources found in db: ", sources_only_in_db)
            print("List of samples and sources found in db: ", samples_and_sources_in_db)

            # Get the database field name based on the 'ena' key in the "DTOL_ENA_MAPPINGS" dictionary
            #             fields = [field for field, field_value in DTOL_ENA_MAPPINGS.items() if
            #                       field_value['ena'] == field.text]
            #             field_values.append(value.text)

            # Convert list of "SPECIMEN_ID" not present in COPO to json
            samples_only_df = pd.DataFrame(data=[specimen_ids_not_in_db], columns=["SPECIMEN_ID"])
            samples_only_df.to_json('specimen_ids_not_present_in_copo.json')

            # Convert data in db to json
            # Samples only
            if samples_only_in_db != [] and sources_only_in_db == []:
                samples_only_in_db = json.loads(json_util.dumps(samples_only_in_db))
                fields = list(samples_only_in_db[0][0].keys())
                field_values = list(samples_only_in_db[0][0].values())
                print("Keys: ", fields)
                print("\n\n")
                print("Values: ", field_values)

                field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
                print("Values 2: ", field_values)
                samples_only_df = pd.DataFrame(data=[field_values], columns=fields)
                samples_only_df.to_json('copo_samples_only.json')
            elif sources_only_in_db != [] and samples_only_in_db == []:
                # Sources only
                sources_only_in_db = json.loads(json_util.dumps(sources_only_in_db))
                fields = list(sources_only_in_db[0][0].keys())
                field_values = list(sources_only_in_db[0][0].values())
                print("Keys: ", fields)
                print("\n\n")
                print("Values: ", field_values)

                field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
                print("Values 2: ", field_values)
                sources_only_df = pd.DataFrame(data=[field_values], columns=fields)
                sources_only_df.to_json('copo_sources_only.json')
            else:
                # Samples and sources
                # sample_in_db != [] and source_in_db != []
                samples_and_sources_in_db = json.loads(json_util.dumps(samples_and_sources_in_db))
                fields = list(samples_and_sources_in_db[0][0].keys())
                field_values = list(samples_and_sources_in_db[0][0].values())
                print("Keys: ", fields)
                # print("\n\n")
                print("Values: ", field_values)
                print(field_values[0])
                # print("\n\n")
                # print([element for index, element in enumerate(field_values) if "$oid" in field_values])
                # columns = [sample. for sample in samples_only_in_db[0]]
                field_values = [list(item.values())[0] if type(item) is dict else item for item in field_values]
                print("Values 2: ", field_values)
                samples_and_sources_only_df = pd.DataFrame(data=[field_values], columns=fields)
                samples_and_sources_only_df.to_json('copo_samples_and_sources.json')

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

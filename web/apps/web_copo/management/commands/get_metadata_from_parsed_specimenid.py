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

# schema_version_path_dtol_lookups = f'web.apps.web_copo.schema_versions.{
# settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
schema_version_path_dtol_lookups = 'web.apps.web_copo.schema_versions.lookup.dtol_lookups'
dtol_lookups_data = importlib.import_module(schema_version_path_dtol_lookups)
DTOL_ENA_MAPPINGS = dtol_lookups_data.DTOL_ENA_MAPPINGS
TOL_PROFILE_TYPES = dtol_lookups_data.TOL_PROFILE_TYPES


class Command(BaseCommand):
    # The following information is shown when a user types "help"
    help = "Extract/parse \"SPECIMEN_ID\" from an .xlsx file then, retrieve metadata from COPO database based on the " \
           "data and output the result in  a .json format"

    def __init__(self):
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument("xlsx", type=str)

    def parse_db_data_to_json(self, data_in_db, json_filename):
        datetime_fields = ["date_modified", "time_created", "time_updated"]
        df_list = []
        data = json.loads(json_util.dumps(data_in_db))

        for sample in data[0]:
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

                    # Convert datetime from milliseconds to timestamp
                    field_value = datetime.fromtimestamp(field_value / 1000.0, tz=timezone.utc).strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    sample[key] = field_value

            # Create a dictionary that maps the COPO database field name (i.e. old key)
            # to the ENA field name (i.e. new key)
            copo_and_ena_field_names_dict = {key: value['ena'] for key, value in DTOL_ENA_MAPPINGS.items() if
                                             key in list(sample.keys())}

            # Replace each COPO database field name with the corresponding ENA field name
            # in the sample dictionary
            for key, value in list(sample.items()):
                sample[copo_and_ena_field_names_dict.get(key, key)] = sample.pop(key)

            # length_of_data_list = 35 if "biospecimens" in json_filename else 128  # ternary operator
            # assert length_of_data_list == len(list(sample.keys()))
            df = pd.DataFrame(data=[list(sample.values())], columns=list(sample.keys()))
            df_list.append(df)

        concat_df = pd.concat(df_list, ignore_index=True)  # Concatenate all the datafarmes
        concat_df.to_json(json_filename)

    # A command must define handle()
    def handle(self, *args, **options):
        file_path_dict = ast.literal_eval(str(options))
        excel_file_path = file_path_dict.get("xlsx")
        try:
            open_workbook(excel_file_path)
            df = pd.read_excel(excel_file_path)  # Convert excel file to a Python Pandas dataframe
            rows_list = df.to_dict('records')  # Get all rows from the excel spreadsheet
            pattern_without_prefix = "EMu/\d{9}"
            pattern_with_prefix = "EMu/NHMUK\d{9}"  # "SPECIMEN_ID" field begins with the prefix - "NHMUK"
            pattern_with_Emu_only = "EMu/"

            # Iterate through each row in the spreadsheet to retrieve the "SPECIMEN_ID"
            specimen_id_list = []

            print("Commence parsing SPECIMEN_ID from spreadsheet...")

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

            print("Finish parsing SPECIMEN_ID from spreadsheet...")

            assert len(specimen_id_list) == 2138

            specimen_ids_not_in_db = []
            samples_only_in_db = []
            sources_only_in_db = []
            samples_and_sources_in_db = []
            # specimen_id_list = ["MBA-190930-001A", "MBA-190930-001B", "MBA-190930-099Q", "EDTOLQ0405"]

            for specimen in specimen_id_list:
                print("Iterating through specimen: ..")

                sample_in_db = cursor_to_list(Sample().get_sample_by_specimen_id(specimen))
                source_in_db = da.Source().get_by_specimen(specimen)

                if not sample_in_db and not source_in_db:
                    specimen_ids_not_in_db.append(specimen)
                elif sample_in_db:
                    samples_only_in_db.append(sample_in_db)
                elif source_in_db:
                    sources_only_in_db.append(source_in_db)
                else:
                    # if sample_in_db and source_in_db
                    samples_and_sources_in_db.append(sample_in_db)
                    samples_and_sources_in_db.append(source_in_db)

            # Convert list of "SPECIMEN_ID" not present in COPO to json format
            if specimen_ids_not_in_db:
                print("Processing specimen_ids that are not found in the database...")
                specimen_ids_df = pd.DataFrame(data=[[specimen_ids_not_in_db]], columns=["SPECIMEN_ID"])
                specimen_ids_df.to_json('specimen_ids_not_present_in_copo_from_nhmdump_excel.json')

            # Parse db list of dictionary data to json
            if samples_only_in_db:
                # Samples only
                print("Processing samples only...")
                self.parse_db_data_to_json(samples_only_in_db, 'copo_biosamples_from_spreadsheet_excel.json')

            if sources_only_in_db:
                # Sources only
                print("Processing sources only...")
                self.parse_db_data_to_json(sources_only_in_db, 'copo_biospecimens_from_spreadsheet_excel.json')

            if samples_and_sources_in_db:
                # Samples and sources....if sample_in_db and source_in_db
                print("Processing samples and sources...")
                self.parse_db_data_to_json(samples_and_sources_in_db,
                                           'copo_biosamples_and_biosources_from_nhmdump_spreadsheet.json')

            if not samples_only_in_db and not sources_only_in_db and not samples_and_sources_in_db:
                print("*********************************")
                print("Error: Data in the .xlsx file do not correspond to any data in the database!")
                print("*********************************")

            print("SPECIMEN_IDS not in db: ", specimen_ids_not_in_db)
            print("\n******************************************************\n")

            print("Samples in db: ", samples_only_in_db)
            print("\n***************************************\n")

            print("Sources in db: ", specimen_ids_not_in_db)
            print("\n****************************************************\n")

            print("Samples and surces in db: ", samples_and_sources_in_db)
            print("\n****************************************")

        except XLRDError as error:
            print("Error: ", error)

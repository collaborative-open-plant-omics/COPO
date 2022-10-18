from dal import cursor_to_list
from dal.copo_da import Sample
from django.conf import settings as settings
from django.core.management import BaseCommand
from xlrd import open_workbook, XLRDError
import dal.copo_da as da
import numpy as np
import pandas as pd
import ast
import dal.copo_da as da
import importlib
import pandas as pd
import re
import xml.etree.cElementTree as ET

# samplesindb = da.Sample().get_by_biosample_ids(list(d_updates.keys()))
#
# # if there's source update it
# if sample.get("sampleDerivedFrom", ""):
#     source_biosample = sample.get("sampleDerivedFrom")
# elif sample.get("sampleSameAs", ""):
#     source_biosample = sample.get("sampleSameAs")
# else:
#     source_biosample = ""
# if source_biosample:
#     sourceindb = da.Source().get_by_field("biosampleAccession", source_biosample)
#     assert len(sourceindb) == 1
#     for field in d_updates[sample['biosampleAccession']]:
#         # only update in source fields that are there -ENA submittable- and not organism part
#         # unique handling of COLLECTION_LOCATION
#         if field == "COLLECTION_LOCATION":
#             value = d_updates[sample['biosampleAccession']][field]
#             da.Source().record_manual_update(field, oldvalue, value, sourceindb[0]['_id'])
#         elif field != "ORGANISM_PART" and DTOL_ENA_MAPPINGS.get(field, ""):
#             value = d_updates[sample['biosampleAccession']][field]
#             da.Source().record_manual_update(field, oldvalue, value, sourceindb[0]['_id'])
#         da.Source().add_field(field, value, sourceindb[0]['_id'])


# manifest_id = options["manifest_id"]
# fromdb = da.handle_dict["sample"].count({"manifest_id": manifest_id, "status": "processing"})
# print("samples stuck: " + str(fromdb))
# fromdb = da.handle_dict["sample"].update_many({"manifest_id": manifest_id, "status": "processing"},
#                                               {"$set": {"status": "pending"}})
# print("samples unstuck: " + str(fromdb.modified_count))
# print("done")

schema_version_path_dtol_lookups = f'web.apps.web_copo.schema_versions.{settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
dtol_lookups_data = importlib.import_module(schema_version_path_dtol_lookups)
DTOL_ENA_MAPPINGS = dtol_lookups_data.DTOL_ENA_MAPPINGS

'''
Extract "SPECIMEN_ID" value from a Excel spreadsheet then, retrieve the sample metadata 
from the COPO database using the "SPECIMEN_ID"

Output the result in a .json file

e.g. python3 manage.py parse_xlsx_to_json "/usr/users/EI_ga012/providen/Downloads/nhmdump.xlsx"
'''


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
        excel_file_path = file_path_dict.get(
            "xlsx")  # '/usr/users/EI_ga012/providen/Downloads/DToL_sample_output_220930.xml'
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

            print("Specimen IDs from excel file: ", specimen_id_list)
            print("Number of Specimen IDs in the list: ", len(specimen_id_list))
            assert 2138 == len(specimen_id_list)  # Number of SPECIMEN_IDs is equal to 2138
            # biosample_and_specimen_id_list =
            sample_list = []
            specimen_ids_not_in_db = []
            samples_only_in_db = []
            sources_only_in_db_list = []
            samples_and_sources_in_db = []
            for specimen in specimen_id_list:
                sample_in_db = cursor_to_list(Sample().get_collection_handle().find({"SPECIMEN_ID": specimen}))
                source_in_db = cursor_to_list(da.Source().get_collection_handle().find({"SPECIMEN_ID": specimen}))
                #  source = sample == [] ? cursor_to_list(Source().get_collection_handle().find({"SPECIMEN_ID": specimen})) : sample
                sample_list.append(cursor_to_list(Sample().get_collection_handle().find(
                    {"SPECIMEN_ID": specimen})))

                if sample_in_db == [] and source_in_db == []:
                    specimen_ids_not_in_db.append(specimen)
                elif sample_in_db != [] and source_in_db == []:
                    samples_only_in_db.append(sample_in_db)
                elif sample_in_db == [] and source_in_db != []:
                    sources_only_in_db_list.append(source_in_db)
                else:
                    # sample_in_db != [] and source_in_db != []
                    samples_and_sources_in_db.append(sample_in_db)
                    samples_and_sources_in_db.append(source_in_db)
            print("List of samples in db: ", sample_list)
            print("List of specimens not found in db: ", specimen_ids_not_in_db)
            print("List of samples found in db: ", samples_only_in_db)
            print("List of sources found in db: ", sources_only_in_db_list)
            print("List of samples and sources found in db: ", samples_and_sources_in_db)

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

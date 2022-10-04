from django.conf import settings as settings
from django.core.management import BaseCommand

import dal.copo_da as da
import numpy as np
import pandas as pd
import importlib
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


class Command(BaseCommand):
    # The following information is shown when a user types "help"
    help = "Extract/parse data from an xml file then, upload its data to the COPO database"

    def __init__(self):
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument('xml', type=str)

    # A command must define handle()
    def handle(self, *args, **options):
        xml_file = str(options)

        # Parse xml file
        try:
            field_values = []
            tree = ET.parse(xml_file)
            root = tree.getroot()

            accession_list = [accession.text for accession in root.iter('PRIMARY_ID')]
            sample_alias_list = [accession.text for accession in root.iter('SUBMITTER_ID')]  # or SUBMITTER_ID
            title_list = [accession.text for accession in root.iter('TITLE')]
            taxon_ID_list = [accession.text for accession in root.iter('TAXON_ID')]
            scientific_name_list = [accession.text for accession in root.iter('SCIENTIFIC_NAME')]

            # SAMPLE_ATTRIBUTE within <SAMPLE_ATTRIBUTES></SAMPLE_ATTRIBUTES> tag
            for sampleAttribute in root.findall('SAMPLE_ATTRIBUTE'):
                field = sampleAttribute.find('TAG')
                value = sampleAttribute.find('VALUE')
                if field is None and value is None:
                    print("Field and its value does not exist for the sample attribute")
                else:
                    # Get the database field name based on the 'ena' key in the "DTOL_ENA_MAPPINGS" dictionary
                    fields = [field for field, field_value in DTOL_ENA_MAPPINGS.items() if
                              field_value['ena'] == field.text]
                    field_values.append(value.text)

        except ET.ParseError:
            # If xml file is empty
            print(ET.ParseError.msg)

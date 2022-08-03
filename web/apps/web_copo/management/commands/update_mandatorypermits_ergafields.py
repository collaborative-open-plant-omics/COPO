from django.core.management import BaseCommand
from web.apps.web_copo.utils.dtol.Dtol_Submission import build_specimen_sample_xml,\
    build_bundle_sample_xml, update_bundle_sample_xml
import xml.etree.ElementTree as ET
import subprocess
from tools import resolve_env
import os
from web.apps.web_copo.lookup.dtol_lookups import DTOL_ENA_MAPPINGS

import dal.copo_da as da



# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    help="update pilot ERGA samples to rename *MANDATORY fields" \
         "with *REQUIRED to comply with version 2.4 updates, keeping old fields too"

    def __init__(self):
        self.TO_UPDATE_FIELDS = {"ETHICS_PERMITS_MANDATORY" : "ETHICS_PERMITS_REQUIRED", "SAMPLING_PERMITS_MANDATORY" :
                                "SAMPLING_PERMITS_REQUIRED",
                               "NAGOYA_PERMITS_MANDATORY": "NAGOYA_PERMITS_REQUIRED"}

    # A command must define handle()
    def handle(self, *args, **options):
        samples_to_update = da.Sample().get_by_project_and_field("ERGA", "manifest_version", ["pilot"])
        for sample in samples_to_update:
            print(sample.get("_id", ""))
            for field in self.TO_UPDATE_FIELDS:
                da.Sample().add_field(self.TO_UPDATE_FIELDS[field], sample.get(field), sample['_id'])

from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from web.apps.web_copo.models import Repository
from dal.copo_da import TestObjectType
from datetime import datetime
import random


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Command to setup.sh COPO groups"

    # A command must define handle()
    def handle(self, *args, **options):

        TestObjectType().get_collection_handle().remove({})
        types = ["ASG", "DTOL", "other"]
        sexes = ["MALE", "FEMALE", "other", "bipedal", "oversized"]
        lifestages = ["egg", "juvenile", "adult", "spawn", "kid", "old"]
        gals = ["Edinburgh", "Kew"]
        for x in range(0, 5000):
            rand = random.randint
            type = types[rand(0, len(types) - 1)]
            sex = sexes[rand(0, len(sexes) - 1)]
            lifestage = lifestages[rand(0, len(lifestages) - 1)]
            gal = gals[rand(0, len(gals) - 1)]
            now = datetime.now()
            t_sample = {
                "COLLECTED_BY": "GAwIN BROADsword",
                "DATE_OF_COLLECTION": "2020-08-27",
                "SEX": sex,
                "LIFESTAGE": lifestage,
                "IDENTIFIED_BY": "GAVIN BROAD",
                "IDENTIFIER_AFFILIATION": "NATURAL HISTORY MUSEUM",
                "SPECIMEN_ID": "NHMUK010635090",
                "COLLECTOR_AFFILIATION": "NATURAL HISTORY MUSEUM",
                "HAZARD_GROUP": "HG1",
                "REGULATORY_COMPLIANCE": "Y",
                "COLLECTION_LOCATION": "UNITED KINGDOM | ENGLAND | HEVER CASTLE",
                "DECIMAL_LATITUDE": "51.188",
                "DECIMAL_LONGITUDE": "0.12",
                "GRID_REFERENCE": "",
                "HABITAT": "WOODLAND | LAKE | GRASSLAND",
                "DEPTH": "",
                "ELEVATION": "",
                "DESCRIPTION_OF_COLLECTION_METHOD": "LIGHT TRAP",
                "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE": "NOT_APPLICABLE",
                "DATE_OF_PRESERVATION": "2020-08-27",
                "TIME_OF_COLLECTION": "",
                "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION": "0.5",
                "PRESERVATION_APPROACH": "DRY ICE",
                "PRESERVATIVE_SOLUTION": "none",
                "RACK_OR_PLATE_ID": "FE00372985",
                "TUBE_OR_WELL_ID": "FR25594795",
                "GAL": gal,
                "PARTNER": "",
                "PARTNER_SAMPLE_ID": "",
                "GAL_SAMPLE_ID": "NHMUK010635090",
                "COLLECTOR_SAMPLE_ID": "NHMUK010635090",
                "PRESERVED_BY": "LAURA SIVESS",
                "PRESERVER_AFFILIATION": "NATURAL HISTORY MUSEUM",
                "ORGANISM_PART": "HEAD",
                "SYMBIONT": "",
                "species_list": [
                    {
                        "SYMBIONT": "TARGET",
                        "TAXON_ID": "987431",
                        "ORDER_OR_GROUP": "LEPIDOPTERA",
                        "FAMILY": "NOCTUIDAE",
                        "GENUS": "XESTIA",
                        "SCIENTIFIC_NAME": "Xestia c-nigrum",
                        "INFRASPECIFIC_EPITHET": "",
                        "CULTURE_OR_STRAIN_ID": "",
                        "COMMON_NAME": "SETACEOUS HEBREW CHARACTER",
                        "TAXON_REMARKS": ""
                    }
                ],
                "RELATIONSHIP": "",
                "IDENTIFIED_HOW": "Morphology",
                "SPECIMEN_ID_RISK": "N",
                "TEMPERATURE": "",
                "SALINITY": "",
                "PH": "",
                "CHLA": "",
                "LIGHT_INTENSITY": "",
                "DISOLVED_OXYGEN": "",
                "OTHER_INFORMATION": "",
                "rack_tube": "FE00372985/FR25594795",
                "SPECIES_RARITY": "",
                "GENOME_SIZE": "",
                "SIZE_OF_TISSUE_IN_TUBE": "M",
                "TISSUE_REMOVED_FOR_BARCODING": "Y",
                "PLATE_ID_FOR_BARCODING": "C9N05RAP",
                "TUBE_OR_WELL_ID_FOR_BARCODING": "A5",
                "SERIES": "1",
                "TISSUE_FOR_BARCODING": "LEG",
                "BARCODE_PLATE_PRESERVATIVE": "Ethanol",
                "PURPOSE_OF_SPECIMEN": "REFERENCE_GENOME",
                "VOUCHER_ID": "NOT_PROVIDED",
                "characteristics": [],
                "factorValues": [],
                "sample_type": "dtol",
                "profile_id": "5ff5ec54f473c7fb2b619c9b",
                "manifest_id": "cb183f4c-3ace-4de7-9da3-9e8e2e2eba7d",
                "biosampleAccession": "",
                "sraAccession": "",
                "submissionAccession": "",
                "status": "pending",
                "tol_project": type,
                "manifest_version": 2.2,
                "public_name": "ilXesCnig1",
                "name": "",
                "organism": "",
                "derivesFrom": "",
                "deleted": "0",
                "date_modified": now,
                "created_by": "felix.shaw@tgac.ac.uk",
                "time_created": now
            }
            if x % 15 == 0:
                t_sample.pop("GAL")
                t_sample["PARTNER"] = gal
                print(x)
            TestObjectType().get_collection_handle().insert(t_sample)

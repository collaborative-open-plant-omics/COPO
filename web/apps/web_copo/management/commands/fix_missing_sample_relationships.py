from Bio import Entrez
from dal import cursor_to_list
from dal.copo_da import Sample
from django.core.management import BaseCommand
from tools import resolve_env
from web.apps.web_copo.lookup.dtol_lookups import DTOL_ENA_MAPPINGS
from web.apps.web_copo.management.commands import update_samplefield
from web.apps.web_copo.utils.dtol.Dtol_Submission import build_specimen_sample_xml
import dal.copo_da as da
import re
import subprocess


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    help = "Fix missing relationships between sample specimens"
    Entrez.email = "copo@earlham.ac.uk"

    def __init__(self):
        self.TAXONOMY_FIELDS = ["TAXON_ID", "ORDER_OR_GROUP", "FAMILY", "GENUS",
                                "SCIENTIFIC_NAME", "COMMON_NAME", "TAXON_REMARKS",
                                "INFRASPECIFIC_EPITHET"]
        self.rankdict = {
            "order": "ORDER_OR_GROUP",
            "family": "FAMILY",
            "genus": "GENUS"
        }
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.ena_service = resolve_env.get_env('ENA_SERVICE')  # 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/'
        self.ena_sample_retrieval = self.ena_service[:-len(
            'submit/')] + "samples/"  # https://devwww.ebi.ac.uk/ena/submit/drop-box/samples/" \

    # A command must define handle()
    def handle(self, *args, **options):
        """ Find the list of biosamples that have no relationship"""
        samples_in_db = cursor_to_list(Sample().get_collection_handle().find(
            {"status": "accepted", "tol_project": {"$in": ["DTOL", "ASG"]}, "sampleDerivedFrom": {"$exists": False},
             "sampleSameAs": {"$exists": False}, "sampleSymbiontOf": {"$exists": False},
             "biosampleAccession": {"$ne": ""}}))

        # Get all the biosamples to be updated based on the value of the field, "biosampleAccession"

        updates_to_make = [x['biosampleAccession'] for x in samples_in_db]
        print("biosampleAccession: ", updates_to_make)

        """ Check if the biosample has a source that has an  accession """

        # Check if the source of a sample has an accession already
        for sample in samples_in_db:
            specimen_id = sample['SPECIMEN_ID']
            print("SPECIMEN_ID: ", specimen_id)
            # Get source object based on the field, "specimen_ID"
            source_object = da.Source().get_by_specimen(specimen_id)

            # Sources should only result in one object
            assert len(source_object) == 1

            # Check if "biosampleAccession" field and "sraAccession" field exist in the source object
            if source_object[0]["biosampleAccession"] and source_object[0]["sraAccession"]:
                print("\"biosampleAccession\" and \"sraAccession\" fields exist")
                organism_part = sample['ORGANISM_PART']
                species_list = sample['species_list'][0]

                if species_list["SYMBIONT"] == "SYMBIONT":
                    biosample_relationship_field = "sampleSymbiontOf"
                elif species_list["SYMBIONT"] == "TARGET" and organism_part != "WHOLE_ORGANISM":
                    biosample_relationship_field = "sampleDerivedFrom"
                else:
                    # If the value of the field, "ORGANISM_PART", is equal to "WHOLE_ORGANISM"
                    biosample_relationship_field = "sampleSameAs"

                # Insert the missing relationship of the biosample by calling the "update_samplefield.py" script
                relationship_value = source_object[0]["biosampleAccession"]
                update_relationship_command = f"{sample['biosampleAccession']}:{biosample_relationship_field}:{relationship_value} "

                # Instantiate the Command() before using it
                command = update_samplefield.Command()
                command.handle(samples=update_relationship_command)

            else:
                print("biosampleAccession field and sraAccession field do not exist")

                """ Access the ENA production webinar Portal to get the values of the "biosampleAccession" and the "accession"""

                error_to_parse = source_object[0]["error"]
                if "The object being added already exists in the submission account with accession" in error_to_parse:
                    # Catch alias and accession
                    pattern_accession = "ERS\d{7}"
                    accession = re.search(pattern_accession, error_to_parse).group()

                    curl_cmd = "curl -u " + self.usertoken + \
                               ':' + self.pass_word + " " + self.ena_sample_retrieval \
                               + accession
                    xml_sample_submitted_on_ENA = subprocess.check_output(curl_cmd, shell=True)
                else:
                        #todo edge case where there's no error, or error in different format than expected
                        pass



                # The "submissionAccession"field is lost so the value, "ERA000000", is entered as the default value
                # in order for it to be consistent with an actual value for "submissionAccession"

                # da.Source().add_field("submissionAccession", "ERA000000", specimen_id)
                # da.Source().add_field("error1", "Wrong submission accession entered manually for db consistency",
                #                       specimen_id)

                # do curl command like line 109 update_sample in update_samplefield.py which return an xml with the information that ENA has
                # work with biosample and sra accession
                # parse the error to get the sra accession
                # the error should be there
                # ....it starts with "ERA"
                # Retrieve the submitted XML of the sample from ENA service
                # Get error field from the source





        return


        d_updates = {}

        for update in updates_to_make:
            sample = update.strip()
            if sample not in d_updates:
                d_updates[sample] = {}

        # Retrieve sample from db
        print(type(list(d_updates.keys())))
        print("List of keys from database: ", list(d_updates.keys()))
        samples_in_db = da.Sample().get_by_biosample_ids(list(d_updates.keys()))

        if len(samples_in_db) < len(list(d_updates.keys())):
            print("**********************************************************************************")
            print("One or more samples could not be found")

            biosample_accessions_found = [sample.get("biosampleAccession") for sample in samples_in_db]
            diff = [x for x in list(d_updates.keys()) if x not in biosample_accessions_found]

            for element in diff:
                print(element, " may be a Source object")

            print("**********************************************************************************")

        for sample in samples_in_db:
            """" 
                Check if the following fields exists for each sample: 
                "sampleDerivedFrom","sampleSameAs","sampleSymbiontOf","error",
                "error1","SPECIMEN_ID", "ORGANISM_PART" and "species_list" 
            """

            for field in d_updates[sample['biosampleAccession']]:
                # Find a biosample based on the field, "SPECIMEN_ID"
                sample_record_based_on_specimen_id = d_updates[sample['biosampleAccession']]["SPECIMEN_ID"]
                assert len(sample_record_based_on_specimen_id) == 1

                value = d_updates[sample['biosampleAccession']][field]
                oldvalue = da.Sample().get_record(sample['_id']).get(field, "")
                da.Sample().record_manual_update(field, oldvalue, value, sample['_id'])
                da.Sample().add_field(field, value, sample['_id'])

                # Determine the relationship of the biosample
                organism_part_field = sample['biosampleAccession']["ORGANISM_PART"]
                species_list_field = sample['biosampleAccession']["species_list"]

                if species_list_field["SYMBIONT"] == "SYMBIONT":
                    biosample_relationship_field = "sampleSymbiontOf"
                elif species_list_field["SYMBIONT"] == "TARGET" and organism_part_field != "WHOLE_ORGANISM":
                    biosample_relationship_field = "sampleDerivedFrom"
                else:
                    # If the value of the field, "ORGANISM_PART", is equal to "WHOLE_ORGANISM",
                    biosample_relationship_field = "sampleSameAs"

            # Find the source object based on the field, "SPECIMEN_ID" then, update its relationship
            source_biosample = sample.get("SPECIMEN_ID")
            source_object_in_db = da.Source().get_by_field("biosampleAccession", source_biosample)
            assert len(source_object_in_db) == 1

            for field in d_updates[sample['biosampleAccession']]:
                # Update the following source fields: "biosampleAccession" field, "sraAccession" field,
                # "submissionAccession" field and "error1" field

                if field == "biosampleAccession":
                    biosample_relationship_value_from_ena = DTOL_ENA_MAPPINGS.get(field)
                    # value = d_updates[sample['biosampleAccession']][field]
                    da.Source().record_manual_update(field, "", biosample_relationship_value_from_ena,
                                                     source_object_in_db[0]['SPECIMEN_ID'])
                elif field == "sraAccession":
                    biosample_relationship_value_from_ena = DTOL_ENA_MAPPINGS.get(field)
                    da.Source().record_manual_update(field, "", biosample_relationship_value_from_ena,
                                                     source_object_in_db[0]['SPECIMEN_ID'])

                # The "submissionAccession"field is lost so the value, "ERA000000", is entered as the default value
                # in order to be consistent with an actual value for "submissionAccession"

                da.Source().add_field("submissionAccession", "ERA000000", source_object_in_db[0]['SPECIMEN_ID'])
                da.Source().add_field("error1", "Wrong submission accession entered manually for db consistency",
                                      source_object_in_db[0]['SPECIMEN_ID'])

                # Update the relationship of the biosample by using the update_samplefield.py script
                update_relationship_command = f"{sample['biosampleAccession']['biosampleAccession']}:{biosample_relationship_field}:{biosample_relationship_value_from_ena} "

                update_samplefield.Command().handle(samples=update_relationship_command)


            # If fields are submitted to ENA, update them
            # print(d_updates[sample['biosampleAccession']])
            # print(list(d_updates[sample['biosampleAccession']].keys()))
            # flag = False
            # for field in list(d_updates[sample['biosampleAccession']].keys()):
            #     if DTOL_ENA_MAPPINGS.get(field, "") or field == "COLLECTION_LOCATION":
            #         flag = True
            # if flag:
            #     self.update_sample(sample['_id'])
            #     if source_biosample:
            #         self.update_source(source_object_in_db[0]['_id'])

    # def update_sample(self, sample):
    #     # Update ENA record
    #     updated_record = da.Sample().get_record(sample)
    #     # retrieve submitted XML for sample
    #     curl_cmd = "curl -u " + self.user_token + \
    #                ':' + self.pass_word + " " + self.ena_sample_retrieval \
    #                + updated_record['biosampleAccession']
    #     registered_sample = subprocess.check_output(curl_cmd, shell=True)
    #
    #     # self.update_samplexml(registered_sample, updated_record['biosampleAccession'])
    #     build_bundle_sample_xml(str(updated_record['_id']))
    #     update_bundle_sample_xml([updated_record['_id']], "bundle_" + str(updated_record['_id']) + ".xml")
    #     print(updated_record['_id'])
    #     self.modify_sample(updated_record['_id'])
    #
    def update_source(self, source):
        # Update ENA record
        updated_record = da.Source().get_record(source)
        # retrieve submitted XML for sample
        curl_cmd = "curl -u " + self.user_token + \
                   ':' + self.pass_word + " " + self.ena_sample_retrieval \
                   + updated_record['biosampleAccession']
        registered_source = subprocess.check_output(curl_cmd, shell=True)

        # self.update_samplexml(registered_source, updated_record['biosampleAccession'])
        build_specimen_sample_xml(updated_record)
        self.modify_sample(updated_record['_id'])
    #
    # def modify_sample(self, id):
    #     fileis = "bundle_" + str(id) + ".xml"
    #     curl_cmd = 'curl -u ' + self.user_token + ':' + self.pass_word \
    #                + ' -F "SUBMISSION=@modifysubmission.xml' \
    #                + '" -F "SAMPLE=@' \
    #                + fileis \
    #                + '" "' + self.ena_service \
    #                + '"'
    #     try:
    #         receipt = subprocess.check_output(curl_cmd, shell=True)
    #         print(receipt)
    #     except Exception as e:
    #         message = 'API call error ' + "Submitting xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
    #             self.pass_word, "xxxxxx")
    #         print(message)
    #         return False
    #
    #    os.remove(fileis)

    # > db.SampleCollection.count({"status":"accepted","tol_project":{"$in":["DTOL","ASG"]},"sampleDerivedFrom":{
    # "$exists":false},"sampleSameAs":{"$exists":false},"sampleSymbiontOf":{"$exists":false}, "biosampleAccession": {
    # "$ne":""}}) 85

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
import xml.etree.ElementTree as element_tree

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

    def get_sample_relationship(self, sample, source_object):
        organism_part = sample['ORGANISM_PART']
        species_list = sample['species_list'][0]

        if species_list["SYMBIONT"] == "SYMBIONT":
            biosample_relationship_field = "sampleSymbiontOf"
        elif species_list["SYMBIONT"] == "TARGET" and organism_part != "WHOLE_ORGANISM":
            biosample_relationship_field = "sampleDerivedFrom"
        else:
            # If the value of the field, "ORGANISM_PART", is equal to "WHOLE_ORGANISM"
            biosample_relationship_field = "sampleSameAs"

        return biosample_relationship_field

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
            # Instantiate the Command() before using it
            command = update_samplefield.Command()

            # Check if "biosampleAccession" field and "sraAccession" field exist in the source object
            if source_object[0]["biosampleAccession"] and source_object[0]["sraAccession"]:
                print("\"biosampleAccession\" and \"sraAccession\" fields exist")

                biosample_relationship_field = self.get_sample_relationship(sample, source_object)

                # Insert the missing relationship of the biosample by calling the "update_samplefield.py" script
                relationship_value = source_object[0]["biosampleAccession"]
                update_relationship_command = f"{sample['biosampleAccession']}:{biosample_relationship_field}:{relationship_value} "

                command.handle(samples=update_relationship_command)

            else:
                print("\"biosampleAccession\" field and \"sraAccession\" field do not exist but an error exists")

                """Access the ENA production webinar Portal to get the values of the "biosampleAccession" and the 
                "accession"""

                error_to_parse = source_object[0]["error"]
                if "The object being added already exists in the submission account with accession" in error_to_parse:
                    # Catch alias and accession
                    pattern_accession = "ERS\d{7}"
                    sraAccession = re.search(pattern_accession, error_to_parse).group()

                    curl_cmd = "curl -u " + self.user_token + \
                               ':' + self.pass_word + " " + self.ena_sample_retrieval \
                               + sraAccession
                    print("sraAccession: ", sraAccession)
                    xml_source_submitted_on_ENA = subprocess.check_output(curl_cmd, shell=True)
                    print("XML Sample from ENA: ", xml_source_submitted_on_ENA)

                    """" Parse xml to retrieve the biosample accession"""
                    self.retrieve_accession_from_ena(xml_source_submitted_on_ENA)


                    # Update the "SourceCollection" with values for the fields:
                    # "biosampleAccession", "sraAccession", "submissionAccession" and "error1"

                    # The value of the "submissionAccession" field is lost so the value, "ERA000000",
                    # is entered as the default value in order for it to be consistent with an
                    # actual value for the "submissionAccession"

                    da.Source().add_field("sraAccession", sraAccession, source_object[0]["_id"])
                    da.Source().add_field("submissionAccession", "ERA000000", source_object[0]["_id"])
                    da.Source().add_field("error1", "Wrong submission accession entered manually for db consistency",
                                          source_object[0]["_id"])

                    biosample_relationship_field = self.get_sample_relationship(sample, source_object)

                    # Insert the missing relationship of the biosample by calling the "update_samplefield.py" script
                    relationship_value = source_object[0]["biosampleAccession"]
                    update_relationship_command = f"{sample['biosampleAccession']}:{biosample_relationship_field}:{relationship_value} "

                    command.handle(samples=update_relationship_command)

                else:
                    # If "error" field does not exist or the error is in a different format than expected

                    print('******************************')
                    print('Look at sample with biosampleAccesion {} to determine what the error might be., '.format(sample['biosampleAccession']))
                    print('******************************')



    # > db.SampleCollection.count({"status":"accepted","tol_project":{"$in":["DTOL","ASG"]},"sampleDerivedFrom":{
    # "$exists":false},"sampleSameAs":{"$exists":false},"sampleSymbiontOf":{"$exists":false}, "biosampleAccession": {
    # "$ne":""}}) 85


    def retrieve_accession_from_ena(xml):
        root = element_tree.parse(xml)
        accession = ''
        #  find and retrieve biosample accession
        # Look at xml format in the DTOLSubmission class to get how to retrieve a value of a tag for the accession
        # biosample accession is in ena#
        # use the links sent to try see if the biosample can be retrieved on MS Teams
        # Use what is already uplaoded on the ENA website
        # https://www.ebi.ac.uk/ena/xref/rest/tsv/search?accession=AY772730
        # https://www.ebi.ac.uk/ena/portal/api/results?dataPortal=ena
        # https://www.ebi.ac.uk/ena/portal/api/searchFields?result=read_run
        # https://www.ebi.ac.uk/ena/portal/api/returnFields?result=read_run
        # https:/www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=country="United Kingdom" AND host_tax_id=9913 AND host_body_site="rumen"&fields=sample_accession
        #

        # https://wwwdev.ebi.ac.uk/ena/submit/webin/report/samples/search?accession=ERS12154896
        # https://wwwdev.ebi.ac.uk/ena/submit/webin/report/samples/search?source=COMPARE-RefGenome&accession=ERS12154896

        # https://wwwdev.ebi.ac.uk/ena/portal/api/searchFields?result=read_run
        # https://wwwdev.ebi.ac.uk/ena/portal/api/returnFields?result=read_run


        # https://wwwdev.ebi.ac.uk/ena/portal/api/search?result=read_run&query=accession="ERS12154896"&fields=sample_accession


        return xml.parse('accession')



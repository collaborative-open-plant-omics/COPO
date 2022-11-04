from django.core.management import BaseCommand
from Bio import Entrez
from web.apps.web_copo.utils.dtol.Dtol_Submission import build_specimen_sample_xml,\
    build_bundle_sample_xml, update_bundle_sample_xml
import xml.etree.ElementTree as ET
import subprocess
from tools import resolve_env
import os
from web.apps.web_copo.lookup.dtol_lookups import DTOL_ENA_MAPPINGS
import json

import dal.copo_da as da

'''this is a script to solve the issue observed in db
in which there are sources with different specimen ids, sra accessions
and submission accessions, but somehow the biosample accession 
is duplicated.  The script takes as input a comma separated list of biosample
accessions to check. The list of sources can be found as:
db.SourceCollection.aggregate([{"$group":{"_id": "$biosampleAccession", "count" : {"$sum":1}}}, 
{"$match": {"$count": {"$gt":1}}}]).toArray()'''


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    help="correct sources with duplicated biosampleAccession -" \
         "provide comma separated list of duplicated biosample accessions in sources"
    Entrez.email = "copo@earlham.ac.uk"

    def __init__(self):
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.ena_service = resolve_env.get_env('ENA_SERVICE')  # 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/'
        self.ena_sample_retrieval = self.ena_service[:-len(
            'submit/')] + "samples/"  # https://devwww.ebi.ac.uk/ena/submit/drop-box/samples/" \
        self.ena_report = resolve_env.get_env('ENA_ENDPOINT_REPORT')


    def add_arguments(self, parser):
        parser.add_argument('accessions', type=str)

    # A command must define handle()
    def handle(self, *args, **options):
        updates_to_make = options['accessions'].split(",")
        print(updates_to_make)
        #query ENA to identify correct specimen id to be associated with biosample accession
        for accession in updates_to_make:
            #todo it's possible isntead of this use the receipt command to get the alias, which is the COPO _id
            curl_cmd = "curl -u " + self.user_token + \
                       ':' + self.pass_word + " " + self.ena_sample_retrieval \
                       + accession
            registered_source = subprocess.check_output(curl_cmd, shell=True)
            #print(registered_source)
            root = ET.fromstring(registered_source)
            for sample in root.findall("SAMPLE"):
                for attributeset in sample.findall("SAMPLE_ATTRIBUTES"):
                    for att in attributeset.findall("SAMPLE_ATTRIBUTE"):
                        if att.find("TAG").text == "specimen_id":
                            correct_specimen = att.find("VALUE").text
            print("************************************************************************\n")
            print("correct SPECIMEN_ID for biosample ", accession, " is ", correct_specimen)
            print("\n************************************************************************\n")
            source_list = da.Source().get_by_field("biosampleAccession", accession)
            for possible_source in source_list:
                if possible_source["SPECIMEN_ID"]==correct_specimen:
                    pass
                else:
                    specimen_to_correct = possible_source["SPECIMEN_ID"]
                    #retrieve information from the SRA accession instead
                    curl_cmd = 'curl -m 300 -u ' + self.user_token + ':' + self.pass_word \
                               + ' ' + self.ena_report \
                               + possible_source["sraAccession"]
                    #print(curl_cmd)
                    ena_receipt = subprocess.check_output(curl_cmd, shell=True)
                    #print(ena_receipt)
                    report = json.loads(ena_receipt.decode('utf8').replace("'",'"'))
                    correct_biosample = report[0]["report"].get("secondaryId", "")
                    print("************************************************************************\n")
                    print("source with SPECIMEN_ID ", specimen_to_correct, " correct biosample is ", correct_biosample)
                    print("\n************************************************************************\n")

                    value = correct_biosample
                    oldvalue = accession
                    da.Source().record_manual_update("biosampleAccession", oldvalue, value, possible_source['_id'])
                    da.Source().add_field("biosampleAccession", value, possible_source['_id'])
                    #correct children samples
                    #identify all samples to be corrected
                    samples_to_correct = da.Sample().get_sample_by_specimen_id(specimen_to_correct)
                    for sample in samples_to_correct:
                        #todo local update in db as for source
                        if sample["ORGANISM_PART"] == "WHOLE_ORGANISM":
                            print("HERE**********************************************************8")
                            #the relationship to update is sampleSameAs
                            da.Sample().record_manual_update("sampleSameAs", oldvalue, value, sample["_id"])
                            da.Sample().add_field("sampleSameAs", value, sample["_id"])
                        else:
                            #the relationship to update is sampleDerivedFrom
                            da.Sample().record_manual_update("sampleDerivedFrom", oldvalue, value, sample["_id"])
                            da.Sample().add_field("sampleDerivedFrom", value, sample["_id"])
                        # todo change function -this needs to be updated in ENA too-
                        self.update_sample(sample['_id'])



    def update_sample(self, sample):
        #update ENA record
        updatedrecord = da.Sample().get_record(sample)
        #retrieve submitted XML for sample
        #curl_cmd = "curl -u " + self.user_token + \
        #           ':' + self.pass_word + " " + self.ena_sample_retrieval \
        #           + updatedrecord['biosampleAccession']
        #registered_sample = subprocess.check_output(curl_cmd, shell=True)
        #     #self.update_samplexml(registered_sample, updatedrecord['biosampleAccession'])
        build_bundle_sample_xml(str(updatedrecord['_id']))
        update_bundle_sample_xml([updatedrecord['_id']], "bundle_" + str(updatedrecord['_id']) + ".xml")
        print(updatedrecord['_id'])
        self.modify_sample(updatedrecord['_id'])

    def modify_sample(self, id):
        fileis = "bundle_"+ str(id)+ ".xml"
        curl_cmd = 'curl -u ' + self.user_token + ':' + self.pass_word \
                   + ' -F "SUBMISSION=@modifysubmission.xml' \
                   + '" -F "SAMPLE=@' \
                   + fileis \
                   + '" "' + self.ena_service \
                   + '"'
        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
            #print(receipt)
        except Exception as e:
            message = 'API call error ' + "Submitting xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
                self.pass_word, "xxxxxx")
            #print(message)
            return False
            os.remove(fileis)


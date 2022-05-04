from django.core.management import BaseCommand

import xml.etree.ElementTree as ET
import subprocess
from tools import resolve_env
import os


import dal.copo_da as da



# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    help="script to update checksums"

    def __init__(self):
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.ena_service = resolve_env.get_env('ENA_SERVICE')  # 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/'
        self.ena_sample_retrieval = self.ena_service[:-len(
            'submit/')] + "runs/"

    def add_arguments(self, parser):
        parser.add_argument('profile_title', type=str)
        parser.add_argument('-barcoding', action='store_true')

    # A command must define handle()
    def handle(self, *args, **options):
        update_dict = {}
        #build dictionary of cheksums
        checksum_dict = {}
        with open("/home/minottoa/adammd5toupdate.chk", 'r') as checksums_file:
            for line in checksums_file.readlines():
                line = line.split()
                checksum_dict[line[1]] = line[0]
        profile = da.Profile().get_by_title(options['profile_title'].strip())
        assert len(profile) == 1
        profile_id = profile[0].get('_id',"")
        print(profile_id)
        submission = da.Submission().get_records_by_field("profile_id", str(profile_id))
        assert len(submission) == 1
        runs = submission[0].get("accessions","").get("run", "")
        bundle_meta = submission[0].get("bundle_meta", "")
        for run in runs:
            accession = run.get("accession", "")
            files = []
            for datafile in run["datafiles"]:
                for dictionary in bundle_meta:
                    if dictionary["file_id"] == datafile:
                        files.append(dictionary["file_path"].split("/")[-1])
            if any(file in checksum_dict for file in files):
                update_dict[accession] = {}
                for file in files:
                    update_dict[accession][file] = checksum_dict[file]
        print(update_dict)

        for run in update_dict:
            # retrieve submitted XML for run
            curl_cmd = "curl -u " + self.user_token + \
                       ':' + self.pass_word + " " + self.ena_sample_retrieval \
                       + run
            registered_run = subprocess.check_output(curl_cmd, shell=True)

            self.update_samplexml(registered_run, update_dict[run], run)


    def modify_run(self, run):
        curl_cmd = 'curl -u ' + self.user_token + ':' + self.pass_word \
                   + ' -F "SUBMISSION=@modifysubmission.xml' \
                   + '" -F "RUN=@' \
                   + run + ".xml" \
                   + '" "' + self.ena_service \
                   + '"'
        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
            print(receipt)
        except Exception as e:
            message = 'API call error ' + "Submitting xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
                self.pass_word, "xxxxxx")
            print(message)
            return False
        os.remove(run + ".xml")

    def update_samplexml(self, registered_sample, updatedict, run):
        #only thing to update in ENA is checksums
        doc = ET.fromstring(registered_sample)
        tree = ET.ElementTree(doc)
        name_block = tree.find('RUN').find('DATA_BLOCK')
        files_block = tree.find('RUN').find('DATA_BLOCK').find('FILES')
        for file in files_block.iter():
            if file.attrib:
                print(file.get("checksum"), updatedict[file.get("filename").split('/')[-1]])
                file.set("checksum", updatedict[file.get("filename").split('/')[-1]])

        ET.dump(tree)
        tree.write(open(run + ".xml", 'w'), encoding='unicode')

        self.modify_run(run)

'''<RUN_SET>
  <RUN accession="ERR7224572"
        alias="copo-reads-6182926e4c7cf3e3393b6961_reads_61815eccb2a1e2071101b770"
        broker_name="COPO"
        center_name="EI">
      <IDENTIFIERS>
         <PRIMARY_ID>ERR7224572</PRIMARY_ID>
         <SUBMITTER_ID namespace="EI">copo-reads-6182926e4c7cf3e3393b6961_reads_61815eccb2a1e2071101b770</SUBMITTER_ID>
      </IDENTIFIERS>
      <TITLE>Oreochromis SNP panel</TITLE>
      <EXPERIMENT_REF accession="ERX6793973">
         <IDENTIFIERS>
            <PRIMARY_ID>ERX6793973</PRIMARY_ID>
         </IDENTIFIERS>
      </EXPERIMENT_REF>
      <DATA_BLOCK>
         <FILES>
            <FILE checksum="b350e7245ad7ac732d19cd720c195d05" checksum_method="MD5"
                  filename="run/ERR722/ERR7224572/PRO1963_Plate1_H8_T7A2_GCGATGACC-GGATATCCT_merged_R1.fastq.gz"
                  filetype="fastq"
                  quality_scoring_system="phred"/>
            <FILE checksum="26994553aa48ccf9da34a47673c091e4" checksum_method="MD5"
                  filename="run/ERR722/ERR7224572/PRO1963_Plate1_H8_T7A2_GCGATGACC-GGATATCCT_merged_R2.fastq.gz"
                  filetype="fastq"
                  quality_scoring_system="phred"/>
         </FILES>
      </DATA_BLOCK>
  </RUN>
</RUN_SET>'''
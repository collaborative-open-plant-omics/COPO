
from django.core.management import BaseCommand
import os
import subprocess
import xml.etree.ElementTree as ET

import datetime

from dal.copo_da import Source, Sample
from dal import cursor_to_list, cursor_to_list_str, cursor_to_list_no_ids
from tools import resolve_env
from web.apps.web_copo.lookup.dtol_lookups import DTOL_ENA_MAPPINGS, DTOL_UNITS, \
    API_KEY


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "change the cutoff date"
    def __init__(self):
        self.pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
        self.user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
        self.ena_service = resolve_env.get_env('ENA_SERVICE') #'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/'
        self.ena_sample_retrieval = self.ena_service[:-len('submit/')]+"samples/" #https://devwww.ebi.ac.uk/ena/submit/drop-box/samples/" \

    # A command must define handle()
    def handle(self, *args, **options):
        cutoff_date = datetime.datetime(2020, 12, 24) #TODO change date
        list_to_update = self.identify_specimen_samples(cutoff_date)

        for accession in list_to_update:
            ###look for related samples in SampleCollection
            sam = Sample().get_by_field("sampleDerivedFrom", [accession])
            assert len(sam) > 0
            ###update source fields as sample
            reference_sam = sam[0]
            specimen_obj_fields = self.populate_source_fields(reference_sam)
            sour = Source().get_by_specimen(reference_sam["SPECIMEN_ID"])[0]
            Source().add_fields(specimen_obj_fields, str(sour['_id']))

            ### retrieve submitted XML for source
            curl_cmd = "curl -u " + self.user_token + \
                       ':' + self.pass_word + " " + self.ena_sample_retrieval \
                       + accession
            print(curl_cmd)
            registered_source = subprocess.check_output(curl_cmd, shell=True)

            ###modify XML (remember to change chcklist and project name)
            sour = Source().get_by_specimen(reference_sam["SPECIMEN_ID"])[0]
            print(type(sour))
            print(type(registered_source))
            self.update_source(registered_source, accession, sour)

            ### submit modified XML to ENA
            self.modify_sample(sour["biosampleAccession"])

            # handling sample level sample
            if reference_sam["ORGANISM_PART"] == "WHOLE_ORGANISM":
                # update db entry, remove value from derived from and add same as

                Sample().add_field("sampleSameAs", sour["biosampleAccession"], reference_sam["_id"])
                Sample().remove_field("sampleDerivedFrom", reference_sam["_id"])
                sample = Sample().get_by_biosample_ids([reference_sam['biosampleAccession']])[0]

                # retrieve submitted xml
                curl_cmd = "curl -u " + self.user_token + \
                           ':' + self.pass_word + " " + self.ena_sample_retrieval \
                           + reference_sam["biosampleAccession"]
                registered_sample = subprocess.check_output(curl_cmd, shell=True)

                # modify xml
                self.update_sample_relationship(registered_sample, sample)

                # submit modified xml to ENA
                self.modify_sample(sample["biosampleAccession"])


    def identify_specimen_samples(self,cutoff_date):
        '''list_to_update = db.getCollection('SourceCollection').find({  "date_created": {
            "$lt": 'ISODate("'+cutoff_date+'")'
        },
        "sample_type" : "dtol_specimen",
        "COLLECTED_BY" :
            {$exists : false}
        }})'''
        fromdb = Source().get_collection_handle().find({"date_created": {
            "$lt": cutoff_date
        },
            "sample_type": "dtol_specimen",
            "COLLECTED_BY":
                {"$exists": False}
        })
        sub = cursor_to_list(fromdb)
        list_to_update = list()
        for s in sub:
            list_to_update.append(s["biosampleAccession"])
        return list_to_update

    def populate_source_fields(self, sampleobj):
        '''populate source in db to copy most of sample fields
        but change organism part and gal sample_id'''
        fields = {"sample_type": "dtol_specimen", "profile_id": sampleobj['profile_id'],
                  "TAXON_ID": sampleobj["species_list"][0]["TAXON_ID"]}
        for item in sampleobj.items():
            try:
                print(item[0])
                if item[0] == "COLLECTION_LOCATION" or DTOL_ENA_MAPPINGS[item[0]]['ena']:
                    if item[0] == "GAL_SAMPLE_ID":
                        fields[item[0]] = "NOT_PROVIDED"
                    elif item[0] == "ORGANISM_PART":
                        fields[item[0]] = "WHOLE_ORGANISM"
                    else:
                        fields[item[0]] = item[1]
            except KeyError:
                pass
        return fields

    def update_source(self, registered_sample, sample_accession, object):
        doc = ET.fromstring(registered_sample)
        tree = ET.ElementTree(doc)
        attributes_block = tree.find('SAMPLE').find('SAMPLE_ATTRIBUTES')
        attributes = tree.find('SAMPLE').find('SAMPLE_ATTRIBUTES').findall('SAMPLE_ATTRIBUTE')
        existing_tags = []
        for attribute in attributes:
            tags_block = attribute.find('TAG')
            existing_tags.append(tags_block.text)
        for item in object.items():
                if item[1]:
                    #check attribute name
                    try:
                        if item[0] == 'COLLECTION_LOCATION':
                            attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_1']['ena']
                        elif item[0] in ["DATE_OF_COLLECTION", "DECIMAL_LATITUDE", "DECIMAL_LONGITUDE"]:
                            attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                        # handling annoying edge case below
                        else:
                            attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                        if attribute_name in existing_tags:
                            pass #because there should not be any change
                        else:
                            # add new attribute to xml
                            try:
                                # exceptional handling of COLLECTION_LOCATION
                                if item[0] == 'COLLECTION_LOCATION':
                                    attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_1']['ena']
                                    sample_attribute = ET.SubElement(attributes_block, 'SAMPLE_ATTRIBUTE')
                                    tag = ET.SubElement(sample_attribute, 'TAG')
                                    tag.text = attribute_name
                                    value = ET.SubElement(sample_attribute, 'VALUE')
                                    value.text = str(item[1]).split('|')[0]
                                    attribute_name = DTOL_ENA_MAPPINGS['COLLECTION_LOCATION_2']['ena']
                                    sample_attribute = ET.SubElement(attributes_block, 'SAMPLE_ATTRIBUTE')
                                    tag = ET.SubElement(sample_attribute, 'TAG')
                                    tag.text = attribute_name
                                    value = ET.SubElement(sample_attribute, 'VALUE')
                                    value.text = '|'.join(str(item[1]).split('|')[1:])
                                elif item[0] in ["DATE_OF_COLLECTION", "DECIMAL_LATITUDE", "DECIMAL_LONGITUDE"]:
                                    attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                                    sample_attribute = ET.SubElement(attributes_block, 'SAMPLE_ATTRIBUTE')
                                    tag = ET.SubElement(sample_attribute, 'TAG')
                                    tag.text = attribute_name
                                    value = ET.SubElement(sample_attribute, 'VALUE')
                                    value.text = str(item[1]).lower().replace("_", " ")
                                # handling annoying edge case below
                                elif item[0] == "LIFESTAGE" and item[1] == "SPORE_BEARING_STRUCTURE":
                                    attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                                    sample_attribute = ET.SubElement(attributes_block, 'SAMPLE_ATTRIBUTE')
                                    tag = ET.SubElement(sample_attribute, 'TAG')
                                    tag.text = attribute_name
                                    value = ET.SubElement(sample_attribute, 'VALUE')
                                    value.text = "spore-bearing structure"
                                else:
                                    attribute_name = DTOL_ENA_MAPPINGS[item[0]]['ena']
                                    sample_attribute = ET.SubElement(attributes_block, 'SAMPLE_ATTRIBUTE')
                                    tag = ET.SubElement(sample_attribute, 'TAG')
                                    tag.text = attribute_name
                                    value = ET.SubElement(sample_attribute, 'VALUE')
                                    value.text = str(item[1]).replace("_", " ")
                                # add ena units where necessary
                                if DTOL_UNITS.get(item[0], ""):
                                    if DTOL_UNITS[item[0]].get('ena_unit', ""):
                                        unit = ET.SubElement(sample_attribute, 'UNITS')
                                        unit.text = DTOL_UNITS[item[0]]['ena_unit']
                            except KeyError:
                                # pass, item is not supposed to be submitted to ENA
                                pass

                    except KeyError:
                        # pass, item is not supposed to be submitted to ENA
                        pass


        # adding project DTOL
        sample_attributes = tree.find('SAMPLE').find('SAMPLE_ATTRIBUTES')
        if "project name" not in existing_tags:
            sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
            tag = ET.SubElement(sample_attribute, 'TAG')
            tag.text = 'project name'
            value = ET.SubElement(sample_attribute, 'VALUE')
            value.text = 'DTOL'

        # modifying checklist from default to DTOL
        for attribute in sample_attributes:
            if attribute.find('TAG').text == "ENA-CHECKLIST":
                attribute.find('VALUE').text = 'ERC000053'
                break

        ET.dump(tree)
        tree.write(open(sample_accession + ".xml", 'w'), encoding='unicode')

    def modify_sample(self, accession):
        curl_cmd = 'curl -u ' + self.user_token + ':' + self.pass_word \
                   + ' -F "SUBMISSION=@modifysubmission.xml' \
                   + '" -F "SAMPLE=@' \
                   + accession + ".xml" \
                   + '" "' + self.ena_service \
                   + '"'
        try:
            receipt = subprocess.check_output(curl_cmd, shell=True)
            print(receipt)
        except Exception as e:
            message = 'API call error ' + "Submitting project xml to ENA via CURL. CURL command is: " + curl_cmd.replace(
                self.pass_word, "xxxxxx")
            return False

        os.remove(accession + ".xml")

    def update_sample_relationship(self, registered_sample, object):
        doc = ET.fromstring(registered_sample)
        tree = ET.ElementTree(doc)
        attributes_block = tree.find('SAMPLE').find('SAMPLE_ATTRIBUTES')

        # modifying relationship
        flag=False
        for attribute in attributes_block:
            if attribute.find('TAG').text == "sample same as":
                flag = True
                break
        if flag == False:
            sample_attribute = ET.SubElement(attributes_block, 'SAMPLE_ATTRIBUTE')
            tag = ET.SubElement(sample_attribute, 'TAG')
            tag.text = 'sample same as'
            value = ET.SubElement(sample_attribute, 'VALUE')
            value.text = object["sampleSameAs"]

        #remove old relationship
        for child in attributes_block:
            if child.text == 'sample derived from':
                attributes_block.remove(child)

        ET.dump(tree)
        tree.write(open(object['biosampleAccession'] + ".xml", 'w'), encoding='unicode')


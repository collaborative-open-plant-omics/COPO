import os
from shutil import rmtree
from pathlib import Path
from django.shortcuts import render
import subprocess
import re

from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal

from submission.helpers.generic_helper import notify_frontend
from tools import resolve_env

from dal.copo_da import Assembly, Submission


# other types of assemblies (not individualss or cultured isolates):
# Metagenome Assembly - Primary Metagenome Assemblies: the diff is the types of samples, an additional virtual sample
# needs to be registered, the rest of the submission is the same. Assembly type is  ‘primary metagenome’
# Metagenome Assembly - Binned Metagenome Assemblies: as above, Assembly type is ‘binned metagenome’
# Metagenome Assembly - A Metagenome-Assembled Genome (MAG): as above, Assembly type is ‘Metagenome-Assembled Genome
# (MAG)’
# Environmental Single-Cell Amplified Genomes: as above, Assembly type is  ‘Environmental Single-Cell Amplified Genome
# (SAG)’
# Transcriptome Assemblies: here the webin-cli command is different as -context transcriptome (instead of genome),
# assembly type is ‘isolate’, there are no fields [coverage, mingaplength, moleculetype] in the manifest, and the only
# file types allowed are FASTA and flatfile
# Metatranscriptome Assemblies: as transcriptome assembly

pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]
ena_service = resolve_env.get_env('ENA_SERVICE')

def upload_assembly_files(files):
    assembly_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files"
    request = ThreadLocal.get_current_request()
    profile_id = request.session["profile_id"]
    these_assemblies = assembly_path / profile_id
    if os.path.isdir(these_assemblies):
        #todo maybe remove this depending on the decision if keeping the reports and about multiple assemblies per project
        rmtree(these_assemblies)
    these_assemblies.mkdir(parents=True)

    write_path = Path(these_assemblies)
    for f in files:
        file = files[f]

        file_path = write_path / file.name
        file_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files" / profile_id / file.name
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        filename = os.path.splitext(file.name)[0].upper()

    # save to session
    request = ThreadLocal.get_current_request()
    output = "done"
    return output

def validate_assembly(form):
    request = ThreadLocal.get_current_request()
    profile_id = request.session["profile_id"]
    assembly_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files"
    these_assemblies = assembly_path / profile_id
    manifest_content =""
    file_fields = ["fasta", "flatfile", "agp", "chromosome_list", "unlocalised_list"]
    for key, value in form.items():
        #skip optional fields that have not been filled
        if value:
            if key == "sample_text":
                manifest_content += "SAMPLE" + "\t" + str(value) + "\n"
            elif key in file_fields:
                manifest_content += key.upper() + "\t" + str(these_assemblies)+"/"+str(value) +"\n"
            else:
                manifest_content += key.upper() + "\t" + str(value) + "\n"
    manifest_path = these_assemblies / "manifest.txt"
    with open(manifest_path, "w") as destination:
        destination.write(manifest_content)
    #verify submission
    test = ""
    if "dev" in ena_service:
        test = " -test "
    webin_cmd = "java -jar webin-cli.jar -username " + user_token + " -password " + pass_word + test +" -context genome -manifest " + str(manifest_path) + " -validate"
    #print(webin_cmd)
    try:
        output = subprocess.check_output(webin_cmd, shell=True)
    except subprocess.CalledProcessError as cpe:
        output = cpe.stdout
    output = output.decode("ascii")
    #print(output)
    #todo decide if keeping or deleting these files
    #report is being stored in webin-cli.report and manifest.txt.report so we can get errors there
    if not "ERROR" in output:
        output = submit_assembly(str(manifest_path))
        if "ERROR" in output:
            #handle possibility submission is not successfull
            #this may happen for instance if the same assembly has already been submitted, which would not get caught
            #by the validation step
            return {"error" : output}
        for f in form:
            if f in file_fields:
                form[f] = str(form[f])
        Assembly(profile_id = profile_id).save_record(auto_fields={},**form)
        accession = re.search( "ERZ\d*\w" , output).group(0).strip()
        existing_sub = Submission().get_records_by_field("profile_id", profile_id)
        if existing_sub:
            existing_sub_id = existing_sub[0].get("_id", "")
            #ENA alias costructed as webin-genome-assemblyname (may be different for transriptome?)
            Submission().add_assembly_accession(existing_sub_id, accession, "webin-genome-"+form["assemblyname"])
        else:
            fieldsdict = {"profile_id": profile_id, "repository": "ena", "complete": True, "accessions" :
                { "assembly" : {"accession" :accession, "alias": "webin-genome-"+form["assemblyname"]}}}
            Submission().save_record(autofields={}, **fieldsdict)
    else:
        return {"error": output}
    return {"accession" : accession}

def submit_assembly(file_path):
    test = ""
    if "dev" in ena_service:
        test = " -test "
    webin_cmd = "java -jar webin-cli.jar -username " + user_token + " -password " + pass_word + test + " -context genome -manifest " + str(file_path) + " -submit"
    #print(webin_cmd)
    #try/except as it turns out this can fail even if validate is successfull
    try:
        output = subprocess.check_output(webin_cmd, shell=True)
    except subprocess.CalledProcessError as cpe:
        output = cpe.stdout
    output = output.decode("ascii")
    #print(output)

    #todo delete files after successfull submission
    #todo decide if keeping manifest.txt and store accession in assembly objec too
    return output


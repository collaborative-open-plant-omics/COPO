import os
from shutil import rmtree
from pathlib import Path
from django.shortcuts import render

from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal

from submission.helpers.generic_helper import notify_frontend
from tools import resolve_env

pass_word = resolve_env.get_env('WEBIN_USER_PASSWORD')
user_token = resolve_env.get_env('WEBIN_USER').split("@")[0]

def upload_assembly_files(files):
    assembly_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files"
    request = ThreadLocal.get_current_request()
    profile_id = request.session["profile_id"]
    these_assemblies = assembly_path / profile_id
    if os.path.isdir(these_assemblies):
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
    fail_flag= False
    request = ThreadLocal.get_current_request()
    output = "done"
    notify_frontend(data={"profile_id": profile_id, "fail_flag": fail_flag}, msg=output,
                    action="",
                    html_id="assemblies")
    return output

def validate_assembly(form):
    request = ThreadLocal.get_current_request()
    profile_id = request.session["profile_id"]
    assembly_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files"
    these_assemblies = assembly_path / profile_id
    #todo find a way to use this to pre-populate samle and project id
    manifest_content =""
    for key, value in form.items():
        #skip optional fields that have not been filled
        if value:
            manifest_content += key.upper() + "\t" + str(value) + "\n"
    print(manifest_content)
    manifest_path = file_path = Path(settings.MEDIA_ROOT) / "ena_assembly_files" / profile_id / "manifest.txt"
    with open(manifest_path, "w") as destination:
        destination.write(manifest_content)
    #verify submission
    #java -jar webin-cli-<version>.jar -username Webin-XXXXX -password YYYYYYY -context genome -manifest manifest.txt -validate
    #todo get webin cli version from dockerfile or environment
    webin_cmd = "java -jar webin-cli-5.2.0.jar -username " + user_token + " -password " + pass_word + " -context genome -manifest manifest.txt -validate"
    print(webin_cmd)
    #DO NOT run the command until we know how to run it against ENA dev
    #if successfull call submit_assembly()
    return

def submit_assembly():
    pass

#todo deciding if it makes more sense to have the file upload as part of the form
'''
    FASTA: sequences in fasta format
    FLATFILE: sequences in EMBL-Bank flat file format
    AGP: sequences in AGP format
    CHROMOSOME_LIST: list of chromosomes
    UNLOCALISED_LIST: list of unlocalised sequences
'''

import os
from shutil import rmtree
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal

from submission.helpers.generic_helper import notify_frontend


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
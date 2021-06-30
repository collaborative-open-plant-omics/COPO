__author__ = 'fshaw'
import gzip
import hashlib
import os
import uuid
import json
import jsonpickle
from chunked_upload.models import ChunkedUpload
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.conf import settings
from django.core import serializers
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template.context_processors import csrf
from rest_framework.renderers import JSONRenderer

import web.apps.web_copo.schemas.utils.data_utils as d_utils
import web.apps.web_copo.utils.EnaUtils as u
from dal.broker_da import BrokerDA
from dal.copo_da import DataFile
from web.apps.web_copo.rest.models import CopoChunkedUpload


class CopoChunkedUploadCompleteView(ChunkedUploadCompleteView):
    do_md5_check = False

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary-like object.
        Called *only* if POST is successful.
        """
        files = {'files': {}}
        files['files']['name'] = chunked_upload.filename
        files['files']['id'] = chunked_upload.id
        files['files']['size'] = chunked_upload.offset / (1000 * 1000.0)
        files['files']['url'] = ''
        files['files']['thumbnailUrl'] = ''
        files['files']['deleteUrl'] = ''
        files['files']['deleteType'] = 'DELETE'

        str = jsonpickle.encode(files)
        return files


class CopoChunkedUploadView(ChunkedUploadView):
    model = CopoChunkedUpload

    '''
    '''


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'

        super(JSONResponse, self).__init__(content, **kwargs)


def receive_data_file(request):
    # this method is called for writing smaller files (<= 260MB) to disk, larger files use the
    # upload method in ChunkedUpload class

    from django.utils import timezone
    # need to make a chunked upload record to store deails of the file
    if request.method == 'POST':

        c = {}
        f = request.FILES['file']

        fname = f.__str__()
        attrs = {'user': request.user, 'filename': fname, 'completed_on': timezone.now(), 'offset': f.size}
        chunked_upload = ChunkedUpload(**attrs)
        # file starts empty
        chunked_upload.file.save(name='', content=ContentFile(''), save=True)

        path = chunked_upload.file
        destination = open(os.path.join(settings.MEDIA_ROOT, path.file.name), 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        c.update(csrf(request))

        # create output structure to pass back to jquery-upload
        files = {'files': {}}
        files['files']['name'] = f._name

        files['files']['size'] = path.size / (1000 * 1000.0)
        files['files']['id'] = chunked_upload.id
        files['files']['url'] = ''
        files['files']['thumbnailUrl'] = ''
        files['files']['deleteUrl'] = ''
        files['files']['deleteType'] = 'DELETE'

        str = jsonpickle.encode(files)
    return HttpResponse(str, content_type='json')


def resume_chunked(request):
    file_name = request.GET.get('filename')
    user_id = request.user.id
    # retrieve incomplete file for user with this name
    d = ChunkedUpload.objects.filter(completed_on__isnull=True, user_id=user_id, filename=file_name).order_by(
        '-offset')[:1]
    if d:
        out = serializers.serialize('json', d)
        return HttpResponse(jsonpickle.encode(out))
    else:
        return HttpResponse(jsonpickle.encode(''))


def get_partial_uploads(request):
    user_id = request.user.id
    d = ChunkedUpload.objects.filter(completed_on__isnull=True, user_id=user_id).order_by('created_on')
    if d:
        out = serializers.serialize('json', d)
        return HttpResponse(jsonpickle.encode(out))
    else:
        return HttpResponse(jsonpickle.encode(''))


def hash_upload(request):
    # utility method to create an md5 hash of a given file path
    # open uploaded file
    file_id = request.GET['file_id']
    print('hash started ' + file_id)
    file_obj = ChunkedUpload.objects.get(pk=file_id)
    file_name = os.path.join(settings.MEDIA_ROOT, file_obj.file.name)

    # now hash opened file
    md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)

    file_obj.hash = md5.hexdigest()
    file_obj.save()

    output_dict = {'output_hash': md5.hexdigest(), 'file_id': file_id}

    # update record in mongo
    record_object = DataFile().get_by_file_id(file_id)
    auto_fields = dict()
    auto_fields[DataFile().get_qualified_field("file_hash")] = file_obj.hash

    profile_id = request.session['profile_id']
    component = "datafile"

    BrokerDA(target_id=str(record_object.get("_id", str())),
             component=component,
             auto_fields=auto_fields
             ).do_save_edit()

    out = json.dumps(output_dict)
    print('hash complete ' + file_id)
    return HttpResponse(out, content_type='json')


def inspect_file(request):
    # utility method to examine a file and return meta-data to the frontend
    output_dict = {'file_type': 'unknown', 'do_compress': False}

    # get reference to file
    file_id = request.GET['file_id']

    chunked_upload = ChunkedUpload.objects.get(id=int(file_id))
    file_name = os.path.join(settings.MEDIA_ROOT, chunked_upload.file.name)

    # size threshold to determine if a file should be compressed
    zip_threshold = 200000000  # size in bytes

    # check if file is compressed
    is_zipped = u.is_gzipped(file_name)

    if chunked_upload.offset >= zip_threshold and not is_zipped:
        output_dict['do_compress'] = True

    # check for file type
    if u.is_pdf_file(file_name):
        output_dict['file_type'] = 'pdf'
    else:
        try:
            if u.is_fastq_file(file_name):
                output_dict['file_type'] = 'fastq'
                if not is_zipped:
                    output_dict['do_compress'] = True
            elif u.is_sam_file(file_name):
                output_dict['file_type'] = 'sam'
                if not is_zipped:
                    output_dict['do_compress'] = False
            elif u.is_bam_file(file_name):
                output_dict['file_type'] = 'bam'
                if not is_zipped:
                    output_dict['do_compress'] = False

            else:  # make file type same as extension
                output_dict['file_type'] = chunked_upload.filename.rsplit('.')[1]
        except:
            output_dict['file_type'] = 'unknown'

    # add datafile schema
    chunked_upload.type = output_dict['file_type']
    chunked_upload.save()

    # ...and obtain the inserted record
    profile_id = request.session['profile_id']
    component = "datafile"

    auto_fields = dict()
    auto_fields[DataFile().get_qualified_field("file_id")] = file_id
    auto_fields[DataFile().get_qualified_field("file_type")] = output_dict['file_type']
    auto_fields[DataFile().get_qualified_field("file_location")] = file_name
    auto_fields[DataFile().get_qualified_field("file_size")] = u.filesize_toString(chunked_upload.offset)
    auto_fields[DataFile().get_qualified_field("name")] = chunked_upload.filename

    # get default type from schema
    type = [f for f in d_utils.get_copo_schema(component) if f.get("id").split(".")[-1] == "type"]
    if type:
        type = type[0]["default_value"]
        auto_fields[DataFile().get_qualified_field("type")] = type

    df = BrokerDA(context=dict(),
                  profile_id=profile_id,
                  component=component,
                  auto_fields=auto_fields,
                  visualize="last_record"
                  ).do_save_edit().get("record_object", dict())

    out = jsonpickle.encode(output_dict)
    return HttpResponse(out, content_type='json')


def zip_file(request):
    # need to get a reference to the file to zip
    file_id = request.GET['file_id']
    print("zip started " + file_id)
    file_obj = ChunkedUpload.objects.get(pk=file_id)

    # get the name of the file to zip and change its suffix to .gz
    output_file_location = os.path.join(settings.MEDIA_ROOT, file_obj.file.name)
    output_file_name = file_obj.filename + '.gz'
    try:
        # open the file as gzip acrchive...set compression level
        temp_name = os.path.join(settings.MEDIA_ROOT, str(uuid.uuid4()) + '.tmp')
        myzip = gzip.open(temp_name, 'wb', compresslevel=1)
        src = open(output_file_location, 'r')

        # write input file to gzip archive in n byte chunks
        n = 100000000
        for chunk in iter(lambda: src.read(n), ''):
            myzip.write(bytes(chunk, 'UTF-8'))
    finally:
        myzip.close()
        src.close()

    print('zip complete ' + file_id)
    # now need to delete the old file and update the file record with the new file
    new_file_name = output_file_location + '.gz'
    os.rename(temp_name, new_file_name)
    os.remove(output_file_location)

    # calculate new file size
    stats = os.stat(new_file_name)
    new_file_size = stats.st_size / 1000 / 1000

    # update filename
    file_obj.filename = output_file_name
    file_obj.file.name = new_file_name

    # update file size
    file_obj.offset = stats.st_size
    file_obj.save()

    out = {'zipped': True, 'file_name': output_file_name, 'file_size': new_file_size}

    # update record in mongo
    record_object = DataFile().get_by_file_id(file_id)
    auto_fields = dict()
    auto_fields[DataFile().get_qualified_field("file_size")] = u.filesize_toString(file_obj.offset)
    auto_fields[DataFile().get_qualified_field("name")] = output_file_name
    auto_fields[DataFile().get_qualified_field("file_location")] = new_file_name

    profile_id = request.session['profile_id']
    component = "datafile"

    BrokerDA(target_id=str(record_object.get("_id", str())),
             component=component,
             auto_fields=auto_fields
             ).do_save_edit()

    out = jsonpickle.encode(out)
    return HttpResponse(out, content_type='json')

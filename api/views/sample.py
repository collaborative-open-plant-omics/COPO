__author__ = 'felix.shaw@tgac.ac.uk - 20/01/2016'

import datetime
import importlib
import sys
import requests
import dateutil.parser as parser
from bson.errors import InvalidId
from django.conf import settings
from django.http import HttpResponse
import json
from api.utils import get_return_template, extract_to_template, finish_request
from web.apps.web_copo.utils.ajax_handlers import sample_spreadsheet
from dal.copo_da import Sample, Source, Submission, APIValidationReport, Profile
# from web.apps.web_copo.lookup import dtol_lookups as lookup
from web.apps.web_copo.lookup.lookup import API_ERRORS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import authentication, permissions
from django.views.decorators.csrf import csrf_exempt

schema_version_path = f'web.apps.web_copo.schema_versions.{settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
lookup = importlib.import_module(schema_version_path)


def get(request, id):
    """
    Method to handle a request for a single sample object from the API
    :param request: a Django HTTPRequest object
    :param id: the id of the Sample object (can be string or ObjectID)
    :return: an HttpResponse object embedded with the completed return template for Sample
    """

    # farm request to appropriate sample type handler
    try:
        ss = Sample().get_record(id)
        source = ss['source']
        sample = ss['sample']

        # get template for return type
        t_source = get_return_template('SOURCE')
        t_sample = get_return_template('SAMPLE')

        # extract fields for both source and sample
        tmp_source = extract_to_template(object=source, template=t_source)
        tmp_sample = extract_to_template(object=sample, template=t_sample)
        tmp_sample['source'] = tmp_source

        out_list = []
        out_list.append(tmp_sample)

        return finish_request(out_list)
    except TypeError as e:
        print(e)
        return finish_request(error=API_ERRORS['NOT_FOUND'])
    except InvalidId as e:
        print(e)
        return finish_request(error=API_ERRORS['INVALID_PARAMETER'])
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def format_date(input_date):
    # format of date fields exported to STS
    return input_date.replace(tzinfo=datetime.timezone.utc).isoformat()


def filter_for_API(sample_list, add_all_fields=False):
    # add field(s) here which should be time formatted
    time_fields = ["time_created", "time_updated"]
    profile_type = None
    if len(sample_list) > 0:
        profile_type = sample_list[0].get("tol_project", "dtol").lower()
    if not profile_type:
        profile_type = "dtol"
    export = lookup.DTOL_EXPORT_TO_STS_FIELDS[profile_type]
    out = list()
    rights_to_lookup = list()
    notices = dict()
    for s in sample_list:
        # ERGA samples may be subject to traditional knowledge labels
        if s.get("tol_project", "") in ["erga", "ERGA"]:
            # check for rights applicable
            if s.get("ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_RIGHTS_APPLICABLE") in ["Y", "y"]:
                # if applicable save project id
                rights_to_lookup.append(s.get("ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID", ""))
    # now we have a list of project ids which pertain to a protected sample, so unique to get only one copy of each project
    rights_to_lookup = list(set(rights_to_lookup))
    for r in rights_to_lookup:
        notices[r] = query_local_contexts_hub(r)

    for s in sample_list:
        embargoed = False
        if isinstance(s, InvalidId):
            break
        species_list = s.pop("species_list", "")
        if species_list:
            s = {**s, **species_list[0]}
        s_out = dict()
        for k, v in s.items():
            # check if there is a traditional right embargo
            if k == "ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_RIGHTS_APPLICABLE":
                if v in ["N", "n", False, ""] or s.get("tol_project") not in ["ERGA", "erga"]:
                    # we need not do anything, since no rights apply
                    s_out[k] = v
                else:
                    # ToDo - check local context hub
                    project_id = s.get("ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID", "")
                    if not project_id:
                        # rights are applicable, but no contexts id provided, therefore embargo
                        s_out = {"status": "embargoed"}
                        out.append(s_out)
                        embargoed = True
                        break
                    else:
                        q = notices[project_id]
                        if q.get("project_privacy", "").lower() == "public":
                            s_out[k] = v
                        else:
                            s_out = {"status": "embargoed"}
                            out.append(s_out)
                            embargoed = True
                            break
            # always export copo id
            if k == "_id":
                s_out["copo_id"] = str(v)
            # check if field is listed to be exported to STS
            # print(k)
            if k in export:
                if k in time_fields:
                    s_out[k] = format_date(v)
                elif k in ["created_by", "updated_by"]:
                    s_out[k] = "*****@" + v.split("@")[1]
                else:
                    s_out[k] = v
            if k == "changelog":
                s_out["latest_update"] = format_date(v[-1].get("date"))

        # iterate through fields to be exported and add them in blank if not present in the sample object
        if not embargoed:
            if add_all_fields:
                for k in export:
                    if k not in s_out.keys():
                        s_out[k] = ""
                out.append(s_out)
            else:
                out.append(s_out)
    return out


def get_manifests(request):
    # get all manifests of dtol samples
    manifest_ids = Sample().get_manifests()
    return finish_request(manifest_ids)


def get_all_manifest_between_dates(request, d_from, d_to):
    # get all manifests between d_from and d_to
    # dates must be ISO 8601 formatted
    d_from = parser.parse(d_from)
    d_to = parser.parse(d_to)
    if d_from > d_to:
        return HttpResponse(status=400, content="'from' must be earlier than'to'")
    manifest_ids = Sample().get_manifests_by_date(d_from, d_to)
    return finish_request(manifest_ids)


def get_project_manifests_between_dates(request, project, d_from, d_to):
    # get $project manifests between d_from and d_to
    # dates must be ISO 8601 formatted
    d_from = parser.parse(d_from)
    d_to = parser.parse(d_to)
    if d_from > d_to:
        return HttpResponse(status=400, content="'from' must be earlier than'to'")
    manifest_ids = Sample().get_manifests_by_date_and_project(project, d_from, d_to)
    return finish_request(manifest_ids)


def get_samples_in_manifest(request, manifest_id):
    # get all samples tagged with the given manifest_id
    sample_list = Sample().get_by_manifest_id(manifest_id)
    out = filter_for_API(sample_list, add_all_fields=True)
    return finish_request(out)


def get_sample_statuses_for_manifest(request, manifest_id):
    sample_list = Sample().get_statuses_by_manifest_id(manifest_id)
    out = filter_for_API(sample_list, add_all_fields=False)
    return finish_request(out)


def get_by_biosample_ids(request, biosample_ids):
    # get sample associated with given biosample_id. This will return nothing if ENA submission has not yet occured
    ids = biosample_ids.split(",")
    # strip white space
    ids = list(map(lambda x: x.strip(), ids))
    # remove any empty elements in the list (e.g. where 2 or more comas have been typed in error
    ids[:] = [x for x in ids if x]
    sample = Sample().get_by_biosample_ids(ids)
    out = list()
    if sample:
        out = filter_for_API(sample)
    return finish_request(out)


def get_num_dtol_samples(request):
    samples = Sample().get_all_dtol_samples()
    number = len(samples)
    return HttpResponse(str(number))


def get_project_samples(request, project):
    projectlist = project.split(",")
    projectlist = list(map(lambda x: x.strip(), projectlist))
    # remove any empty elements in the list (e.g. where 2 or more comas have been typed in error
    projectlist[:] = [x for x in projectlist if x]
    samples = Sample().get_project_samples(projectlist)
    out = list()
    if samples:
        out = filter_for_API(samples)
    return finish_request(out)


def get_by_copo_ids(request, copo_ids):
    # get sample by COPO id if known
    ids = copo_ids.split(",")
    # strip white space
    ids = list(map(lambda x: x.strip(), ids))
    # remove any empty elements in the list (e.g. where 2 or more comas have been typed in error
    ids[:] = [x for x in ids if x]
    samples = Sample().get_records(ids)
    out = list()
    if samples:
        if not type(samples) == InvalidId:
            out = filter_for_API(samples, add_all_fields=True)
        else:
            return HttpResponse(status=400, content="InvalidId found in request")
    return finish_request(out)


def get_by_field(request, dtol_field, value):
    # generic method to return all samples where given "dtol_field" matches "value"
    vals = value.split(",")
    # strip white space
    vals = list(map(lambda x: x.strip(), vals))
    # remove any empty elements in the list (e.g. where 2 or more comas have been typed in error
    vals[:] = [x for x in vals if x]
    out = list()
    sample_list = Sample().get_by_field(dtol_field, vals)
    if sample_list:
        out = filter_for_API(sample_list, add_all_fields=True)
    return finish_request(out)


def get_study_from_sample_accession(request, accessions):
    ids = accessions.split(",")
    # strip white space
    ids = list(map(lambda x: x.strip(), ids))
    # remove any empty elements in the list (e.g. where 2 or more comas have been typed in error
    ids[:] = [x for x in ids if x]
    # try to get sample from either sra or biosample id
    samples = Sample().get_by_field(dtol_field="sraAccession", value=ids)
    if not samples:
        samples = Sample().get_by_field(dtol_field="biosampleAccession", value=ids)
        if not samples:
            return finish_request([])
    # if record found, find associated submission record
    out = []
    for s in samples:
        sub = Submission().get_submission_from_sample_id(str(s["_id"]))
        d = sub[0]["accessions"]["study_accessions"]
        d["sample_biosampleId"] = s["biosampleAccession"]
        out.append(d)
    return finish_request(out)


def get_samples_from_study_accessions(request, accessions):
    ids = accessions.split(",")
    # strip white space
    ids = list(map(lambda x: x.strip(), ids))
    # remove any empty elements in the list (e.g. where 2 or more comas have been typed in error
    ids[:] = [x for x in ids if x]
    subs = Submission().get_dtol_samples_in_biostudy(ids)
    to_finish = list()
    sample_count = 0
    for s in subs:
        out = dict()
        out["study_accessions"] = s["accessions"]["study_accessions"]
        out["sample_accessions"] = []
        for sa in s["accessions"]["sample_accessions"]:
            sample_count += 1
            smpl_accessions = s["accessions"]["sample_accessions"][sa]
            smpl_accessions["copo_sample_id"] = sa
            out["sample_accessions"].append(smpl_accessions)
        to_finish.append(out)
    return finish_request(to_finish, num_found=sample_count)


def query_local_contexts_hub(project_id):
    lch_url = "https://localcontextshub.org/api/v1/projects/" + project_id
    resp = requests.get(lch_url)
    j_resp = json.loads(resp.content)
    print(j_resp)
    return j_resp


def get_all(request):
    """
    Method to handle a request for all
    :param request: a Django HttpRequest object
    :return: A dictionary containing all samples in COPO
    """

    out_list = []

    # get sample and source objects
    try:
        sample_list = Sample().get_samples_across_profiles()
    except TypeError as e:
        # print(e)
        return finish_request(error=API_ERRORS['NOT_FOUND'])
    except InvalidId as e:
        # print(e)
        return finish_request(error=API_ERRORS['INVALID_PARAMETER'])
    except:
        # print("Unexpected error:", sys.exc_info()[0])
        raise

    for s in sample_list:
        # get template for return type
        t_source = get_return_template('SOURCE')
        t_sample = get_return_template('SAMPLE')

        # get source for sample
        source = Source().GET(s['source_id'])
        # extract fields for both source and sample
        tmp_source = extract_to_template(object=source, template=t_source)
        tmp_sample = extract_to_template(object=s, template=t_sample)
        tmp_sample['source'] = tmp_source

        out_list.append(tmp_sample)

    return finish_request(out_list)


class APIValidateManifest(APIView):

    def post(self, request):
        id = APIValidationReport().get_collection_handle().insert(
            {"profile_id": request.POST["profile_id"], "status": "pending", "content": "",
             "submitted": datetime.datetime.utcnow(), "user_id": request.user.id})
        sample_spreadsheet(request, report_id=id)

        out = {"validation_report_id": str(id)}
        return Response(out)


class APIGetManifestValidationReport(APIView):
    def post(self, request):
        uid = request.user.id
        validation_id = request.POST.get("validation_report_id")
        v_record = APIValidationReport().get_record(validation_id)
        profile_record = Profile().get_record(v_record["profile_id"])
        if profile_record["user_id"] == uid:
            out = {"status": v_record["status"], "content": v_record["content"], "submitted": v_record["submitted"]}
        else:
            out = {"content": "User not permitted to view resource"}
        return Response(out)


class APIGetUserValidations(APIView):
    def post(self, request):
        uid = request.user.id
        v_records = APIValidationReport().get_collection_handle().find({"user_id": uid}, {"_id": 0})
        return Response(list(v_records))

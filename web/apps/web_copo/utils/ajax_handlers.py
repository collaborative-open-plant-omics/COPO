__author__ = 'felix.shaw@tgac.ac.uk - 01/12/2015'

# this python file is for small utility functions which will be called from Javascript
import json
import os
import re
import time
import urllib.parse
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from io import BytesIO
from openpyxl.utils.cell import get_column_letter
from Bio import Entrez
import jsonpickle
import pandas as pd
import requests
from bson import json_util, ObjectId
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from jsonpickle import encode

import pickle
import web.apps.web_copo.lookup.lookup as ol
import web.apps.web_copo.templatetags.html_tags as htags
from dal import mongo_util as util
from dal.copo_da import Profile
from dal.copo_da import ProfileInfo, Submission, DataFile, Sample, Source, CopoGroup, Annotation, \
    Repository, Person, ValidationQueue
from dal.figshare_da import Figshare
from dal.orcid_da import Orcid
from submission.ckanSubmission import CkanSubmit as ckan
from submission.dataverseSubmission import DataverseSubmit as ds
from submission.dspaceSubmission import DspaceSubmit as dspace
from submission.figshareSubmission import FigshareSubmit
from submission.helpers import generic_helper as ghlper
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.lookup.copo_enums import Logtype
from web.apps.web_copo.lookup.copo_lookup_service import COPOLookup
from web.apps.web_copo.lookup.lookup import WIZARD_FILES as wf
from web.apps.web_copo.models import UserDetails
from web.apps.web_copo.models import ViewLock
from web.apps.web_copo.schemas.utils import data_utils

# from web.apps.web_copo.utils.dtol.Dtol_Spreadsheet import make_validation_record
from web.apps.web_copo.utils.dtol.Dtol_Spreadsheet import DtolSpreadsheet
from collections import OrderedDict
from web.apps.web_copo.utils.group_functions import get_group_membership_asString
from exceptions_and_logging import logger
from web.apps.web_copo.lookup import dtol_lookups as lkup
from web.apps.web_copo.s3.s3Connection import S3Connection as s3
from submission.submissionDelegator import schedule_submission

l = logger.Logger("exceptions_and_logging/logs")
DV_STRING = 'HARVARD_TEST_API'


def get_source_count(self):
    profile_id = data_utils.get_current_request().session['profile_id']
    num_sources = ProfileInfo(profile_id).source_count()
    return HttpResponse(encode({'num_sources': num_sources}))


def search_ontology_ebi(request, ontology_names, wrap_in_response=True):
    term = request.GET['q']
    term = term.lower()
    term = term.split("(")[0]
    term = term.replace("_", " ")
    term = term.strip()
    if ontology_names == "999":
        ontology_names = str()
    if ontology_names == "ncbitaxon":
        # for taxonomy lookups we need to search ncbi directly as we cannot filter by rank==species in OLS
        data = query_ncbi_entrez(term)
    else:
        ontologies = ontology_names
        fields = ol.ONTOLOGY_LKUPS['fields_to_search']
        query = ol.ONTOLOGY_LKUPS['ebi_ols_autocomplete'].format(**locals())
        data = requests.get(query, timeout=2).text

    # TODO - add return here for when OLS is down
    if wrap_in_response == True:
        return HttpResponse(data)
    else:
        return data


def query_ncbi_entrez(term):
    data = {}
    data["response"] = {}
    data["response"]["docs"] = []
    taxonid = term

    # Entrez.email = "copo@earlham.ac.uk"
    Entrez.api_key = lkup.NIH_API_KEY
    handle = Entrez.esearch(db="taxonomy", term=taxonid, retmode="xml")
    # get list of ids for string query
    records = Entrez.read(handle)

    if len(records["IdList"]) == 0:
        return HttpResponse(status=400, content="Nothing for for ID")
    # now query these for full details
    ids = [str(element) for element in records["IdList"]]
    ids_str = (",").join(ids)
    taxhandle = Entrez.efetch(db="taxonomy", id=ids_str)

    records = Entrez.read(taxhandle)
    output = dict()
    for r in records:
        if r["Rank"] == "species":
            data["response"]["docs"].append(
                {"annotationValue": r["ScientificName"], "iri": "http://purl.obolibrary.org/obo/NCBITaxon_" + r[
                    "TaxId"],
                 "ontology_prefix": "NCBITAXON",
                 "label": r["ScientificName"], "description": "Not Available"})
    return json.dumps(data)


def search_copo_components(request, data_source):
    """
    function does local lookup of items given data_source
    :param request:
    :param data_source:
    :return:
    """

    search_term = request.GET.get("q", str())
    accession = request.GET.get("accession", str())
    profile_id = request.GET.get("profile_id", str())
    referenced_field = request.GET.get("referenced_field", str())

    if request.method == 'POST':
        search_term = request.POST.get("q", str())
        accession = request.POST.get("accession", str())
        profile_id = request.POST.get("profile_id", str())
        referenced_field = request.POST.get("referenced_field", str())

    data = COPOLookup(
        search_term=search_term,
        accession=accession,
        data_source=data_source,
        profile_id=profile_id,
        referenced_field=referenced_field
    ).broker_component_search()

    return HttpResponse(jsonpickle.encode(data), content_type='application/json')


def get_submission_status(request):
    """
    function returns the status of a submission record
    :param request:
    :return:
    """

    context = dict()
    submission_ids = json.loads(request.POST.get("submission_ids", "[]"))
    submission_ids = [ObjectId(x) for x in submission_ids]

    # get completed submissions
    submission_records = Submission().get_collection_handle().find(
        {"_id": {"$in": submission_ids}},
        {'_id': 1, 'complete': 1, 'transcript': 1, 'manifest_submission': 1})

    for rec in submission_records:

        record_id = str(rec['_id'])
        new_data = dict(record_id=record_id)
        if rec.get("manifest_submission", 0):
            new_data["manifest_submission"] = 1
        context[new_data["record_id"]] = new_data

        new_data["complete"] = str(rec.get("complete", False)).lower()

        # get any transcript to provide a clearer picture
        status = rec.get("transcript", dict()).get('status', dict())
        new_data['transcript_status'] = status.get('type', str())  # status type is: 'info', 'error', or 'success'
        new_data['transcript_message'] = status.get('message', str())

        # completed submissions
        if new_data["complete"] == 'true':  # this is where we part ways
            continue

        # processing or queued for processing
        submission_queue_handle = ghlper.get_submission_queue_handle()

        if submission_queue_handle.find_one({"submission_id": record_id}):
            new_data["complete"] = "processing"
            continue

        # not submitted, not in processing queue, must be unsubmitted or in error state
        # we turn to transcript for answer: reason why recording status in transcript is important!
        # see: update_submission_status() in generic_helper.py
        new_data["complete"] = "error" if new_data['transcript_status'] == 'error' else "pending"

    return HttpResponse(jsonpickle.encode(context), content_type='application/json')


def get_upload_information(request):
    context = dict()

    ids = json.loads(request.POST.get("ids", "[]"))
    sub_info_list = list()

    submission_queue_handle = ghlper.get_submission_queue_handle()

    for id in ids:
        # get submission record and check submission status
        try:
            sub = Submission().get_record(id)
        except:
            sub = dict()

        if not sub:
            continue

        sub_info_dict = dict()
        sub_info_dict["submission_id"] = id
        sub_info_dict["enable_submit_button"] = True

        repo = sub.get("repository", str()).lower()

        if repo in ["cg_core", "dataverse", "dspace", "ckan"]:
            if "meta" in sub and "fields" in sub["meta"] or "identifier" in sub["meta"]:
                pass
            else:
                sub_info_dict["enable_submit_button"] = False

        if str(sub.get("complete", False)).lower() == 'true':
            # submission has finished
            sub_info_dict["submission_status"] = True
            sub_info_dict["completed_on"] = sub.get('completed_on', str()).strftime('%d %b, %Y, %H:%M') if sub.get(
                'completed_on', str()) else 'unavailable'
            try:
                sub_info_dict["article_id"] = sub['article_id']
            except:
                sub_info_dict["article_id"] = "unavailable"

            # get study embargo info
            if repo == "ena":
                # get study accession
                prj = sub.get('accessions', dict()).get('project', [{}])
                status = prj[0].get("status", "Unknown")
                release_date = prj[0].get("release_date", str())
                if status.upper() == "PRIVATE":
                    sub_info_dict["release_status"] = "PRIVATE"

                    sub_info_dict["release_date"] = release_date
                    if len(release_date) >= 10:  # e.g. '2019-08-30'
                        try:
                            datetime_object = datetime.strptime(release_date[:10], '%Y-%m-%d')
                            sub_info_dict["release_date"] = time.strftime('%a, %d %b %Y %H:%M',
                                                                          datetime_object.timetuple())
                        except:
                            pass

                    sub_info_dict["release_message"] = "<div>All objects in this " \
                                                       "submission are set to " \
                                                       "private (confidential) status.</div>" \
                                                       "<div style='margin-top:10px;'>The release date is set for " \
                                                       "" + sub_info_dict["release_date"] + \
                                                       ".</div><div style='margin-top:10px;'>" \
                                                       "To release this study to the public, " \
                                                       "click the release study button.</div>"
                elif status.upper() == "PUBLIC":
                    sub_info_dict["release_status"] = "PUBLIC"
                    sub_info_dict["study_view_url"] = "https://www.ebi.ac.uk/ena/data/view/" + prj[0].get("accession",
                                                                                                          str())
                    sub_info_dict["release_message"] = "<div>All objects in " \
                                                       "this submission are set to public status.</div> " \
                                                       "<div style='margin-top:10px;'>To view this study " \
                                                       "on the ENA browser (opens in a new browser tab), " \
                                                       "click the view on ENA button.</div>"
                else:
                    sub_info_dict["release_status"] = "Unknown"
                    sub_info_dict["release_message"] = "<div>The embargo status of " \
                                                       "this study is unknown.</div>" \
                                                       "<div>For more details, please contact your administrator. " \
                                                       "Alternatively, you can try searching for the study on the " \
                                                       "ENA browser to verify its status.</div>"
        else:
            sub_info_dict["is_active_submission"] = False
            if repo == "ena":  # this will be extended to other repositories/submission end-points
                submission_in_queue = submission_queue_handle.find_one(
                    {"submission_id": sub_info_dict["submission_id"]})
                if submission_in_queue:  # submission not queued, flag up to enable resubmission
                    sub_info_dict["is_active_submission"] = True

            # get status report
            status = sub.get("transcript", dict()).get('status', dict())
            if status:
                # status types are either 'info' or 'error'
                sub_info_dict["submission_report"] = dict(type=status.get('type', str()),
                                                          message=status.get('message', str()))

            # report on submitted datafiles - ENA for now...
            if repo == "ena":
                run_accessions = sub.get('accessions', dict()).get('run', list())
                submitted_files = [x for y in run_accessions for x in y.get('datafiles', list())]

                if submitted_files:
                    sub_info_dict["submitted_files"] = submitted_files

        sub_info_list.append(sub_info_dict)

    context["submission_information"] = sub_info_list
    out = jsonpickle.encode(context)
    return HttpResponse(out, content_type='application/json')


def publish_figshare(request):
    sub_id = request.POST['submission_id']
    s = Submission().get_record(sub_id)
    resp = FigshareSubmit(sub_id).publish_article(s['accession'])
    return HttpResponse(
        json.dumps({'status_code': resp.status_code, 'location': json.loads(resp.content.decode('utf8'))['location']}))


def release_ena_study(request):
    from submission import enareadSubmission
    submission_id = request.POST.get("target_id", str())
    result = enareadSubmission.EnaReads(submission_id=submission_id).release_study()

    if result.get("status", True) is True:
        return HttpResponse(jsonpickle.dumps({'status': 0}))
    else:
        return HttpResponse(jsonpickle.dumps({'status': 1, 'message': result.get("message", str())}))


def get_tokens_for_user(request):
    user = data_utils.get_current_user().id
    # get Figshare Tokens
    t = util.cursor_to_list(Figshare().get_figshare_tokens_for_user(user))
    return HttpResponse(json_util.dumps({'figshare_tokens': t}))


def delete_token(request):
    tok_id = request.POST['token_id']
    resp = Figshare().delete_token(tok_id)
    return HttpResponse(json_util.dumps({'resp': resp.acknowledged}))


def get_accession_data(request):
    sub_id = request.GET.get('sub_id')
    sub = Submission().get_file_accession(sub_id)
    return HttpResponse(json_util.dumps({'sub': sub}))


def get_dataset_details(request):
    profile_id = request.GET['profile_id']
    resp = Profile().check_for_dataset_details(profile_id)
    return HttpResponse(json.dumps(resp))


def get_samples_for_study(request):
    # get all samples which have corresponding profile_id number
    profile_id = request.POST['profile_id']
    samples = Sample().get_from_profile_id(profile_id=profile_id)
    output = list()
    for s in samples:
        source = Source().get_record(s['derivesFrom'][0])
        # s.update(source)
        d = {"organism": source["organism"], "_id": s["_id"], "name": s["name"]}
        output.append(d)
    return HttpResponse(json_util.dumps(output))


def set_session_variable(request):
    try:
        key = request.POST['key']
        value = request.POST['value']
        request.session[key] = value
    except:
        pass

    key = request.POST['key']
    try:
        value = request.POST['value']
    except:
        value = None
    request.session[key] = value
    return HttpResponse(True)


def get_continuation_studies():
    user = data_utils.get_current_user()
    profiles = Profile().get_for_user(user.id)
    output = list()
    for p in profiles:
        output.append(
            {
                "value": p.title,
                "label": p._id
            }
        )
    return output


def create_group(request):
    name = request.GET['group_name']
    description = request.GET['description']
    uid = CopoGroup().create_shared_group(name=name, description=description)

    if uid:
        return HttpResponse(json.dumps({'id': str(uid), 'name': name}))
    else:
        return HttpResponseBadRequest('Error Creating Group - Try Again')


def delete_group(request):
    id = request.GET['group_id']
    deleted = CopoGroup().delete_group(group_id=id)
    if deleted:
        return HttpResponse(json.dumps({'deleted': True}))
    else:
        return HttpResponseBadRequest('Error Deleting Group - Try Again')


def add_profile_to_group(request):
    group_id = request.GET['group_id']
    profile_id = request.GET['profile_id']
    resp = CopoGroup().add_profile(group_id=group_id, profile_id=profile_id)
    if resp:
        return HttpResponse(json.dumps({'resp': 'Added to Group'}))
    else:
        return HttpResponseBadRequest(json.dumps({'resp': 'Server Error - Try again'}))


def remove_profile_from_group(request):
    group_id = request.GET['group_id']
    profile_id = request.GET['profile_id']
    resp = CopoGroup().remove_profile(group_id=group_id, profile_id=profile_id)
    if resp:
        return HttpResponse(json.dumps({'resp': 'Removed from Group'}))
    else:
        return HttpResponseBadRequest(json.dumps({'resp': 'Server Error - Try again'}))


def get_profiles_in_group(request):
    group_id = request.GET['group_id']
    grp_info = CopoGroup().get_profiles_for_group_info(group_id=group_id)
    return HttpResponse(json_util.dumps({'resp': grp_info}))


def get_users_in_group(request):
    group_id = request.GET['group_id']
    usr_info = CopoGroup().get_users_for_group_info(group_id=group_id)
    return HttpResponse(json_util.dumps({'resp': usr_info}))


def get_users(request):
    q = request.GET['q']
    x = list(User.objects.filter(
        Q(first_name__istartswith=q) | Q(last_name__istartswith=q) | Q(username__istartswith=q))
             .values_list('id', 'first_name', 'last_name', 'email', 'username'))
    if not x:
        return HttpResponse()
    return HttpResponse(json.dumps(x))


def add_user_to_group(request):
    group_id = request.GET['group_id']
    user_id = request.GET['user_id']
    grp_info = CopoGroup().add_user_to_group(group_id=group_id, user_id=user_id)
    return HttpResponse(json_util.dumps({'resp': grp_info}))


def remove_user_from_group(request):
    group_id = request.GET['group_id']
    user_id = request.GET['user_id']
    grp_info = CopoGroup().remove_user_from_group(group_id=group_id, user_id=user_id)
    return HttpResponse(json_util.dumps({'resp': grp_info}))


def get_ontologies(request):
    resp = requests.get('http://www.ebi.ac.uk/ols/api/ontologies?size=5000&sort=ontologyId')
    data = json_util.dumps(json_util.loads(resp.content.decode('utf-8'))['_embedded']['ontologies'])
    return HttpResponse(data)


def export_generic_annotation(request):
    ant_id = request.POST["annotation_id"]
    doc = Annotation().get_annotations_for_page(ant_id)
    out = {"raw": json.loads(doc["raw"]), "annotations": doc["annotation"]}
    return HttpResponse(json_util.dumps(out))


def create_new_repo(request):
    name = request.POST['name']
    type = request.POST['type']
    url = request.POST['url']
    apikey = request.POST['apikey']
    username = request.POST['username']
    password = request.POST['password']
    isCG = request.POST['isCG']
    uid = request.user.id

    if isCG == 'true':
        isCG = True
    else:
        isCG = False

    args = {'isCG': isCG, 'name': name, 'type': type, 'url': url, 'apikey': apikey, 'username': username,
            'password': password,
            'uid': uid}
    Repository().save_record(dict(), **args)
    out = {'name': name, 'type': type, 'url': url}
    return HttpResponse(json_util.dumps(out))


def get_repos_data(request):
    uid = request.user.id
    u_type = request.GET["u_type"]
    if u_type == "managers":
        doc = Repository().get_by_uid(uid)
    elif u_type == "submitters":
        u = User.objects.get(pk=uid)
        repo_ids = u.userdetails.repo_manager
        doc = list()
        for r in repo_ids:
            doc.append(Repository().get_record(ObjectId(r)))
    return HttpResponse(json_util.dumps(doc))


def assign_repo_users(request):
    """
    function assigns users to a repository as managers or submitters
    :param request:
    :return:
    """
    repo_id = request.POST['repo_id']
    user_ids = json.loads(request.POST.get("user_ids", "[]"))
    user_type = request.POST['user_type']
    user_objects = list()

    for user_id in user_ids:
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            continue
        else:
            user_objects.append(user)

    if user_type == "managers":
        dms = Group.objects.get(name='data_managers')
        for user in user_objects:
            dms.user_set.add(user)
            user_repos = user.userdetails.repo_manager
            if user_repos is None:
                user.userdetails.repo_manager = [repo_id]
                user.save()
            elif repo_id not in user_repos:
                user.userdetails.repo_manager.append(repo_id)
                user.save()
    elif user_type == "submitters":
        for user in user_objects:
            user_repos = user.userdetails.repo_submitter
            if user_repos is None:
                user.userdetails.repo_submitter = [repo_id]
                user.save()
            elif repo_id not in user_repos:
                user.userdetails.repo_submitter.append(repo_id)
                user.save()
    out = jsonpickle.encode({}, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def deassign_repo_users(request):
    """
    function removes users from a repository as managers or submitters, etc
    :param request:
    :return:
    """
    repo_id = request.POST['repo_id']
    user_ids = json.loads(request.POST.get("user_ids", "[]"))
    user_type = request.POST['user_type']
    user_objects = list()

    for user_id in user_ids:
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            continue
        else:
            user_objects.append(user)

    if user_type == "managers":
        dms = Group.objects.get(name='data_managers')
        for user in user_objects:
            user.userdetails.repo_manager.remove(repo_id)
            user.save()

            if len(user.userdetails.repo_manager) == 0:
                dms.user_set.remove(user)
    elif user_type == "submitters":
        for user in user_objects:
            user.userdetails.repo_submitter.remove(repo_id)
            user.save()
    out = jsonpickle.encode({}, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def add_user_to_repo(request):
    repo_id = request.GET['repo_id']
    user_id = request.GET['user_id']
    first_name = request.GET['first_name']
    last_name = request.GET['last_name']
    username = request.GET['username']
    email = request.GET['email']
    u_type = request.GET['u_type']
    u = User.objects.get(pk=user_id)
    if u_type == "managers":
        dms = Group.objects.get(name='data_managers')
        dms.user_set.add(u)
        # User.UserDetails is an extension to User via a one-to-one django field....look in models.py
        repos = u.userdetails.repo_manager
        if repos is None:
            u.userdetails.repo_manager = [repo_id]
            u.save()
        else:
            if repo_id not in repos:
                u.userdetails.repo_manager.append(repo_id)
                u.save()
    elif u_type == "submitters":
        repos = u.userdetails.repo_submitter
        if repos is None:
            u.userdetails.repo_submitter = [repo_id]
            u.save()
        else:
            if repo_id not in repos:
                u.userdetails.repo_submitter.append(repo_id)
                u.save()

    out = {"out": "0", "user_id": user_id, "first_name": first_name, "last_name": last_name, "username": username,
           "email": email}
    return HttpResponse(json_util.dumps(out))


def remove_user_from_repo(request):
    repo_id = request.GET['repo_id']
    user_id = request.GET['uid']
    u = User.objects.get(pk=user_id)
    u.userdetails.repo_manager.remove(repo_id)
    u.save()
    if len(u.userdetails.repo_manager) == 0:
        # remove from admins group
        dms = Group.objects.get(name='data_managers')
        dms.user_set.remove(u)

    return HttpResponse(json_util.dumps({"out": "1"}))


def get_users_in_repo(request):
    repo_id = request.GET['repo_id']
    u_type = request.GET['user_type']
    if u_type == 'managers':
        data = UserDetails.objects.filter(repo_manager__contains=[repo_id])
    elif u_type == 'submitters':
        data = UserDetails.objects.filter(repo_submitter__contains=[repo_id])
    u_list = list()
    for d in data:
        u_list.append({'uid': d.user.id, 'first_name': d.user.first_name, 'last_name': d.user.last_name})
    # data = serializers.serialize('json', u_list)
    return HttpResponse(json_util.dumps(u_list))


def get_users_repo_users(request):
    repository_id = request.POST.get("repository_id", str())
    context = request.POST.get("context", str())

    result_dict = dict()

    if context == 'managers':
        repo_users = UserDetails.objects.filter(repo_manager__contains=[repository_id])
    elif context == 'submitters':
        repo_users = UserDetails.objects.filter(repo_submitter__contains=[repository_id])

    assigned_user_ids = [x[0] for x in list(repo_users.all().values_list('user_id'))]

    # get all users
    all_users = list(User.objects.all().values_list('id', 'first_name', 'last_name', 'email', 'username'))

    result_dict['context_users'] = [dict(id=x[0], first_name=x[1], last_name=x[2], email=x[3], username=x[4]) for x in
                                    all_users if x[0] in assigned_user_ids]

    result_dict['filtered_users'] = [dict(id=x[0], first_name=x[1], last_name=x[2], email=x[3], username=x[4]) for x in
                                     all_users if x[0] not in assigned_user_ids]

    out = jsonpickle.encode(result_dict, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def get_repos_for_user(request):
    # u_type = request.GET['u_type']
    uid = str(request.user.id)
    group_id = request.GET['group_id']
    doc = CopoGroup().get_repos_for_group_info(uid, group_id)
    return HttpResponse(json_util.dumps({'resp': doc}))


def add_repo_to_group(request):
    group_id = request.GET['group_id']
    repo_id = request.GET['repo_id']
    resp = CopoGroup().add_repo(group_id=group_id, repo_id=repo_id)
    if resp:
        return HttpResponse(json.dumps({'resp': 'Added to Group'}))
    else:
        return HttpResponseBadRequest(json.dumps({'resp': 'Server Error - Try again'}))


def remove_repo_from_group(request):
    group_id = request.GET['group_id']
    repo_id = request.GET['repo_id']
    resp = CopoGroup().remove_repo(group_id=group_id, repo_id=repo_id)
    if resp:
        return HttpResponse(json.dumps({'resp': 'Removed from Group'}))
    else:
        return HttpResponseBadRequest(json.dumps({'resp': 'Server Error - Try again'}))


def get_submission_metadata(request):
    """
    function returns the metadata associated with a submission
    :param request:
    :return:
    """

    result = Submission().get_submission_metadata(submission_id=request.POST.get("submission_id", str()))

    out = jsonpickle.encode(result, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def get_repo_info(request, sub=None):
    # this ajax method is called when user clicks "inspect repo" button on submission view
    try:
        if not sub:
            sub_id = request.GET['sub_id']
        else:
            sub_id = sub
        s = Submission().get_record(ObjectId(sub_id))
        repo = s['destination_repo']
        # if sub type is cg_core, do conversion from interim to dc
        if s["is_cg"]:
            if repo["type"] == "dataverse":
                ds().dc_dict_to_dc(sub_id)
            elif repo["type"] == "ckan":
                ckan().dc_dict_to_dc(sub_id)
            elif repo["type"] == "dspace":
                dspace().dc_dict_to_dc(sub_id)
    except Exception as e:
        # print(e)
        return HttpResponse(json.dumps({"status": 404, "message": "error getting dataverse"}))
    s = Submission().get_record(ObjectId(sub_id))
    out = dict(repo_type=repo['type'], repo_url=repo['url'], meta=s.get("meta", list()))
    out = jsonpickle.encode(out, unpicklable=False)
    return HttpResponse(out, content_type='application/json')

    # return HttpResponse(json.dumps(out))


def search_dataverse(request):
    box = request.GET['box']
    q = request.GET['q']
    url = Submission().get_dataverse_details(request.GET['submission_id'])
    dv_url = url['url'] + '/api/v1/search'
    payload = {'q': q, 'per_page': 100, 'show_entity_ids': True, 'type': box}
    resp = requests.get(url=dv_url, params=payload)
    if not resp.status_code == 200:
        return HttpResponse(None)
    resp = resp.content.decode('utf-8')

    return HttpResponse(resp)


def get_dataset_info(request):
    doi = request.GET["doi"]
    sub = request.GET["sub_id"]
    details = Submission().get_dataverse_details(sub)
    # 'https://dataverse.harvard.edu/api/datasets/export?exporter=schema.org&persistentId=doi:10.7910/DVN/ECFS7N'
    # 'https://dataverse.harvard.edu/api/datasets/export?exporter=schema.org&persistentId=doi.org/10.7910/DVN/ZDGJ7S'
    if not details['url'].endswith("/"):
        url = details['url'] + '/'
    else:
        url = details['url']
    dv_url = url + 'api/datasets/export?exporter=schema.org&persistentId=doi:' + doi
    resp = requests.get(url=dv_url)
    if not resp.status_code == 200:
        return HttpResponse(status=503)
    else:
        data = json_util.dumps(resp.content.decode("utf-8"))
        return HttpResponse(data)


def search_dataverse_vf(request):
    """
    this variation of the 'search_dataverse' function provides a formatted output to return caller's requested fields
    :param request:
    :return:
    """
    context = request.GET.get("context", str())
    q = request.GET.get("q", str())
    submission_id = request.GET.get("submission_id", str())
    api_schema = json.loads(request.GET.get("api_schema", "[]"))

    # example api_schema:
    # api_schema = [
    #     {'id': 'name', 'label': 'Name', 'show_in_table': true},
    #     {'id': 'type', 'label': 'Type', 'show_in_table': false}
    # ]

    # validate api_schema before proceeding
    if api_schema:
        schema_keys = [x.get('id', str()) for x in api_schema if isinstance(x, dict)]
        if len(schema_keys) != len(api_schema):
            return format_json_response({'status': "error", 'message': "Badly formed API schema"})

    try:
        url = Submission().get_repository_details(submission_id=submission_id)['url']
    except Exception as e:
        return format_json_response({'status': "error", 'message': str(e)})

    dv_url = urllib.parse.urljoin(url, '/api/v1/search')

    params = [
        ('q', q),
        ('per_page', 100),
        ('show_entity_ids', True),
    ]

    if not context:
        context = ['dataset,dataverse']  # search will be filtered by dataset and dataverse types

    context = [('type', x) for x in context.split(",")]
    params = tuple(params + context)

    try:
        response = requests.get(url=dv_url, params=params)
        if str(response.status_code).lower() in ("ok", "200"):
            response_data = response.json().get("data", dict())
        else:
            return format_json_response({'status': "error", 'message': response.json().get("message", str())})
    except Exception as e:
        return format_json_response({'status': "error", 'message': "Error retrieving information: " + str(e)})

    items = response_data.get('items', list())

    pluralise = 'records' if len(items) != 1 else 'record'
    message = f'Search returned {len(items)} {pluralise}.'

    if len(items) == 0:
        message = message + " You can try searching with a different term."

    result_dict = dict(status='success', message=message)

    # if no schema was supplied, form one by aggregating fields from all items
    if not api_schema:
        all_keys = {k for b in items for k, v in b.items()}
        api_schema = [dict(id=x, label=x.title(), show_in_table=True) for x in all_keys]
        result_dict['api_schema'] = api_schema

    filtered_items = list()

    for indx, rec in enumerate(items):
        new_dict = {k["id"]: rec.get(k["id"], 'N/A') for k in api_schema}

        # add two control fields: for 'id' and 'label' in display
        new_dict['copo_idblank'] = f'item_{str(indx)}'
        new_dict['copo_labelblank'] = new_dict[api_schema[0]['id']]
        # prefix display by type
        new_dict['copo_labelblank'] = new_dict.get("type", "Unknown").capitalize() + ": " + new_dict['copo_labelblank']
        filtered_items.append(new_dict)

    result_dict['items'] = filtered_items

    out = jsonpickle.encode(result_dict, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def get_dataverse_content_vf(request):
    """
    given some identifier of a dataverse, this function returns the datasets under the dataverse
    :param request:
    :return:
    """
    dataverse_record = request.POST.get("dataverse_record", dict())
    submission_id = request.POST.get("submission_id", str())
    api_schema = json.loads(request.POST.get("api_schema", "[]"))

    if dataverse_record and isinstance(dataverse_record, str):
        dataverse_record = json.loads(dataverse_record)

    # example api_schema:
    # api_schema = [
    #     {'id': 'name', 'label': 'Name', 'show_in_table': true},
    #     {'id': 'type', 'label': 'Type', 'show_in_table': false}
    # ]

    # validate api_schema before proceeding
    if api_schema:
        schema_keys = [x.get('id', str()) for x in api_schema if isinstance(x, dict)]
        if len(schema_keys) != len(api_schema):
            return format_json_response({'status': "error", 'message': "Badly formed API schema"})

    try:
        url = Submission().get_repository_details(submission_id=submission_id)['url']
    except Exception as e:
        return format_json_response({'status': "error", 'message': str(e)})

    dv_url = urllib.parse.urljoin(url, '/api/v1/search')

    name_of_dataverse = dataverse_record.get("name", str())
    identifier_of_dataverse = dataverse_record.get("identifier", str()).lower()

    params = [
        ('q', f'name_of_dataverse {name_of_dataverse}'),
        ('per_page', 500),
        ('show_entity_ids', True),
    ]
    params = tuple(params)

    try:
        response = requests.get(url=dv_url, params=params)
        if str(response.status_code).lower() in ("ok", "200"):
            response_data = response.json().get("data", dict())
        else:
            return format_json_response({'status': "error", 'message': response.json().get("message", str())})
    except Exception as e:
        return format_json_response({'status': "error", 'message': "Error retrieving information: " + str(e)})

    # filter based on object type and parent
    items = [x for x in response_data.get('items', list()) if
             x.get("type", str()).lower() == 'dataset' and x.get("identifier_of_dataverse",
                                                                 str()).lower() == identifier_of_dataverse]

    pluralise = 'records' if len(items) != 1 else 'record'
    message = f'Search returned {len(items)} {pluralise}.'

    if len(items) == 0:
        message = message + " You can try searching a different dataverse"

    result_dict = dict(status='success', message=message)

    # if no schema was supplied, form one by aggregating fields from returned items
    if not api_schema:
        all_keys = {k for b in items for k, v in b.items()}
        api_schema = [dict(id=x, label=x.title(), show_in_table=True) for x in all_keys]
        result_dict['api_schema'] = api_schema

    filtered_items = list()

    for indx, rec in enumerate(items):
        new_dict = {k["id"]: rec.get(k["id"], 'N/A') for k in api_schema}

        # add two control fields: for 'id' and 'label' in display
        new_dict['copo_idblank'] = f'item_{str(indx)}'
        new_dict['copo_labelblank'] = new_dict[api_schema[0]['id']]
        new_dict['copo_labelblank'] = new_dict['type'].capitalize() + ": " + new_dict['copo_labelblank']
        filtered_items.append(new_dict)

    result_dict['items'] = filtered_items

    out = jsonpickle.encode(result_dict, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def ckan_package_search(request):
    """
    this function searches a ckan for datasets based on the search term
    :param request:
    :return:
    """
    q = request.GET.get("q", str())
    submission_id = request.GET.get("submission_id", str())
    api_schema = json.loads(request.GET.get("api_schema", "[]"))

    # example api_schema:
    # api_schema = [
    #     {'id': 'name', 'label': 'Name', 'show_in_table': true},
    #     {'id': 'type', 'label': 'Type', 'show_in_table': false}
    # ]

    # validate api_schema before proceeding
    if api_schema:
        schema_keys = [x.get('id', str()) for x in api_schema if isinstance(x, dict)]
        if len(schema_keys) != len(api_schema):
            out = jsonpickle.encode({'status': "error", 'message': "Badly formed API schema"}, unpicklable=False)
            return HttpResponse(out, content_type='application/json')

    try:
        url = Submission().get_repository_details(submission_id=submission_id)['url']
    except Exception as e:
        out = jsonpickle.encode({'status': "error", 'message': str(e)}, unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    dv_url = urllib.parse.urljoin(url, '/api/3/action/package_search')

    params = [
        ('q', q),
        ('rows', 500),
    ]

    params = tuple(params)

    try:
        response = requests.get(url=dv_url, params=params)
        if str(response.status_code).lower() in ("ok", "200"):
            response_data = response.json()
        else:
            out = jsonpickle.encode({'status': "error", 'message': response.json().get("message", str())},
                                    unpicklable=False)
            return HttpResponse(out, content_type='application/json')
    except Exception as e:
        out = jsonpickle.encode({'status': "error", 'message': "Error retrieving datasets: " + str(e)},
                                unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    # check for error
    if str(response_data.get('success', str())).lower() == "false":
        message = "Error retrieving datasets "
        if response_data.get('error', dict()).get('message', str()):
            message = message + response_data.get('error', dict()).get('message', str())
        out = jsonpickle.encode({'status': "error", 'message': message}, unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    # get record count
    result_count = response_data.get('result', dict()).get('count', 0)
    pluralise = 'records' if result_count != 1 else 'record'
    message = f'Search returned {result_count} {pluralise}.'

    if result_count == 0:
        message = message + " You can try searching with a different term."

    result_dict = dict(status='success', message=message)
    items = response_data.get('result', dict()).get('results', list())

    # if no schema was supplied, form one by aggregating fields from all items
    if not api_schema:
        api_schema = [
            {'id': 'title', 'label': 'Title', 'show_in_table': True},
            {'id': 'name', 'label': 'Name', 'show_in_table': True},
            {'id': 'author', 'label': 'Author', 'show_in_table': True},
            {'id': 'author_email', 'label': 'Author Email', 'show_in_table': True},
            {'id': 'id', 'label': 'Identifier', 'show_in_table': True}
        ]
        result_dict['api_schema'] = api_schema

    filtered_items = list()

    for indx, rec in enumerate(items):
        new_dict = {k["id"]: rec.get(k["id"], 'N/A') for k in api_schema}

        # add two control fields: for 'id' and 'label' in display
        new_dict['copo_idblank'] = f'item_{str(indx)}'
        new_dict['copo_labelblank'] = new_dict[api_schema[0]['id']]
        filtered_items.append(new_dict)

    result_dict['items'] = filtered_items

    out = jsonpickle.encode(result_dict, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def retrieve_dspace_objects(request):
    """
    function retrieves dspace objects, specified by object_type
    :param request:
    :return:
    """
    submission_id = request.POST.get("submission_id", str())
    community_id = request.POST.get("community_id", str())
    collection_id = request.POST.get("collection_id", str())
    object_type = request.POST.get("object_type", str())
    api_schema = json.loads(request.POST.get("api_schema", "[]"))

    # example api_schema:
    # api_schema = [
    #     {'id': 'name', 'label': 'Name', 'show_in_table': true},
    #     {'id': 'type', 'label': 'Type', 'show_in_table': false}
    # ]

    # validate api_schema before proceeding
    if api_schema:
        schema_keys = [x.get('id', str()) for x in api_schema if isinstance(x, dict)]
        if len(schema_keys) != len(api_schema):
            out = jsonpickle.encode({'status': "error", 'message': "Badly formed API schema"}, unpicklable=False)
            return HttpResponse(out, content_type='application/json')

    try:
        url = Submission().get_repository_details(submission_id=submission_id)["url"]
    except Exception as e:
        out = jsonpickle.encode({'status': "error", 'message': str(e)}, unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    url_maps = dict(
        communities='/rest/communities',
        collections=f'/rest/communities/{community_id}/collections',
        items=f'/rest/collections/{collection_id}/items',
    )

    dv_url = urllib.parse.urljoin(url, url_maps.get(object_type, str()))

    params = [
        ('limit', 100),
    ]

    params = tuple(params)

    try:
        response = requests.get(url=dv_url, params=params)
        if str(response.status_code).lower() in ("ok", "200"):
            items = response.json()
        else:
            out = jsonpickle.encode({'status': "error", 'message': response.json().get("message", str())},
                                    unpicklable=False)
            return HttpResponse(out, content_type='application/json')
    except Exception as e:
        out = jsonpickle.encode({'status': "error", 'message': f"Error retrieving DSpace {object_type}: " + str(e)},
                                unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    result_dict = dict(status='success', message='')

    # if no schema was supplied, form one by aggregating fields from all items
    if not api_schema:
        api_schema = [
            {'id': 'name', 'label': 'Name', 'show_in_table': True},
            {'id': 'id', 'label': 'Id', 'show_in_table': False},
            {'id': 'handle', 'label': 'Handle', 'show_in_table': False},
        ]
        result_dict['api_schema'] = api_schema

    filtered_items = list()
    result_dict['items'] = filtered_items

    if len(items):
        df = pd.DataFrame(items)
        if 'uuid' in df.columns:
            df["id"] = df.uuid
        for k in [x['id'] for x in api_schema if x['id'] not in df.columns]:
            df.loc[k] = df.loc[k].fillna('n/a')

        df = df[[x['id'] for x in api_schema]]
        result_dict['items'] = df.to_dict('records')

    out = jsonpickle.encode(result_dict, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def get_dataverse_content(request):
    id = request.GET['id']
    url = Submission().get_dataverse_details(request.GET['submission_id'])
    dv_url = url['url'] + '/api/v1/dataverses/' + id + '/contents'
    resp_dv = requests.get(dv_url).content.decode('utf-8')
    ids = json.loads(resp_dv)
    if not ids['data']:
        return HttpResponse(json.dumps({"no_datasets": "No datasets found in this dataverse."}))
    return HttpResponse(json.dumps(ids['data']))


def get_info_for_new_dataverse(request):
    # method to prepopulate dataverse creation form with currently available metadata values
    out = dict()
    p_id = request.session['profile_id']
    profile = Profile().get_record(p_id)
    out['dvAlias'] = str(profile['title']).lower()
    person_list = list(Person(p_id).get_people_for_profile())
    out['dvPerson'] = person_list
    orcid = Orcid().get_orcid_profile(request.user)
    try:
        affiliation = orcid.get('op', {}).get('activities_summary', {}).get('employments', {}) \
            .get('employment_summary', {})[0].get('organization', "").get('name', "")
    except:
        affiliation = ""
    out['dsAffiliation'] = affiliation
    df = list(DataFile().get_for_profile(p_id))
    file = df[0]
    out['dvName'] = profile.get('title', "")
    out['dsTitle'] = file.get('description', {}).get('attributes', {}) \
        .get('title_author_contributor', {}).get('dcterms:title', "")
    out['dsDescriptionValue'] = file.get('description', {}).get('attributes', {}) \
        .get('subject_description', {}).get('dcterms:description', "")
    out['dsSubject'] = file.get('description', {}).get('attributes', {}) \
        .get('subject_description', {}).get('dcterms:subject', "")
    return HttpResponse(json_util.dumps(out))


def set_destination_repository(request):
    """
    function sets the destination repository of a submission record, the updated record is returned
    :param request:
    :return:
    """
    submission_id = request.POST['submission_id']
    destination_repo_id = request.POST['destination_repo_id']
    kwargs = dict(target_id=submission_id, destination_repo=destination_repo_id, meta=dict())
    Submission().save_record(dict(), **kwargs)

    result = htags.generate_submissions_records(component="submission", record_id=str(submission_id))

    out = jsonpickle.encode(result, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def update_submission_meta(request):
    """
    function updates a submission record with relevant metadata to aid in fulfilling a submission
    :param request:
    :return:
    """

    submission_id = request.POST.get("submission_id", str())
    form_values = request.POST.get("form_values", dict())

    if form_values and isinstance(form_values, str):
        form_values = json.loads(form_values)

    submission_record = Submission().get_collection_handle().find_one({'_id': ObjectId(submission_id)}, {"meta": 1})

    submission_record["meta"]["type"] = form_values.pop("type", 'unknown')
    submission_record["meta"]["params"] = form_values

    Submission().get_collection_handle().update(
        {"_id": ObjectId(submission_id)},
        {'$set': submission_record})

    result = dict(status=True, message="", value="")

    out = jsonpickle.encode(result, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def update_submission_repo_data(request):
    task = request.POST['task']
    submission_id = request.POST['submission_id']
    if task == 'change_destination':
        custom_repo_id = request.POST['custom_repo_id']
        submission_id = request.POST['submission_id']
        s = Submission().update_destination_repo(repo_id=custom_repo_id, submission_id=submission_id)
        s['record_id'] = str(submission_id)

        clear_submission_metadata(request)

        # return updated submission record for calling agent display
        result = htags.generate_submissions_records(component="submission", record_id=str(submission_id))

        return HttpResponse(json_util.dumps(result))
    elif task == 'change_meta':
        meta = json.loads(request.POST['meta'])
        new_or_existing = meta["new_or_existing"]
        if request.POST.get("type") == "dspace":
            if new_or_existing == "new":
                r_type = request.POST["type"]
                # add meta to separate dict field
                meta["new_or_existing"] = new_or_existing
                meta["repo_type"] = r_type
                m = Submission().get_record(ObjectId(submission_id))["meta"]
                meta["fields"] = m
        elif request.POST.get("type") == "dataverse" or request.POST.get("type") == "ckan":
            if new_or_existing == "new":
                m = Submission().get_record(ObjectId(submission_id))["meta"]
                meta["fields"] = m
                meta["repo_type"] = request.POST["type"]

        # now update submission record
        if type(meta) == type(dict()):
            meta = json.dumps(meta)
        s = Submission().update_meta(submission_id=submission_id, meta=meta)
        return HttpResponse(json.dumps(s))


def clear_submission_metadata(request):
    Submission().clear_submission_metadata(request.POST['submission_id'])


def publish_dataverse(request):
    resp = ds().publish_dataverse(request.POST['sub_id'])
    return HttpResponse(resp)


def delete_repo_entry(request):
    repo_id = request.GET["target_id"]
    deleted = Repository().delete(repo_id)
    return HttpResponse(json.dumps({"deleted": deleted}))


def get_dspace_communities(request):
    sub_id = request.GET['submission_id']
    resp = dspace(sub_id).get_dspace_communites()
    return HttpResponse(resp)


def get_dspace_collection(request):
    sub_id = request.GET['submission_id']
    collection_id = request.GET['collection_id']
    resp = dspace(sub_id).get_dspace_collection(collection_id)
    return HttpResponse(resp)


def get_dspace_items(request):
    sub_id = request.GET['submission_id']
    collection_id = request.GET['collection_id']
    resp = dspace(sub_id).get_dspace_items(collection_id)
    return HttpResponse(resp)


def get_existing_metadata(request):
    # get base metadata for view showing new dspace item
    try:
        sub_id = request.GET["submission_id"]
    except KeyError:
        return HttpResponse(json.dumps({}))
    sub = Submission().get_record(ObjectId(sub_id))

    out = sub["meta"]
    return HttpResponse(json.dumps(out))


def get_ckan_items(request):
    s = request.GET["submission_id"]
    resp = ckan(s)._get_all_datasets()
    return HttpResponse(resp)


def add_personal_dataverse(request):
    url = request.POST["url"]
    name = request.POST["name"]
    apikey = request.POST["apikey"]
    type = request.POST["type"]
    username = request.POST["username"]
    password = request.POST["password"]

    doc = Repository().add_personal_dataverse(url, name, apikey, type, username, password)
    return HttpResponse(json_util.dumps(doc))


def get_personal_dataverses(request):
    repo_ids = request.user.userdetails.repo_submitter
    my_repos = Repository().get_from_list(repo_ids)
    return HttpResponse(json.dumps(my_repos))


def delete_personal_dataverse(request):
    id = request.POST["repo_id"]
    res = Repository().delete(id)
    return HttpResponse(res)


def format_json_response(dict_obj):
    out = jsonpickle.encode(dict_obj, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


def get_subsample_stages(request):
    stage = request.GET["stage"]
    # here we should return a list of the stages which should be displayed for the given sample type
    with open(os.path.join(wf["dtol_manifests"], stage + ".json")) as f:
        sections = json.load(f)
    return HttpResponse(json.dumps(sections))


def sample_spreadsheet(request):
    file = request.FILES["file"]
    name = file.name
    dtol = DtolSpreadsheet(file=file, p_id=request.session["profile_id"])
    if name.endswith("xlsx") or name.endswith("xls"):
        fmt = 'xls'
    elif name.endswith("csv"):
        fmt = 'csv'

    if fmt not in ["xls", "csv"]:
        l.log("ajax handlers: 1324 - unrecognised file format for spreadsheet", type=Logtype.FILE)
        pass

    if dtol.loadManifest(m_format=fmt):
        srlz_dtol = pickle.dumps(dtol.file)
        p_id = request.session["profile_id"]
        r = {"$set": {"manifest_data": srlz_dtol, "profile_id": p_id, "schema_validation_status": "pending",
                      "taxon_validation_status": "pending", "err_msg": [],
                      "time_added": datetime.utcnow(),
                      "file_name": name,
                      "isupdate": False
                      }}
        ValidationQueue().get_collection_handle().update_one({"profile_id": p_id}, r, upsert=True)

    return HttpResponse()

    '''
    else:
        return HttpResponse(status=415,
                            content="Only Excel or CSV files in the exact Darwin Core format are supported.")
    '''


def create_spreadsheet_samples(request):
    validation_record_id = request.GET["validation_record_id"]
    # note calling DtolSpreadsheet without a spreadsheet object will attempt to load one from the session
    dtol = DtolSpreadsheet(validation_record_id=validation_record_id)
    dtol.save_records()
    return HttpResponse(status=200)


def update_spreadsheet_samples(request):
    validation_record_id = request.GET["validation_record_id"]
    # note calling DtolSpreadsheet without a spreadsheet object will attempt to load one from the session
    dtol = DtolSpreadsheet(validation_record_id=validation_record_id)
    dtol.update_records()
    return HttpResponse(status=200)


def update_pending_samples_table(request):
    # samples = Sample().get_unregistered_dtol_samples()
    member_groups = get_group_membership_asString()
    # todo control for someone being both
    profiles = []
    if "dtol_sample_managers" in member_groups:
        profiles = Profile().get_dtol_profiles()
    if "erga_sample_managers" in member_groups:
        profiles += Profile().get_erga_profiles()
    if "dtolenv_sample_managers" in member_groups:
        profiles += Profile().get_dtolenv_profiles()
    return HttpResponse(json_util.dumps(profiles))


def get_samples_for_profile(request):
    url = request.build_absolute_uri()
    if not ViewLock().isViewLockedCreate(url=url):
        profile_id = request.GET["profile_id"]
        filter = request.GET["filter"]
        samples = Sample().get_dtol_from_profile_id(profile_id, filter)
        # notify_frontend(msg="Creating Sample: " + "sprog", action="info",
        #                     html_id="dtol_sample_info")
        return HttpResponse(json_util.dumps(samples))
    else:
        return HttpResponse(json_util.dumps({"locked": True}))


def mark_sample_rejected(request):
    sample_ids = request.GET.get("sample_ids")
    sample_ids = json.loads(sample_ids)
    if sample_ids:
        for sample_id in sample_ids:
            d1 = Sample().mark_rejected(sample_id)
            d2 = Sample().timestamp_dtol_sample_updated(sample_id)
            if not d1 and d2:
                return HttpResponse(status=500)
        return HttpResponse(status=200)
    return HttpResponse(status=500)


def add_sample_to_dtol_submission(request):
    sample_ids = request.GET.get("sample_ids")
    sample_ids = json.loads(sample_ids)
    profile_id = request.GET.get("profile_id")
    # check we have required params
    if sample_ids and profile_id:
        # check for submission object, and create if absent
        sub = Submission().get_dtol_submission_for_profile(profile_id)
        type_sub = Profile().get_record(profile_id)["type"]
        if not sub:
            if type_sub == "Aquatic Symbiosis Genomics (ASG)":
                sub = Submission(profile_id).save_record(dict(), **{"type": "asg"})
            elif type_sub == "European Reference Genome Atlas (ERGA)":
                sub = Submission(profile_id).save_record(dict(), **{"type": "erga"})
            else:
                sub = Submission(profile_id).save_record(dict(), **{"type": "dtol"})
        sub["dtol_status"] = "pending"
        sub["target_id"] = sub.pop("_id")

        for sample_id in sample_ids:
            # iterate over samples and add to submission
            notify_frontend(action="delete_row", html_id=sample_id, data={})
            if not sample_id in sub["dtol_samples"]:
                sub["dtol_samples"].append(sample_id)
            Sample().mark_processing(sample_id)
            Sample().timestamp_dtol_sample_updated(sample_id)
        if Submission().save_record(dict(), **sub):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=500, content="Sample IDs or profile_id not provided")


def delete_dtol_samples(request):
    ids = json.loads(request.POST.get("sample_ids"))
    dtol = DtolSpreadsheet()
    dtol.delete_sample(sample_ids=ids)
    return HttpResponse(json.dumps({}))


def sample_images(request):
    files = request.FILES
    dtol = DtolSpreadsheet()
    matchings = dtol.check_image_names(files)

    return HttpResponse(json.dumps(matchings))


def sample_permits(request):
    files = request.FILES
    dtol = DtolSpreadsheet(validation_record_id=request.POST["validation_record_id"])
    matchings = dtol.check_permit_names(files)

    return HttpResponse(json.dumps(matchings))


def process_column_name(column):
    if "[" in column:
        column_p = column.split("[")[1].split("]")[0]
    else:
        column_p = column
    return column_p


def handle_csv_column_update_spreadsheet(request):
    if request.POST.get("task") == "get":
        sample_ids = json.loads(request.POST.get("records"))
        column = request.POST.get("column")
        column_p = process_column_name(column)
        sample_ids_bson = list(map(lambda id: ObjectId(id), sample_ids))
        if "Name" in column_p:
            # if user wants name, just query for name field in provided ids
            samples = Sample().get_name(column_p, records=sample_ids_bson)
            sample_object = list(samples)
            # create dataframe from returned data
            df = pd.DataFrame(sample_object)
            ex = df.to_csv(index=False)
            # now server as csv
            resp = HttpResponse(ex)
            resp["content_type"] = "text/csv"
            resp["Content-Disposition"] = 'attachment; filename="test.csv"'
            return resp
        if "Characteristics" in column:
            # otherwise user must query querying for characteristics or factors
            samples = Sample().get_characteristic(column=column_p, records=sample_ids_bson)
            lookuptype = "characteristics"
        elif "Factors" in column:
            samples = Sample().get_factor(column=column_p, records=sample_ids_bson)
            lookuptype = "factorValues"
        sample_object = list()
        # create the columns which should appear in the spreadsheet
        for s in samples:
            row = {"_id": s["_id"],
                   "name": s["name"],
                   "label": s[lookuptype]["category"]["annotationValue"],
                   "value": s[lookuptype]["value"]["annotationValue"],
                   "unit": s[lookuptype]["unit"]["annotationValue"],
                   }
            sample_object.append(row)
        # convert to csv and serve
        df = pd.DataFrame(sample_object)
        ex = df.to_csv(index=False)
        resp = HttpResponse(ex)
        resp["content_type"] = "text/csv"
        resp["Content-Disposition"] = 'attachment; filename="test.csv"'
        return resp

    elif request.POST.get("task") == "post":
        file = request.FILES["file"]
        column = request.POST["column"]
        column_p = process_column_name(column)
        profile_id = request.POST["profile_id"]
        if request.POST["update_type"] == "sample":
            # we need to query the sample collection
            out = dict()
            print("reading csv")
            df = pd.read_csv(file, index_col=False)
            nans = pd.isna(df)
            df = df.astype(str)

            df[nans] = ""
            ids = df["_id"]
            sample_ids_bson = list(map(lambda id: ObjectId(id), ids))
            if "Characteristics" in column:
                # otherwise user must query querying for characteristics or factors
                samples = Sample().get_characteristic(column=column_p, records=sample_ids_bson)
                lookuptype = "characteristics"
            elif "Factors" in column:
                samples = Sample().get_factor(column=column_p, records=sample_ids_bson)
                lookuptype = "factorValues"
            # now iterate through returned samples to see what has changed
            updates = list()
            for saved_sample in list(samples):
                # for sample in db, get the old field values
                updated_sample = df.loc[df["_id"] == str(saved_sample["_id"])]
                label = saved_sample[lookuptype]["category"]["annotationValue"]
                label_source = saved_sample[lookuptype]["category"]["termSource"]
                value = saved_sample[lookuptype]["value"]["annotationValue"]
                value_source = saved_sample[lookuptype]["value"]["termSource"]
                unit = saved_sample[lookuptype]["unit"]["annotationValue"]
                unit_source = saved_sample[lookuptype]["unit"]["termSource"]

                # now compare the old field values with what has been parsed out of the
                # updated spreadsheet, and where there are differences, add them to
                # the updates return object
                if (label != updated_sample["label"]).bool():
                    updates.append(
                        {"_id": saved_sample["_id"], "updated_field": "label", "updated_value": updated_sample[
                            "label"].to_string(index=False)})
                '''
                if (label_source != updated_sample["label_source"]).bool():
                    updates.append({"_id": saved_sample["_id"], "updated_field": "label_source", "updated_value":
                        updated_sample["label_source"].to_string(index=False)})
                '''
                if (value != updated_sample["value"]).bool():
                    updates.append({"_id": saved_sample["_id"], "updated_field": "value", "updated_value":
                        updated_sample["value"].to_string(index=False)})
                '''
                if (value_source != updated_sample["value_source"]).bool():
                    updates.append({"_id": saved_sample["_id"], "updated_field": "value_source", "updated_value":
                        updated_sample["value_source"].to_string(index=False)})
                '''
                if (unit != updated_sample["unit"]).bool():
                    updates.append({"_id": saved_sample["_id"], "updated_field": "unit", "updated_value":
                        updated_sample["unit"].to_string(index=False)})
                '''
                if (unit_source != updated_sample["unit_source"]).bool():
                    updates.append({"_id": saved_sample["_id"], "updated_field": "unit_source", "updated_value":
                        updated_sample["unit_source"].to_string(index=False)})
                '''
            return HttpResponse(json_util.dumps(updates))


    elif request.POST["update_type"] == "datafile":
        # query datafile collection
        pass

    return HttpResponse()


def handle_csv_column_validate_spreadsheet(request):
    data = json.loads(request.POST["data"])

    out = list()
    to_lookup = list()

    # make data frame out of to_lookup and unique it to minimize calls to ols
    df = pd.DataFrame(data)
    df["column"] = ""
    df["description"] = ""
    df["ontology_prefix"] = ""
    df["label"] = ""
    df["status"] = ""
    u = df["value"].unique()
    for idx, el in enumerate(u):
        if is_number(el):
            # automatically accept numeric updates for category cells, these don't need ols validation e.g. 13 (
            # milimeters)
            all = df.loc[df["value"] == el]
            all["status"] = "accepted"
            vals = all.to_dict(orient="records")
            out.extend(vals)
            continue;
        fields = ol.ONTOLOGY_LKUPS['fields_to_search']
        q = 'http://www.ebi.ac.uk/ols/api/search?q=' + el
        resp = requests.get(q, timeout=5)
        if resp.status_code == 200:
            print(str(idx) + " Success: " + el)
            data = json.loads(resp.content)
            try:
                ont = data["response"]["docs"][0]
            except IndexError:
                e = dict()
                e["label"] = "Invalid"
                e["status"] = "error"
                out.append(e)
            all = df.loc[df["value"] == el]
            all["description"] = ont.get("description", "No Description")[0]
            all["iri"] = ont["iri"]
            all["ontology_prefix"] = ont["ontology_prefix"]
            all["label"] = ont["label"]
            all["status"] = "tentative"
            vals = all.to_dict(orient="records")
            out.extend(vals)
        else:
            print(str(idx) + " Fail: " + resp.reason)
    return HttpResponse(json.dumps(out))


def get_manifest_submission_list(request):
    profile_id = request.session["profile_id"]
    docs = Submission().get_collection_handle().find({"$and": [
        {"profile_id": profile_id},
        {"manifest_submission": {"$exists": True}},
        {"manifest_submission": {"$eq": 1}}
    ]})
    output = list(docs)
    out = json_util.dumps(output)
    return HttpResponse(out)


def init_manifest_submission(request):
    submission_id = request.POST["submission_id"]
    schedule_submission(submission_id, "ena")
    return HttpResponse()


def process_urls(request):
    file_list = json.loads(request.POST["data"])
    bucket_name = str(request.user.id) + "_" + request.user.username
    s3con = s3()
    if not s3con.check_for_s3_bucket(bucket_name):
        s3con.make_s3_bucket(bucket_name)
    urls_list = list()
    for file_name in file_list:
        if file_name and not file_name.endswith("/"):
            file_name = file_name.replace("*", "")
            url = s3con.get_presigned_url(bucket=bucket_name, key=file_name)
            file_url = {"name": file_name, "url": url}
            urls_list.append(file_url)
    return HttpResponse(json.dumps(urls_list))


def handle_csv_column_update_samples(request):
    data = json.loads(request.POST["data"])
    for el in data:
        sample_ids_bson = [ObjectId(el["record_id"])]
        column_p = process_column_name(el["column"])
        if "Characteristics" in el["column"]:
            # otherwise user must query querying for characteristics or factors
            lookuptype = "characteristics"
        elif "Factors" in el["column"]:
            lookuptype = "factorValues"
        Sample().set_characteristic_or_factor(column=column_p, records=sample_ids_bson, element=el,
                                              char_or_fac=lookuptype)
    return HttpResponse("Complete")


def parse_ena_spreadsheet(request):
    return HttpResponse(request)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_manifest_fields(request):
    manifest_type = request.GET["manifest_type"]
    all_sample_fields = lkup.DTOL_EXPORT_TO_STS_FIELDS[manifest_type]
    # Get field names that begin with an uppercase letter
    sample_fields = list(filter(lambda x: x[0].isupper() == True, all_sample_fields))
    sample_fields.sort()  # Sort the list in ascending order
    return HttpResponse(json.dumps(sample_fields))


def get_common_value_dropdown_list(request):
    manifest_type = request.GET["manifest_type"]
    common_field = request.GET["common_field"]
    common_value_dropdownlist = get_common_field_dropdownlist(common_field, manifest_type)

    return HttpResponse(json.dumps(common_value_dropdownlist))


def generate_manifest_template(request):
    manifest_type = json_util.loads(request.body)["manifest_type"]
    number_of_samples = int(
        json_util.loads(request.body)["row_count"])  # Convert to int
    common_fields = json_util.loads(request.body)[
        "common_fields_list"]
    common_values = json_util.loads(request.body)[
        "common_values_list"]
    manifests_dir = os.path.join("static", "assets", "manifests")

    # Set the path to the blank manifest template based on the manifest type
    if manifest_type == "asg":
        filename = 'ASG_MANIFEST_v2.4.xlsx'  # ASG manifest v2.4 is not available as yet
    elif manifest_type == "dtol":
        filename = 'DToL_SAMPLE_MANIFEST_v2.4.xlsx'
    elif manifest_type == "erga":
        filename = 'ERGA_SAMPLE_MANIFEST_V2.4.xlsx'
    else:
        filename = ''

    manifest_template_path = os.path.join(manifests_dir, filename)

    # Duplicate the common field value according to the number of samples desired
    row_values = [[i] * int(number_of_samples) for i in common_values]

    # Create an Excel file dataframe for the common fields and values using dictionary comprehension
    excel_data = {common_fields[i]: row_values[i] for i in range(len(common_fields))}

    common_field_values_dataframe = pd.DataFrame(excel_data)

    # Read all worksheets from the blank manifest
    blank_manifest_dataframe = pd.read_excel(manifest_template_path, sheet_name=None)

    # Read Metadata Entry worksheet
    metadataEntry_worksheet = blank_manifest_dataframe['Metadata Entry']

    # Read Data Validation worksheet
    dataValidation_worksheet = blank_manifest_dataframe['Data Validation']

    # Read OrganismPartDefinitions worksheet
    organismPartDefinitions_worksheet = blank_manifest_dataframe['OrganismPartDefinitions']

    # Get only the column names from the blank manifest
    # Convert the list of column names into a dataframe
    metadataEntry_worksheet_columns = pd.DataFrame(columns=metadataEntry_worksheet.columns)

    # Get column names from the "OrganismPartDefinitions" worksheet from the blank manifest
    organismPartDefinitions_worksheet_columns = pd.DataFrame(columns=organismPartDefinitions_worksheet.columns)

    # Concatenate the common field and its common values with the respective column names
    # from the blank manifest template
    metadataEntry_worksheet_concatenation = pd.concat([metadataEntry_worksheet_columns, common_field_values_dataframe],
                                                      ignore_index=True)

    bytesIO = BytesIO()
    pandas_writer = pd.ExcelWriter(bytesIO, engine='xlsxwriter')

    # Add the Metadata Entry worksheet to the generated manifest
    # worksheet using data from the blank manifest worksheet
    metadataEntry_worksheet_concatenation.to_excel(pandas_writer, index=False, startrow=0, sheet_name='Metadata Entry')

    # metadataEntry_worksheet_concatenation.style.set_table_styles([{
    #     'selector': 'th',
    #     'props': [
    #         ('text_wrap', True),
    #         ('bold', True),
    #         ('background-color', '#93c47d'),
    #         ('color', 'black')]
    # }])

    # Add the Data Validation worksheet to the generated manifest
    # worksheet using data from the blank manifest worksheet
    dataValidation_worksheet.to_excel(pandas_writer, index=False, startrow=0,
                                      sheet_name='Data Validation')

    # Add the OrganismPartDefinitions worksheet to the generated manifest
    # worksheet using datafrom the blank manifest worksheet
    organismPartDefinitions_worksheet.to_excel(pandas_writer, index=False, startrow=0,
                                               sheet_name='OrganismPartDefinitions')

    # Adjust column width within each worksheet and add a dropdown list to the desired columns
    adjustExcelWorksheetColumnWidth(metadataEntry_worksheet_concatenation, pandas_writer, 'Metadata Entry',
                                    manifest_type)
    adjustExcelWorksheetColumnWidth(dataValidation_worksheet, pandas_writer, 'Data Validation',
                                    manifest_type)
    adjustExcelWorksheetColumnWidth(organismPartDefinitions_worksheet, pandas_writer,
                                    'OrganismPartDefinitions', manifest_type)

    addDropdownlist(metadataEntry_worksheet_concatenation, pandas_writer, 'Metadata Entry',
                    organismPartDefinitions_worksheet_columns, manifest_type)
    pandas_writer.save()

    bytesIO.seek(0)
    excel_workbook = bytesIO.getvalue()

    # 'application/ms-excel'
    response = HttpResponse(excel_workbook,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response


def adjustExcelWorksheetColumnWidth(dataframe, pandas_writer, sheet_name, manifest_type):
    # Get current date then, extract what is between the brackets
    current_date = pd.to_datetime('today').date()
    # Get date from 100 years ago from current date
    century_date = datetime.now() - relativedelta(years=100)
    # Get year from 100 years ago from current year
    century_year = century_date.year
    # .split('(', 1)[1].split(')')[0]
    # Style the header/first row of each each worksheet
    dataframe.style.set_table_styles([{
        'selector': 'th',
        'props': [
            ('background-color', '#93c47d')]
    }])
    for column in dataframe:
        column_length = max(dataframe[column].astype(str).map(len).max(), len(column))
        column_index = dataframe.columns.get_loc(column)
        pandas_writer.sheets[sheet_name].set_column(column_index, column_index, column_length)

        # # Check if sheet is 'Metadata Entry' and column name is present amongst the fields that require a dropdownlist
        # if sheet_name == 'Metadata Entry' and column in lkup.DTOL_ENUMS:
        #     # Get MS Excel official column header letter
        #     # Indexing starts at 0 by default but in this case, it should start at 1 so increment by 1
        #     excel_column_header_letter = get_column_letter(column_index + 1)
        #
        #     # Generate a dropdown list for 96 rows of the desired columns in the Excel spreadsheet
        #     for row_count in range(2, 97):
        #         # Excel and XlsxWriter has a 255 character limit on list/string validation
        #         # therefore, not all items can be listed in a dropdownlist
        #         # Workaround is to pull the list of items from another worksheet in the workbook
        #         # NB: The list of items in the columns - "ORGANISM_PART" and "TISSUE_FOR_BARCODING"
        #         # exceed the 255 character limit so pull the list from the "Data Validation" worksheet
        #
        #         common_value_dropdownlist = get_common_field_dropdownlist(column, manifest_type)
        #         if "DATE" in column:
        #             pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
        #                                                              {'validate': 'date',
        #                                                               'criteria': 'between',
        #                                                               'minimum': date(century_year, 1, 1),
        #                                                               'maximum': current_date})
        #         elif "TIME" in column:
        #             pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
        #                                                              {'validate': 'list',
        #                                                               'criteria': 'between',
        #                                                               'minimum': time(0, 0),
        #                                                               'maximum': time(24, 0)})
        #         elif "ORGANISM_PART" in column:
        #             # 'source': '=$"Data Validation".$C$3:$C$78'
        #             pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
        #                                                              {
        #                                                                  'validate': 'list',
        #                                                                  'source': '=OFFSET("Data Validation"!$C$3,'
        #                                                                            '0,0,COUNTA("Data '
        #                                                                            'Validation"!$C:$C) - 0,1)',
        #                                                              })
        #         elif "TISSUE_FOR_BARCODING" in column:
        #             pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
        #                                                              {'validate': 'list',
        #                                                               'source': '=Data Validation!$I$3:$I$79'})
        #
        #         else:
        #
        #             pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
        #                                                              {'validate': 'list',
        #                                                               'source': common_value_dropdownlist})
        #
        #         if "ORGANISM_PART" in column or "TISSUE_FOR_BARCODING" in column:
        #             print('Field: ', column)
        #             print('"' + column + '" field column: ', excel_column_header_letter + str(row_count))
        #             print('"' + column + '" field dropdownlist: ', common_value_dropdownlist)


def addDropdownlist(dataframe, pandas_writer, sheet_name, organismPartDefinitions_worksheet_columns, manifest_type):
    # Get current date then, extract what is between the brackets
    current_date = pd.to_datetime('today').date()
    # Get date from 100 years ago from current date
    century_date = datetime.now() - relativedelta(years=100)
    # Get year from 100 years ago from current year
    century_year = century_date.year
    dataValidation_worksheet_name = 'Data Validation'

    for column in dataframe:
        column_length = max(dataframe[column].astype(str).map(len).max(), len(column))
        column_index = dataframe.columns.get_loc(column)
        pandas_writer.sheets[sheet_name].set_column(column_index, column_index, column_length)

        # Check if sheet is 'Metadata Entry' and column name is present amongst the fields that require a dropdownlist
        if column in lkup.DTOL_ENUMS:
            # Get MS Excel official column header letter
            # Indexing starts at 0 by default but in this case, it should start at 1 so increment by 1
            excel_column_header_letter = get_column_letter(column_index + 1)

            # Generate a dropdown list for 96 rows of the desired columns in the Excel spreadsheet
            for row_count in range(2, 97):
                # Excel and XlsxWriter has a 255 character limit on list/string validation therefore, not all items
                # can be listed in a dropdownlist
                # Workaround is to pull the list of items from another worksheet in the workbook
                # NB: The list of items in the columns - "ORGANISM_PART", "TISSUE_FOR_BARCODING" and
                # "TISSUE_FOR_BIOBANKING" exceed the 255 character limit so pull the list from the "Data Validation"
                # worksheet

                common_value_dropdownlist = get_common_field_dropdownlist(column, manifest_type)
                if "DATE" in column:
                    pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
                                                                     {'validate': 'date',
                                                                      'criteria': 'between',
                                                                      'minimum': date(century_year, 1, 1),
                                                                      'maximum': current_date})
                elif "TIME" in column:
                    pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
                                                                     {'validate': 'list',
                                                                      'criteria': 'between',
                                                                      'minimum': time(0, 0),
                                                                      'maximum': time(24, 0)})
                elif "ORGANISM_PART" in column:
                    # 'source': '=$"Data Validation".$C$3:$C$78'

                    pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
                                                                     {
                                                                         'validate': 'list',
                                                                         'source': "='" + dataValidation_worksheet_name + "'!$C$3:$C78"
                                                                         ,
                                                                     })
                elif "TISSUE_FOR_BARCODING" in column:
                    pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
                                                                     {'validate': 'list',
                                                                      'source': "='" + dataValidation_worksheet_name + "'!$I$3:$I$79"})

                elif "TISSUE_FOR_BIOBANKING" in column:
                    pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
                                                                     {'validate': 'list',
                                                                      'source': "='" + dataValidation_worksheet_name + "'!$O$3:$I$79"})
                else:

                    pandas_writer.sheets[sheet_name].data_validation(excel_column_header_letter + str(row_count),
                                                                     {'validate': 'list',
                                                                      'source': common_value_dropdownlist})


def get_common_field_dropdownlist(common_field, manifest_type):
    def get_dropdown_items():
        if common_field in fieldsBasedOnManifestType:
            # Get dropdown list based on the manifest type
            dropdownlist = lkup.DTOL_ENUMS[common_field][manifest_type.upper()]
        else:
            # Get dropdown list
            dropdownlist = lkup.DTOL_ENUMS.get(common_field, [])

        dropdownlist.sort()  # Sort the list in ascending order
        return dropdownlist

    fieldsBasedOnManifestType = ["GAL", "HAZARD_GROUP", "PURPOSE_OF_SPECIMEN"]
    common_value_dropdownlist = []

    # The "common field" parameter can be a list or not because the function,
    # get_common_field_dropdownlist(common_field, manifest_type), is called in a
    # couple functions in this file, ajax_handlers.py for various purposes

    # Check if the "common field" parameter is a list or not
    if isinstance(common_field, list):
        common_field_lst = common_field  # Reassign the variable for naming convention's sake, readability and clarity
        # Iterate through the list of common fields for each common field
        for common_field in common_field_lst:
            common_value_dropdownlist = get_dropdown_items()
    else:
        # "Common field" parameter is not a list
        common_value_dropdownlist = get_dropdown_items()

    return common_value_dropdownlist


def validate_common_input_value(request):
    # from web.apps.web_copo.lookup import dtol_lookups as lkup
    # import re

    common_field = request.GET["common_field"]  # common_field = "SAMPLE_DERIVED_FROM"
    common_value_input_value = request.GET["common_input_value"]  # common_value_input_value = 'sdjgzkgzd'
    isInputValueValid = False
    error_message = ''

    if common_field not in lkup.DTOL_RULES:  # common_field in lkup.DTOL_RULES:
        isInputValueValid = True
        print('1')
    else:
        if "strict_regex" in lkup.DTOL_RULES[common_field] and "ena_regex" in lkup.DTOL_RULES[common_field]:
            field_regex = lkup.DTOL_RULES[common_field].get("strict_regex", "ena_regex")
        elif "ena_regex" in lkup.DTOL_RULES[common_field]:
            field_regex = lkup.DTOL_RULES[common_field]["ena_regex"]
        elif "strict_regex" in lkup.DTOL_RULES[common_field]:
            field_regex = lkup.DTOL_RULES[common_field]["strict_regex"]
        else:
            #  "optional_regex" in lkup.DTOL_RULES[common_field]
            field_regex = lkup.DTOL_RULES[common_field]["optional_regex"]

        error_message = lkup.DTOL_RULES[common_field]["human_readable"]

        pattern = re.compile('r' + field_regex)
        isInputValueValid = bool(pattern.match(common_value_input_value))
        print('2')

    if isInputValueValid:
        print('3')
        return HttpResponse(json.dumps({'response': isInputValueValid}))
    else:
        print('4')
        notify_frontend(data={"profile_id": profile_id}, msg="Error occured: " + error_message,
                        action="info",
                        html_id="sample_info")
        return HttpResponseBadRequest(json.dumps({'response': isInputValueValid, 'error': error_message}))

import json
import os
import shutil
import uuid
import pandas
import requests
from allauth.account.forms import LoginForm
from allauth.socialaccount.models import SocialAccount
from bson import ObjectId
from bson import json_util as j
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from jsonpickle import encode
from pexpect import run
from rauth import OAuth2Service
from io import StringIO
import web.apps.web_copo.templatetags.html_tags as htags
from api.views.general import *
from dal import cursor_to_list
from dal.OAuthTokens import OAuthToken
from dal.broker_da import BrokerDA, BrokerVisuals
from dal.copo_da import DataFile, ProfileInfo, Profile, Submission, Annotation, CopoGroup, Repository, MetadataTemplate, Sequnece_annotation, Assembly
from web.apps.web_copo.decorators import user_is_staff
from web.apps.web_copo.lookup.lookup import REPO_NAME_LOOKUP
from web.apps.web_copo.models import banner_view
from web.apps.web_copo.schemas.utils import data_utils
from web.apps.web_copo.utils import EnaImports as eimp
from web.apps.web_copo.utils import group_functions
from .lookup.lookup import HTML_TAGS
from tools.resolve_env import get_env
from web.apps.web_copo.s3.s3Connection import S3Connection
from submission.helpers.generic_helper import notify_frontend

LOGGER = settings.LOGGER
from web.apps.web_copo.models import UserDetails, StatusMessage
from web.forms import AssemblyForm, AnnotationForm, AnnotationFilesForm
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse,  HttpResponseBadRequest
from web.apps.web_copo.utils import EnaAssembly, EnaAnnotation
from submission.helpers.generic_helper import notify_frontend, notify_assembly_status
from django.contrib import messages
from submission.helpers import generic_helper as ghlper



# @login_required
# def index(request):
#     print(get_env("MEDIA_ROOT"))
#     banner = banner_view.objects.all()
#     if len(banner) > 0:
#         context = {'user': request.user, "banner": banner[0]}
#     else:
#         context = {'user': request.user}
#     groups = group_functions.get_group_membership_asString()
#     context['groups'] = groups
#     return render(request, 'copo/index.html', context)


def login(request):
    context = {
        'login_form': LoginForm(),
    }
    return render(request, 'copo/auth/login.html', context)


def stats(request, view=""):
    if view == "time_series":
        return render(request, context={}, template_name="copo/stats/time_series_statistics.html")
    elif view == "variable_histogram":
        return render(request, context={}, template_name="copo/stats/variable_histogram_statistics.html")
    else:
        return render(request, context={}, template_name="copo/stats/time_series_statistics.html")


def test(request):
    return render(request, template_name='copo/test.html')


'''
def test_submission(request):
    delegate_submission(request)
    return render(request, 'copo/copo_annotate_pdf.html', {})
'''


def error_page(request):
    return render(request, context={}, template_name="copo/error_page.html")


def test(request):
    return render(request, "copo/test.html")


@login_required()
def ena_read_manifest_validate(request, profile_id):
    request.session["profile_id"] = profile_id
    return render(request, "copo/ena_read_manifest_validate.html", {"profile_id": profile_id})

@login_required()
def ena_annotation_list(request, profile_id):
    request.session["profile_id"] = profile_id
    return render(request, "copo/ena_annotation_list.html", {"profile_id": profile_id})

'''
def ena_annotation_view(request, profile_id, seq_annotation_id):
    request.session["profile_id"] = profile_id

    seq_annotation = Sequnece_annotation().get_record(seq_annotation_id)
    if not seq_annotation:
        return HttpResponse(content="Sequence Annotation not exists", status=400)
    
    study_accession = ""
    sample_accession = []
    run_accession=[]
    experiment_accession=[]
    existing_sub = Submission().get_records_by_field("profile_id", profile_id)
    existing_accessions = ""
    if existing_sub:
        existing_accessions = existing_sub[0].get("accessions", "")
    if  existing_accessions:
        study = existing_accessions.get("project", "")
        if study:
            if isinstance(study, dict):
                study_accession = study.get("accession", "")
            elif isinstance(study, list):
                study_accession = study[0].get("accession", "")          
        runs = existing_accessions.get("run", "")
        if runs:
            for run in runs:
                if run.get("accession", ""):
                    run_accession.append(run.get("accession", ""))
        experiments = existing_accessions.get("experiment", "")
        if experiments:
            for experiment in experiments:
                if experiment.get("accession", ""):
                    experiment_accession.append(experiment.get("accession", ""))            
        samples = existing_accessions.get("sample", "")
        if samples:
            for sample in samples:
                if sample.get("sample_accession", ""):
                    sample_accession.append(sample.get("sample_accession", ""))

    AnnotationFilesFormSet = formset_factory(AnnotationFilesForm, extra=3 )
    formset = AnnotationFilesFormSet(prefix="annotation_files")
    filenames = seq_annotation.get("filenames", "")
    filetypes = seq_annotation.get("filetypes", "")
    formset = AnnotationFilesFormSet(prefix="annotation_files", initial= [{'file': filenames[i], 'type': filetypes[i]} for i in range(len(filenames))])

    form = AnnotationForm(study_accession=study_accession, sample_accession=sample_accession,run_accession=run_accession,experiment_accession=experiment_accession, seq_annotation=seq_annotation)


    return render(request, "copo/ena_annotation_form.html", {"profile_id": profile_id, "form": form, "formset": formset, "hide_form": False})
'''

@login_required()
def ena_annotation(request, profile_id, seq_annotation_id=None):
    request.session["profile_id"] = profile_id
    is_error = False
    seq_annotation = None

    if seq_annotation_id:
        seq_annotation = Sequnece_annotation().get_record(seq_annotation_id)
        if not seq_annotation:
            return HttpResponse(content="Sequence Annotation not exists", status=400)

    study_accession = ""
    sample_accession = []
    run_accession=[]
    experiment_accession=[]
    existing_sub = Submission().get_records_by_field("profile_id", profile_id)
    existing_accessions = ""
    if existing_sub:
        existing_accessions = existing_sub[0].get("accessions", "")
    if  existing_accessions:
        study = existing_accessions.get("project", "")
        if study:
            if isinstance(study, dict):
                study_accession = study.get("accession", "")
            elif isinstance(study, list):
                study_accession = study[0].get("accession", "")          
        runs = existing_accessions.get("run", "")
        if runs:
            for run in runs:
                if run.get("accession", ""):
                    run_accession.append(run.get("accession", ""))
        experiments = existing_accessions.get("experiment", "")
        if experiments:
            for experiment in experiments:
                if experiment.get("accession", ""):
                    experiment_accession.append(experiment.get("accession", ""))            
        samples = existing_accessions.get("sample", "")
        if samples:
            for sample in samples:
                if sample.get("sample_accession", ""):
                    sample_accession.append(sample.get("sample_accession", ""))

    AnnotationFilesFormSet = formset_factory(AnnotationFilesForm, extra=3 )
    if request.method == 'POST' or request.method == 'PUT':
        # return render(request, "copo/ena_assembly.html", {"profile_id": profile_id, "form": [], "hide_form": False})
        form = AnnotationForm(request.POST, request.FILES, sample_accession=sample_accession, study_accession=study_accession, run_accession=run_accession, experiment_accession=experiment_accession, seq_annotation=seq_annotation)
        formset = AnnotationFilesFormSet(request.POST,request.FILES,prefix="annotation_files")
        if form.is_valid() and formset.is_valid():
            ghlper.notify_annotation_status(data={"profile_id": profile_id},
                            msg="Intitialising Annotation Submission",
                            action="info",
                            html_id="annotation_info")
            # this is a dict
            formdata = form.cleaned_data
            seq_annotation_id = request.POST.get("seq_annotation_id", "")
 
            sub_result = EnaAnnotation.validate_annotation(formdata, formset,  profile_id, seq_annotation_id)
            if sub_result.get("error", ""):
                ghlper.notify_annotation_status(data={"profile_id": profile_id},
                                                msg=sub_result.get("error", ""),
                                                action="error",
                                                html_id="annotation_info")
            else:
                ghlper.notify_annotation_status(data={"profile_id": profile_id},
                                                msg=sub_result.get("success", ""),
                                                action="info",
                                                html_id="annotation_info")
                return JsonResponse(status=201,  data=sub_result)

        else:
            msg = ""
            if not form.is_valid():
                msg = str(form.errors) 
            if not formset.is_valid():
                for f in formset:
                    if f.errors:
                        msg = msg + str(f.errors)
            ghlper.notify_annotation_status(data={"profile_id": profile_id},
                                          msg=msg,
                                          action="error",
                                          html_id="annotation_info")
        return HttpResponse(content="Validation Error", status=400)

    else:

        form = AnnotationForm(study_accession=study_accession, sample_accession=sample_accession,run_accession=run_accession,experiment_accession=experiment_accession, seq_annotation=seq_annotation)
        AnnotationFilesFormSet = formset_factory(AnnotationFilesForm, extra=3 )
        formset = AnnotationFilesFormSet(prefix="annotation_files")
        if seq_annotation:
            filenames = seq_annotation.get("filenames", "")
            filetypes = seq_annotation.get("filetypes", "")
            formset = AnnotationFilesFormSet(prefix="annotation_files", initial= [{'file': filenames[i], 'type': filetypes[i]} for i in range(len(filenames))])

        return render(request, "copo/ena_annotation_form.html", {"profile_id": profile_id, "form": form, "formset": formset, "hide_form": False})


@login_required()
def ena_assembly(request, profile_id, assembly_id=None):
    is_error = False
    request.session["profile_id"] = profile_id
    assembly = None

    if assembly_id:
        assembly = Assembly().get_record(assembly_id)
        if not assembly:
            return HttpResponse(content="Assembly not exists", status=400)

    study_accession = ""
    sample_accession = []

    existing_sub = Submission().get_records_by_field("profile_id", profile_id)
    existing_accessions = ""
    if existing_sub:
        existing_accessions = existing_sub[0].get("accessions", "")
    if  existing_accessions:
        study = existing_accessions.get("project", "")
        if study:
            if isinstance(study, dict):
                study_accession = study.get("accession", "")
            elif isinstance(study, list):
                study_accession = study[0].get("accession", "")
        else:
            study_accession = ""
        samples = existing_accessions.get("sample", "")
        if samples:
            for sample in samples:
                if sample.get("sample_accession", ""):
                    sample_accession.append(sample.get("sample_accession", ""))

    if request.method == 'POST' or request.method == 'PUT':
        # return render(request, "copo/ena_assembly.html", {"profile_id": profile_id, "form": [], "hide_form": False})
        form = AssemblyForm(request.POST,sample_accession=sample_accession, assembly=assembly)
        if form.is_valid():
            notify_frontend(data={"profile_id": profile_id},
                            msg="Intitialising Assembly Submission",
                            action="info",
                            html_id="assembly_info")
            # this is a dict
            formdata = form.cleaned_data
            files = request.FILES
            if not files:
                ghlper.notify_assembly_status(data={"profile_id": profile_id},
                                              msg='At least one assembly file is required',
                                              action="error",
                                              html_id="assembly_info")
                is_error = True
            else:
                # uploading files to folder in COPO
                notify_frontend(data={"profile_id": profile_id}, msg="", action="show",
                                html_id="loading_span")
                EnaAssembly.upload_assembly_files(files)
                assembly_id = request.POST.get("assembly_id", "")

                sub_result = EnaAssembly.validate_assembly(formdata, profile_id,assembly_id)
                if sub_result.get("error", ""):
                    ghlper.notify_assembly_status(data={"profile_id": profile_id},
                                                  msg=sub_result.get("error", ""),
                                                  action="error",
                                                  html_id="assembly_info")
                    is_error = True
                    # messages.error(request,sub_result)
                else:
                    ghlper.notify_assembly_status(data={"profile_id": profile_id},
                                                  msg="The assembly has been created with accession: " + sub_result.get(
                                                      "accession", "Success"),
                                                  action="info",
                                                  html_id="assembly_info")
                # form = AssemblyForm(study_accession=study_accession, sample_accession=sample_accession)
                # return HttpResponse()
        else:
            ghlper.notify_assembly_status(data={"profile_id": profile_id},
                                          msg=str(form.errors),
                                          action="error",
                                          html_id="assembly_info")
            is_error = True
            # messages.error(request, form.errors)

    else:

        # todo I'm probably out of time to do this, but we need to account -maybe?- for a situation in which we have
        # multiple assemblies submitted as part of the same profile, probably the structure in the database need to
        # change slightly so that it is possible for us to link accession and relative sample
        # eg. accessions: {assembly: {accession:,alias:, SAMPLE}} in copo_da add_assembly_accession
        #
        # pass the accessions as "study_accession" and "sample_ccession" to the form so that they are
        # set authomatically and cannot be changed by the user
        form = AssemblyForm(study_accession=study_accession, sample_accession=sample_accession, assembly=assembly
                            # initial={"assemblyname": "jdklsad", "coverage": 1, "program": "jiwjd", "platform": "kkfjoep", "mingaplength": 10,
                            #         "description": "jfksjkdlfs"}
                            )
        return render(request, "copo/ena_assembly_form.html", {"profile_id": profile_id, "form": form, "hide_form": False})
    if is_error:
        return HttpResponse(content="Validation Error", status=400)
    return HttpResponse(status=200)


@login_required
def copo_repository(request, profile_id):
    profile = Profile().get_record(profile_id)
    return render(request, 'copo/copo_repo.html', {'profile_id': profile_id, 'profile': profile})


def forward_to_info(request):
    message = request.GET['message']
    control = request.GET['control']
    return render(request, 'copo/info_page.html', {'message': message, 'control': control})


def authenticate_figshare(request):
    return render(request, 'copo/info_page.html',
                  {'message': 'COPO needs permission to submit to Figshare on your behalf.<br/>' +
                              'Please sign into Figshare and try again.',
                   'control': HTML_TAGS['oauth_required']})


def test_dataverse_submit(request):
    return render(request, 'copo/copo_annotate_pdf.html', {})


@login_required
def view_copo_profile(request, profile_id):
    request.session["profile_id"] = profile_id

    profile = Profile().get_record(profile_id)
    if not profile:
        return render(request, 'copo/error_page.html')
    context = {"p_id": profile_id, 'counts': ProfileInfo(profile_id).get_counts(), "profile": profile}
    return render(request, 'copo/copo_profile.html', context)


@login_required
def get_profile_counts(request):
    profile_id = request.session["profile_id"]
    counts = ProfileInfo(profile_id).get_counts()
    return HttpResponse(encode(counts))


@login_required
def view_templates(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)

    return render(request, 'copo/metadata_templates.html', {'profile_id': profile_id, 'profile': profile})


@login_required
def author_template(request, template_id):
    record = MetadataTemplate().get_by_id(template_id)
    context = {"template_name": record["template_name"], "template_id": template_id}
    return render(request, "copo/author_metadata_template.html", context)


@login_required
def copo_publications(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)

    return render(request, 'copo/copo_publications.html', {'profile_id': profile_id, 'profile': profile})


@login_required
def copo_people(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)

    return render(request, 'copo/copo_people.html', {'profile_id': profile_id, 'profile': profile})


@login_required
def copo_repositories(request):
    user = request.user.id
    return render(request, 'copo/my_repositories.html')


@login_required
def copo_samples(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)
    groups = group_functions.get_group_membership_asString()
    return render(request, 'copo/copo_sample.html', {'profile_id': profile_id, 'profile': profile, 'groups': groups})


@login_required
def copo_sample_accept_reject(request):
    return render(request, 'copo/copo_sample_accept_reject.html', {})


@login_required()
def annotate_meta(request, file_id):
    if "ss_data" in request.session:
        del request.session["ss_data"]
    if "ss_sheet_names" in request.session:
        del request.session["ss_sheet_names"]
    df = DataFile().get_record(ObjectId(file_id))
    name = df["name"]
    if name.endswith(('xls', 'xlsx')):
        return render(request, 'copo/copo_annotate_spreadsheet.html',
                      {'file_id': file_id, 'file_name': name, 'file_type': "ss"})
    elif name.endswith("csv"):
        return render(request, 'copo/copo_annotate_spreadsheet.html',
                      {'file_id': file_id, 'file_name': name, 'file_type': "csv"})
    elif name.endswith(("txt", "tsv")):
        return render(request, 'copo/copo_annotate_spreadsheet.html',
                      {'file_id': file_id, 'file_name': name, 'file_type': "tab"})
    elif name.endswith(('pdf')):
        html = ""
        records = Annotation().get_all_records()
        if "annotation_html" not in request.session:
            # if True:
            folder_name = str(uuid.uuid1())
            full_path = os.path.join(settings.MEDIA_ROOT, folder_name)
            os.makedirs(full_path)
            run("ebook-convert  " + df[
                "file_location"] + " " + full_path + " --no-images --pretty-print --insert-blank-line")
            with open(os.path.join(full_path, "index.html"), 'r') as f:
                html = f.read()
            shutil.rmtree(full_path)
            # request.session["annotation_html"] = html
        else:
            print("using session text data")
            html = request.session["annotation_html"]
        return render(request, 'copo/copo_annotate_pdf.html',
                      {'html': html, 'file_id': file_id, 'file_name': name, "file_type": "pdf"})


@login_required
def copo_data(request, profile_id):
    request.session['datafile_url'] = request.path
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)
    table_columns = htags.generate_table_columns("datafile")
    return render(request, 'copo/copo_data.html',
                  {'profile_id': profile_id, 'profile': profile, 'table_columns': jsonpickle.encode(table_columns)})


def copo_docs(request):
    context = dict()
    return render(request, 'copo/copo_docs.html', {'context': context})


def resolve_submission_id(request, submission_id):
    sub = Submission().get_record(submission_id)
    # get all file metadata
    output = dict()
    files = list()
    for f in sub.get("bundle", list()):
        file = DataFile().get_record(f)
        files.append(file["description"]["attributes"])
    output["files"] = files
    output["accessions"] = sub["accessions"]
    output["metadata"] = {}
    output["metadata"]["dc"] = sub["meta"]["fields"]
    return HttpResponse(j.dumps(output))


@login_required
def copo_visualize(request):
    context = dict()

    task = request.POST.get("task", str())

    profile_id = request.session.get("profile_id", str())

    context["quick_tour_flag"] = request.session.get("quick_tour_flag", True)
    request.session["quick_tour_flag"] = context["quick_tour_flag"]  # for displaying tour message across site

    broker_visuals = BrokerVisuals(context=context,
                                   profile_id=profile_id,
                                   request=request,
                                   user_id=request.user.id,
                                   component=request.POST.get("component", str()),
                                   target_id=request.POST.get("target_id", str()),
                                   quick_tour_flag=request.POST.get("quick_tour_flag", False),
                                   datafile_ids=json.loads(request.POST.get("datafile_ids", "[]"))
                                   )

    task_dict = dict(table_data=broker_visuals.do_table_data,
                     server_side_table_data=broker_visuals.do_server_side_table_data,
                     profiles_counts=broker_visuals.do_profiles_counts,
                     wizard_messages=broker_visuals.do_wizard_messages,
                     metadata_ratings=broker_visuals.do_metadata_ratings,
                     description_summary=broker_visuals.do_description_summary,
                     un_describe=broker_visuals.do_un_describe,
                     attributes_display=broker_visuals.do_attributes_display,
                     help_messages=broker_visuals.get_component_help_messages,
                     update_quick_tour_flag=broker_visuals.do_update_quick_tour_flag,
                     get_component_info=broker_visuals.do_get_component_info,
                     get_profile_info=broker_visuals.do_get_profile_info,
                     get_submission_accessions=broker_visuals.do_get_submission_accessions,
                     get_submission_datafiles=broker_visuals.do_get_submission_datafiles,
                     get_destination_repo=broker_visuals.do_get_destination_repo,
                     get_repo_stats=broker_visuals.do_get_repo_stats,
                     managed_repositories=broker_visuals.do_managed_repositories,
                     get_submission_meta_repo=broker_visuals.do_get_submission_meta_repo,
                     view_submission_remote=broker_visuals.do_view_submission_remote,
                     )

    if task in task_dict:
        context = task_dict[task]()

    out = jsonpickle.encode(context, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


@login_required
def copo_forms(request):
    context = dict()
    task = request.POST.get("task", str())

    profile_id = request.session.get("profile_id", str())

    if request.POST.get("profile_id", str()):
        profile_id = request.POST.get("profile_id")
        request.session["profile_id"] = profile_id

    broker_da = BrokerDA(context=context,
                         profile_id=profile_id,
                         component=request.POST.get("component", str()),
                         referenced_field=request.POST.get("referenced_field", str()),
                         referenced_type=request.POST.get("referenced_type", str()),
                         target_id=request.POST.get("target_id", str()),
                         target_ids=json.loads(request.POST.get("target_ids", "[]")),
                         datafile_ids=json.loads(request.POST.get("datafile_ids", "[]")),
                         auto_fields=request.POST.get("auto_fields", dict()),
                         visualize=request.POST.get("visualize", str()),
                         id_handle=request.POST.get("id_handle", str()),
                         user_id=request.user.id,
                         action_type=request.POST.get("action_type", str()),
                         id_type=request.POST.get("id_type", str()),
                         data_source=request.POST.get("data_source", str()),
                         user_email=request.POST.get("user_email", str()),
                         bundle_name=request.POST.get("bundle_name", str()),
                         )

    task_dict = dict(resources=broker_da.do_form_control_schemas,
                     save=broker_da.do_save_edit,
                     edit=broker_da.do_save_edit,
                     delete=broker_da.do_delete,
                     validate_and_delete=broker_da.validate_and_delete,
                     form=broker_da.do_form,
                     form_and_component_records=broker_da.do_form_and_component_records,
                     doi=broker_da.do_doi,
                     initiate_submission=broker_da.do_initiate_submission,
                     user_email=broker_da.do_user_email,
                     component_record=broker_da.do_component_record,
                     component_form_record=broker_da.component_form_record,
                     sanitise_submissions=broker_da.do_sanitise_submissions,
                     create_rename_description_bundle=broker_da.create_rename_description_bundle,
                     clone_description_bundle=broker_da.do_clone_description_bundle,
                     lift_submission_embargo=broker_da.do_lift_submission_embargo,
                     submit_assembly=broker_da.do_submit_assembly,
                     submit_annotation=broker_da.do_submit_annotation,
                     submit_read=broker_da.do_submit_read,
                     delete_read=broker_da.do_delete_read,
                     )

    if task in task_dict:
        context = task_dict[task]()

    out = jsonpickle.encode(context, unpicklable=False)
    status = context.get("action_feedback", dict()).get("status", "success")
    if status=="success":
        return HttpResponse(status=200, content=out, content_type='application/json')
    
    return HttpResponse(status=400, content=out, content_type='application/json')


@login_required()
def delete_profile(request):
    context = dict()
    task = request.POST.get("task", str())

    x = 0
    profile_ids = []
    while request.POST.get("target_id[" + str(x) + "][record_id]", ""):
        profile_ids.append(request.POST.get("target_id[" + str(x) + "][record_id]", ""))
        x += 1

    response = HttpResponse(content_type="application/json")
    response.status_code = 200
    profiles_undeleted = []
    if not profile_ids:
        response.status_code = 405
    else:
        for profile in profile_ids:
            if not Profile().validate_and_delete(profile):
                profiles_undeleted.append(profile)
                response.status_code = 405
    undeleted_json = json.dumps({"undeleted": profiles_undeleted})
    response.write(undeleted_json)
    return response


@login_required
@staff_member_required
def copo_admin(request):
    context = dict()
    task = request.POST.get("task", str())

    out = jsonpickle.encode(context)
    return HttpResponse(out, content_type='application/json')


@login_required
def copo_submissions(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)

    return render(request, 'copo/copo_submission.html', {'profile_id': profile_id, 'profile': profile})


@login_required
def copo_get_submission_table_data(request):
    profile_id = request.POST.get('profile_id')
    submission = Submission(profile_id=profile_id).get_all_records(sort_by="date_created", sort_direction="-1")
    for s in submission:
        s['date_created'] = s['date_created'].strftime('%d %b %Y - %I:%M %p')
        s['date_modified'] = s['date_modified'].strftime('%d %b %Y - %I:%M %p')
        s['display_name'] = REPO_NAME_LOOKUP[s['repository']]
        if s['complete'] == 'false' or s['complete'] == False:
            s['status'] = 'Pending'
        else:
            s['status'] = 'Submitted'

    out = j.dumps(submission)
    return HttpResponse(out)


@login_required
def goto_error(request, message="Something went wrong, but we're not sure what!"):
    try:
        LOGGER.log(message)
    finally:
        context = {'message': message}
        return render(request, 'copo/error_page.html', context)


def copo_logout(request):
    logout(request)
    return render(request, 'copo/auth/logout.html', {})


def copo_register(request):
    if request.method == 'GET':
        return render(request, 'copo/register.html')
    else:
        # create user and return to auth page
        firstname = request.POST['frm_register_firstname']
        lastname = request.POST['frm_register_lastname']
        email = request.POST['frm_register_email']
        username = request.POST['frm_register_username']
        password = request.POST['frm_register_password']

        user = User.objects.create_user(username, email, password)
        user.set_password(password)
        user.last_name = lastname
        user.first_name = firstname
        user.save()

        return render(request, 'copo/templates/account/auth.html')


@login_required
def view_user_info(request):
    user = data_utils.get_current_user()
    # op = Orcid().get_orcid_profile(user)
    d = SocialAccount.objects.get(user_id=user.id)
    op = json.loads(json.dumps(d.extra_data).replace("-", "_"))

    repo_ids = user.userdetails.repo_submitter
    repos = Repository().get_by_ids(repo_ids)
    # data_dict = jsonpickle.encode(data_dict)
    data_dict = {'orcid': op, "repos": repos}

    return render(request, 'copo/user_info.html', data_dict)


def register_to_irods(request):
    status = register_to_irods()
    return_structure = {'exit_status': status}
    out = jsonpickle.encode(return_structure)
    return HttpResponse(out, content_type='json')


def view_oauth_tokens(request):
    return render(request, 'copo/copo_tokens.html', {})


def annotate_data(request):
    doc = Annotation().get_record(request.POST.get('target_id'))
    return HttpResponse(j.dumps(doc))


def load_cyverse_files(request, url, token):
    # get file data and pass to copo_data view
    url_filesystem = 'https://agave.iplantc.org/terrain/v2/secured/filesystem/directory?path=/iplant/home/shared'
    headers = {"Authorization": "Bearer " + token['token']['access_token']}
    cvd = requests.get(url_filesystem, headers=headers)
    cyverse_data = json.loads(cvd.content.decode('utf-8'))
    fnames = list()
    for el in cyverse_data['folders']:
        fnames.append({'text': el['label']})
    return copo_data(request, request.session['profile_id'], json.dumps(fnames))


def agave_oauth(request):
    # check for token
    token = OAuthToken().cyverse_get_token(request.user.id)
    if token:
        # get token and pass
        OAuthToken().check_token(token)
        url = request.path
        return load_cyverse_files(request, url, token)
    else:

        service = OAuth2Service(
            name='copo_api',
            client_id='KOm9gFBPVwq6sfCMgumZRJG5j8wa',
            client_secret='gAnX96MinyBfZ_gsvkr0nEDLpR8a',
            access_token_url='https://agave.iplantc.org/oauth2/token',
            authorize_url='https://agave.iplantc.org/oauth2/authorize',
            base_url='https://agave.iplantc.org/oauth2/')

        # the return URL is used to validate the request
        params = {'redirect_uri': 'http://127.0.0.1:8000/copo/agave_oauth',
                  'response_type': 'code'}
        if not 'code' in request.GET:
            # save url for initial page

            url = service.get_authorize_url(**params)
            return redirect(url)
        else:

            # once the above URL is consumed by a client we can ask for an access
            # token. note that the code is retrieved from the redirect URL above,
            # as set by the provider
            code = request.GET['code']

            params = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": "KOm9gFBPVwq6sfCMgumZRJG5j8wa",
                "client_secret": "gAnX96MinyBfZ_gsvkr0nEDLpR8a",
                "redirect_uri": "http://127.0.0.1:8000/copo/agave_oauth"
            }

            r = requests.post("https://agave.iplantc.org/oauth2/token", data=params)

            if r.status_code == 401:
                # refresh token
                pass
            else:
                # save token
                t = json.loads(r.content.decode('utf-8'))
                OAuthToken().cyverse_save_token(request.user.id, t)
                return redirect(request.session['datafile_url'])


def import_ena_accession(request):
    if request.method == 'GET':
        profile_id = request.session['profile_id']
        return render(request, 'copo/import_ena_accession.html', {'profile_id': profile_id})
    else:
        accessions = request.POST['accessions']
        accessions = accessions.split(',')

        output = list()
        for acc in accessions:
            output.append(eimp.do_import_ena_accession(acc))
        return HttpResponse(output)


@login_required()
def view_groups(request):
    # g = Group().create_group(description="test descrition")
    profile_list = cursor_to_list(Profile().get_for_user())
    group_list = cursor_to_list(CopoGroup().get_by_owner(request.user.id))
    return render(request, 'copo/copo_group.html',
                  {'request': request, 'profile_list': profile_list, 'group_list': group_list})


# @login_required()
@user_is_staff
def administer_repos(request):
    return render(request, 'copo/copo_repository.html', {'request': request})


@user_is_staff
def copo_repositories(request):
    return render(request, 'copo/copo_repository_admin.html', {'request': request})


def manage_repos(request):
    return render(request, 'copo/copo_repo_management.html', {'request': request})


def manage_repositories(request):
    return render(request, 'copo/copo_repository_manage.html', {'request': request})


def handler404(request, exception):
    return error_page(request)


def handler500(request):
    return error_page(request)

@login_required
def copo_seq_annotation(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)
    return render(request, 'copo/copo_seq_annotation.html', {'profile_id': profile_id, 'profile': profile})

@login_required
def copo_assembly(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)
    return render(request, 'copo/copo_assembly.html', {'profile_id': profile_id, 'profile': profile})

@login_required
def copo_reads(request, profile_id):
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)
    groups = group_functions.get_group_membership_asString()
    return render(request, 'copo/copo_read.html', {'profile_id': profile_id, 'profile': profile, 'groups': groups})
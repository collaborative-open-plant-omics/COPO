import json
import os
import shutil
import uuid
import pandas
import requests
from allauth.account.forms import LoginForm
from allauth.socialaccount.models import SocialAccount
from bson import json_util, ObjectId
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
from dal import cursor_to_list, cursor_to_list_str
from dal.OAuthTokens import OAuthToken
from dal.broker_da import BrokerDA, BrokerVisuals
from dal.copo_da import DataFile
from dal.copo_da import ProfileInfo, Profile, Submission, Annotation, CopoGroup, Repository, MetadataTemplate
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
from web.forms import AssemblyForm
from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse, HttpResponseRedirect
import operator
from web.apps.web_copo.utils import EnaAssembly
from submission.helpers.generic_helper import notify_frontend, notify_assembly_status
from django.contrib import messages
from submission.helpers import generic_helper as ghlper

# @login_required
# def copo_accessions(request, profile_id):
#     request.session["profile_id"] = profile_id
#     profile = Profile().get_record(profile_id)
#     groups = group_functions.get_group_membership_asString()
#     return render(request, 'copo/accessions/copo_accessions.html',
#                   {'profile_id': profile_id, 'profile': profile, 'groups': groups})

# def copo_accessions_visualise(request):
# print("Hi in python")
# sample_id = request.POST.get("sample_id", str())
# isSampleProfileTypeStandalone = request.POST.get("isSampleProfileTypeStandalone", False)
# # profile_id = request.session.get("profile_id", str())
# print("Sample ID: ", sample_id)
#
# # p_type = Profile().get_type(profile_id=profile_id)
#
# # print("Ajax/request profile ID: ", profile_id)
# print("Is project type standalone: ", isSampleProfileTypeStandalone)
#
# if isSampleProfileTypeStandalone:  # "Standalone" not in p_type:
#     samples = Sample().get_accessions(sample_id, isSampleProfileTypeStandalone=False, isCurrentUser=True)
#
# else:
#     samples = Sample().get_accessions(sample_id, isSampleProfileTypeStandalone=True, isCurrentUser=True)
#
# return HttpResponse(json_util.dumps(samples))

# context = dict()
#
# task = request.POST.get("task", str())
#
# context["quick_tour_flag"] = request.session.get("quick_tour_flag", True)
# request.session["quick_tour_flag"] = context["quick_tour_flag"]  # for displaying tour message across site
#
# broker_visuals = BrokerVisuals(context=context,
#                                profile_id=profile_id,
#                                request=request,
#                                component=request.POST.get("component", str()),
#                                target_id=request.POST.get("target_id", str())
#                                )
#
# task_dict = dict(table_data=broker_visuals.do_table_data)
#
# if task in task_dict:
#     context = task_dict[task]()
#
# out = jsonpickle.encode(context, unpicklable=False)
# return HttpResponse(out, content_type='application/json')
required_member_groups = ['dtol_users', 'dtol_sample_managers', 'dtolenv_users', 'dtolenv_sample_managers',
                          'erga_users', 'erga_sample_managers']


@login_required
def copo_accessions(request, profile_id):
    # The input parameter, 'profile_id' is actually 'sample_id'
    # profile_id = Sample().get_profileID_by_sampleID(profile_id)
    request.session["profile_id"] = profile_id
    profile = Profile().get_record(profile_id)
    groups = group_functions.get_group_membership_asString()
    return render(request, 'copo/accessions/copo_accessions.html',
                  {'profile_id': profile_id, 'profile': profile, 'groups': groups})


@login_required
def copo_accessions_visualise(request):
    isUserProfileActive = convertStringToBoolean(request.POST.get("isUserProfileActive", str()))
    profile_id = request.session.get("profile_id")
    isSampleProfileTypeStandalone = convertStringToBoolean(request.POST.get("isSampleProfileTypeStandalone", str()))

    samples = Sample().get_accessions(profile_id, isSampleProfileTypeStandalone, isUserProfileActive)
    samples = [dict(sorted(i.items())) for i in samples]  # Sort the list of samples by key

    return HttpResponse(json_util.dumps(samples))


@login_required
def copo_accessions_all(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()
    groups = group_functions.get_group_membership_asString()

    if any(item in member_groups for item in required_member_groups):
        return render(request, 'copo/accessions/copo_accessions_all.html',
                      {'groups': groups, 'profile_id': '999'})
    else:
        return goto_unauthorised_page()


@login_required
def goto_unauthorised_page(request, message="Apologies, you do not have permission to view this web page"):
    try:
        LOGGER.log(message)
    finally:
        context = {'message': message}
        return render(request, 'copo/unauthorised_page.html', context)


def convertStringToBoolean(string):
    # Convert string boolean to boolean
    return str(string).lower() in ("yes", "true", "t", "1")

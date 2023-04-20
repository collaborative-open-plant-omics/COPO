from api.views.general import *
from dal import cursor_to_list_str2
from dal.broker_da import BrokerDA, BrokerVisuals
from dal.copo_da import ProfileInfo, Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from jsonpickle import encode
from tools.resolve_env import get_env
from web.apps.web_copo.models import banner_view
from web.apps.web_copo.utils import group_functions

import pymongo
import re

LOGGER = settings.LOGGER


@login_required
def copo_profile_index(request):
    print(get_env("MEDIA_ROOT"))
    # Profiles
    num_of_profiles_per_page = 8  # number of records to display by default on a single page
    uid = request.user.id
    page = int(request.GET.get('page', 1))  # current page
    profiles_length = Profile().get_collection_handle().find({"user_id": uid}).count()
    num_of_pages = profiles_length / num_of_profiles_per_page  # row count
    db_skip_num = num_of_profiles_per_page * (page - 1)

    # Get/load 8 profiles on downwards scroll
    existing_profiles_paginated = Profile().get_collection_handle().find({"user_id": uid}).sort("date_modified",
                                                                                                pymongo.DESCENDING).skip(
        db_skip_num).limit(
        num_of_profiles_per_page)

    profile_page = cursor_to_list_str2(existing_profiles_paginated, use_underscore_in_id=False)

    profile_page_length = len(profile_page)
    profile_page_length += profile_page_length

    # Banner and groups
    banner = banner_view.objects.all()
    if len(banner) > 0:
        context = {'user': request.user, "banner": banner[0]}
    else:
        context = {'user': request.user}
    groups = group_functions.get_group_membership_asString()
    context['groups'] = groups

    if not request.is_ajax():
        # Set up the profile grids that are loaded by default when a user launches the web page
        context['profiles'] = profile_page
        context['profiles_total'] = profiles_length
        return render(request, 'copo/profile/copo_profile_index.html', context)
    else:
        # Set up the profile grids that are loaded when a user scrolls down the web page
        content = ''

        for profile in profile_page:
            content += render_to_string('copo/profile/copo_profile_record.html',
                                        {'profile': profile},
                                        request=request)
        return JsonResponse({
            "content": content,
            "end_pagination": True if page >= num_of_pages else False})


@login_required
def copo_profile_forms(request):
    context = dict()
    task = request.POST.get("task", str())

    profile_id = request.session.get("profile_id", str())

    if request.POST.get("profile_id", str()):
        profile_id = request.POST.get("profile_id")
        request.session["profile_id"] = profile_id

    broker_da = BrokerDA(auto_fields=request.POST.get("auto_fields", dict()),
                         component=request.POST.get("component", str()),
                         context=context,
                         profile_id=profile_id,
                         target_id=request.POST.get("target_id", str()),
                         user_email=request.POST.get("user_email", str()),
                         visualize=request.POST.get("visualize", str()))

    task_dict = dict(edit=broker_da.do_save_edit,
                     delete=broker_da.do_delete,
                     form=broker_da.do_form,
                     resources=broker_da.do_form_control_schemas,
                     save=broker_da.do_save_edit,
                     user_email=broker_da.do_user_email,
                     validate_and_delete=broker_da.validate_and_delete)

    if task in task_dict:
        context = task_dict[task]()

    out = jsonpickle.encode(context, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


@login_required
def copo_profile_visualise(request):
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
                                   quick_tour_flag=request.POST.get("quick_tour_flag", False))

    task_dict = dict(help_messages=broker_visuals.get_component_help_messages,
                     profiles_counts=broker_visuals.do_profiles_counts,
                     update_quick_tour_flag=broker_visuals.do_update_quick_tour_flag)

    if task in task_dict:
        context = task_dict[task]()

    out = jsonpickle.encode(context, unpicklable=False)
    return HttpResponse(out, content_type='application/json')


@login_required()
def delete_profile(request):
    profile_id = request.POST.get("target_id", "")

    response = HttpResponse(content_type="application/json")
    response.status_code = 200
    profile_undeleted = []

    if not profile_id:
        response.status_code = 405
    else:
        if not Profile().validate_and_delete(profile_id):
            profile_undeleted.append(profile_id)
            response.status_code = 405
    undeleted_json = json.dumps({"undeleted": [profile_undeleted]})
    response.write(undeleted_json)
    return response


@login_required
def get_profile_counts(request):
    profile_id = request.session["profile_id"]
    counts = ProfileInfo(profile_id).get_counts()
    return HttpResponse(encode(counts))


@login_required
def view_copo_profile(request, profile_id):
    request.session["profile_id"] = profile_id

    profile = Profile().get_record(profile_id)
    if not profile:
        return render(request, 'copo/error_page.html')
    context = {"p_id": profile_id, 'counts': ProfileInfo(profile_id).get_counts(), "profile": profile}
    return render(request, 'copo/copo_profile.html', context)


def setup_associated_profile_types(element, associated_type, additional_info_dict):
    if associated_type:
        associated_type_count = len(associated_type)
        associated_type_columnCount = "2" if associated_type_count > 3 else "1"
        regex = '\(([^)]+)'

        additional_info_dict = {"associated_type_columnCount": associated_type_columnCount}
        element.update(additional_info_dict)

        # Create a dictionary of associated type acronym and associated_type
        element_lst = []
        for associated_type in associated_type:
            # Extract parentheses and its enclosed value from associated type
            acronym = re.search(regex, associated_type).group(1) if re.search(regex,
                                                                              associated_type) else associated_type

            element_lst.append({"associated_type": associated_type, "acronym": acronym})

        associated_type_elements = {"associated_type_elements": element_lst}
        element.update(associated_type_elements)
    else:
        element.update(additional_info_dict)

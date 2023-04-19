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
    num_of_profiles_per_page = 8  # number of records to display by default on a single page
    uid = request.user.id
    page = int(request.GET.get('page', 1))  # current page

    # Banner and groups
    banner = banner_view.objects.all()
    if len(banner) > 0:
        context = {'user': request.user, "banner": banner[0]}
    else:
        context = {'user': request.user}
    groups = group_functions.get_group_membership_asString()
    context['groups'] = groups

    # Get all profiles
    existing_profiles = Profile().get_collection_handle().find({"user_id": uid}).sort("date_modified",
                                                                                      pymongo.DESCENDING)
    profiles_length = len([i for i in existing_profiles if i])
    num_of_pages = profiles_length / num_of_profiles_per_page  # row count
    db_skip_num = num_of_profiles_per_page * (page - 1)

    # Get/load 8 profiles on downwards scroll
    existing_profiles_paginated = Profile().get_collection_handle().find({"user_id": uid}).sort("date_modified",
                                                                                                pymongo.DESCENDING).skip(
        db_skip_num).limit(
        num_of_profiles_per_page * page)

    profile_page = cursor_to_list_str2(existing_profiles_paginated, use_underscore_in_id=False)

    profile_page_length = len([i for i in profile_page if i])
    profile_page_length += profile_page_length
    profiles_legend_lst = []

    # Set up the profile grids when a user launches the web page
    for i in profile_page:
        # Set panel heading background colour and small text for each profile record
        # set_profile_heading(i, additional_info_dict, profiles_legend_lst)

        if "DTOL_ENV" in i.get("type", ""):
            additional_info_dict = {"heading_bgColour": "#fb7d0d", "title_smallText": "(DTOL-ENV)"}
            profiles_legend = {'profileType': i.get("type", ""), "profileTypeAcronym": "DTOL-ENV",
                               "profileTypeColour": "#fb7d0d"}
            i.update(additional_info_dict)

            # Check if legend data for this profile type already exists in the legend list
            if not any(x.get('profileType', "") == i.get("type", "") for x in profiles_legend_lst):
                i.update(profiles_legend)
            else:
                continue

        elif "DTOL" in i.get("type", ""):
            additional_info_dict = {"heading_bgColour": "#16ab39", "title_smallText": "(DTOL)"}
            profiles_legend = {'profileType': i.get("type", ""), "profileTypeAcronym": "DTOL",
                               "profileTypeColour": "#16ab39"}
            i.update(additional_info_dict)

            # Check if legend data for this profile type already exists in the legend list
            if not any(x.get('profileType', "") == i.get("type", "") for x in profiles_legend_lst):
                i.update(profiles_legend)
            else:
                continue
        elif "ASG" in i.get("type", ""):
            additional_info_dict = {"heading_bgColour": "#5829bb", "title_smallText": "(ASG)"}
            profiles_legend = {'profileType': i.get("type", ""), "profileTypeAcronym": "ASG",
                               "profileTypeColour": "#5829bb"}
            i.update(additional_info_dict)

            # Check if legend data for this profile type already exists in the legend list
            if not any(x.get('profileType', "") == i.get("type", "") for x in profiles_legend_lst):
                i.update(profiles_legend)
            else:
                continue
        elif "ERGA" in i.get("type", ""):
            additional_info_dict = {"heading_bgColour": "#E61A8D", "title_smallText": "(ERGA)"}
            profiles_legend = {'profileType': i.get("type", ""), "profileTypeAcronym": "ERGA",
                               "profileTypeColour": "#E61A8D"}
            i.update(additional_info_dict)

            # Check if legend data for this profile type already exists in the legend list
            if not any(x.get('profileType', "") == i.get("type", "") for x in profiles_legend_lst):
                i.update(profiles_legend)
            else:
                continue
        else:
            if not i.get("shared", ""):
                additional_info_dict = {"heading_bgColour": "#009c95", "title_smallText": "(Standalone)"}
                profiles_legend = {'profileType': "Standalone", "profileTypeAcronym": "Standalone",
                                   "profileTypeColour": "#009c95"}
                i.update(additional_info_dict)

                # Check if legend data for this profile type already exists in the legend list
                if not any(x.get('profileType', "") == "Standalone" for x in profiles_legend_lst):
                    i.update(profiles_legend)
                else:
                    continue
            else:
                additional_info_dict = {"heading_bgColour": "#f26202", "title_smallText": "(Shared With Me)"}
                profiles_legend = {'profileType': "Shared with Me", "profileTypeAcronym": "Shared With Me",
                                   "profileTypeColour": "#f26202"}
                i.update(additional_info_dict)

                # Check if legend data for this profile type already exists in the legend list
                if not any(x.get('profileType', "") == "Shared with Me" for x in profiles_legend_lst):
                    i.update(profiles_legend)
                else:
                    continue

        # Add profile type legend to a list
        profiles_legend_lst.append(profiles_legend)

        # Set associated type length/count, columnCount, width, acronym
        setup_associated_profile_types(i, i.get("associated_type", ""), additional_info_dict)

    if not request.is_ajax():
        # Set up the profile grids that are loaded by default when a user launches the web page
        context['profiles'] = profile_page
        context['profiles_total'] = profiles_length
        context['profiles_legend'] = profiles_legend_lst
        return render(request, 'copo/profile/copo_profile_index.html', context)
    else:
        # Set up the profile grids that are loaded when a user scrolls down the web page
        content = ''

        for profile in profile_page:
            # Set panel heading background colour and small text for each profile record
            if "DTOL_ENV" in profile.get("type", ""):
                additional_info_dict = {"heading_bgColour": "#fb7d0d", "title_smallText": "(DTOL-ENV)"}
                profiles_legend = {'profileType': profile.get("type", ""), "profileTypeAcronym": "DTOL-ENV",
                                   "profileTypeColour": "#fb7d0d"}
                profile.update(additional_info_dict)

                # Check if legend data for this profile type already exists in the legend list
                if not any(x.get('profileType', "") == profile.get("type", "") for x in profiles_legend_lst):
                    profile.update(profiles_legend)

            elif "DTOL" in profile.get("type", ""):
                additional_info_dict = {"heading_bgColour": "#16ab39", "title_smallText": "(DTOL)"}
                profiles_legend = {'profileType': profile.get("type", ""), "profileTypeAcronym": "DTOL",
                                   "profileTypeColour": "#16ab39"}
                profile.update(additional_info_dict)

                # Check if legend data for this profile type already exists in the legend list
                if not any(x.get('profileType', "") == profile.get("type", "") for x in profiles_legend_lst):
                    profile.update(profiles_legend)

            elif "ASG" in profile.get("type", ""):
                additional_info_dict = {"heading_bgColour": "#5829bb", "title_smallText": "(ASG)"}
                profiles_legend = {'profileType': profile.get("type", ""), "profileTypeAcronym": "ASG",
                                   "profileTypeColour": "#5829bb"}
                profile.update(additional_info_dict)

                # Check if legend data for this profile type already exists in the legend list
                if not any(x.get('profileType', "") == profile.get("type", "") for x in profiles_legend_lst):
                    profile.update(profiles_legend)

            elif "ERGA" in profile.get("type", ""):
                additional_info_dict = {"heading_bgColour": "#E61A8D", "title_smallText": "(ERGA)"}
                profiles_legend = {'profileType': profile.get("type", ""), "profileTypeAcronym": "ERGA",
                                   "profileTypeColour": "#E61A8D"}
                profile.update(additional_info_dict)

                # Check if legend data for this profile type already exists in the legend list
                if not any(x.get('profileType', "") == profile.get("type", "") for x in profiles_legend_lst):
                    profile.update(profiles_legend)
            else:
                if not profile.get("shared", ""):
                    additional_info_dict = {"heading_bgColour": "#009c95", "title_smallText": "(Standalone)"}
                    profiles_legend = {'profileType': "Standalone", "profileTypeAcronym": "Standalone",
                                       "profileTypeColour": "#009c95"}
                    profile.update(additional_info_dict)

                    # Check if legend data for this profile type already exists in the legend list
                    if not any(x.get('profileType', "") == "Standalone" for x in profiles_legend_lst):
                        profile.update(profiles_legend)
                else:
                    additional_info_dict = {"heading_bgColour": "#f26202", "title_smallText": "(Shared With Me)"}
                    profiles_legend = {'profileType': "Shared with Me", "profileTypeAcronym": "Shared With Me",
                                       "profileTypeColour": "#f26202"}
                    profile.update(additional_info_dict)

                    # Check if legend data for this profile type already exists in the legend list
                    if not any(x.get('profileType', "") == "Shared with Me" for x in profiles_legend_lst):
                        profile.update(profiles_legend)

            # Add profile type legend to a list
            profiles_legend_lst.append(profiles_legend)

            # Set associated type length/count, columnCount, width, acronym
            setup_associated_profile_types(profile, profile.get("associated_type", ""), additional_info_dict)

            content += render_to_string('copo/profile/copo_profile_record.html',
                                        {'profile': profile},
                                        request=request)

        return JsonResponse({
            "content": content,
            "end_pagination": True if page <= num_of_pages else False,
            "profiles_legend": profiles_legend_lst
        })


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

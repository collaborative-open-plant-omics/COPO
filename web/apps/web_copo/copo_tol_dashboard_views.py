from api.utils import finish_request
from api.views.general import *
from api.views.sample import filter_for_API
from bson import json_util, ObjectId
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from geopy.geocoders import Nominatim
from itertools import groupby
from operator import itemgetter
from web.apps.web_copo.models import ViewLock
from web.apps.web_copo.schema_versions.lookup.dtol_lookups import TOL_PROFILE_TYPES, DTOL_ENUMS, \
    PARTNER_MAP_LOCATION_COORDINATES, GAL_MAP_LOCATION_COORDINATES
from web.apps.web_copo.schemas.utils import data_utils
from web.apps.web_copo.utils import group_functions

import ast
import json
import re

LOGGER = settings.LOGGER
required_member_groups = ['dtol_users', 'dtol_sample_managers', 'dtolenv_users', 'dtolenv_sample_managers',
                          'erga_users', 'erga_sample_managers']


def convert_string_to_titlecase(txt):
    txt = txt.upper()  # Convert string word to uppercase

    # Convert titlecase prepositions to lowercase
    word_exceptions = ["OF", "AND", "FOR", "THE"]  # Prepositions/conjuctions should be lowercase
    temp1 = ' '.join(
        word.title() if index == 0 or not word.upper() in word_exceptions else word.lower()
        for index, word in
        enumerate(txt.split(' ')))

    # Convert sentencecase words to uppercase
    words_to_be_uppercase_lst = ['Dna', 'Ngs']
    temp2 = ' '.join(
        temp1.replace(item, item.upper()) if item in temp1 else temp1 for item in
        words_to_be_uppercase_lst if item in temp1)

    titlecase_word = ''.join(temp2 if any(x in temp1 for x in words_to_be_uppercase_lst) else temp1)

    # Get (one occurence of) string within regular brackets if it exists
    # (given that there should be no nested parenthesis)
    is_parenthesis_in_word = re.search(r'\((.*?)\)', titlecase_word)
    word_within_parenthesis = is_parenthesis_in_word.group(1) if is_parenthesis_in_word else ""
    result = titlecase_word.replace(word_within_parenthesis, word_within_parenthesis.upper())

    return result if word_within_parenthesis else titlecase_word


def copo_tol_dashboard(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()

    # Stand-alone users/annoymous users can only view certain aspects of the tol dashboard
    if any(item in member_groups for item in required_member_groups):
        context = {'group_status': False}
    else:
        context = {'group_status': True}

    return render(request, 'copo/tol_dashboard/copo_tol_dashboard.html', context)


@login_required
def copo_tol_inspect(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()

    if any(item in member_groups for item in required_member_groups):
        return render(request, 'copo/tol_dashboard/copo_tol_inspect.html', {})
    else:
        return goto_unauthorised_page(request)


@login_required
def copo_tol_inspect_gal(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()

    if any(item in member_groups for item in required_member_groups):
        return render(request, 'copo/tol_dashboard/copo_tol_inspect_gal.html', {})
    else:
        return goto_unauthorised_page(request)


def gal_and_partners(request):
    # Field name: "PARTNER"
    partner_enums = DTOL_ENUMS["PARTNER"]
    partner_map_marker_colour = "#F8E23B"
    partner_lst = [convert_string_to_titlecase(item) for item in partner_enums]

    # Get PARTNER co-ordinates locations and other details
    partner_locations_lst = []

    for key, value in PARTNER_MAP_LOCATION_COORDINATES.items():
        if key in partner_enums:
            partner_coordinates = PARTNER_MAP_LOCATION_COORDINATES.get(key, "")
            name = convert_string_to_titlecase(key)
            location_details = get_location_details(partner_coordinates["latitude"], partner_coordinates["longitude"])
            samples_count = get_number_of_samples_produced("PARTNER", key)
            style = {"r": 5, "fill": partner_map_marker_colour}

            # {**x, **y} # merges dictionary x and dictionary y
            partner_locations_lst.append(
                {**{"name": name}, **partner_coordinates, **location_details, **{"samples_count": samples_count},
                 **{"style": style}})

    # partner_locations_lst = [
    #     {**{"name": convert_string_to_titlecase(key)}, **PARTNER_MAP_LOCATION_COORDINATES.get(key, ""),
    #      **get_location_details(PARTNER_MAP_LOCATION_COORDINATES.get(key, "")["latitude"],
    #                             PARTNER_MAP_LOCATION_COORDINATES.get(key, "")["longitude"]),
    #      **{"samples_count": get_number_of_samples_produced("PARTNER", key)},
    #      **{"style": {"r": 5, "fill": partner_map_marker_colour}}} for
    #     key, value in PARTNER_MAP_LOCATION_COORDINATES.items() if key in partner_enums]

    # Field name: "GAL"
    gal_map_marker_colour = "#3B7DDD"

    # Get list of GAL names based on manifest type and once GAL name begins with an uppercase letter
    gal_lst = [(convert_string_to_titlecase(item), manifest_type) for manifest_type, gal in
               DTOL_ENUMS["GAL"].items() for item in gal if item[0].isupper()]

    gal_lst_sorted = sorted(gal_lst, key=itemgetter(0))  # Sort before grouping list
    gal_lst_grouped = groupby(gal_lst_sorted, key=itemgetter(0))  # Group list by GAL name
    gal_lst = {k: list(map(itemgetter(1), v)) for k, v in gal_lst_grouped}

    # Get GAL co-ordinates locations and other details
    gal_lst_uppercase = [x.upper() for x in list(gal_lst.keys())]  # Convert GAL names to uppercase
    gal_locations_lst = []

    for key, value in GAL_MAP_LOCATION_COORDINATES.items():
        if key.upper() in gal_lst_uppercase:
            gal_coordinates = GAL_MAP_LOCATION_COORDINATES.get(key, "")
            name = convert_string_to_titlecase(key)
            location_details = get_location_details(gal_coordinates["latitude"], gal_coordinates["longitude"])
            samples_count = get_number_of_samples_produced("GAL", key)
            style = {"r": 5, "fill": gal_map_marker_colour}

            # {**x, **y} # merges dictionary x and dictionary y
            gal_locations_lst.append(
                {**{"name": name}, **gal_coordinates, **location_details, **{"samples_count": samples_count},
                 **{"style": style}})

    # gal_locations_lst = [
    #     {**{"name": convert_string_to_titlecase(key)}, **GAL_MAP_LOCATION_COORDINATES.get(key, ""),
    #      **get_location_details(GAL_MAP_LOCATION_COORDINATES.get(key, "")["latitude"],
    #                             GAL_MAP_LOCATION_COORDINATES.get(key, "")["longitude"]),
    #      **{"samples_count": get_number_of_samples_produced("GAL", key)},
    #      **{"style": {"r": 5, "fill": gal_map_marker_colour}}} for
    #     key, value in GAL_MAP_LOCATION_COORDINATES.items() if
    #     key.upper() in gal_lst_uppercase]

    out = {'gal_lst': gal_lst, 'gal_locations_lst': gal_locations_lst, 'partner_lst': partner_lst,
           'partner_locations_lst': partner_locations_lst}

    return HttpResponse(json.dumps(out))


def get_gal_names(request):
    projects = TOL_PROFILE_TYPES
    samples = Sample().get_gal_names(projects)
    # Get 'GAL' field value, if it is not empty
    gal_names = [sample.get('GAL') for sample in samples if sample.get('GAL')]
    gal_names = set(gal_names)  # Get unique values for the 'GAL' field name
    return HttpResponse(json_util.dumps(gal_names))


def get_location_details(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(str(latitude) + "," + str(longitude))
    address = location.raw['address']
    out = {"city": address.get("city", ""), "state": address.get("state", ""), "country": address.get("country", "")}
    return out


def get_number_of_samples_produced(field_name, field_value):
    return Sample().get_collection_handle().count({field_name: field_value})


def get_profile_titles_nav_tabs(request):
    queryUserProfileRecords = request.GET["queryUserProfileRecords"]
    regex = r'\((.*?)\)'  # value within enclosed parentheses regex

    if queryUserProfileRecords:
        owner_id = data_utils.get_user_id()
        profiles = Profile().get_all_profiles(user=owner_id)
    else:
        profiles = Profile().get_all_profiles()

    profile_types = [i.get("type", "") for i in profiles if i.get("type", "") != "Stand-alone"]  # Get tol profile types

    #  Extract value within enclosed parentheses from a unique set of profile types
    #  If the value exists, return it else, return the profile type
    profile_types = [re.search(regex, i).group(1) if re.search(regex, i) else i for i in set(profile_types)]
    profile_types.sort()  # Sort profile types in ascending order

    return HttpResponse(json_util.dumps(profile_types))


def get_profiles_for_tol_inspection(request):
    data = request.POST["data"]  # "project" or "samples_data"
    searchByFaceting = request.POST["searchByFaceting"]
    getProjectTitlesForUserOnly = request.POST["getProjectTitlesForUserOnly"]

    if searchByFaceting == "true":
        # Get profiles by project type with search faceting
        match_dict = ast.literal_eval(data)  # Convert string to dictionary
        samples = Sample().get_dtol_by_aggregation(match_dict)
        projects = list(set([sample.get("tol_project", "") for sample in samples]))  # Get unique project types
        projects.sort()  # Sort list in ascending order
        manifest_ids = [sample.get("manifest_id", "") for sample in samples if
                        sample.get("tol_project", "") == projects[0]]
        profile_samples_count = [len(manifest_ids)]
        manifest_ids = list(set(manifest_ids))  # Get unique manifest IDs
        profiles = Profile().get_profiles_based_on_sample_data(projects, manifest_ids)

        out = {'profiles': profiles, 'profile_samples_count': profile_samples_count, 'projects': projects}

    else:
        # Get profiles by project type without search faceting
        profiles = Profile().get_profiles_by_aggregation(data, currentUser=getProjectTitlesForUserOnly)
        samples = [Sample().get_dtol_from_profile_id_and_project(str(profile["_id"]), data) for profile in profiles]
        profile_samples_count = [len(sample) for sample in samples]

        out = {'profiles': profiles, 'profile_samples_count': profile_samples_count}

    return HttpResponse(json_util.dumps(out))


def get_profiles_based_on_sample_data(request):
    samples_data = request.POST["samples_data"]
    samples_data = json.loads(samples_data)  # Convert string array to a list of dictionaries

    projects = [x.get("project", "") for x in samples_data]
    manifest_ids = [x.get("sample_manifest_IDs", "")[0] for x in samples_data]
    profile_samples_count = [x.get("profile_samples_count", "") for x in samples_data]  # Number of samples per profile

    profiles = Profile().get_profiles_based_on_sample_data(projects, manifest_ids)

    return HttpResponse(
        json_util.dumps({'profiles': profiles, 'profile_samples_count': profile_samples_count}))


def get_sample_details(request):
    sample_id = ObjectId(request.POST["sample_id"])
    sample_data = Sample().get_sample_by_id(sample_id)
    excluded_fields = ["profile_id", "biosample_id", "_id"]  # Filter dictionary field keys with dict comprehension
    sample_data_with_blank_field_values = {field: value for (field, value) in sample_data[0].items() if
                                           field not in excluded_fields}

    # Change "public_name" field name to "tolid" field name
    sample_data_with_blank_field_values["tolid"] = sample_data_with_blank_field_values.pop("public_name")

    sorted_sample_data_with_blank_field_values = dict(sorted(sample_data_with_blank_field_values.items()))

    return HttpResponse(json_util.dumps(sorted_sample_data_with_blank_field_values))


def get_samples_by_search_faceting(request):
    url = request.build_absolute_uri()

    if not ViewLock().isViewLockedCreate(url=url):
        match_dict = request.POST["match_items"]
        match_dict = ast.literal_eval(match_dict)  # Convert string to dictionary
        samples = Sample().get_dtol_by_aggregation(match_dict)

        return HttpResponse(json_util.dumps(samples))
    else:
        return HttpResponse(json_util.dumps({"locked": True}))


@login_required
def goto_unauthorised_page(request, message="Apologies, you do not have permission to view this web page"):
    try:
        LOGGER.log(message)
    finally:
        context = {'message': message}
        return render(request, 'copo/unauthorised_page.html', context)

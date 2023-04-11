from api.views.general import *
from bson import json_util, ObjectId
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from geopy.geocoders import Nominatim
from web.apps.web_copo.models import ViewLock
from web.apps.web_copo.schemas.utils import data_utils
from web.apps.web_copo.utils import group_functions

import itertools
import operator
import re

LOGGER = settings.LOGGER


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


@login_required
def copo_dashboard(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()
    required_member_groups = ['dtol_users', 'dtol_sample_managers', 'erga_users', 'erga_sample_managers']

    if any(item in member_groups for item in required_member_groups):
        return render(request, 'copo/dashboard/copo_dashboard.html', {})
    else:
        return goto_unauthorised_page()


@login_required
def copo_tol_inspect(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()
    required_member_groups = ['dtol_users', 'dtol_sample_managers', 'erga_users', 'erga_sample_managers']

    if any(item in member_groups for item in required_member_groups):
        return render(request, 'copo/dashboard/copo_tol_inspect.html', {})
    else:
        return goto_unauthorised_page()


@login_required
def copo_tol_inspect_gal(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()
    required_member_groups = ['dtol_users', 'dtol_sample_managers', 'erga_users', 'erga_sample_managers']

    if any(item in member_groups for item in required_member_groups):
        return render(request, 'copo/dashboard/copo_tol_inspect_gal.html', {})
    else:
        return goto_unauthorised_page()


def gal_and_partners(request):
    # {**x, **y} # merges dictionary x and dictionary y
    # Field name: "PARTNER"
    partner_map_marker_colour = "#F8E23B"
    partner_lst = [convert_string_to_titlecase(item) for item in lkup.DTOL_ENUMS["PARTNER"]]
    # partner_location_information = [get_location_details(lkup.PARTNER_MAP_LOCATION_COORDINATES.get(key, "")["latitude"],
    #                                                      lkup.PARTNER_MAP_LOCATION_COORDINATES.get(key, "")[
    #                                                          "longitude"]) for
    #                                 key, value in lkup.PARTNER_MAP_LOCATION_COORDINATES.items() if
    #                                key in lkup.DTOL_ENUMS["PARTNER"]]
    partner_locations_lst = [
        {**{"name": convert_string_to_titlecase(key)}, **lkup.PARTNER_MAP_LOCATION_COORDINATES.get(key, ""),
         **get_location_details(lkup.PARTNER_MAP_LOCATION_COORDINATES.get(key, "")["latitude"],
                                lkup.PARTNER_MAP_LOCATION_COORDINATES.get(key, "")["longitude"]),
         **{"samples_count": get_number_of_samples_produced("PARTNER", key)},
         **{"style": {"r": 5, "fill": partner_map_marker_colour}}} for
        key, value in lkup.PARTNER_MAP_LOCATION_COORDINATES.items() if key in lkup.DTOL_ENUMS["PARTNER"]]

    # Field name: "GAL"
    gal_map_marker_colour = "#3B7DDD"
    # Get list of GAL names based on manifest type and once GAL name begins with an uppercase letter
    gal_lst = [(convert_string_to_titlecase(item), manifest_type) for manifest_type, gal in
               lkup.DTOL_ENUMS["GAL"].items() for item in gal if item[0].isupper()]

    gal_lst_sorted = sorted(gal_lst, key=operator.itemgetter(0))  # Sort before grouping list
    gal_lst_grouped = itertools.groupby(gal_lst_sorted, key=operator.itemgetter(0))  # Group list by GAL name
    gal_lst = {k: list(map(operator.itemgetter(1), v)) for k, v in gal_lst_grouped}

    gal_lst_uppercase = [x.upper() for x in list(gal_lst.keys())]  # Convert GAL names to uppercase
    gal_locations_lst = [
        {**{"name": convert_string_to_titlecase(key)}, **lkup.GAL_MAP_LOCATION_COORDINATES.get(key, ""),
         **get_location_details(lkup.GAL_MAP_LOCATION_COORDINATES.get(key, "")["latitude"],
                                lkup.GAL_MAP_LOCATION_COORDINATES.get(key, "")["longitude"]),
         **{"samples_count": get_number_of_samples_produced("GAL", key)},
         **{"style": {"r": 5, "fill": gal_map_marker_colour}}} for
        key, value in lkup.GAL_MAP_LOCATION_COORDINATES.items() if
        key.upper() in gal_lst_uppercase]

    out = {'gal_lst': gal_lst, 'gal_locations_lst': gal_locations_lst, 'partner_lst': partner_lst,
           'partner_locations_lst': partner_locations_lst}

    return HttpResponse(json.dumps(out))  # partner_locations_lst  # HttpResponse(json.dumps(out))


def get_gal_names(request):
    projects = lkup.TOL_PROFILE_TYPES
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
    print('Is query in user profile checked: ', queryUserProfileRecords)
    if queryUserProfileRecords:
        owner_id = data_utils.get_user_id()
        all_profiles = Profile().get_all_profiles(user=owner_id)
        print('All user profiles: ', all_profiles)
        #   profile_types = [Profile().get_type(str(profile["_id"])) for profile in allUserProfiles]
        #   profile_types = set(profile_types)  # Remove duplicates
        #   profile_types = list(map(str.lower, profile_types)) # Convert each string to lowercase
        # profile_types_abbreviations = [i.upper()  for i in lkup.TOL_PROFILE_TYPES for j in profile_types if i in j]
    else:
        all_profiles = Profile().get_all_profiles()
        print('All COPO profiles: ', all_profiles)

    profile_types = [all_profiles[x]['type'] for x in range(len(all_profiles))]
    profile_types = set(profile_types)  # Remove duplicates
    # profile_types = list(map(str.lower, profile_types))  # Convert each string to lowercase

    profile_types_abbreviations = [i.upper() for i in lkup.TOL_PROFILE_TYPES if
                                   i.upper() in profile_types and re.search(r'\((.*?)\)', i).group(1)]

    print('Profile types: ', profile_types_abbreviations)
    # lkup.TOL_PROFILE_TYPES
    #
    # if project == "ERGA":
    #     ergprofiles = Profile().get_erga_profiles_based_on_user_id()
    # elif project == "DTOL":
    #     profiles = Profile().get_dtol_only_profiles_based_on_user_id()
    # elif project == "ASG":
    #     profiles = Profile().get_asg_profiles_based_on_user_id()
    # else:
    #     profiles = Profile().get_dtolenv_profiles_based_on_user_id()
    #
    # samples = [Sample().get_dtol_from_profile_id_and_project(str(profile["_id"]), project) for profile
    #            in profiles]

    return HttpResponse(json_util.dumps(profile_types_abbreviations))


def get_profiles_based_on_project(request):
    project = request.GET["project"]

    if project == "ERGA":
        profiles = Profile().get_erga_profiles_based_on_user_id()
    elif project == "DTOL":
        profiles = Profile().get_dtol_only_profiles_based_on_user_id()
    elif project == "ASG":
        profiles = Profile().get_asg_profiles_based_on_user_id()
    else:
        profiles = Profile().get_dtolenv_profiles_based_on_user_id()

    samples = [Sample().get_dtol_from_profile_id_and_project(str(profile["_id"]), project) for profile
               in profiles]

    return HttpResponse(
        json_util.dumps({'profiles': profiles, 'profile_samples_count': len(samples[0])}))


def get_profiles_based_on_project_by_aggregation(request):
    project = request.GET["project"]

    if project == "ERGA":
        profiles = Profile().get_erga_profiles()
    elif project == "DTOL":
        profiles = Profile().get_dtol_only_profiles()
    elif project == "ASG":
        profiles = Profile().get_asg_profiles()
    else:
        profiles = Profile().get_dtolenv_profiles()

    samples = [Sample().get_dtol_from_profile_id_and_project(str(profile["_id"]), project) for profile
               in profiles]

    return HttpResponse(
        json_util.dumps({'profiles': profiles, 'profile_samples_count': len(samples[0])}))


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
        match_dict = request.GET["match_items"]
        samples = Sample().get_dtol_by_aggregation(match_dict)

        return HttpResponse(json_util.dumps(samples))
    else:
        return HttpResponse(json_util.dumps({"locked": True}))


def get_samples_for_project_and_profileID(request):
    url = request.build_absolute_uri()
    if not ViewLock().isViewLockedCreate(url=url):
        profile_id = request.GET["profile_id"]
        project = request.GET["project"]
        samples = Sample().get_dtol_from_profile_id_and_project(profile_id, project)

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

from api.views.general import *
from bson import json_util
from dal import cursor_to_list
from dal.copo_da import Profile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from web.apps.web_copo.schema_versions.lookup.dtol_lookups import TOL_PROFILE_TYPES, STANDALONE_ACCESSION_TYPES
from web.apps.web_copo.utils import group_functions

LOGGER = settings.LOGGER
required_member_groups = ['dtol_users', 'dtol_sample_managers', 'dtolenv_users', 'dtolenv_sample_managers',
                          'erga_users', 'erga_sample_managers']


@login_required
def copo_accessions(request, profile_id):
    # The input parameter, 'profile_id' is actually 'sample_id'
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


def copo_accessions_dashboard(request):
    # Determine if users are in the appropriate membership group to view the web page
    member_groups = group_functions.get_group_membership_asString()
    groups = group_functions.get_group_membership_asString()

    return render(request, 'copo/accessions/copo_accessions_dashboard.html',
                  {'groups': groups, 'profile_id': '999'})


def get_filter_accession_titles(request):
    # Get the text and value for the filter accession checkboxes
    accession_titles = list()
    isSampleProfileTypeStandalone = convertStringToBoolean(request.POST.get("isSampleProfileTypeStandalone", str()))

    if isSampleProfileTypeStandalone:
        # Stand-alone projects
        accession_types = [{item: item.title().replace('_', ' ').replace("Seq ", "Sequence ")} for item in
                           STANDALONE_ACCESSION_TYPES]
        accession_titles = accession_types
    else:
        # Other project types
        profile_types = list()

        for i in TOL_PROFILE_TYPES:
            profile_type = Profile().get_collection_handle().find_one({"type": {"$regex": i.upper(), "$options": "i"}},
                                                                      {"_id": 0, "type": 1})
            if profile_type:
                profile_types.append({i.upper(): profile_type.get("type", "")})

        accession_titles = profile_types

    return HttpResponse(json_util.dumps(accession_titles))


def goto_unauthorised_page(request, message="Apologies, you do not have permission to view this web page"):
    try:
        LOGGER.log(message)
    finally:
        context = {'message': message}
        return render(request, 'copo/unauthorised_page.html', context)


def convertStringToBoolean(string):
    # Convert string boolean to boolean
    return str(string).lower() in ("yes", "true", "t", "1")

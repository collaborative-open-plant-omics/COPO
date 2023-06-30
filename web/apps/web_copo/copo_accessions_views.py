from api.views.general import *
from bson import json_util
from dal.copo_da import Profile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
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

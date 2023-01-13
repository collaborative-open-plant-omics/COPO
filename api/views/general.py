__author__ = 'felix.shaw@tgac.ac.uk - 14/05/15'

import importlib
import itertools
import json
import jsonpickle
import operator
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

import web.apps.web_copo.repos.figshare as f
from api.doi_metadata import DOI2Metadata
from dal.copo_base_da import Collection_Head
from dal.copo_da import Profile, Sample, DataFile
from dal.ena_da import EnaCollection
from geopy.geocoders import Nominatim
from web.apps.web_copo.schemas.utils.data_formats import DataFormats
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

schema_version_path_dtol_lookups = f'web.apps.web_copo.schema_versions.{settings.CURRENT_SCHEMA_VERSION}.lookup.dtol_lookups'
lkup = importlib.import_module(schema_version_path_dtol_lookups)


def forward_to_swagger(request):
    response = redirect('/static/swagger/apidocs_index.html')

    return response


def upload_to_figshare_profile(request):
    if request.method == 'POST':
        user = request.user
        file = request.FILES['file']
        repo_type = request.POST['repo']
        out = f.FigshareCollection.receive_data_file(file, repo_type, user)
        return HttpResponse(out, content_type='json')


def submit_to_figshare(request, article_id):
    # check status of figshare collection
    if FigshareCollection().is_clean(article_id):
        # there are no changes to the collection so don't submit
        data = {'success': False}
        return HttpResponse(jsonpickle.encode(data))
    else:
        # get collection_details
        details = FigshareCollection().get_collection_details_from_collection_head(article_id)
        for d in details['collection_details']:
            figshare_article_id = f.submit_to_figshare(d)
            if (figshare_article_id is not None):
                # figshare_article_id is the Figshare article id
                FigshareCollection().mark_as_clean(article_id)
                data = {'success': True}
        return HttpResponse(jsonpickle.encode(data))


def view_in_figshare(request, article_id):
    url = FigshareCollection().get_url(article_id)
    return HttpResponse(jsonpickle.encode(url))


def delete_from_figshare(request, article_id):
    if (f.delete_from_figshare(article_id)):
        collection_id = request.session["collection_head_id"]
        FigshareCollection().delete_article(article_id, collection_id)

        data = {'success': True}
    else:
        data = {'success': False}
    return HttpResponse(jsonpickle.encode(data))


def check_orcid_credentials(request):
    # TODO - here we check if the orcid tokens are valid
    out = {'exists': False, 'authorise_url': settings['REPOSITORIES']['ORCID']['urls']['authorise_url']}
    return HttpResponse(jsonpickle.encode(out))


# call only if you want to generate a new template
def generate_ena_template(request):
    temp_dict = DataFormats("ENA").generate_ui_template()
    return HttpResponse(jsonpickle.encode(temp_dict))


def doi2publication_metadata(request, id_handle):
    if id_handle:
        out_dict = DOI2Metadata(id_handle).publication_metadata()
    else:
        message = "DOI missing"
        out_dict = {"status": "failed", "messages": message, "data": {}}
    return HttpResponse(jsonpickle.encode(out_dict))


def get_collection_type(request):
    collection_id = request.GET['collection_id']
    c = Collection_Head().GET(collection_id)
    return HttpResponse(c['type'])


def convert_to_sra(request):
    from converters import exporter
    collection_id = request.POST['collection_id']
    if exporter().do_validate(collection_id):
        exporter().do_export(collection_id, settings['EXPORT_LOCATIONS']['ENA']['export_path'])
    return HttpResponse('here')

    return HttpResponse(json.dumps(out_dict, ensure_ascii=False))


def refactor_collection_schema(request):
    collection_head_id = request.POST['collection_head_id']
    collection_type = request.POST['collection_type']

    collection_head = Collection_Head().GET(collection_head_id)
    status = ""

    if collection_type.lower() == "ena submission":
        ena_collection_id = str(collection_head['collection_details'][0])
        status = EnaCollection().refactor_ena_schema(ena_collection_id)

    out_dict = {"status": status}
    return HttpResponse(jsonpickle.encode(out_dict), content_type='json')


def numbers(request):
    profiles = number_of_profiles()
    samples = number_of_samples()
    users = number_of_users()
    datafiles = number_of_datafiles()
    out = {"profiles": profiles, "samples": samples, "users": users, "datafiles": datafiles}
    return HttpResponse(json.dumps(out))


def number_of_profiles():
    return Profile().get_number()


def number_of_samples():
    # get total number of sample records in COPO instance
    return Sample().get_number()


def number_of_users():
    return User.objects.all().count()


def number_of_datafiles():
    return DataFile().get_number()


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


def get_location_details(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(str(latitude) + "," + str(longitude))
    address = location.raw['address']
    out = {"city": address.get("city", ""), "state": address.get("state", ""), "country": address.get("country", "")}
    return out


def get_number_of_samples_produced(field_name, field_value):
    return Sample().get_collection_handle().count({field_name: field_value})


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': "Token " + token.key,
            'user_id': user.pk,
            'email': user.email
        })


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

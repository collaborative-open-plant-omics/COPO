__author__ = 'felix.shaw@tgac.ac.uk - 14/05/15'

import json

import jsonpickle
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

import web.apps.web_copo.repos.figshare as f
from api.doi_metadata import DOI2Metadata
from dal.copo_base_da import Collection_Head
from dal.copo_da import Profile, Sample, DataFile
from dal.ena_da import EnaCollection
from web.apps.web_copo.schemas.utils.data_formats import DataFormats
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


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

__author__ = 'felix.shaw@tgac.ac.uk - 20/01/2016'
import sys

from bson.errors import InvalidId

from api.utils import get_return_template, extract_to_template, finish_request
from dal.copo_da import Person
from web.apps.web_copo.lookup.lookup import API_ERRORS


def get(request, id):
    """
    Method to handle a request for a single person object from the API
    :param request: Django HttpRequest Object
    :param id: the ID of the Person object to get (can be string or ObjectID)
    :return: an HttpResponse object embedded with the completed return template for Person
    """

    # get person object
    try:
        p = Person().GET(id)
    except TypeError as e:
        print(e)
        return finish_request(error=API_ERRORS['NOT_FOUND'])
    except InvalidId as e:
        print(e)
        return finish_request(error=API_ERRORS['INVALID_PARAMETER'])
    except:
        return finish_request(error="Unexpected error:" + sys.exc_info()[0])


    #get return template
    t = get_return_template('PERSON')

    out_list = []

    out_list.append(extract_to_template(object=p, template=t))

    return finish_request(out_list)


def get_all(request):
    """
    Method to handle a request for all Person objects
    :param request: Django HttpRequest Object
    :return: an HttpResponse object embedded with the completed return template for all People
    """
    # get all people
    try:
        people_list = Person().get_all()
    except TypeError as e:
        print(e)
        return finish_request(error=API_ERRORS['NOT_FOUND'])
    except InvalidId as e:
        print(e)
        return finish_request(error=API_ERRORS['INVALID_PARAMETER'])
    except:
        return finish_request(error="Unexpected error:" + sys.exc_info()[0])


    # get return template
    t = get_return_template('PERSON')

    out_list = []

    for p in people_list:
        out_list.append(extract_to_template(object=p, template=t))


    return finish_request(out_list)

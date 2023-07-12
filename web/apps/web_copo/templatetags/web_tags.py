__author__ = 'fshaw'
from django import template
from django.contrib.auth.models import Group
from django.conf import settings

register = template.Library()
from dal.copo_da import DataFile
import re

@register.filter("mongo_id")
def mongo_id(value):
    # return the $oid field of _id (which is a dict)
    try:
        return str(value['_id']['$oid'])
    except:
        return str(value['_id'])


@register.filter("datafile_title")
def datafile_title(value):
    d = DataFile().get_record(value)
    cu = DataFile().get_relational_record_for_id(d['file_id'])
    return cu.filename


@register.filter("make_repo_name")
def make_repo_name(value):
    str = ''
    if value == "ena":
        str += "ENA"
    else:
        str += value.capitalize()
    return str + ' ' + 'Submission'


@register.filter("make_file_count")
def make_file_count(value):
    num = len(value.get('bundle', 0))
    if num > 1:
        return str(num) + ' ' + 'file'
    else:
        return str(num) + ' ' + 'files'


@register.filter("produce_submission_header")
def produce_submission_header(value):
    str = ''
    str += make_repo_name(value.get('repository', 'Default'))
    str += ' - '
    str += make_file_count(value)

    return str


@register.filter("has_group")
def check_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()

@register.filter(is_safe=True, name="get_blank_manifest_url")
def get_blank_manifest_url(value):
    manfiest_version = settings.MANIFEST_VERSION
    version = manfiest_version.get(value, "")
    version = "_v" + version if version else ""
    return settings.MANIFEST_DOWNLOAD_URL.format(value, version)

@register.filter(is_safe=True, name="get_short_profile_type")
def get_short_profile_type(value):
    result = re.search(r"\((.*?)\)", value)
    return result.group(1) if result else value

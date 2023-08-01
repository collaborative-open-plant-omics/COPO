__author__ = 'felixshaw'

import pymongo
from bson import ObjectId

from django.conf import settings


def get_collection_ref(collection_name):
    return settings.MONGO_CLIENT[collection_name]


def get_mongo_client():
    MONGO_CLIENT = pymongo.MongoClient(host=settings.MONGO_HOST, maxPoolSize=settings.MONGO_MAX_POOL_SIZE, )[
        settings.MONGO_DB]
    MONGO_CLIENT.authenticate(settings.MONGO_USER, settings.MONGO_USER_PASSWORD, source='admin')
    return MONGO_CLIENT


def to_mongo_id(id):
    return ObjectId(id)


# web templates take a list or dictionary object as their context, so mongodb cursor objects
# need to be converted before being used in templates
def to_django_context(cursor):
    records = []
    for r in cursor:
        records.append(r.to_json_type())
    return records


def cursor_to_list(cursor):
    records = []
    for r in cursor:
        records.append(r)
    return records


def cursor_to_list_no_ids(cursor):
    '''
    return list with ids remove e.g.
    [
        {
            "_id": "0233b5ba-9133-4e54-856e-089194ec6b26"
        },
        {
            "_id": "bbed622a-3771-41f5-b8b8-217ff3bd9b5e"
        }
    ]
    becomes
    [
        "0233b5ba-9133-4e54-856e-089194ec6b26",
        "bbed622a-3771-41f5-b8b8-217ff3bd9b5e"
    ]
    '''
    records = []
    for r in cursor:
        records.append(r["_id"])
    return records


def cursor_to_list_str(cursor, use_underscore_in_id=True):
    # method to return pymongo cursor into standard python list
    # with ids as strings rather than ObjectIds
    records = cursor_to_list(cursor)
    for r in records:
        if use_underscore_in_id:
            r["_id"] = str(r["_id"])
        else:
            r["id"] = str(r["_id"])
            r.pop("_id")
    return records


def cursor_to_list_str2(cursor, use_underscore_in_id=True):
    # method to return pymongo cursor into standard python list
    # with IDs as strings instead than ObjectIds
    # and datetimes as string datetime instead of datetime objects
    records = cursor_to_list(cursor)
    for r in records:
        if use_underscore_in_id:
            r["_id"] = str(r["_id"])
        else:
            r["id"] = str(r["_id"])
            r.pop("_id")

        r["date_created"] = r['date_created'].strftime('%a, %d %b %Y %H:%M')
        r["date_modified"] = r['date_modified'].strftime('%a, %d %b %Y %H:%M')

        if r.get('study_status',''):
            r['study_release_date'] = r['study_release_date'].strftime('%a, %d %b %Y %H:%M')
    return records


def verify_doc_type(doc):
    data = []
    if isinstance(doc, dict):
        if doc["result"]:
            return doc["result"][0]["data"]
    elif isinstance(doc, pymongo.command_cursor.CommandCursor):
        data = list(doc)
        if data:
            return data[0]["data"]
    return data


def change_mongo_id_format_to_standard(cursor):
    # changes ids of records in a cursor to be 'id' instead of '_id'
    l = cursor_to_list(cursor)
    for r in l:
        r['id'] = r.pop('_id')
    return l


def convert_text(data):
    # change text to shortform :=: iri
    l = list()
    for r in data:
        if 'annotation_value' in r:
            r['text'] = r['annotation_value'] + ' :-: ' + r['term_accession']
        l.append(r)
    return l

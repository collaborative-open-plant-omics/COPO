__author__ = 'etuka'

import copy
import json
import os
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import datetime, tzinfo, timedelta

import jsonref
import pandas as pd
from bson.json_util import dumps
from django.conf import settings
from django.contrib.auth.models import User
from django_tools.middlewares import ThreadLocal

import web.apps.web_copo.lookup.lookup as lookup
from web.apps.web_copo.lookup.resolver import RESOLVER


class simple_utc(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


def pretty_print(data, path=None):
    if path is None:
        print(dumps(data, sort_keys=True,
                    indent=4, separators=(',', ': ')))
    else:
        s = dumps(data, sort_keys=True,
                  indent=4, separators=(',', ': '))
        with open(path, 'w+') as file:
            file.write(s)


# converts a dictionary to object
def json_to_object(data_object):
    data = ""
    if isinstance(data_object, dict):
        data = json.loads(json.dumps(data_object), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    return data


def get_label(value, list_of_elements, key_name):
    for dict in list_of_elements:
        return dict["label"] if dict[key_name] == value else ''


def lookup_study_type_label(val):
    # get study types
    lbl = str()
    study_types = lookup.DROP_DOWNS['STUDY_TYPES']

    for st in study_types:
        if st["value"].lower() == val.lower():
            lbl = st["label"]
            break

    return lbl


def get_copo_exception(key):
    messages = json_to_pytype(lookup.MESSAGES_LKUPS["exception_messages"])["properties"]

    return messages.get(key, str())


def log_copo_exception(message):
    pass


def get_db_template(schema):
    f_path = lookup.DB_TEMPLATES[schema]
    data = ""
    with open(f_path, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
    return data


def get_sample_attributes():
    sample_attributes = json_to_pytype(lookup.X_FILES["SAMPLE_ATTRIBUTES"])
    # maybe some logic here to filter the returned attributes,
    # for instance, based on the tags?
    return sample_attributes


def get_isajson_refactor_type(key):
    out_dict = {}
    if key in json_to_pytype(lookup.X_FILES["ISA_JSON_REFACTOR_TYPES"]):
        out_dict = json_to_pytype(lookup.X_FILES["ISA_JSON_REFACTOR_TYPES"])[key]
    return out_dict


def json_to_pytype(path_to_json, compatibility_mode=True):
    # use compatability mode if jsonref is causing problems
    with open(path_to_json, encoding='utf-8') as data_file:
        f = data_file.read()
        if compatibility_mode:
            data = json.loads(f)
        else:
            data = jsonref.loads(f)
        if "properties" in data and isinstance(data["properties"], list):
            cp = list(data["properties"])
            idxes = list()
            # expand references
            tmp = list()
            for idx, el in enumerate(data["properties"]):
                if type(el) == jsonref.JsonRef:
                    tmp = tmp + data["properties"][idx]
                else:
                    tmp.append(el)
                    # data["properties"] = data["properties"] + data["properties"][idx]
            data["properties"] = tmp

    return data


def get_samples_options():
    from dal.copo_da import Sample
    profile_id = get_current_request().session['profile_id']
    samples = Sample(profile_id).get_all_records()

    option_values = []
    for sd in samples:
        label = sd["name"]
        option_values.append({"value": str(sd["_id"]), "label": label})

    return option_values


def get_figshare_category_options():
    # r = requests.get('https://api.figshare.com/v2/categories')
    # l = json.loads(r.text)
    # output = list()
    #
    # for x in l:
    #     st = dict()
    #     st['value'] = x['id']
    #     st['label'] = x['title']
    #     output.append(st)
    # todo: resolved locally to mitigate network congestion - feel free to uncomment to return to remote resolution

    drop_downs_pth = RESOLVER['copo_drop_downs']

    df = pd.DataFrame(
        json_to_pytype(os.path.join(drop_downs_pth, 'figshare_categories.json')).get("properties", list()))
    df["label"] = df["title"]
    df['value'] = df['id']

    df = df[['value', 'label']]
    result = df.to_dict('records')

    return result


def get_repo_type_options():
    return lookup.DROP_DOWNS['REPO_TYPE_OPTIONS']


def get_dataverse_subject_dropdown():
    return lookup.DROP_DOWNS['DATAVERSE_SUBJECTS']


def get_figshare_article_options():
    return lookup.DROP_DOWNS['FIGSHARE_ARTICLE_TYPES']


def get_figshare_license_options():
    return lookup.DROP_DOWNS['LICENSE_TYPES']


def get_figshare_publish_options():
    return lookup.DROP_DOWNS['YES_NO']


def get_existing_study_options():
    from dal.copo_da import Submission
    subs = Submission().get_complete()
    out = list()
    out.append({
        "value": "required",
        "label": "-- select one --"
    })
    out.append({
        "value": "none",
        "label": "Not in COPO"
    })
    for s in subs:
        try:
            out.append(
                {
                    "value": s['profile_id'],
                    "label": s['accessions']['project']['accession']
                }
            )
        except:
            pass
    return out


def get_isasamples_json():
    """
    returns isa samples in a profile
    :return:
    """
    from dal.copo_da import Sample
    profile_id = get_current_request().session['profile_id']
    samples = Sample(profile_id).get_all_records()

    value_field = str("id")
    label_field = str("sample_name")
    search_field = ["id", "sample_name"]
    secondary_label_field = ["meta_sample_name"]

    elem_json = dict(value_field=value_field,
                     label_field=label_field,
                     secondary_label_field=secondary_label_field,
                     search_field=search_field,
                     options=list())

    for sd in samples:
        if sd["sample_type"] == "isasample":
            elem_json.get("options").append(
                {
                    value_field: str(sd["_id"]),
                    label_field: sd["name"],
                    secondary_label_field[0]: sd["name"],
                    "sample_type": sd.get("sample_type", str())
                }
            )

    return elem_json


def generate_sources_json(target_id=None):
    from dal.copo_da import Source
    profile_id = get_current_request().session['profile_id']

    if target_id:
        sources = list()
        sources.append(Source().get_record(target_id))
    else:
        sources = Source(profile_id).get_all_records()

    schema = Source().get_schema().get("schema_dict")

    value_field = str("id")
    label_field = str("source_name")
    search_field = ["id", "source_name"]
    secondary_label_field = ["meta_source_name"]
    component_records = dict()

    elem_json = dict(value_field=value_field,
                     label_field=label_field,
                     secondary_label_field=secondary_label_field,
                     search_field=search_field,
                     options=list(),
                     component_records=component_records)

    for src in sources:
        elem_json.get("options").append(
            {
                value_field: str(src["_id"]),
                label_field: src["name"],
                secondary_label_field[0]: src["name"]
            })

    return elem_json


def get_samples_json(target_id=None):
    """
    returns all samples in a profile (i.e isa and biosamples)
    :return:
    """
    from dal.copo_da import Sample
    profile_id = get_current_request().session['profile_id']

    if target_id:
        samples = list()
        samples.append(Sample().get_record(target_id))
    else:
        samples = Sample(profile_id).get_all_records()

    value_field = str("id")
    label_field = str("sample_name")
    search_field = ["id", "sample_name"]
    secondary_label_field = ["meta_sample_name"]

    elem_json = dict(value_field=value_field,
                     label_field=label_field,
                     secondary_label_field=secondary_label_field,
                     search_field=search_field,
                     options=list())

    for sd in samples:
        elem_json.get("options").append(
            {
                value_field: str(sd["_id"]),
                label_field: sd["name"],
                secondary_label_field[0]: sd["name"],
                "sample_type": sd.get("sample_type", str())
            })

    return elem_json


def get_datafiles_json(target_id=None):
    """
    returns all datafile record
    :return:
    """
    from dal.copo_da import DataFile
    profile_id = get_current_request().session['profile_id']

    if target_id:
        datafiles = list()
        datafiles.append(DataFile().get_record(target_id))
    else:
        datafiles = DataFile(profile_id).get_all_records()

    value_field = str("id")
    label_field = str("datafile_name")
    search_field = ["id", "datafile_name"]
    secondary_label_field = ["meta_datafile_name"]

    elem_json = dict(value_field=value_field,
                     label_field=label_field,
                     secondary_label_field=secondary_label_field,
                     search_field=search_field,
                     options=list())

    for sd in datafiles:
        elem_json.get("options").append(
            {
                value_field: str(sd["_id"]),
                label_field: sd["name"],
                secondary_label_field[0]: sd["name"]
            })

    return elem_json


def get_study_type_options():
    return lookup.DROP_DOWNS['STUDY_TYPES']


def get_assembly_type_option():
    return lookup.DROP_DOWNS['ASSEMBLY_TYPES']


def get_sample_type_options():
    from web.apps.web_copo.lookup.copo_lookup_service import COPOLookup
    return COPOLookup(data_source='sample_type_options').broker_data_source()


def get_repository_options():
    from web.apps.web_copo.lookup.copo_lookup_service import COPOLookup
    return COPOLookup(data_source='repository_options').broker_data_source()

def get_repository_types_list():
    from web.apps.web_copo.lookup.copo_lookup_service import COPOLookup
    return COPOLookup(data_source='repository_types_list').broker_data_source()


def get_omics_type_options():
    return lookup.DROP_DOWNS['OMICS_TYPE']


def get_growth_area_options():
    return lookup.DROP_DOWNS['GROWTH_AREAS']


def get_rooting_medium_options():
    return lookup.DROP_DOWNS['ROOTING_MEDIUM']


def get_nutrient_control_options():
    return lookup.DROP_DOWNS['GROWTH_NUTRIENTS']


def get_watering_control_options():
    return lookup.DROP_DOWNS['WATERING_OPTIONS']


def get_copo_id():
    # todo: remove this and uncomment the below try block!!!
    import uuid
    u = uuid.uuid4()
    return int(str(u.time_low) + str(u.time_mid))
    # make unique copo id
    # try:
    #     return get_uid()
    # except ConnectionError:
    #     return "0" * 13


def get_user_id():
    if settings.UNIT_TESTING:
        User.objects.get(username=settings.TEST_USER_NAME).id
    else:
        return ThreadLocal.get_current_user().id


def get_current_user():
    if settings.UNIT_TESTING:
        return User.objects.get(username=settings.TEST_USER_NAME)
    else:
        return ThreadLocal.get_current_user()


def get_current_request():
    return ThreadLocal.get_current_request()


def get_base_url():
    r = ThreadLocal.get_current_request()
    scheme = r.scheme
    domain = r.get_host()
    return scheme + "://" + domain


def get_datetime():
    """
    provides a consistent way of storing fields of this type across modules
    :return:
    """
    return datetime.utcnow()


def get_not_deleted_flag():
    """
    provides a consistent way of setting records as not deleted
    :return:
    """
    return "0"


def get_deleted_flag():
    """
    provides a consistent way of setting records as not deleted
    :return:
    """
    return "1"


def get_button_templates():
    return copy.deepcopy(lookup.BUTTON_TEMPLATES)["templates"]


def get_db_json_schema(component):
    """
    function returns a JSON schema configuration given a component.
    Note: these are db models schemas, necessarily conforming to the JSON Schema specification and different from
    UI schemas, which provide the configuration that COPO UI schemas map to.
    :param component:
    :return:
    """

    isa_path = RESOLVER['isa_json_db_models']

    # ...set other paths accordingly depending on where the actual files reside or, conceptually, the schema provider

    schema_dict = dict(
        publication=json_to_pytype(os.path.join(isa_path, 'publication_schema.json')).get("properties", dict()),
        person=json_to_pytype(os.path.join(isa_path, 'person_schema.json')).get("properties", dict()),
        datafile=json_to_pytype(os.path.join(isa_path, 'data_schema.json')).get("properties", dict()),
        sample=json_to_pytype(os.path.join(isa_path, 'sample_schema.json')).get("properties", dict()),
        source=json_to_pytype(os.path.join(isa_path, 'source_schema.json')).get("properties", dict()),
        material=json_to_pytype(os.path.join(isa_path, 'material_schema.json')).get("properties", dict()),
        comment=json_to_pytype(os.path.join(isa_path, 'comment_schema.json')).get("properties", dict()),
        material_attribute_value=json_to_pytype(os.path.join(isa_path, 'material_attribute_value_schema.json')).get(
            "properties", dict()),
        material_attribute=json_to_pytype(os.path.join(isa_path, 'material_attribute_schema.json')).get("properties",
                                                                                                        dict()),
        investigation=json_to_pytype(os.path.join(isa_path, 'investigation_schema.json')).get("properties", dict()),
        ontology_annotation=json_to_pytype(os.path.join(isa_path, 'ontology_annotation_schema.json')).get("properties",
                                                                                                          dict()),
        study=json_to_pytype(os.path.join(isa_path, 'study_schema.json')).get("properties", dict()),
        assay=json_to_pytype(os.path.join(isa_path, 'assay_schema.json')).get("properties", dict()),
        protocol=json_to_pytype(os.path.join(isa_path, 'protocol_schema.json')).get("properties", dict()),
        protocol_parameter=json_to_pytype(os.path.join(isa_path, 'protocol_parameter_schema.json')).get("properties",
                                                                                                        dict()),
        factor=json_to_pytype(os.path.join(isa_path, 'factor_schema.json')).get("properties", dict()),
        factor_value=json_to_pytype(os.path.join(isa_path, 'factor_value_schema.json')).get("properties", dict()),
        process=json_to_pytype(os.path.join(isa_path, 'process_schema.json')).get("properties", dict()),
        process_parameter_value=json_to_pytype(os.path.join(isa_path, 'process_parameter_value_schema.json')).get(
            "properties", dict()),
        ontology_source_reference=json_to_pytype(os.path.join(isa_path, 'ontology_source_reference_schema.json')).get(
            "properties", dict()),

    )

    return schema_dict.get(component, dict())


def get_isa_schema_xml(file_name):
    pth = RESOLVER['isa_xml_db_models']

    output_dict = dict(status=str(), content=str())

    try:
        output_dict["status"] = "success"
        output_dict["content"] = ET.parse(os.path.join(pth, file_name))

    except:
        output_dict["status"] = "error"
        output_dict["content"] = "Couldn't find any resource that corresponds to the supplied parameter!"

    return output_dict


def get_ena_remote_path(submission_token):
    """
    defines the path for datafiles uploaded to ENA Dropbox
    :param submission_token: the submission id
    :return:
    """
    remote_path = os.path.join(submission_token, str(get_current_user()))

    return remote_path


def get_ena_submission_url(user_name, password):
    """
    function builds the submission url to point to the specified (test or live box) ENA service
    :param user_name:
    :param password:
    :return:
    """


def get_copo_schema(component, as_object=False):
    """
    function retrieves a required UI schema from the DB.
    :param component: a key in the schema_dict to be retrieved
    :param as_object: True returns the schema as an object whose element can be accessed using the '.' notation. False
            for the traditional python dictionary access
    :return:
    """
    from dal.copo_base_da import DataSchemas
    schema_base = DataSchemas("COPO").get_ui_template().get("copo")

    schema_dict = dict(
        publication=schema_base.get("publication").get("fields", list()),
        person=schema_base.get("person").get("fields", list()),
        datafile=schema_base.get("datafile").get("fields", list()),
        sample=schema_base.get("sample").get("fields", list()),
        source=schema_base.get("source").get("fields", list()),
        ontology_annotation=schema_base.get("ontology_annotation").get("fields", list()),
        comment=schema_base.get("comment").get("fields", list()),
        material_attribute_value=schema_base.get("material_attribute_value").get("fields", list()),
        duration=schema_base.get("duration").get("fields", list()),
        miappe_rooting_greenhouse=schema_base.get('miappe').get('rooting').get('greenhouse').get("fields", list()),
        miappe_rooting_field=schema_base.get('miappe').get('rooting').get('field').get("fields", list()),
        hydroponics=schema_base.get('miappe').get('nutrients').get('hydroponics').get('fields', list()),
        soil=schema_base.get('miappe').get('nutrients').get('soil').get('fields', list()),
        phenotypic_variables=schema_base.get("miappe").get("phenotypic_variables").get("fields", list()),
        environment_variables=schema_base.get("miappe").get("environment_variables").get("fields", list()),
        metadata_template=schema_base.get("metadata_template").get("fields", list())
    )

    schema = schema_dict.get(component, list())

    if schema and as_object:
        schema = json_to_object(dict(fields=schema)).fields

    return schema


def object_type_control_map():
    """
    function keeps a mapping of object type controls to schema names
    :return:
    """
    control_dict = dict()
    control_dict["copo-characteristics"] = "material_attribute_value"
    control_dict["ontology term"] = "ontology_annotation"
    control_dict["copo-comment"] = "comment"
    control_dict["copo-duration"] = "duration"
    control_dict["copo-environmental-characteristics"] = "environment_variables"
    control_dict["copo-phenotypic-characteristics"] = "phenotypic_variables"

    return control_dict


def get_object_array_schema():
    control_dict = dict()
    control_dict["copo-characteristics"] = get_copo_schema("material_attribute_value")
    control_dict["copo-comment"] = get_copo_schema("comment")
    control_dict["copo-environmental-characteristics"] = get_copo_schema("environment_variables")
    control_dict["copo-phenotypic-characteristics"] = get_copo_schema("phenotypic_variables")

    return control_dict


def default_jsontype(type):
    d_type = str()

    if type == "object":
        d_type = dict()
    elif type == "array":
        d_type = list()
    elif type == "boolean":
        d_type = False

    return d_type


def get_studies():
    return lookup.DROP_DOWNS['OMICS_TYPE']
    # data = {
    #    "value": "na",
    #    "label": "Not Applicable"
    # }
    # return data


def get_args_from_parameter(parameter, param_value_dict):
    """
    given a comma seprated parameter string, function returns an argument tuple
    :param parameter:
    :param param_value_dict:
    :return:
    """

    parameter = parameter.split(",")
    parameter = [x.strip() for x in parameter]  # remove unwanted whitespaces
    args = [param_value_dict[p] for p in parameter if p in param_value_dict]
    args = tuple(args)

    return args


def san_check(val):
    return val if val is not None else ''

def get_unqualified_id(qual):
    return qual.split(".")[-1]

class DecoupleFormSubmission:
    def __init__(self, auto_fields, schema):
        """
        :param auto_fields: fields/values list from form submission
        :param schema: the particular schema used for resolving DB fields
        """

        # clear None types
        auto_fields = {k: san_check(v) for k, v in auto_fields.items() if k}

        self.auto_fields = auto_fields
        self.schema = schema
        self.object_has_value = False
        self.global_key_split = "___0___"

    def get_schema_fields_updated(self):
        from converters.ena.copo_isa_ena import ISAHelpers

        auto_dict = dict()

        for f in self.schema:
            if f.type == "array":
                # handle array types
                value_list = list()

                object_type_control = object_type_control_map().get(f.control.lower(), str())

                if object_type_control:
                    # handle object type controls e.g., ontology term, comment

                    object_fields = get_copo_schema(object_type_control, True)

                    # get the primary data...and secondary data
                    primary_data = dict()
                    secondary_data_list = list()

                    for o_f in object_fields:
                        comp_key = f.id + "." + o_f.id.split(".")[-1]

                        # and even the field may, also, very well be of type object, decouple further...
                        decoupled_list = self.decouple_object(comp_key, list(), o_f)

                        # match decoupled elements
                        key_list = list()
                        key_value_list = list()

                        for key in decoupled_list:
                            if key in self.auto_fields.keys():

                                c = [k for k in self.auto_fields.keys() if k.startswith(key + self.global_key_split)]
                                if c:
                                    secondary_data_list.append(c)

                                key_split = (key.split(f.id + ".")[-1]).split(".")
                                if len(key_split) == 1:
                                    primary_data[key_split[0]] = self.auto_fields[key]
                                else:
                                    key_list.append(key_split[:-1])
                                    key_value_list.append(dict(keys=key_split, value=self.auto_fields[key]))

                        if key_list:
                            object_model = self.form_object_model(dict(), key_list)

                            for kvl in key_value_list:
                                object_model = self.set_object_fields(object_model, kvl["keys"], kvl["value"])

                            for kk, vv in object_model.items():
                                primary_data[kk] = vv

                    # don't save empty objects
                    self.object_has_value = False
                    self.has_value(primary_data)

                    if self.object_has_value:

                        # sanitise schema: make it compliant with schema provider's specifications
                        target_schema = get_db_json_schema(object_type_control)
                        if target_schema:
                            for kx in target_schema:
                                target_schema = ISAHelpers().resolve_schema_key(target_schema, kx, object_type_control,
                                                                                primary_data)
                            value_list.append(target_schema)
                        else:
                            value_list.append(primary_data)

                    # sort secondary data
                    if secondary_data_list:
                        for s in secondary_data_list:
                            s.sort()

                        grouped_indx = list()
                        for i in range(0, len(secondary_data_list[0])):
                            h_indx = list()

                            for sdl in secondary_data_list:
                                h_indx.append(sdl[i])

                            grouped_indx.append(h_indx)

                        for g_i in grouped_indx:
                            primary_data = dict()
                            key_list = list()
                            key_value_list = list()

                            for key in g_i:
                                if key in self.auto_fields.keys():

                                    key_split = (key.split(f.id + ".")[-1]).split(".")
                                    if len(key_split) == 1:
                                        primary_data[(key_split[0]).rsplit(self.global_key_split, 1)[0]] = \
                                            self.auto_fields[key]
                                    else:
                                        key_list.append(key_split[:-1])
                                        key_split[-1] = key_split[-1].rsplit(self.global_key_split, 1)[0]
                                        key_value_list.append(dict(keys=key_split, value=self.auto_fields[key]))

                            if key_list:
                                object_model = self.form_object_model(dict(), key_list)

                                for kvl in key_value_list:
                                    object_model = self.set_object_fields(object_model, kvl["keys"], kvl["value"])

                                for kk, vv in object_model.items():
                                    primary_data[kk] = vv

                            # don't save empty objects
                            self.object_has_value = False
                            self.has_value(primary_data)

                            if self.object_has_value:
                                # sanitise schema: make it compliant with schema provider's specifications
                                target_schema = get_db_json_schema(object_type_control)

                                if target_schema:
                                    for kx in target_schema:
                                        target_schema = ISAHelpers().resolve_schema_key(target_schema, kx,
                                                                                        object_type_control,
                                                                                        primary_data)
                                    value_list.append(target_schema)
                                else:
                                    value_list.append(primary_data)

                    auto_dict[f.id.split(".")[-1]] = value_list
                else:
                    # handle array non-object type control

                    # get the primary field...and secondary data
                    if f.id in self.auto_fields.keys():
                        value_list.append(self.auto_fields[f.id])
                        secondary_data_list = [k for k in self.auto_fields.keys() if
                                               k.startswith(f.id + self.global_key_split)]

                        # sort secondary data, keeping the input order
                        if secondary_data_list:
                            secondary_data_list.sort()

                            for sdl in secondary_data_list:
                                value_list.append(self.auto_fields[sdl])

                        auto_dict[f.id.split(".")[-1]] = value_list
            else:
                # handle non-array types
                object_type_control = object_type_control_map().get(f.control.lower(), str())

                if object_type_control:
                    # handle object type controls e.g., ontology term, comment

                    object_fields = get_copo_schema(object_type_control, True)

                    # get the data
                    primary_data = dict()

                    for o_f in object_fields:
                        comp_key = f.id + "." + o_f.id.split(".")[-1]

                        # and even the field may, also, very well be of type object, decouple further...
                        decoupled_list = self.decouple_object(comp_key, list(), o_f)

                        # match decoupled elements
                        key_list = list()
                        key_value_list = list()

                        for key in decoupled_list:
                            if key in self.auto_fields.keys():

                                key_split = (key.split(f.id + ".")[-1]).split(".")
                                if len(key_split) == 1:
                                    primary_data[key_split[0]] = self.auto_fields[key]
                                else:
                                    key_list.append(key_split[:-1])
                                    key_value_list.append(dict(keys=key_split, value=self.auto_fields[key]))

                        if key_list:
                            object_model = self.form_object_model(dict(), key_list)

                            for kvl in key_value_list:
                                object_model = self.set_object_fields(object_model, kvl["keys"], kvl["value"])

                            for kk, vv in object_model.items():
                                primary_data[kk] = vv

                        # don't save empty objects
                        self.object_has_value = False
                        auto_dict[f.id.split(".")[-1]] = dict()

                        self.has_value(primary_data)

                        if self.object_has_value:
                            auto_dict[f.id.split(".")[-1]] = primary_data

                    # sanitise schema: make it compliant with schema provider's specifications
                    target_schema = get_db_json_schema(object_type_control)

                    if target_schema:
                        for kx in target_schema:
                            target_schema = ISAHelpers().resolve_schema_key(target_schema, kx, object_type_control,
                                                                            primary_data)
                        auto_dict[f.id.split(".")[-1]] = target_schema
                    else:
                        auto_dict[f.id.split(".")[-1]] = primary_data


                else:
                    # not an object type control

                    if f.id in self.auto_fields.keys():
                        auto_dict[f.id.split(".")[-1]] = self.auto_fields[f.id]

        return auto_dict

    def get_schema_fields_updated_dict(self):
        """
        this is an alternative to the '.' object version - converting to object '.' seems expensive
        :return:
        """
        from converters.ena.copo_isa_ena import ISAHelpers

        auto_dict = dict()

        for f in self.schema:
            f_id = f['id']
            f_type = f['type']
            f_control = f['control']
            if f_type == "array":
                # handle array types
                value_list = list()

                object_type_control = object_type_control_map().get(f_control.lower(), str())

                if object_type_control:
                    # handle object type controls e.g., ontology term, comment

                    object_fields = get_copo_schema(object_type_control)

                    # get the primary data...and secondary data
                    primary_data = dict()
                    secondary_data_list = list()

                    for o_f in object_fields:
                        comp_key = f_id + "." + o_f['id'].split(".")[-1]

                        # and even the field may very well be of type object, decouple further...
                        decoupled_list = self.decouple_object_dict(comp_key, list(), o_f)

                        # match decoupled elements
                        key_list = list()
                        key_value_list = list()

                        for key in decoupled_list:
                            if key in self.auto_fields.keys():

                                c = [k for k in self.auto_fields.keys() if k.startswith(key + self.global_key_split)]
                                if c:
                                    secondary_data_list.append(c)

                                key_split = (key.split(f_id + ".")[-1]).split(".")
                                if len(key_split) == 1:
                                    primary_data[key_split[0]] = self.auto_fields[key]
                                else:
                                    key_list.append(key_split[:-1])
                                    key_value_list.append(dict(keys=key_split, value=self.auto_fields[key]))

                        if key_list:
                            object_model = self.form_object_model(dict(), key_list)

                            for kvl in key_value_list:
                                object_model = self.set_object_fields(object_model, kvl["keys"], kvl["value"])

                            for kk, vv in object_model.items():
                                primary_data[kk] = vv

                    # don't save empty objects
                    self.object_has_value = False
                    self.has_value(primary_data)

                    if self.object_has_value:

                        # sanitise schema: make it compliant with schema provider's specifications
                        target_schema = get_db_json_schema(object_type_control)
                        if target_schema:
                            for kx in target_schema:
                                target_schema = ISAHelpers().resolve_schema_key(target_schema, kx, object_type_control,
                                                                                primary_data)
                            value_list.append(target_schema)
                        else:
                            value_list.append(primary_data)

                    # sort secondary data
                    if secondary_data_list:
                        for s in secondary_data_list:
                            s.sort()

                        grouped_indx = list()
                        for i in range(0, len(secondary_data_list[0])):
                            h_indx = list()

                            for sdl in secondary_data_list:
                                h_indx.append(sdl[i])

                            grouped_indx.append(h_indx)

                        for g_i in grouped_indx:
                            primary_data = dict()
                            key_list = list()
                            key_value_list = list()

                            for key in g_i:
                                if key in self.auto_fields.keys():

                                    key_split = (key.split(f_id + ".")[-1]).split(".")
                                    if len(key_split) == 1:
                                        primary_data[(key_split[0]).rsplit(self.global_key_split, 1)[0]] = \
                                            self.auto_fields[key]
                                    else:
                                        key_list.append(key_split[:-1])
                                        key_split[-1] = key_split[-1].rsplit(self.global_key_split, 1)[0]
                                        key_value_list.append(dict(keys=key_split, value=self.auto_fields[key]))

                            if key_list:
                                object_model = self.form_object_model(dict(), key_list)

                                for kvl in key_value_list:
                                    object_model = self.set_object_fields(object_model, kvl["keys"], kvl["value"])

                                for kk, vv in object_model.items():
                                    primary_data[kk] = vv

                            # don't save empty objects
                            self.object_has_value = False
                            self.has_value(primary_data)

                            if self.object_has_value:
                                # sanitise schema: make it compliant with schema provider's specifications
                                target_schema = get_db_json_schema(object_type_control)

                                if target_schema:
                                    for kx in target_schema:
                                        target_schema = ISAHelpers().resolve_schema_key(target_schema, kx,
                                                                                        object_type_control,
                                                                                        primary_data)
                                    value_list.append(target_schema)
                                else:
                                    value_list.append(primary_data)

                    auto_dict[f_id.split(".")[-1]] = value_list
                else:
                    # handle array non-object type control

                    # get the primary field...and secondary data
                    if f_id in self.auto_fields.keys():
                        value_list.append(self.auto_fields[f_id])
                        secondary_data_list = [k for k in self.auto_fields.keys() if
                                               k.startswith(f_id + self.global_key_split)]

                        # sort secondary data, keeping the input order
                        if secondary_data_list:
                            secondary_data_list.sort()

                            for sdl in secondary_data_list:
                                tmp_val = self.auto_fields.get(sdl, str()).strip()
                                if tmp_val:
                                    value_list.append(tmp_val)

                        auto_dict[f_id.split(".")[-1]] = value_list
            else:
                # handle non-array types
                object_type_control = object_type_control_map().get(f_control.lower(), str())

                if object_type_control:
                    # handle object type controls e.g., ontology term, comment

                    object_fields = get_copo_schema(object_type_control)

                    # get the data
                    primary_data = dict()

                    for o_f in object_fields:
                        comp_key = f_id + "." + o_f['id'].split(".")[-1]

                        # and even the field may, also, very well be of type object, decouple further...
                        decoupled_list = self.decouple_object_dict(comp_key, list(), o_f)

                        # match decoupled elements
                        key_list = list()
                        key_value_list = list()

                        for key in decoupled_list:
                            if key in self.auto_fields.keys():

                                key_split = (key.split(f_id + ".")[-1]).split(".")
                                if len(key_split) == 1:
                                    primary_data[key_split[0]] = self.auto_fields[key]
                                else:
                                    key_list.append(key_split[:-1])
                                    key_value_list.append(dict(keys=key_split, value=self.auto_fields[key]))

                        if key_list:
                            object_model = self.form_object_model(dict(), key_list)

                            for kvl in key_value_list:
                                object_model = self.set_object_fields(object_model, kvl["keys"], kvl["value"])

                            for kk, vv in object_model.items():
                                primary_data[kk] = vv

                        # don't save empty objects
                        self.object_has_value = False
                        auto_dict[f_id.split(".")[-1]] = dict()

                        self.has_value(primary_data)

                        if self.object_has_value:
                            auto_dict[f_id.split(".")[-1]] = primary_data

                    # sanitise schema: make it compliant with schema provider's specifications
                    target_schema = get_db_json_schema(object_type_control)

                    if target_schema:
                        for kx in target_schema:
                            target_schema = ISAHelpers().resolve_schema_key(target_schema, kx, object_type_control,
                                                                            primary_data)
                        auto_dict[f_id.split(".")[-1]] = target_schema
                    else:
                        auto_dict[f_id.split(".")[-1]] = primary_data


                else:
                    # not an object type control

                    if f_id in self.auto_fields.keys():
                        auto_dict[f_id.split(".")[-1]] = self.auto_fields[f_id]

        return auto_dict

    def decouple_object(self, comp_key, decoupled_list, field):
        base_key = comp_key

        object_type_control = object_type_control_map().get(field.control.lower(), str())

        if object_type_control:  # handle object type controls e.g., ontology term, comment
            object_fields = get_copo_schema(object_type_control, True)

            for o_f in object_fields:
                comp_key = base_key + "." + o_f.id.split(".")[-1]
                decoupled_list = self.decouple_object(comp_key, decoupled_list, o_f)
        else:
            decoupled_list.append(comp_key)

        return decoupled_list

    def decouple_object_dict(self, comp_key, decoupled_list, field):
        """
        this function mirrors the '.' notation function with similar name (without _dict)
        :param comp_key:
        :param decoupled_list:
        :param field:
        :return:
        """
        base_key = comp_key

        object_type_control = object_type_control_map().get(field['control'].lower(), str())

        if object_type_control:  # handle object type controls e.g., ontology term, comment
            object_fields = get_copo_schema(object_type_control)

            for o_f in object_fields:
                comp_key = base_key + "." + o_f['id'].split(".")[-1]
                decoupled_list = self.decouple_object_dict(comp_key, decoupled_list, o_f)
        else:
            decoupled_list.append(comp_key)

        return decoupled_list

    def set_object_fields(self, d, keys, val):
        out = d
        for k in keys[:-2]:
            out = out[k]
        out[keys[-2]][keys[-1]] = val

        return d

    def form_object_model(self, d, key_list):
        object_model = d
        for path in key_list:
            current_level = object_model
            for part in path:
                if part not in current_level:
                    current_level[part] = dict()
                current_level = current_level[part]

        return d

    def has_value(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self.has_value(v)
            else:
                if v:
                    # set some global value
                    self.object_has_value = True

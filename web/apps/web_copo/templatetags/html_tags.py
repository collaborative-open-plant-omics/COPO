__author__ = 'tonietuk'

import time
import json
import copy
import pandas as pd
from uuid import uuid4
from bson import ObjectId
from django import template
from dal import cursor_to_list
from django.urls import reverse
from django.contrib.auth.models import User
from web.apps.web_copo.schemas.utils import data_utils
from web.apps.web_copo.lookup.lookup import HTML_TAGS
import web.apps.web_copo.lookup.lookup as lkup
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from web.apps.web_copo.lookup.copo_lookup_service import COPOLookup
from dal.copo_base_da import DataSchemas
from dal.copo_da import ProfileInfo, Repository, Description, Profile, Publication, Source, Person, Sample, \
    Submission, \
    DataFile, DAComponent, Annotation, CGCore, MetadataTemplate
from allauth.socialaccount import providers
from hurry.filesize import size as hurrysize
from django_tools.middlewares import ThreadLocal

register = template.Library()

# dictionary of components table id, gotten from the UI
table_id_dict = dict(publication="publication_table",
                     person="person_table",
                     sample="sample_table",
                     datafile="datafile_table",
                     annotation="annotation_table",
                     profile="profile_table",
                     metadata_template="metadata_template_table"
                     )
da_dict = dict(
    publication=Publication,
    person=Person,
    sample=Sample,
    source=Source,
    profile=Profile,
    datafile=DataFile,
    submission=Submission,
    annotation=Annotation,
    cgcore=CGCore,
    metadata_template=MetadataTemplate
)


@register.simple_tag
def get_providers_orcid_first():
    """
    Returns a list of social authentication providers with Orcid as the first entry

    Usage: `{% get_providers_orcid_first as socialaccount_providers %}`.

    Then within the template context, `socialaccount_providers` will hold
    a list of social providers configured for the current site.
    """
    p_list = providers.registry.get_list()
    for idx, p in enumerate(p_list):
        if p.id == 'orcid':
            o = p_list.pop(idx)
    return [o] + p_list


def get_element_by_id(field_id):
    elem = {}
    out_list = get_fields_list(field_id)
    for f in out_list:
        if f["id"] == field_id:
            f["label"] = trim_parameter_value_label(f["label"])
            elem = f
            break
    return elem


def trim_parameter_value_label(label):
    if "Parameter Value" in label:
        return str.capitalize(label[label.index('[') + 1:label.index(']')])
    else:
        return label


@register.filter("generate_ui_labels")
def generate_ui_labels(field_id):
    out_list = get_fields_list(field_id)
    label = ""
    for f in out_list:
        if f["id"] == field_id:
            label = f["label"]
            break
    return label


def get_control_options(f):
    # option values are typically defined as a list,
    # or in some cases (e.g., 'copo-multi-search'),
    # as a dictionary. However, option values could also be resolved or generated dynamically
    # using callbacks. Callbacks, essentially, define functions that resolve options data

    option_values = list()

    if f.get("control", "text") in ["copo-lookup", "copo-lookup2"]:
        return COPOLookup(accession=f.get('data', str()),
                          data_source=f.get('data_source', str())).broker_component_search()['result']

    if "option_values" not in f:  # you shouldn't be here
        return option_values

    # return existing option values
    if isinstance(f["option_values"], list) and f["option_values"]:
        return f["option_values"]

    # resolve option values from a data source
    if f.get("data_source", str()):
        return COPOLookup(data_source=f.get('data_source', str())).broker_data_source()

    if isinstance(f["option_values"], dict):
        if f.get("option_values", dict()).get("callback", dict()).get("function", str()):
            call_back_function = f.get("option_values", dict()).get("callback", dict()).get("function", str())
            option_values = getattr(d_utils, call_back_function)()
        else:
            # e.g., multi-search has this format
            option_values = f["option_values"]

    return option_values


@register.filter("generate_copo_form")
def generate_copo_form(component=str(), target_id=str(), component_dict=dict(), message_dict=dict(), profile_id=None,
                       **kwargs):
    # message_dict templates are defined in the lookup dictionary: "MESSAGES_LKUPS"

    label_dict = get_labels()

    da_object = DAComponent(component=component, profile_id=profile_id)

    if component in da_dict:
        da_object = da_dict[component](profile_id)

    form_value = component_dict

    # get record, if in edit mode
    if target_id:
        form_value = da_object.get_record(target_id)

    form_schema = list()

    # get schema fields
    for f in da_object.get_component_schema(**kwargs):
        if f.get("show_in_form", True):

            # if required, resolve data source for select-type controls,
            # i.e., if a callback is defined on the 'option_values' field
            if "option_values" in f or f.get("control", "text") in ["copo-lookup", "copo-lookup2"]:
                f['data'] = form_value.get(f["id"].split(".")[-1], str())
                f["option_values"] = get_control_options(f)

            # resolve values for unique items...
            # if a list of unique items is provided with the schema, use it, else dynamically
            # generate unique items based on the component records
            if "unique" in f and not f.get("unique_items", list()):
                f["unique_items"] = generate_unique_items(component=component, profile_id=profile_id,
                                                          elem_id=f["id"].split(".")[-1], record_id=target_id, **kwargs)

            # filter based on sample type
            if component == "sample" and not filter_sample_type(form_value, f):
                continue

            if component == "profile":
                if "type" in f["id"]:
                    # check if this user is in dtol group, if not, break so as to not add dropdown to form
                    request = ThreadLocal.get_current_request()
                    is_DTOL = request.user.groups.filter(name__in=['dtol_users']).exists()
                    if not is_DTOL:
                        break

            form_schema.append(f)

    if form_value:
        form_value["_id"] = str(target_id)
    else:
        form_value = str()

    return dict(component_name=component,
                form_label=label_dict.get(component, dict()).get("label", str()),
                form_value=form_value,
                target_id=target_id,
                form_schema=form_schema,
                form_message=message_dict,
                )


@register.filter("get_labels")
def get_labels():
    label_dict = dict(publication=dict(label="Publication"),
                      person=dict(label="Person"),
                      sample=dict(label="Sample"),
                      source=dict(label="Source"),
                      profile=dict(label="Profile"),
                      annotation=dict(label="Annotation"),
                      datafile=dict(label="Datafile"),
                      metadata_template=dict(label="Metadata Template"),
                      repository=dict(label="Repository"),
                      )

    return label_dict


@register.filter("filter_sample_type")
def filter_sample_type(form_value, elem):
    # filters UI elements based on sample type

    allowable = True
    default_type = "biosample"
    sample_types = list()

    for s_t in d_utils.get_sample_type_options():
        sample_types.append(s_t["value"])

    if "sample_type" in form_value:
        default_type = form_value["sample_type"]

    if default_type not in elem.get("specifications", sample_types):
        allowable = False

    return allowable


@register.filter("generate_component_record")
def generate_component_records(component=str(), profile_id=str(), label_key=str(), **kwargs):
    da_object = DAComponent(component=component, profile_id=profile_id)

    if component in da_dict:
        da_object = da_dict[component](profile_id)

    component_records = list()
    schema = da_object.get_component_schema(**kwargs)

    # if label_key is not provided, we will assume the first element in the schema to be the label_key

    if not label_key:
        label_key = schema[0]["id"].split(".")[-1] if schema else ''

    for record in da_object.get_all_records(**kwargs):
        option = dict(value=str(record["_id"]), label=record.get(label_key, "N/A"))
        component_records.append(option)

    return component_records


@register.filter("generate_unique_items")
def generate_unique_items(component=str(), profile_id=str(), elem_id=str(), record_id=str(), **kwargs):
    da_object = DAComponent(component=component, profile_id=profile_id)
    action_type = kwargs.get("action_type", str())
    component_records = list()

    all_records = da_object.get_all_records()

    if action_type == "cloning":
        component_records = [x[elem_id] for x in all_records if elem_id in x]
    else:
        component_records = [x[elem_id] for x in all_records if elem_id in x and not str(x["_id"]) == record_id]

    return component_records


@register.filter("generate_table_columns")
def generate_table_columns(component=str()):
    da_object = DAComponent(component=component)

    # get and filter schema elements based on displayable columns
    schema = [x for x in da_object.get_schema().get("schema_dict") if x.get("show_in_table", True)]

    columns = list()
    columns.append(dict(data="record_id", visible=False))
    detail_dict = dict(className='summary-details-control detail-hover-message', orderable=False, data=None,
                       title='', defaultContent='', width="5%")

    columns.insert(0, detail_dict)

    # get indexed fields - only fields that are indexed can be ordered when using server-side processing
    # indexed_fields = list()
    #
    # for k, v in da_object.get_collection_handle().index_information().items():
    #     indexed_fields.append(v['key'][0][0])

    for x in schema:
        x["id"] = x["id"].split(".")[-1]
        columns.append(dict(data=x["id"], title=x["label"], orderable=True))

        # orderable = False
        # if x["id"] in indexed_fields:
        #     orderable = True
        # columns.append(dict(data=x["id"], title=x["label"], orderable=orderable))

    # add column for annotation control
    if component == "datafile":
        special_dict = dict(className='annotate-datafile', orderable=False, data=None,
                            title='', width="1%",
                            defaultContent='<span title="Annotate datafile" style="cursor: '
                                           'pointer;" class="copo-tooltip">'
                                           '<i class="ui icon violet write" aria-hidden="true"></i></span>')
        columns.append(special_dict)

    return columns


@register.filter("generate_server_side_table_records")
def generate_server_side_table_records(profile_id=str(), component=str(), request=dict()):
    # function generates component records for building an UI table using server-side processing
    # - please note that for effective data display,
    # all array and object-type fields (e.g., characteristics) are deferred to sub-table display.
    # please define such in the schema as "show_in_table": false and "show_as_attribute": true

    data_set = list()

    n_size = int(request.get("length", 10))  # assumes 10 records per page if length not set
    draw = int(request.get("draw", 1))
    start = int(request.get("start", 0))

    # instantiate data access object
    da_object = DAComponent(profile_id, component)

    return_dict = dict()

    records_total = da_object.get_collection_handle().count(
        {'profile_id': profile_id, 'deleted': data_utils.get_not_deleted_flag()})

    # retrieve and process records
    filter_by = dict()

    if component == "datafile":
        # get all active bundles in the profile
        existing_bundles = Description().get_all_records_columns(projection=dict(_id=1),
                                                                 filter_by=dict(profile_id=profile_id,
                                                                                component=component))
        existing_bundles = [str(x["_id"]) for x in existing_bundles]
        records_total = da_object.get_collection_handle().count({"$and": [
            {"profile_id": profile_id, 'deleted': data_utils.get_not_deleted_flag()},
            {"$or": [
                {"description_token": {"$in": [None, False, ""]}},
                {"description_token": {"$nin": existing_bundles}}]}
        ]})

        filter_by = {"$or": [
            {"description_token": {"$in": [None, False, ""]}},
            {"description_token": {"$nin": existing_bundles}}]}

    # get and filter schema elements based on displayable columns
    schema = [x for x in da_object.get_schema().get("schema_dict") if x.get("show_in_table", True)]

    # build db column projection
    projection = [(x["id"].split(".")[-1], 1) for x in schema]

    # order by
    sort_by = request.get('order[0][column]', '0')
    sort_by = request.get('columns[' + sort_by + '][data]', '')
    sort_direction = request.get('order[0][dir]', 'asc')

    sort_by = '_id' if not sort_by else sort_by
    sort_direction = 1 if sort_direction == 'asc' else -1

    # search
    search_term = request.get('search[value]', '').strip()

    records = da_object.get_all_records_columns_server(sort_by=sort_by, sort_direction=sort_direction,
                                                       search_term=search_term, projection=dict(projection),
                                                       limit=n_size, skip=start, filter_by=filter_by)

    records_filtered = records_total

    if search_term:
        records_filtered = da_object.get_collection_handle().count(
            {'profile_id': profile_id, 'deleted': data_utils.get_not_deleted_flag(),
             'name': {'$regex': search_term, "$options": 'i'}})

    if records:
        df = pd.DataFrame(records)

        df['record_id'] = df._id.astype(str)
        df["DT_RowId"] = df.record_id
        df.DT_RowId = 'row_' + df.DT_RowId
        df = df.drop('_id', axis='columns')

        for x in schema:
            x["id"] = x["id"].split(".")[-1]
            df[x["id"]] = df[x["id"]].apply(resolve_control_output_apply, args=(x,)).astype(str)

        data_set = df.to_dict('records')

    return_dict["records_total"] = records_total
    return_dict["records_filtered"] = records_filtered
    return_dict["data_set"] = data_set
    return_dict["draw"] = draw

    return return_dict


@register.filter("generate_table_records")
def generate_table_records(profile_id=str(), component=str(), record_id=str()):
    # function generates component records for building an UI table - please note that for effective tabular display,
    # all array and object-type fields (e.g., characteristics) are deferred to sub-table display.
    # please define such in the schema as "show_in_table": false and "show_as_attribute": true
    type = Profile().get_type(profile_id=profile_id)
    columns = list()
    data_set = list()

    # instantiate data access object
    da_object = DAComponent(profile_id, component)

    get_dtol_fields = type in ["Aquatic Symbiosis Genomics (ASG)", "Darwin Tree of Life (DTOL)"]
    # get and filter schema elements based on displayable columns and profile type
    if get_dtol_fields:
        schema = list()
        for x in da_object.get_schema().get("schema_dict"):
            if (x.get("show_in_table", True) and ("asg" in x.get("specifications", []) or "dtol" in x.get(
                    "specifications", []))):
                schema.append(x)
    else:
        schema = list()
        for x in da_object.get_schema().get("schema_dict"):
            if (x.get("show_in_table", True) and ("biosample" in x.get("specifications", []) or "isasample" in x.get(
                    "specifications", []))):
                schema.append(x)

    # build db column projection
    projection = [(x["id"].split(".")[-1], 1) for x in schema]

    filter_by = dict()
    if record_id:
        filter_by["_id"] = ObjectId(str(record_id))

    # retrieve and process records
    records = da_object.get_all_records_columns(sort_by="date_modified", sort_direction=1,
                                                projection=dict(projection), filter_by=filter_by)

    if len(records):
        df = pd.DataFrame(records)
        df['s_n'] = df.index

        df['record_id'] = df._id.astype(str)
        df["DT_RowId"] = df.record_id
        df.DT_RowId = 'row_' + df.DT_RowId
        df = df.drop('_id', axis='columns')

        columns.append(dict(data="record_id", visible=False))
        detail_dict = dict(className='summary-details-control detail-hover-message', orderable=False, data=None,
                           title='', defaultContent='', width="5%")

        columns.insert(0, detail_dict)

        df_columns = list(df.columns)

        for x in schema:
            x["id"] = x["id"].split(".")[-1]
            columns.append(dict(data=x["id"], title=x["label"]))
            if x["id"] not in df_columns:
                df[x["id"]] = str()
            df[x["id"]] = df[x["id"]].fillna('')

            if "dtol" not in x.get("specifications", []) or "asg" not in x.get("specifications", []):
                df[x["id"]] = df[x["id"]].apply(resolve_control_output_apply, args=(x,))

        data_set = df.to_dict('records')

    return_dict = dict(dataSet=data_set,
                       columns=columns
                       )

    return return_dict


@register.filter("generate_submissions_records")
def generate_submissions_records(profile_id=str(), component=str(), record_id=str()):
    # function generates component records for building an UI table - please note that for effective tabular display,
    # all array and object-type fields (e.g., characteristics) are deferred to sub-table display.
    # please define such in the schema as "show_in_table": false and "show_as_attribute": true

    data_set = list()

    # build db column projection
    submission_projection = [('date_modified', 1), ('complete', 1), ('deleted', 1)]
    repository_projection = [('name', 1), ('type', 1)]

    schema = [x for x in Submission().get_schema().get("schema_dict") if
              x["id"].split(".")[-1] in [y[0] for y in submission_projection]]

    repository_schema = [x for x in Repository().get_schema().get("schema_dict") if
                         x["id"].split(".")[-1] in [y[0] for y in repository_projection]]

    # specify filtering
    filter_conditions = [dict(deleted=data_utils.get_not_deleted_flag())]

    # add profile
    if profile_id:
        filter_conditions.append(dict(profile_id=profile_id))

    if record_id:
        filter_conditions.append(dict(_id=ObjectId(str(record_id))))

    # specify projection
    query_projection = {
        "deleted": 1,
        "date_modified": 1,
        "complete": 1,
        "repository_docs.name": 1,
        "description_docs.name": 1,
        "repository_docs.type": 1,
        "profile_id": 1
    }

    doc = Submission().get_collection_handle().aggregate(
        [
            {"$addFields": {
                "destination_repo_converted": {
                    "$convert": {
                        "input": "$destination_repo",
                        "to": "objectId",
                        "onError": 0
                    }
                },
                "description_token_converted": {
                    "$convert": {
                        "input": "$description_token",
                        "to": "objectId",
                        "onError": 0
                    }
                }
            }
            },
            {
                "$lookup":
                    {
                        "from": "RepositoryCollection",
                        "localField": "destination_repo_converted",
                        "foreignField": "_id",
                        "as": "repository_docs"
                    }
            },
            {
                "$lookup":
                    {
                        "from": "DescriptionCollection",
                        "localField": "description_token_converted",
                        "foreignField": "_id",
                        "as": "description_docs"
                    }
            },
            {
                "$project": query_projection
            },
            {
                "$match": {"$and": filter_conditions}
            },
            {"$sort": {"date_modified": 1}}
        ])

    records = cursor_to_list(doc)

    for indx, rec in enumerate(records):
        new_data = dict()
        new_data["s_n"] = indx

        for f in schema:
            f_id = f["id"].split(".")[-1]
            new_data[f_id] = resolve_control_output(rec, f)

        new_data["record_id"] = str(rec["_id"])
        new_data["DT_RowId"] = "row_" + str(rec["_id"])

        try:
            new_data["bundle_name"] = rec['description_docs'][0].get('name', str())
        except (IndexError, AttributeError) as error:
            new_data["bundle_name"] = str()

        try:
            repository_record = rec['repository_docs'][0]
        except (IndexError, AttributeError) as error:
            repository_record = dict()

        for f in repository_schema:
            f_id = f["id"].split(".")[-1]
            new_data["repository_" + f_id] = resolve_control_output(repository_record, f)

        data_set.append(new_data)

    return dict(dataSet=data_set, )


@register.filter("generate_repositories_records")
def generate_repositories_records(component=str(), record_id=str()):
    # function generates component records for building an UI table - please note that for effective tabular display,
    # all array and object-type fields (e.g., characteristics) are deferred to sub-table display.
    # please define such in the schema as "show_in_table": false and "show_as_attribute": true

    data_set = list()

    # get and filter schema elements based on displayable columns
    schema = [x for x in Repository().get_schema().get("schema_dict") if x.get("show_in_table", True)]

    # build db column projection
    projection = [(x["id"].split(".")[-1], 1) for x in schema]

    filter_by = dict()
    if record_id:
        filter_by["_id"] = ObjectId(str(record_id))

    # retrieve and process records
    records = Repository().get_all_records_columns(sort_by="date_modified", sort_direction=1,
                                                   projection=dict(projection),
                                                   filter_by=filter_by)

    for indx, rec in enumerate(records):
        new_data = dict()
        new_data["s_n"] = indx
        new_data["record_id"] = str(rec["_id"])
        new_data["DT_RowId"] = "row_" + str(rec["_id"])

        for f in schema:
            f_id = f["id"].split(".")[-1]
            new_data[f_id] = resolve_control_output(rec, f)

        data_set.append(new_data)

    return dict(dataSet=data_set, )


@register.filter("generate_managed_repositories")
def generate_managed_repositories(component=str(), user_id=str()):
    # function generates component records for building an UI table - please note that for effective tabular display,
    # all array and object-type fields (e.g., characteristics) are deferred to sub-table display.
    # please define such in the schema as "show_in_table": false and "show_as_attribute": true

    data_set = list()
    records = list()

    # get and filter schema elements based on displayable columns
    schema = [x for x in Repository().get_schema().get("schema_dict") if x.get("show_in_table", True)]

    # build db column projection
    projection = [(x["id"].split(".")[-1], 1) for x in schema]

    filter_by = dict()

    user = User.objects.get(pk=user_id)
    user_repo_ids = user.userdetails.repo_manager
    user_repo_ids = {ObjectId(x) for x in user_repo_ids}

    if user_repo_ids:
        filter_by["_id"] = {"$in": list(user_repo_ids)}

        # retrieve and process records
        records = Repository().get_all_records_columns(sort_by="date_modified", sort_direction=1,
                                                       projection=dict(projection),
                                                       filter_by=filter_by)

    for indx, rec in enumerate(records):
        new_data = dict()
        new_data["s_n"] = indx
        new_data["record_id"] = str(rec["_id"])
        new_data["DT_RowId"] = "row_" + str(rec["_id"])

        for f in schema:
            f_id = f["id"].split(".")[-1]
            new_data[f_id] = resolve_control_output(rec, f)

        data_set.append(new_data)

    return dict(dataSet=data_set, )


@register.filter("generate_copo_table_data")
def generate_copo_table_data(profile_id=str(), component=str()):
    # This method generates the 'json' for building an UI table

    # instantiate data access object
    da_object = DAComponent(profile_id, component)

    # get records
    records = da_object.get_all_records()

    columns = list()
    dataSet = list()

    displayable_fields = list()

    # headers
    for f in da_object.get_schema().get("schema_dict"):
        if f.get("show_in_table", True):
            displayable_fields.append(f)
            columns.append(dict(title=f["label"]))

    columns.append(dict(title=str()))  # extra 'blank' header for record actions column

    # data
    for rec in records:
        row = list()
        for df in displayable_fields:
            row.append(resolve_control_output(rec, df))

        row.append(str(rec["_id"]))  # last element in a row exposes the id of the record
        dataSet.append(row)

    # define action buttons
    button_templates = d_utils.get_button_templates()

    common_btn_dict = dict(row_btns=[button_templates['edit_row'], button_templates['delete_row']],
                           global_btns=[button_templates['delete_global']])

    sample_info = copy.deepcopy(button_templates['info_row'])
    sample_info["text"] = "Sample Attributes"

    buttons_dict = dict(publication=common_btn_dict,
                        person=common_btn_dict,
                        sample=dict(row_btns=[sample_info, button_templates['edit_row'],
                                              button_templates['delete_row']],
                                    global_btns=[button_templates['add_new_samples_global'],
                                                 button_templates['delete_global']]),
                        source=common_btn_dict,
                        profile=common_btn_dict,
                        annotation=common_btn_dict,
                        metadata_template=common_btn_dict,
                        datafile=dict(
                            row_btns=[button_templates['info_row'], button_templates['describe_row'],
                                      button_templates['delete_row']],
                            global_btns=[button_templates['describe_global'],
                                         button_templates['undescribe_global']])
                        )

    action_buttons = dict(row_btns=buttons_dict.get(component).get("row_btns"),
                          global_btns=buttons_dict.get(component).get("global_btns")
                          )

    return_dict = dict(columns=columns,
                       dataSet=dataSet,
                       table_id=table_id_dict.get(component, str()),
                       action_buttons=action_buttons
                       )

    return return_dict


def get_record_data(record_object=dict(), component=str()):
    # This function is targeted for tabular record display for a single row data

    schema = DAComponent(component=component).get_schema().get("schema_dict")

    row = list()

    for f in schema:
        if f.get("show_in_table", True):
            if "dtol" in f["specifications"]:
                row.append(record_object[(f.id.split(".")[-1])])
            else:
                row.append(resolve_control_output(record_object, f))

    row.append(str(record_object["_id"]))  # last element in a row exposes the id of the record

    return_dict = dict(row_data=row,
                       table_id=table_id_dict.get(component, str())
                       )

    return return_dict


@register.filter("generate_copo_profiles_data")
def generate_copo_profiles_data(profiles=list()):
    data_set = list()

    for pr in profiles:
        temp_set = list()
        temp_set.append({"header": "ID", "data": str(pr["_id"]), "key": "_id"})
        for f in Profile().get_schema().get("schema_dict"):
            if f.get("show_in_table", True):
                temp_set.append({"header": f.get("label", str()), "data": resolve_control_output(pr, f),
                                 "key": f["id"].split(".")[-1]})
        # add whether this is a shared profile
        shared = dict()
        shared['header'] = None
        shared['data'] = pr.get('shared', False)
        shared['key'] = 'shared_profile'
        temp_set.append(shared)

        data_set.append(temp_set)

    return_dict = dict(dataSet=data_set)

    return return_dict


@register.filter("generate_copo_shared_profiles_data")
def generate_copo_shared_profiles_data(profiles=list()):
    data_set = list()

    for pr in profiles:
        temp_set = list()
        temp_set.append({"header": "ID", "data": str(pr["_id"]), "key": "_id"})
        for f in Profile().get_schema().get("schema_dict"):
            if f.get("show_in_table", True):
                temp_set.append({"header": f.get("label", str()), "data": resolve_control_output(pr, f),
                                 "key": f["id"].split(".")[-1]})

        data_set.append(temp_set)

    return_dict = dict(dataSet=data_set)

    return return_dict


@register.filter("get_repo_stats")
def get_repo_stats(repository_id=str()):
    """
    function
    :param repository_id:
    :return:
    """

    result = list()

    schema = [x for x in Repository().get_schema().get("schema_dict") if x.get("show_in_table", True)]

    # build db column projection
    projection = [(x["id"].split(".")[-1], 1) for x in schema]

    filter_by = dict(_id=str(repository_id))
    if repository_id:
        filter_by["_id"] = ObjectId(filter_by["_id"])

    records = Repository().get_all_records_columns(projection=dict(projection),
                                                   filter_by=filter_by)

    if records:
        for f in schema:
            result.append(dict(label=f["label"], value=resolve_control_output(records[0], f)))

    return result


@register.filter("get_submission_remote_url")
def get_submission_remote_url(submission_id=str()):
    """
    function generates the resource urls/identifiers to a submission in its remote location
    :param submission_id:
    :return:
    """

    result = dict(status='info', urls=list(), message="Remote identifiers not found or unspecified procedure.")

    # get repository type, and use this to decide what to return

    try:
        repository = Submission().get_repository_type(submission_id=submission_id)
    except (IndexError, AttributeError) as error:
        result['status'] = 'error'
        result['message'] = 'Could not retrieve record'
        return result

    # sacrificing an extra call to the db, based on what is needed, than dumping all accessions to memory
    if repository == "ena":
        doc = Submission().get_collection_handle().find_one({"_id": ObjectId(submission_id)},
                                                            {"accessions.project": 1})
        if not doc:
            return result

        prj = doc.get('accessions', dict()).get('project', list())
        result["urls"].append("https://www.ebi.ac.uk/ena/data/view/" + prj[0].get("accession", str()))
        return result

    # generate for other repository types here

    return result


@register.filter("get_submission_meta_repo")
def get_submission_meta_repo(submission_id=str(), user_id=str()):
    """
    function returns metadata and repository details for a submission
    :param submission_id:
    :param user_id:
    :return:
    """

    result = dict(status='success')

    # specify filtering
    filter_by = dict(_id=ObjectId(str(submission_id)))

    # specify projection
    query_projection = {
        "_id": 1,
        ""
        "description_docs.stages": 1,
        "description_docs.attributes": 1,
        "repository_docs.name": 1,
        "repository_docs.type": 1,
        "repository_docs._id": 1,
    }

    doc = Submission().get_collection_handle().aggregate(
        [
            {"$addFields": {
                "destination_repo_converted": {
                    "$convert": {
                        "input": "$destination_repo",
                        "to": "objectId",
                        "onError": 0
                    }
                },
                "description_token_converted": {
                    "$convert": {
                        "input": "$description_token",
                        "to": "objectId",
                        "onError": 0
                    }
                }
            }
            },
            {
                "$lookup":
                    {
                        "from": "RepositoryCollection",
                        "localField": "destination_repo_converted",
                        "foreignField": "_id",
                        "as": "repository_docs"
                    }
            },
            {
                "$lookup":
                    {
                        "from": "DescriptionCollection",
                        "localField": "description_token_converted",
                        "foreignField": "_id",
                        "as": "description_docs"
                    }
            },
            {
                "$project": query_projection
            },
            {
                "$match": filter_by
            }
        ])

    records = cursor_to_list(doc)

    if not records:
        result['status'] = "error"
        result['message'] = "Couldn't find submission record!"
        return result

    try:
        description_record = records[0]['description_docs'][0]
    except (IndexError, AttributeError) as error:
        result['status'] = "error"
        result['message'] = "Couldn't find related description bundle!"
        return result

    # get description template
    attributes = description_record.get("attributes", dict())
    dt_value = attributes.get("target_repository", dict()).get("deposition_context", str())
    dt_label = [x['label'] for x in d_utils.get_repository_options() if x['value'].lower() == dt_value.lower()]

    if not dt_label:
        result['status'] = "error"
        result['message'] = "Description template not found or is invalid!"
        return result

    result['description_template'] = dt_label[0]

    # get destination repository
    try:
        repository_record = records[0]['repository_docs'][0]
    except (IndexError, AttributeError) as error:
        repository_record = dict()

    result["destination_repository_id"] = str(repository_record.get("_id", str()))

    # get relevant user repositories given metadata template
    user = User.objects.get(pk=user_id)
    user_repo_ids = user.userdetails.repo_submitter
    if user_repo_ids == None:
        user_repo_ids = []
    else:
        user_repo_ids = {ObjectId(x) for x in list(user_repo_ids) if x}

    repository_projection = [('name', 1), ('type', 1), ('templates', 1), ('url', 1)]
    repository_schema = [x for x in Repository().get_schema().get("schema_dict") if
                         x["id"].split(".")[-1] in [y[0] for y in repository_projection]]

    user_repositories = cursor_to_list(Repository().get_collection_handle().find({"$and": [
        {'deleted': d_utils.get_not_deleted_flag()},
        {'templates': {"$in": [dt_value]}},
        {"$or": [
            {"_id": {"$in": list(user_repo_ids)}},
            {"visibility": 'public'}]}]},
        dict(repository_projection)))

    result['relevant_repositories'] = list()

    is_destination_valid = False
    for rec in user_repositories:
        repo_data = dict()
        repo_data["_id"] = str(rec["_id"])
        repo_data["repo_type_unresolved"] = str(rec.get("type", str()))

        if result["destination_repository_id"] == repo_data["_id"]:
            is_destination_valid = True

        for f in repository_schema:
            f_id = f["id"].split(".")[-1]
            repo_data[f_id] = resolve_control_output(rec, f)

        result['relevant_repositories'].append(repo_data)

    if is_destination_valid is False:  # assigned repository no longer valid for this user/submission
        result["destination_repository_id"] = str()

    return result


@register.filter("get_destination_repo")
def get_destination_repo(submission_id=str()):
    """
    function returns destination repository details for a submission
    :param submission_id:
    :return:
    """

    result = list()

    repository_schema = [x for x in Repository().get_schema().get("schema_dict") if x.get("show_in_table", True)]
    repository_projection = [(x["id"].split(".")[-1], 1) for x in repository_schema]

    # specify filtering
    filter_by = dict(_id=ObjectId(str(submission_id)))

    # specify projection
    query_projection = {'repository_docs.' + x[0]: x[1] for x in repository_projection}
    query_projection['_id'] = 1

    doc = Submission().get_collection_handle().aggregate(
        [
            {"$addFields": {
                "destination_repo_converted": {
                    "$convert": {
                        "input": "$destination_repo",
                        "to": "objectId",
                        "onError": 0
                    }
                }
            }
            },
            {
                "$lookup":
                    {
                        "from": "RepositoryCollection",
                        "localField": "destination_repo_converted",
                        "foreignField": "_id",
                        "as": "repository_docs"
                    }
            },
            {
                "$project": query_projection
            },
            {
                "$match": filter_by
            }
        ])

    records = cursor_to_list(doc)

    if not records:
        return result

    try:
        repository_record = records[0]['repository_docs'][0]
    except (IndexError, AttributeError) as error:
        return result
    else:
        for f in repository_schema:
            result.append(dict(label=f["label"], value=resolve_control_output(repository_record, f)))

    return result


@register.filter("generate_submission_datafiles_data")
def generate_submission_datafiles_data(submission_id=str()):
    """
    function returns submission datafiles
    :param submission_id:
    :return:
    """

    columns = list()
    data_set = list()

    columns.append(dict(className='summary-details-control detail-hover-message', orderable=False, data=None,
                        title='', defaultContent='', width="5%"))
    columns.append(dict(data="record_id", visible=False))
    columns.append(dict(data="name", title="Name"))

    try:
        submission_record = Submission().get_record(submission_id)
    except:
        return dict(dataSet=data_set,
                    columns=columns
                    )

    submission_record = Submission().get_record(submission_id)
    bundle = submission_record.get("bundle", list())
    datafile_object_list = [ObjectId(datafile_id) for datafile_id in bundle]

    projection = dict(name=1)
    filter_by = dict()
    filter_by["_id"] = {'$in': datafile_object_list}

    records = DataFile().get_all_records_columns(sort_by='created_on', sort_direction=1, projection=projection,
                                                 filter_by=filter_by)

    if len(records):
        df = pd.DataFrame(records)
        df['s_n'] = df.index

        df['record_id'] = df._id.astype(str)
        df["DT_RowId"] = df.record_id
        df.DT_RowId = 'row_' + df.DT_RowId
        df = df.drop('_id', axis='columns')

        data_set = df.to_dict('records')

    return dict(dataSet=data_set,
                columns=columns
                )


@register.filter("generate_submission_accessions_data")
def generate_submission_accessions_data(submission_id=str()):
    """
    method presents accession data in a tabular display friendly way
    great care should be taken here to manipulate accessions from different repositories,
    as they might be stored differently
    :param submission_id:
    :return:
    """

    columns = list()
    data_set = list()

    try:
        repository = Submission().get_repository_type(submission_id=submission_id)
    except Exception as error:
        return dict(dataSet=data_set,
                    columns=columns,
                    message="Could not retrieve repository type"
                    )

    try:
        submission_record = Submission().get_collection_handle().find_one({'_id': ObjectId(submission_id)},
                                                                          {"accessions": 1})
    except Exception as error:
        return dict(dataSet=data_set,
                    columns=columns,
                    message="Could not retrieve submission record"
                    )

    accessions = submission_record.get("accessions", dict())

    if accessions:
        # -----------COLLATE ACCESSIONS FOR ENA SEQUENCE READS----------
        if repository == "ena":
            columns = [{"title": "Accession"}, {"title": "Alias"}, {"title": "Comment"}, {"title": "Type"}]

            for key, value in accessions.items():
                if isinstance(value, dict):  # single accession instance expected
                    data_set.append([value["accession"], value["alias"], str(), key])
                elif isinstance(value, list):  # multiple accession instances expected
                    for v in value:
                        if key == "sample":
                            data_set.append([v["sample_accession"], v["sample_alias"], v["biosample_accession"], key])
                        else:
                            data_set.append([v["accession"], v["alias"], str(), key])

        elif repository == "ena-ant":
            # -----------COLLATE ACCESSIONS FOR ENA ANNOTATIONS----------
            columns = [{"title": "Accession"}, {"title": "Alias"}, {"title": "Comment"}, {"title": "Type"}]

            for key, value in accessions.items():
                if isinstance(value, dict):  # single accession instance expected
                    data_set.append([value["accession"], value["alias"], str(), key])
                elif isinstance(value, list):  # multiple accession instances expected
                    for v in value:
                        if key == "sample":
                            try:
                                data_set.append(
                                    [v["sample_accession"], v["sample_alias"], v["biosample_accession"], key])
                            except:
                                pass
                        else:
                            try:
                                data_set.append([v["accession"], v["alias"], str(), key])
                            except:
                                pass

        elif repository == "figshare":
            # -----------COLLATE ACCESSIONS FOR FIGSHARE REPO----------
            columns = [{"title": "Accession"}, {"title": "Alias"}, {"title": "Comment"}, {"title": "Type"}]

            for idx, value in enumerate(accessions):
                data_set.append([value, "Figshare File: " + str(idx + 1), str(), str()])

        elif repository == "dataverse":
            # -----------COLLATE ACCESSIONS FOR DATAVERSE REPO----------
            columns = [{"title": "DOI"}, {"title": "Dataverse"}, {"title": "Dataverse Alias"},
                       {"title": "Dataset Title"}]

            data_set.append(
                [accessions.get("dataset_doi", str()), accessions.get("dataverse_title", str()),
                 accessions.get("dataverse_alias", str()),
                 accessions.get("dataset_title", str())]
            )

        elif repository == "dspace":
            columns = [{"title": "Description"}, {"title": "Format"}, {"title": "Filesize"}, {"title": "Retrieve Link"},
                       {"title": "Metadata Link"}]
            for a in accessions:
                link_ref = a["dspace_instance"] + a["link"]
                meta_link = '<a target="_blank" href="' + a["meta_url"] + '">' + a["meta_url"] + '</a>'
                retrieve_link = '<a href="' + link_ref + '/retrieve">' + link_ref + '</a>'
                data_set.append(
                    [a["description"], a["format"], (hurrysize(a["sizeBytes"])),
                     retrieve_link,
                     meta_link]
                )

        elif repository == "ckan":
            columns = [{"title": "Title"}, {"title": "Metadata Link"}, {"title": "Resource Link"}, {"title": "Name"}]
            retrieve_link = '<a target="_blank" href="' + accessions["url"] + '/dataset/' + accessions[
                "dataset_name"] + '">' + accessions["url"] + '/dataset/' + accessions["dataset_name"] + '</a>'
            meta_link = '<a target="_blank" href="' + accessions["repo_url"] + 'package_show?id=' + accessions[
                'dataset_id'] + '">' + 'Show Metadata' + '</a>'
            data_set.append(
                [accessions["dataset_title"], meta_link, retrieve_link, accessions["dataset_name"]]
            )

    return_dict = dict(dataSet=data_set,
                       columns=columns,
                       repository=repository
                       )

    return return_dict


@register.filter("generate_attributes")
def generate_attributes(component, target_id):
    da_object = DAComponent(component=component)

    if component in da_dict:
        da_object = da_dict[component]()

    # get and filter schema elements based on displayable columns
    schema = [x for x in da_object.get_schema().get("schema_dict") if x.get("show_as_attribute", False)]

    # build db column projection
    projection = [(x["id"].split(".")[-1], 1) for x in schema]

    # account for description metadata in datafiles
    if component == "datafile":
        projection.append(('description', 1))

    filter_by = dict(_id=ObjectId(target_id))
    record = da_object.get_all_records_columns(projection=dict(projection), filter_by=filter_by)

    result = dict()

    if len(record):
        record = record[0]

        if component == "sample":  # filter based on sample type
            sample_types = [s_t['value'] for s_t in d_utils.get_sample_type_options()]
            sample_type = record.get("sample_type", str())
            schema = [x for x in schema if sample_type in x.get("specifications", sample_types)]

        for x in schema:
            x['id'] = x["id"].split(".")[-1]

        if component == "datafile":
            key_split = "___0___"
            attributes = record.get("description", dict()).get("attributes", dict())
            stages = record.get("description", dict()).get("stages", list())

            datafile_attributes = dict()
            datafile_items = list()

            for st in stages:
                for item in st.get("items", list()):
                    if str(item.get("hidden", False)).lower() == "false":
                        atrib_val = attributes.get(st["ref"], dict()).get(item["id"], str())
                        item["id"] = st["ref"] + key_split + item["id"]
                        datafile_attributes[item["id"]] = atrib_val
                        datafile_items.append(item)

            record.update(datafile_attributes)
            schema = schema + datafile_items

        result = resolve_display_data(schema, record)

    return result


def resolve_control_output_apply(data, args):
    if args.get("type", str()) == "array":  # resolve array data types
        resolved_value = list()
        for d in data:
            resolved_value.append(get_resolver(d, args))
    else:  # non-array types
        resolved_value = get_resolver(data, args)

    return resolved_value


def resolve_control_output_description(data, args):
    key_split = "___0___"
    st_key_split = args.id.split(key_split)

    data = data['attributes'][st_key_split[0]][st_key_split[1]]

    if args.get("type", str()) == "array":  # resolve array data types
        resolved_value = list()
        for d in data:
            resolved_value.append(get_resolver(d, args))
    else:  # non-array types
        resolved_value = get_resolver(data, args)

    return resolved_value


def resolve_control_output(data_dict, elem):
    resolved_value = str()

    key_split = elem["id"].split(".")[-1]
    if key_split in data_dict:
        # resolve array data types
        if elem.get("type", str()) == "array":
            resolved_value = list()
            data = data_dict[key_split]
            for d in data:
                resolved_value.append(get_resolver(d, elem))
        else:
            # non-array types
            resolved_value = get_resolver(data_dict[key_split], elem)

    return resolved_value


def get_resolver(data, elem):
    """
    function resolves data for UI display, by mapping control to a resolver function
    :param data:
    :param elem:
    :return:
    """
    if not data:
        return ""
    func_map = dict()
    func_map["copo-characteristics"] = resolve_copo_characteristics_data
    func_map["copo-environmental-characteristics"] = resolve_environmental_characteristics_data
    func_map["copo-phenotypic-characteristics"] = resolve_phenotypic_characteristics_data
    func_map["copo-comment"] = resolve_copo_comment_data
    func_map["copo-multi-select"] = resolve_copo_multi_select_data
    func_map["copo-multi-select2"] = resolve_copo_multi_select_data
    func_map["copo-general-ontoselect"] = resolve_copo_multi_select_data
    func_map["copo-single-select"] = resolve_copo_multi_select_data
    func_map["copo-multi-search"] = resolve_copo_multi_search_data
    func_map["copo-lookup"] = resolve_copo_lookup_data
    func_map["copo-lookup2"] = resolve_copo_lookup2_data
    func_map["select"] = resolve_select_data
    func_map["copo-button-list"] = resolve_select_data
    func_map["ontology term"] = resolve_ontology_term_data
    func_map["copo-select"] = resolve_copo_select_data
    func_map["datetime"] = resolve_datetime_data
    func_map["datafile-description"] = resolve_description_data
    func_map["date-picker"] = resolve_datepicker_data
    func_map["copo-duration"] = resolve_copo_duration_data
    func_map["copo-datafile-id"] = resolve_copo_datafile_id_data

    control = elem.get("control", "text").lower()
    if control in func_map:
        resolved_data = func_map[control](data, elem)
    else:
        resolved_data = resolve_default_data(data)

    return resolved_data


def resolve_display_data(datafile_items, datafile_attributes):
    data = list()
    columns = list()
    key_split = "___0___"
    object_controls = d_utils.get_object_array_schema()

    schema_df = pd.DataFrame(datafile_items)

    for index, row in schema_df.iterrows():
        resolved_data = resolve_control_output(datafile_attributes, dict(row.dropna()))
        label = row["label"]

        if row['control'] in object_controls.keys():
            # get object-type-control schema
            control_df = pd.DataFrame(object_controls[row['control']])
            control_df['id2'] = control_df['id'].apply(lambda x: x.split(".")[-1])

            if resolved_data:
                object_array_keys = [list(x.keys())[0] for x in resolved_data[0]]
                object_array_df = pd.DataFrame([dict(pair for d in k for pair in d.items()) for k in resolved_data])

                for o_indx, o_row in object_array_df.iterrows():
                    # add primary header/value - first element in object_array_keys taken as header, second value
                    # e.g., category, value in material_attribute_value schema
                    # a slightly different implementation will be needed for an object-type-control
                    # that require a different display structure

                    class_name = key_split.join((row.id, str(o_indx), object_array_keys[1]))
                    columns.append(dict(title=label + " [{0}]".format(o_row[object_array_keys[0]]), data=class_name))
                    data.append({class_name: o_row[object_array_keys[1]]})

                    # add other headers/values e.g., unit in material_attribute_value schema
                    for subitem in object_array_keys[2:]:
                        class_name = key_split.join((row.id, str(o_indx), subitem))
                        columns.append(dict(
                            title=control_df[control_df.id2.str.lower() == subitem.lower()].iloc[0].label,
                            data=class_name))
                        data.append({class_name: o_row[subitem]})
        else:
            # account for array types
            if row["type"] == "array":
                for tt_indx, tt_val in enumerate(resolved_data):
                    shown_keys = (row["id"], str(tt_indx))
                    class_name = key_split.join(shown_keys)
                    columns.append(
                        dict(title=label + " [{0}]".format(str(tt_indx + 1)), data=class_name))

                    if isinstance(tt_val, list):
                        tt_val = ', '.join(tt_val)

                    data_attribute = dict()
                    data_attribute[class_name] = tt_val
                    data.append(data_attribute)
            else:
                shown_keys = row["id"]
                class_name = shown_keys
                columns.append(dict(title=label, data=class_name))
                val = resolved_data

                if isinstance(val, list):
                    val = ', '.join(val)

                data_attribute = dict()
                data_attribute[class_name] = val
                data.append(data_attribute)

    data_record = dict(pair for d in data for pair in d.items())

    # for k in columns:
    #     k["data"] = data_record[k["data"]]

    return dict(columns=columns, data_set=data_record)


def resolve_description_data(data, elem):
    attributes = data.get("attributes", dict())
    stages = data.get("stages", list())

    datafile_attributes = dict()
    datafile_items = list()
    key_split = "___0___"

    for st in stages:
        attributes[st["ref"]] = attributes.get(st["ref"], dict())
        for item in st.get("items", list()):
            if str(item.get("hidden", False)).lower() == "false":
                atrib_val = attributes.get(st["ref"], dict()).get(item["id"], str())
                item["id"] = st["ref"] + key_split + item["id"]
                datafile_attributes[item["id"]] = atrib_val
                datafile_items.append(item)

    return resolve_display_data(datafile_items, datafile_attributes)


def resolve_copo_characteristics_data(data, elem):
    schema = d_utils.get_copo_schema("material_attribute_value")

    resolved_data = list()

    for f in schema:
        if f.get("show_in_table", True):
            a = dict()
            if f["id"].split(".")[-1] in data:
                a[f["id"].split(".")[-1]] = resolve_ontology_term_data(data[f["id"].split(".")[-1]], elem)
                resolved_data.append(a)

    return resolved_data


def resolve_environmental_characteristics_data(data, elem):
    schema = d_utils.get_copo_schema("environment_variables")

    resolved_data = list()

    for f in schema:
        if f.get("show_in_table", True):
            a = dict()
            if f["id"].split(".")[-1] in data:
                a[f["id"].split(".")[-1]] = resolve_ontology_term_data(data[f["id"].split(".")[-1]], elem)
                resolved_data.append(a)

    return resolved_data  # turn this casting off after merge


def resolve_phenotypic_characteristics_data(data, elem):
    schema = d_utils.get_copo_schema("phenotypic_variables")

    resolved_data = list()

    for f in schema:
        if f.get("show_in_table", True):
            a = dict()
            if f["id"].split(".")[-1] in data:
                a[f["id"].split(".")[-1]] = resolve_ontology_term_data(data[f["id"].split(".")[-1]], elem)
                resolved_data.append(a)

    return resolved_data  # turn this casting off after merge


def resolve_copo_comment_data(data, elem):
    schema = d_utils.get_copo_schema("comment")

    resolved_data = list()

    for f in schema:
        if f.get("show_in_table", True):
            a = dict()
            if f["id"].split(".")[-1] in data:
                a[f["id"].split(".")[-1]] = data[f["id"].split(".")[-1]]
                resolved_data.append(a)

    if not resolved_data:
        resolved_data = str()
    elif len(resolved_data) == 1:
        resolved_data = resolved_data[0]
    return resolved_data


def resolve_copo_multi_select_data(data, elem):
    resolved_value = list()

    option_values = None

    if "option_values" in elem:
        option_values = get_control_options(elem)

    if data:
        if isinstance(data, str):
            data = data.split(",")

        data = [str(x) for x in data]

        if option_values:
            if isinstance(option_values[0], str):
                option_values = [dict(value=x, label=x) for x in option_values]

            o_df = pd.DataFrame(option_values)
            o_df.value = o_df.value.astype(str)
            resolved_value = list(o_df[o_df.value.isin(data)].label)

    return resolved_value


def resolve_copo_multi_search_data(data, elem):
    resolved_value = list()

    option_values = None

    if isinstance(data, list):
        data = ','.join(map(str, data))

    if "option_values" in elem:
        option_values = get_control_options(elem)

    if option_values and data:
        for d_v in data.split(","):
            resolved_value = resolved_value + [x[option_values["label_field"]] for x in option_values["options"] if
                                               d_v == x[option_values["value_field"]]]

    return resolved_value


def resolve_copo_lookup_data(data, elem):
    resolved_value = str()

    elem['data'] = data
    option_values = get_control_options(elem)

    if option_values:
        resolved_value = option_values[0]['label']

    return resolved_value


def resolve_copo_lookup2_data(data, elem):
    resolved_value = str()

    elem['data'] = data
    option_values = get_control_options(elem)

    if option_values:
        resolved_value = [x[
                              'label'] + "<span class='copo-embedded' style='margin-left: 5px;' data-source='{" \
                                         "data_source}' data-accession='{data_accession}' >" \
                                         "<i title='click for related information' style='cursor: pointer;' class='fa " \
                                         "" \
                                         "fa-info-circle'></i></span>".format(
            data_source=elem['data_source'], data_accession=x['accession']) for x in option_values]

    return resolved_value


def resolve_select_data(data, elem):
    option_values = None
    resolved_value = str()

    if "option_values" in elem:
        option_values = get_control_options(elem)

    if option_values and data:
        for option in option_values:
            if isinstance(option, str):
                sv = option
                sl = option
            elif isinstance(option, dict):
                sv = option['value']
                sl = option['label']
            if str(sv) == str(data):
                resolved_value = sl

    return resolved_value


def resolve_ontology_term_data(data, elem):
    schema = DataSchemas("COPO").get_ui_template().get("copo").get("ontology_annotation").get("fields")

    resolved_data = list()

    for f in schema:
        if f.get("show_in_table", True):
            if f["id"].split(".")[-1] in data:
                resolved_data.append(data[f["id"].split(".")[-1]])

    if not resolved_data:
        resolved_data = str()
    elif len(resolved_data) == 1:
        resolved_data = resolved_data[0]
    return resolved_data


def resolve_copo_select_data(data, elem):
    return data


def resolve_datetime_data(data, elem):
    resolved_value = str()

    if data:
        if data.date:
            try:
                resolved_value = time.strftime('%a, %d %b %Y %H:%M', data.timetuple())
            except ValueError:
                pass
    return resolved_value


def resolve_datepicker_data(data, elem):
    resolved_value = str()
    if data:
        resolved_value = data
    return resolved_value


def resolve_copo_duration_data(data, elem):
    schema = d_utils.get_copo_schema("duration")

    resolved_data = list()

    for f in schema:
        if f.get("show_in_table", True):
            # a = dict()
            if f["id"].split(".")[-1] in data:
                # a[f["label"]] = data[f["id"].split(".")[-1]]
                resolved_data.append(f["label"] + ": " + data[f["id"].split(".")[-1]])

    return resolved_data


def resolve_copo_datafile_id_data(data, elem):
    resolved_data = dict()

    da_object = DAComponent(component="datafile")

    if data:
        datafile = da_object.get_record(data)
        resolved_data["recordLabel"] = datafile.get("name", str())
        resolved_data["recordID"] = data

    return resolved_data


def resolve_default_data(data):
    return data


@register.filter("generate_copo_profiles_counts")
def generate_copo_profiles_counts(profiles=list()):
    data_set = list()

    for pr in profiles:
        data_set.append(dict(profile_id=str(pr["_id"]), counts=ProfileInfo(str(pr["_id"])).get_counts()))
    return data_set


@register.filter("lookup_info")
def lookup_info(val):
    if val in lkup.UI_INFO.keys():
        return lkup.UI_INFO[val]
    return ""


def get_fields_list(field_id):
    key_split = field_id.split(".")

    new_dict = DataSchemas(field_id.split(".")[0].upper()).get_ui_template()

    for kp in key_split[:-1]:
        if kp in new_dict:
            new_dict = new_dict[kp]

    return new_dict["fields"]


@register.filter("id_to_class")
def id_to_class(val):
    return val.replace(".", "_")


def generate_figshare_oauth_html():
    elem = {'label': 'Figshare', 'control': 'oauth_required'}
    do_tag(elem)


def get_ols_url():
    req = data_utils.get_current_request()
    protocol = req.META['wsgi.url_scheme']
    r = req.build_absolute_uri()
    ols_url = protocol + '://' + data_utils.get_current_request().META['HTTP_HOST'] + reverse(
        'copo:ajax_search_ontology')

    return ols_url


def do_tag(the_elem, default_value=None):
    elem_id = the_elem["id"]
    try:
        copo_module = elem_id.split('.')[1]
        field_type = elem_id.rsplit('.', 1)[1]
    except:
        pass
    elem_label = the_elem["label"]
    elem_help_tip = the_elem["help_tip"]
    div_id = uuid4()

    # try and get elem_class - this can be used as a hook for the form item in javascript
    try:
        elem_class = the_elem["additional_class"]
    except:
        elem_class = ''

    # get url of ols lookup for ontology fields
    ols_url = get_ols_url()

    if default_value is None:
        elem_value = the_elem["default_value"]
    else:
        elem_value = default_value

    elem_control = the_elem["control"].lower()
    option_values = ""
    html_tag = ""

    html_all_tags = HTML_TAGS

    if (elem_control == "select" or elem_control == "copo-multi-select") and the_elem["option_values"]:
        for ov in the_elem["option_values"]:
            if isinstance(ov, str):
                sv = ov
                sl = ov
            elif isinstance(ov, dict):
                sv = ov['value']
                sl = ov['label']

            selected = ""
            if elem_value:
                if elem_control == "select" and elem_value == sv:
                    selected = "selected"
                elif elem_control == "copo-multi-select" and sv in elem_value.split(","):
                    selected = "selected"
            option_values += "<option value='{sv!s}' {selected!s}>{sl!s}</option>".format(**locals())

    if elem_control == "copo-multi-search" and the_elem["elem_json"]:
        elem_json = json.dumps(the_elem["elem_json"])

    if the_elem["hidden"] == "true":
        html_tag = html_all_tags["hidden"].format(**locals())
    else:
        if elem_control in [x.lower() for x in list(html_all_tags.keys())]:
            if elem_control == "ontology term" or elem_control == "characteristic/factor":
                v = ''
                termAccession = ''
                termSource = ''
                annotationValue = ''
                value = ''
                unit = ''
                if isinstance(elem_value, list):
                    elem_value = elem_value[0]

                if isinstance(elem_value, dict):
                    if "key" in elem_value:
                        annotationValue = elem_value["key"]
                    if "termSource" in elem_value:
                        termSource = elem_value["termSource"]
                    if "termAccession" in elem_value:
                        termAccession = elem_value["termAccession"]
                    if "value" in elem_value:
                        value = elem_value["value"]
                    if "unit" in elem_value:
                        unit = elem_value["unit"]
                    if "annotationValue" in elem_value:
                        annotationValue = elem_value["annotationValue"]
                elif isinstance(elem_value, str):
                    annotationValue = elem_value

            html_tag = html_all_tags[elem_control].format(**locals())

    return html_tag


'''
@register.filter("partial_submission_bannerpartial_submission_banner")
def do_partial_submission_banner(val):
    html = ''
    if val is None:
        pass
    else:
        html = '<div class="page-header warning-banner">' \
               '<div class="icon">' \
               '<i class="fa fa-cloud-upload fa-4x"></i>' \
               '</div>' \
               '<div class="resume-text">' \
               '<h3 class="h3">Resume Submission?</h3>' \
               'It looks like you were in the middle of a submission. <a href="' + val[0][
                   'url'] + '"> Click here to resume</a>' \
                            '</div>' \
                            '</div>'
    return format_html(html)
'''

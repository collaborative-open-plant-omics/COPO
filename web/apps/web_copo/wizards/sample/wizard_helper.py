__author__ = 'etuka'

import os
import re
import json
import numpy as np
import pandas as pd
from bson import ObjectId
from django.conf import settings
import urllib.request as urllib2

from dal.copo_da import Sample, Description
import web.apps.web_copo.lookup.lookup as lkup
from converters.ena.copo_isa_ena import ISAHelpers
import web.apps.web_copo.templatetags.html_tags as htags
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from web.apps.web_copo.lookup.copo_enums import Loglvl, Logtype
from web.apps.web_copo.schemas.utils.data_utils import DecoupleFormSubmission

lg = settings.LOGGER


class WizardHelper:
    def __init__(self, description_token, profile_id):
        self.description_token = description_token
        self.profile_id = self.set_profile_id(profile_id)
        self.schema = Sample().get_schema().get("schema_dict")
        self.wiz_message = d_utils.json_to_pytype(lkup.MESSAGES_LKUPS["wizards_messages"])["properties"]

        self.key_split = "___0___"
        self.object_key = "sample_" + self.description_token

    def initiate_description(self):
        """
        function initates a new description or reinstantiates an existing description
        :return:
        """

        initiate_result = dict(status="success", message="")
        initiate_result['wiz_message'] = self.wiz_message

        if self.description_token:  # this is a call to reload an existing description; validate token

            # start by getting the description record
            description = Description().GET(self.description_token)

            if not description:
                # description record doesn't exist; flag error
                initiate_result['status'] = "error"
                initiate_result['message'] = self.wiz_message["invalid_token_message"]
                del initiate_result['wiz_message']
            else:
                # reset timestamp, which will also reset the 'grace period' for the description
                Description().edit_description(self.description_token, dict(created_on=d_utils.get_datetime()))
                initiate_result['description_token'] = self.description_token

        else:  # this is a call to instantiate a new description; create description record and issue token
            # get start stages
            wizard_stages = d_utils.json_to_pytype(lkup.WIZARD_FILES["sample_start"])['properties']
            self.resolve_select_data(wizard_stages)

            # create description record
            description_token = str(
                Description().create_description(stages=wizard_stages, attributes=dict(), profile_id=self.profile_id,
                                                 component='sample', meta=dict())['_id'])

            initiate_result['description_token'] = description_token

        return initiate_result

    def resolve_select_data(self, stages):
        """
        function resolves data source for select-type controls
        :param stages:
        :return:
        """

        for stage in stages:
            for st in stage.get("items", list()):
                if st["control"] == "copo-lookup":
                    continue
                if st.get("option_values", False) is False:
                    st.pop('option_values', None)
                    continue

                st["option_values"] = htags.get_control_options(st)

        return True

    def verify_lookup_items(self, stage):
        """
        function verifies if stage items have lookups to be resolved
        :param stage:
        :return:
        """

        for item in stage.get("items", list()):
            if item.get("control", "text") in ["copo-lookup", "copo-lookup2"]:
                item['data'] = stage['data'].get(item["id"].split(".")[-1], str())
                item["option_values"] = htags.get_control_options(item)

        return True

    def set_profile_id(self, profile_id):
        p_id = profile_id
        if not p_id and self.description_token:
            description = Description().GET(self.description_token)
            p_id = description.get("profile_id", str())

        return p_id

    def resolve_next_stage(self, auto_fields):
        """
        given data from a stage, function tries to resolve the next stage to be displayed to the user by the wizard
        :param auto_fields:
        :return:
        """

        next_stage_dict = dict(abort=False)
        current_stage = auto_fields.get("current_stage", str())

        if not current_stage:
            # there's no way of telling what next stage is requested; send signal to abort the wizard
            next_stage_dict["abort"] = True
            return next_stage_dict

        # get the description record
        description = Description().GET(self.description_token)

        if not description:
            # invalid description; send signal to abort the wizard
            next_stage_dict["abort"] = True
            return next_stage_dict

        stages = description["stages"]
        attributes = description["attributes"]

        # resolve next stage
        next_stage_index = [indx for indx, stage in enumerate(stages) if stage['ref'] == current_stage]

        if not next_stage_index and not current_stage == 'intro':  # invalid current stage; send abort signal
            next_stage_dict["abort"] = True
            return next_stage_dict

        next_stage_index = next_stage_index[0] + 1 if len(next_stage_index) else 0

        # save in-coming stage data, check for changes, re-validate wizard, serve next stage

        previous_data = dict()
        if next_stage_index > 0:  # we don't have to save 'intro' stage attributes;
            previous_data = attributes.get(current_stage, dict())
            current_data = DecoupleFormSubmission(auto_fields,
                                                  d_utils.json_to_object(
                                                      stages[next_stage_index - 1]).items).get_schema_fields_updated()
            # save current stage data
            attributes[current_stage] = current_data

            # save attributes
            Description().edit_description(self.description_token, dict(attributes=attributes))

        # get next stage
        next_stage_dict['stage'] = self.serve_stage(next_stage_index)

        # refresh values from db after serve stage as this has the potential of modifying things
        description = Description().GET(self.description_token)
        attributes = description["attributes"]
        meta = description.get("meta", dict())

        if not next_stage_dict['stage']:
            # no stage to retrieve, this should signal end
            return next_stage_dict

        if next_stage_index > 0 and previous_data and not (previous_data == current_data):
            # stage data has changed, refresh wizard
            next_stage_dict['refresh_wizard'] = True

            # remove any stored object associated with this description
            if os.path.exists(self.get_object_file_path()):
                os.remove(self.get_object_file_path())

            # update meta
            meta["generated_columns"] = list()

        # build data dictionary for stage
        if next_stage_dict['stage']['ref'] in attributes and "data" not in next_stage_dict['stage']:
            next_stage_dict['stage']['data'] = attributes[next_stage_dict['stage']['ref']]
        # save last rendered stage
        if next_stage_dict['stage']['ref']:
            meta["last_rendered_stage"] = next_stage_dict['stage']['ref']

        Description().edit_description(self.description_token, dict(meta=meta))

        # check and resolve value for lookup fields
        if "data" in next_stage_dict['stage']:
            self.verify_lookup_items(next_stage_dict['stage'])

        return next_stage_dict

    def serve_stage(self, next_stage_index):
        """
        function determines how a given stage should be served
        :param stage:
        :return:
        """

        # start by getting the description record
        description = Description().GET(self.description_token)
        stages = description["stages"]

        stage = dict()

        if next_stage_index < len(stages):
            stage = stages[next_stage_index]

        while True:
            if "callback" in stage:
                # resolve stage from callback function
                try:
                    stage = getattr(WizardHelper, stage["callback"])(self, next_stage_index)
                except:
                    stage = dict()

            # we expect a stage that cannot be directly rendered to return a False, thus prompting
            # progression to the next
            # stage in the sequence of stages (see below). Such non-renderable stages
            # may just be processes or stubs meant for resolving other dynamically culled stages
            if isinstance(stage, dict):
                break

            # refresh stages and index of the next stage - why do this? callbacks can potentially modify things
            description = Description().GET(self.description_token)
            stages = description["stages"]

            next_stage_index = next_stage_index + 1  # progress to next index in this very quest for a valid next stage

            if next_stage_index < len(stages):
                stage = stages[next_stage_index]
            else:
                stage = dict()
                break

        return stage

    def display_sample_clone(self, next_stage_index):
        """
        stage callback function: determines if sample clone stage should be displayed
        :param stage:
        :return:
        """

        stage = dict()

        description = Description().GET(self.description_token)
        stages = description["stages"]
        attributes = description["attributes"]

        if next_stage_index < len(stages):
            stage = stages[next_stage_index]

        user_choice = attributes.get("sample_clone", dict()).get("sample_clone", str())

        if not stage["ref"] == user_choice:
            return False

        return stage

    def sample_clone_options(self, next_stage_index):
        """
        stage callback function: determines if local sample clone option should be displayed given presence of samples
        :param next_stage_index:
        :return:
        """

        description = Description().GET(self.description_token)
        stages = description["stages"]

        stage = dict()

        if next_stage_index < len(stages):
            stage = stages[next_stage_index]

            if len(d_utils.get_samples_json()["options"]) == 0:
                # remove option for local sample clone

                for item in stage["items"]:
                    if item["id"] == "sample_clone":
                        indx = [indx for indx, x in enumerate(item["option_values"]) if x["value"] == "clone_existing"]
                        if indx:
                            del item["option_values"][indx[0]]

        return stage

    def display_sample_naming(self, next_stage_index):
        """
        stage callback function: determines sample naming method to display based on user choice
        :param next_stage_index:
        :return:
        """

        stage = dict()

        description = Description().GET(self.description_token)
        stages = description["stages"]
        attributes = description["attributes"]

        if next_stage_index < len(stages):
            stage = stages[next_stage_index]

        user_choice = attributes.get("sample_naming_method", dict()).get("sample_naming_method", str())

        if not stage["ref"] == user_choice:
            return False

        # check for number of samples dependency, re-validate if necessary

        number_of_samples = attributes.get("number_of_samples", dict()).get("number_of_samples", 1)

        meta = description.get("meta", dict())
        number_of_samples_old = meta.get(stage["ref"] + "_number_of_samples", None)

        if number_of_samples_old and not number_of_samples == number_of_samples_old:
            status = self.revalidate_sample_name(user_choice)  # revalidate
            if stage["ref"] in attributes and status == 'error':
                data = attributes[stage["ref"]]

                data[user_choice + "_hidden"] = str()
                stage["data"] = DecoupleFormSubmission(data,
                                                       d_utils.json_to_object(stage).items).get_schema_fields_updated()

        return stage

    def get_sample_attributes(self, next_stage_index):
        """
        stage callback function: identifies sample attribute to present to user, mostly based on sample type choice
        :param next_stage_index:
        :return:
        """
        stage = dict()

        sample_types = list()

        for s_t in d_utils.get_sample_type_options():
            sample_types.append(s_t["value"])

        description = Description().GET(self.description_token)
        stages = description["stages"]
        attributes = description["attributes"]
        meta = description["meta"]

        # get sample type - user choice
        user_choice = attributes.get("sample_type", dict()).get("sample_type", str())

        if next_stage_index < len(stages):
            stage = stages[next_stage_index]

            # compose stage items if first time here
            stage_items = list()

            for f in self.schema:
                # get relevant attributes based on sample type
                if f.get("show_in_form", True) and user_choice in f.get("specifications", sample_types):
                    # if required, resolve data source for select-type controls,
                    # i.e., if a callback is defined on the 'option_values' field
                    if "option_values" in f:
                        f["option_values"] = htags.get_control_options(f)

                    # get short-form id
                    f["id"] = f["id"].split(".")[-1]

                    # don't need to include sample name
                    if f["id"] == "name":
                        continue

                    stage_items.append(f)

            stage["items"] = stage_items

            # update description
            stages[next_stage_index] = stage

            Description().edit_description(self.description_token, dict(stages=stages))

            # build data dictionary depending on clone option
            clone_option = attributes.get("sample_clone", dict()).get("sample_clone", str())

            # this stage is dependent on sample clone; if this has changed, re-validate data...
            clone_option_old = meta.get(stage["ref"] + "_sample_clone", None)

            stage['data'] = attributes.get(stage["ref"], dict())

            if not clone_option == "no":
                if clone_option_old and not clone_option_old == clone_option:
                    # clone option changed, re-validate attributes:
                    clone_value = attributes.get(clone_option, dict())
                    stage['data'] = self.resolve_clone_data(clone_value, clone_option)
                else:
                    # clone option not changed, but has value changed
                    clone_value = attributes.get(clone_option, dict())
                    clone_value_old = attributes.get(clone_option + "_old", None)
                    if (clone_value_old and not clone_value_old == clone_value) or not attributes.get(stage["ref"],
                                                                                                      dict()):
                        # clone value changed or first time
                        clone_value = attributes.get(clone_option, dict())
                        stage['data'] = self.resolve_clone_data(clone_value, clone_option)

        # store dependency
        meta[stage["ref"] + "_sample_clone"] = clone_option
        Description().edit_description(self.description_token, dict(meta=meta))

        # select rendering routine given sample type
        if user_choice == 'dtol':
            stage['renderer'] = 'generate_dtol_stage'
            stage['field_groupings'] = d_utils.json_to_pytype(lkup.WIZARD_FILES["dtol_mappings"])

        return stage

    def perform_sample_generation(self, next_stage_index):
        """
        stage callback function: to initiate display of requested number of samples and attributes
        :param next_stage_index:
        :return:
        """

        stage = dict()

        description = Description().GET(self.description_token)
        stages = description["stages"]

        if next_stage_index < len(stages):
            stage = stages[next_stage_index]

        return stage

    def generate_discrete_attributes(self):
        """
        function generate discrete attributes for individual sample editing
        :return:
        """

        # if there's stored object, use that rather than generating dataset from scratch
        object_path = self.get_object_path()
        if not os.path.exists(object_path):
            os.makedirs(object_path)

        try:
            with pd.HDFStore(self.get_object_file_path()) as store:
                if self.object_key in store:
                    stored_data_set = store[self.object_key].to_dict('records')
        except Exception as e:
            print('Data Access Error: ' + str(e))
            stored_data_set = list()

        # check if samples have previously been updated from defaults and if so, add these updates to stored_data_set
        getIds = list()
        for sample in stored_data_set:
            getIds.append(ObjectId(sample["DT_RowId"].split('row_')[1]))

        mongo_samples = list(Sample().get_collection_handle().find({"_id": {"$in": getIds}}))
        for idx, sample in enumerate(stored_data_set):
            for key in sample.keys():
                if "characteristics" in key or "factorValues" in key:
                    chunks = key.split("___")
                    index = chunks[2]
                    fac_char = chunks[0]
                    val_unit = chunks[-1]
                    value = sample[key]
                    orig = mongo_samples[idx][fac_char][int(index)][val_unit]["annotationValue"]
                    if value != orig:
                        sample[key] = orig

        description = Description().GET(self.description_token)
        stored_columns = description["meta"].get("generated_columns", list())

        if stored_columns and stored_data_set:
            return dict(columns=stored_columns, rows=stored_data_set)

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        # data and columns lists
        data = list()

        columns = [dict(title=' ', name='s_n', data="s_n", className='select-checkbox'),
                   dict(title='Name', name='name', data="name")]

        attributes = description["attributes"]
        meta = description["meta"]

        # get stored sample attributes
        sample_attributes = attributes.get("sample_attributes", dict())

        # get stage items list and remove hidden fields
        items = [x["items"] for x in description["stages"] if x["ref"] == "sample_attributes"]
        items = [x for x in items[0] if str(x.get("hidden", False)).lower() == "false"]

        schema_df = pd.DataFrame(items)

        for index, row in schema_df.iterrows():

            resolved_data = htags.resolve_control_output(sample_attributes, dict(row.dropna()))
            label = row["label"]

            if row['control'] in object_controls.keys():
                # get object-type-control schema
                # get the key field and value field
                control_df = pd.DataFrame(object_controls[row['control']])
                control_df['id2'] = control_df['id'].apply(lambda x: x.split(".")[-1])

                if resolved_data:
                    object_array_keys = [list(x.keys())[0] for x in resolved_data[0]]
                    object_array_df = pd.DataFrame([dict(pair for d in k for pair in d.items()) for k in resolved_data])

                    for o_indx, o_row in object_array_df.iterrows():
                        # add primary header/value - first element in object_array_keys taken as header, second value
                        # e.g., category, value in material_attribute_value schema
                        # a separate block will be needed for object type control that do not conform to this display

                        row_id_split = row["id"].split(".")[-1]
                        class_name = self.key_split.join((row_id_split, str(o_indx), object_array_keys[1]))
                        columns.append(dict(title=label + "[{0}]".format(o_row[object_array_keys[0]]), data=class_name))
                        data.append({class_name: o_row[object_array_keys[1]]})

                        # add other headers/values e.g., unit in material_attribute_value schema
                        for subitem in object_array_keys[2:]:
                            class_name = self.key_split.join((row_id_split, str(o_indx), subitem))
                            columns.append(dict(
                                title=control_df[control_df.id2.str.lower() == subitem.lower()].iloc[0].label,
                                data=class_name))
                            data.append({class_name: o_row[subitem]})
            elif row["type"] == "array":
                for tt_indx, tt_val in enumerate(resolved_data):
                    shown_keys = (row["id"].split(".")[-1], str(tt_indx))
                    class_name = self.key_split.join(shown_keys)
                    columns.append(
                        dict(title=label + "[{0}]".format(str(tt_indx + 1)), data=class_name))

                    if isinstance(tt_val, list):
                        tt_val = ', '.join(tt_val)

                    data.append({class_name: tt_val})
            else:
                shown_keys = row["id"].split(".")[-1]
                class_name = shown_keys
                columns.append(dict(title=label, data=class_name))
                val = resolved_data

                if isinstance(val, list):
                    val = ', '.join(val)

                data.append({class_name: val})

        # generate sample names
        sample_names = meta["generated_names"]
        name_series = pd.Series(sample_names.split(","))

        number_of_samples = attributes.get("number_of_samples", dict()).get("number_of_samples", 1)

        # save control information
        auto_fields = dict()
        auto_fields[Sample().get_qualified_field("name")] = str()
        auto_fields[Sample().get_qualified_field("sample_type")] = attributes.get("sample_type", dict()).get(
            "sample_type", str())

        fields = DecoupleFormSubmission(auto_fields, Sample().get_schema().get("schema")).get_schema_fields_updated()

        for k, v in sample_attributes.items():
            fields[k] = v

        fields["target_id"] = str()
        fields["validate_only"] = True  # prevents saving of record

        record = Sample(profile_id=self.profile_id).save_record(dict(), **fields)

        # save initial attributes to db

        # remove previous entries associated with this token
        Sample().get_collection_handle().delete_many(
            {"description_token": self.description_token, "deleted": d_utils.get_deleted_flag()})

        record['deleted'] = d_utils.get_deleted_flag()
        record['description_token'] = self.description_token

        # build db dataset
        samples_df = pd.DataFrame(name_series)
        samples_df.columns = ['name']

        new_samples_list = samples_df.to_dict('records')
        result = Sample().get_collection_handle().insert_many(new_samples_list)
        object_ids = result.inserted_ids
        record.pop('name', None)

        Sample().get_collection_handle().update_many(
            {"_id": {"$in": object_ids}},
            {'$set': record})

        # build display dataset
        samples_df["DT_RowId"] = object_ids
        samples_df.DT_RowId = 'row_' + samples_df.DT_RowId.astype(str)

        data_record = dict(pair for d in data for pair in d.items())
        for k, v in data_record.items():
            samples_df[k] = v

        samples_df.insert(loc=0, column='s_n', value=[''] * int(number_of_samples))  # - for sorting

        data_set = samples_df.to_dict('records')

        # save generated dataset
        samples_df.index = samples_df.DT_RowId
        try:
            with pd.HDFStore(self.get_object_file_path()) as store:
                store[self.object_key] = samples_df
        except Exception as e:
            lg.log('Data Access Error: ' + str(e), level=Loglvl.ERROR, type=Logtype.FILE)

        # save generated columns
        meta = description.get("meta", dict())
        meta["generated_columns"] = columns

        # save meta
        Description().edit_description(self.description_token, dict(meta=meta))

        return dict(columns=columns, rows=data_set)

    def revalidate_sample_name(self, naming_method):
        """
        function checks that supplied names are still valid - needed when a any stage change is encountered
        :param naming_method:
        :return:
        """

        description = Description().GET(self.description_token)
        attributes = description["attributes"]

        name_value = attributes.get(naming_method, dict()).get(naming_method, str())

        if naming_method == "bundle_name":
            return self.validate_bundle_name(name_value)
        elif naming_method == "provided_names":
            return self.validate_sample_names(name_value)["status"]

        return

    def resolve_clone_data(self, clone_value, clone_option):
        """
        function resolves stage data based on clone option
        :param clone_value:
        :param clone_option:
        :return:
        """

        data = dict()

        if clone_option == "clone_existing":
            data = Sample().get_record(clone_value["clone_existing"])
            del data["_id"]
        elif clone_option == "clone_biosample":
            data = json.loads(clone_value["clone_resolved_hidden"])

        return data

    def resolve_sample_object(self, resolved_object):
        """
        function normalises a resolved sample object to extract relevant sample attributes
        :param resolved_object: sample object to be normalised
        :return: the normalised object, which should conform to the sample schema
        """

        sample_object = dict(organism=dict(), characteristics=list(), comments=list())

        ch = resolved_object.get("characteristics", dict())

        for key in list(ch.keys()):
            key_refined = re.findall('[a-zA-Z][^A-Z]*', key)
            key_refined = [i.lower() for i in key_refined]
            key_refined = ' '.join([str(i.lower()) for i in key_refined])
            key_refined = key_refined.strip()

            # each attribute can be divided into either of two buckets:
            # characteristics; if it is ontologised, comment; if free text.

            if isinstance(ch[key], list):  # attribute values are observed to be wrapped up as lists
                for value in ch[key]:
                    if isinstance(value, dict):
                        if all(x in list(value.keys()) for x in ['ontologyTerms', 'text']):
                            if isinstance(value['text'], str):
                                material_value_dict = dict()

                                # category
                                category_dict = dict(annotationValue=key_refined)

                                # purify category schema
                                ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                                for onto in ontology_schema:
                                    ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, onto,
                                                                                      "ontology_annotation",
                                                                                      category_dict)

                                material_value_dict['category'] = ontology_schema

                                # value
                                value_dict = dict(annotationValue=value['text'])

                                ontology_term = value['ontologyTerms'][0]  # interested only in the first entry,
                                # ...we do recognise that there might be more than one entries here,
                                # but selecting one should suffice

                                value_dict['termAccession'] = ontology_term
                                term_source = ''
                                c_split = (ontology_term.split("/"))[-1]
                                if c_split != ontology_term and c_split.split("_")[0] != c_split:
                                    term_source = c_split.split("_")[0]
                                value_dict['termSource'] = term_source

                                # purify value schema
                                ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                                for onto in ontology_schema:
                                    ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, onto,
                                                                                      "ontology_annotation",
                                                                                      value_dict)

                                material_value_dict['value'] = ontology_schema

                                # unit - not really expecting any values or not yet determined how to extract if any
                                unit_dict = dict(annotationValue=str(), termAccession=str(), termSource=str())

                                # purify unit schema
                                ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                                for onto in ontology_schema:
                                    ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, onto,
                                                                                      "ontology_annotation",
                                                                                      unit_dict)

                                material_value_dict['unit'] = ontology_schema

                                material_attribute_schema = d_utils.get_db_json_schema("material_attribute_value")
                                for onto in material_attribute_schema:
                                    material_attribute_schema = ISAHelpers().resolve_schema_key(
                                        material_attribute_schema, onto,
                                        "material_attribute_value",
                                        material_value_dict)

                                if key_refined == 'organism':  # organism entered differently
                                    sample_object[key_refined] = material_value_dict['value']
                                else:
                                    sample_object['characteristics'].append(material_attribute_schema)
                        elif all(x in list(value.keys()) for x in ['text']):
                            if isinstance(value['text'], str):
                                comment_schema = d_utils.get_db_json_schema("comment")
                                for k in comment_schema:
                                    comment_schema = ISAHelpers().resolve_schema_key(comment_schema, k,
                                                                                     "comment",
                                                                                     dict(name=key_refined,
                                                                                          value=value['text']))

                                sample_object['comments'].append(comment_schema)

        return sample_object

    def do_validation(self, validation_parameters):
        """
        validates supplied entry
        :param validation_parameters: dict(schema=dict(), data=str())
        :return:
        """
        validation_result = dict(status="success", message="")

        schema = validation_parameters.get("schema", dict())
        data = validation_parameters.get("data", str())

        # validate required attributes
        if "required" in schema and str(schema["required"]).lower() == "true":
            if isinstance(data, str) and data.strip() == str():
                validation_result["status"] = "error"
                validation_result["message"] = "This is a required attribute!"

                return validation_result

                # should probably add validation for object types here, that might need some thinking with nested dicts

        # validate unique attributes
        if "unique" in schema and str(schema["unique"]).lower() == "true":
            if isinstance(data, str) and Sample().get_collection_handle().find(
                    {schema["id"].split(".")[-1]: {'$regex': "^" + data + "$",
                                                   "$options": 'i'}}).count() >= 1:
                validation_result["status"] = "error"
                validation_result["message"] = "This is a unique attribute!"

                return validation_result

                # should probably add validation for object types here, that might need some thinking though

        # validate characteristics attributes
        if schema.get("control", str()) == "copo-characteristics":
            if set(['value', 'unit']) < set(data.keys()):
                value = data['value']['annotationValue'].strip()
                unit = data['unit']['annotationValue'].strip()

                is_numeric = False
                try:
                    float(value)
                    is_numeric = True
                except ValueError:
                    pass

                if is_numeric and not unit:
                    validation_result["status"] = "error"
                    validation_result["message"] = "Numeric value requires a unit!"

                    # commenting out the 'elif' condition below prevents an update lock up;
                    # a case where you can't update the value because of the unit, and vice versa

                    return validation_result

        return validation_result

    def resolver_uri(self, uri):
        """
        function resolves given uri to some remote service to retrieve data
        :param resolver_uri:
        :return:
        """
        result = dict(status="error")

        try:
            response = urllib2.urlopen(uri).read()
            my_json = response.decode('utf8').replace("\n", '')

            result["status"] = "success"
            result["value"] = self.resolve_sample_object(json.loads(my_json))
        except:
            pass

        return result

    def validate_sample_names(self, sample_names):
        """
        function validates sample names - sample names are expected as comma or tab separated string
        :param sample_names:
        :return:
        """
        result = dict(status="success")
        errors = list()

        description = Description().GET(self.description_token)
        attributes = description.get("attributes", dict())
        meta = description.get("meta", dict())

        name_series = pd.Series(sample_names.split(",") if "," in sample_names else sample_names.split())
        name_series = name_series[name_series.str.strip() != '']

        # check for uniqueness of supplied names with existing sample names
        records_df = pd.DataFrame(
            Sample(profile_id=self.profile_id).get_all_records_columns(projection={'name': 1, '_id': 0}))

        if len(records_df):
            existing_name = list(name_series[name_series.isin(records_df.name)].unique())

            if len(existing_name):
                errors.append(["Existing names", "Supplied name(s) already exist", ', '.join(existing_name)])

        # check for duplicates in supplied names
        repeated_names = name_series.value_counts()[name_series.value_counts() > 1]
        if len(repeated_names):
            errors.append([
                "Repeating names",
                "Supplied name(s) are repeated",
                repeated_names.to_string().replace("\n", '<br/>')
            ])

        # do we have matching number of supplied names to proposed number of samples?

        number_of_samples = attributes.get("number_of_samples", dict()).get("number_of_samples", 0)

        if len(name_series) < int(number_of_samples):
            errors.append([
                "Insufficient names",
                "Supplied names are less than the requested number of samples",
                "Supplied names: {0}<br/>Requested number of samples: {1}".format(str(len(name_series)),
                                                                                  number_of_samples)
            ])

        # set error status
        if len(errors):
            result['status'] = "error"
            result['errors'] = errors
            result["error_columns"] = [{"title": "Error code"}, {"title": "Error message"}, {"title": "Error details"}]

        else:
            # store dependency
            name_series = name_series.head(int(number_of_samples))
            meta["generated_names"] = ','.join(list(name_series))
            user_choice = attributes.get("sample_naming_method", dict()).get("sample_naming_method", str())
            meta[user_choice + "_number_of_samples"] = number_of_samples
            # save meta
            Description().edit_description(self.description_token, dict(meta=meta))

        return result

    def validate_bundle_name(self, bundle_name):
        """
        function validates the suitability of bundle_name for generating unique sample names
        :param bundle_name:
        :return:
        """

        # get number of samples to inform name generation
        description = Description().GET(self.description_token)
        number_of_samples = description["attributes"].get("number_of_samples", dict()).get("number_of_samples", 0)

        # generate and validate names from bundle stub
        bn_df = pd.DataFrame(pd.Series([bundle_name] * int(number_of_samples)), columns=['bundle_name'])
        bn_df.insert(loc=0, column='s_n', value=np.arange(1, int(number_of_samples) + 1))
        bn_df['new_name'] = bn_df['bundle_name'].map(str) + '_' + bn_df['s_n'].map(str)

        validate = self.validate_sample_names(','.join(list(bn_df.new_name)))

        return dict(status=validate["status"])

    def get_cell_control(self, cell_reference, record_id):
        """
        function builds control for a UI data cell
        :param cell_reference:
        :param row_data:
        :return:
        """

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        key = cell_reference.split(self.key_split)

        parent_schema = [f for f in self.schema if f["id"].split(".")[-1] == key[0]]
        parent_schema = parent_schema[0] if parent_schema else {}
        control_schema = parent_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            control_schema = [f for f in object_controls[parent_schema['control']] if
                              f["id"].split(".")[-1] == key[2]]
            control_schema = control_schema[0] if control_schema else {}

        if "option_values" in control_schema:
            control_schema["option_values"] = htags.get_control_options(control_schema)

        # get target record
        record = Sample().get_record(record_id)

        # compose return object
        result_dict = dict()
        result_dict["control_schema"] = control_schema

        result_dict["schema_data"] = record[key[0]]
        if parent_schema.get("control", str()) in object_controls.keys():
            result_dict["schema_data"] = record[key[0]][int(key[1])][key[2]]
        elif parent_schema["type"] == "array":
            result_dict["control_schema"]["type"] = "string"  # constraints control to be rendered as an non-array
            result_dict["schema_data"] = record[key[0]][int(key[1])]

        # resolve option values for special controls
        if result_dict["control_schema"].get("control", "text") in ["copo-lookup", "copo-lookup2"]:
            result_dict["control_schema"]['data'] = result_dict["schema_data"]
            result_dict["control_schema"]["option_values"] = htags.get_control_options(
                result_dict["control_schema"])

        return result_dict

    def save_cell_data(self, cell_reference, record_id, auto_fields):
        """
        function save updated cell data; for the target record_id
        :param cell_reference:
        :param record_id:
        :param auto_fields:
        :return:
        """
        result = dict(status='success', value='')

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        key = cell_reference.split(self.key_split)

        # gather parameters for validation
        validation_parameters = dict(schema=dict(), data=str())

        parent_schema = [f for f in self.schema if f["id"].split(".")[-1] == key[0]]
        parent_schema = parent_schema[0] if parent_schema else {}
        control_schema = parent_schema
        validation_parameters["schema"] = control_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            control_schema = [f for f in object_controls[parent_schema['control']] if
                              f["id"].split(".")[-1] == key[2]]
            control_schema = control_schema[0] if control_schema else {}

        # resolve the new entry using the control schema
        resolved_data = DecoupleFormSubmission(auto_fields, d_utils.json_to_object(
            dict(fields=[control_schema])).fields).get_schema_fields_updated()

        # get target record
        record = Sample().get_record(record_id)

        if parent_schema.get("control", str()) in object_controls.keys():
            record[key[0]][int(key[1])][key[2]] = resolved_data[key[2]]
            validation_parameters["data"] = record[key[0]][int(key[1])]
            result["value"] = htags.get_resolver(resolved_data[key[2]], control_schema)
        elif parent_schema["type"] == "array":
            record[key[0]][int(key[1])] = resolved_data[key[0]][0]
            validation_parameters["data"] = resolved_data[key[0]][0]
            result["value"] = htags.get_resolver(resolved_data[key[0]][0], control_schema)
        else:
            record[key[0]] = resolved_data[key[0]]
            validation_parameters["data"] = resolved_data[key[0]]
            result["value"] = htags.get_resolver(resolved_data[key[0]], control_schema)

        # ...this, to get lists to render properly
        if isinstance(result["value"], list):
            result["value"] = " ".join(result["value"])

        # kick in some validation here before proceeding to save!
        validate_status = self.do_validation(validation_parameters)

        result["status"] = validate_status["status"]
        result["message"] = validate_status["message"]

        # return if error
        if result["status"] == "error":
            return result

        _id = record.pop('_id', None)

        if _id:
            Sample().get_collection_handle().update(
                {"_id": _id},
                {'$set': record})

        # update dataset with new value
        try:
            with pd.HDFStore(self.get_object_file_path()) as store:
                gd_df = store[self.object_key]
                gd_df.loc["row_" + record_id, cell_reference] = result["value"]
                store[self.object_key] = gd_df
        except Exception as e:
            print('Data Access Error: ' + str(e))
            lg.log('Data Access Error: ' + str(e), level=Loglvl.ERROR, type=Logtype.FILE)
            raise

        return result

    def batch_update_cells(self, cell_reference, record_id, target_rows):
        """
        function uses a reference cell to update a batch of records
        :param cell_reference:
        :param record_id:
        :param target_rows:
        :return:
        """

        # to enhance performance UI-side, use the refresh_threshold to decide if to send back the entire dataset
        refresh_threshold = 1000

        result = dict(status='success', value='')

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        key = cell_reference.split(self.key_split)

        # gather parameters for validation
        validation_parameters = dict(schema=dict(), data=str())

        parent_schema = [f for f in self.schema if f["id"].split(".")[-1] == key[0]]
        parent_schema = parent_schema[0] if parent_schema else {}
        control_schema = parent_schema
        validation_parameters["schema"] = control_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            control_schema = [f for f in object_controls[parent_schema['control']] if
                              f["id"].split(".")[-1] == key[2]]
            control_schema = control_schema[0] if control_schema else {}

        # get target record
        record = Sample().get_record(record_id)

        if parent_schema.get("control", str()) in object_controls.keys():
            resolved_data = record[key[0]][int(key[1])][key[2]]
            validation_parameters["data"] = record[key[0]][int(key[1])]
            result["value"] = htags.get_resolver(resolved_data, control_schema)
        elif parent_schema["type"] == "array":
            resolved_data = record[key[0]][int(key[1])]
            validation_parameters["data"] = resolved_data
            result["value"] = htags.get_resolver(resolved_data, control_schema)
        else:
            resolved_data = record[key[0]]
            validation_parameters["data"] = resolved_data
            result["value"] = htags.get_resolver(resolved_data, control_schema)

        # ...this to get lists to render properly
        if isinstance(result["value"], list):
            result["value"] = " ".join(result["value"])

        # kick in some validation here before proceeding to save!
        validate_status = self.do_validation(validation_parameters)

        result["status"] = validate_status["status"]
        result["message"] = validate_status["message"]

        # terminate if error
        if result["status"] == "error":
            return result

        # update db records
        object_ids = [ObjectId(x.split("row_")[-1]) for x in target_rows]

        if parent_schema.get("control", str()) in object_controls.keys():
            Sample().get_collection_handle().update_many(
                {"_id": {"$in": object_ids}},
                {'$set': {key[0] + "." + key[1] + "." + key[2]: resolved_data}})
        elif parent_schema["type"] == "array":
            Sample().get_collection_handle().update_many(
                {"_id": {"$in": object_ids}},
                {'$set': {key[0] + "." + key[1]: resolved_data}})
        else:
            Sample().get_collection_handle().update_many(
                {"_id": {"$in": object_ids}},
                {'$set': {key[0]: resolved_data}})

        # update dataset with new value
        try:
            with pd.HDFStore(self.get_object_file_path()) as store:
                gd_df = store[self.object_key]
                gd_df.loc[target_rows, cell_reference] = result["value"]
                store[self.object_key] = gd_df
                if len(target_rows) > refresh_threshold:
                    result["data_set"] = gd_df.to_dict('records')
        except Exception as e:
            print('Data Access Error: ' + str(e))
            lg.log('Data Access Error: ' + str(e), level=Loglvl.ERROR, type=Logtype.FILE)
            raise

        return result

    def finalise_description(self):
        """
        function updates described samples to make them visible
        :return:
        """
        result = dict(status='success', value='')

        fields = dict()
        fields['deleted'] = d_utils.get_not_deleted_flag()

        Sample().get_collection_handle().update_many(
            {"description_token": self.description_token},
            {'$set': fields})

        Description().delete_description([self.description_token])

        # delete store object
        Description().remove_store_object(object_path=self.get_object_path())

        return result

    def discard_description(self):
        """
        function discards the current description
        :return:
        """

        result = dict(status='success')

        # delete store object
        Description().remove_store_object(object_path=self.get_object_path())

        # remove entries associated with this token
        Sample().get_collection_handle().delete_many(
            {"description_token": self.description_token, "deleted": d_utils.get_deleted_flag()})

        Description().delete_description([self.description_token])

        return result

    def get_pending_description(self):
        """
        function returns any pending description records
        :return:
        """

        projection = dict(created_on=1, attributes=1, meta=1, stages=1)
        filter_by = dict(profile_id=self.profile_id, component='sample')
        records = Description().get_all_records_columns(sort_by='created_on', projection=projection,
                                                        filter_by=filter_by)

        # step toward computing grace period before automatic removal of description
        description_df = Description().get_elapsed_time_dataframe()
        refined_records = list()

        for r in records:
            ll = description_df[description_df._id == r['_id']]
            last_rendered_stage = r.get('meta', dict()).get('last_rendered_stage', str())
            stages = r['stages']
            lrs = [x['title'] for x in stages if x['ref'] == last_rendered_stage]
            lrs = lrs[0] if lrs else 'N/A'
            val = dict(
                created_on=htags.resolve_datetime_data(r['created_on'], dict()),
                _id=str(r['_id']),
                number_of_samples=r['attributes'].get("number_of_samples", dict()).get("number_of_samples", 'N/A'),
                last_rendered_stage=lrs
            )

            refined_records.append(val)

        return refined_records

    def get_object_path(self):
        """
        function returns directory to description data
        :return:
        """
        object_path = os.path.join(settings.MEDIA_ROOT, 'description_data', self.description_token)
        return object_path

    def get_object_file_path(self):
        """
        function returns file path to description data
        :return:
        """
        file_path = os.path.join(self.get_object_path(), 'generated.h5')
        return file_path

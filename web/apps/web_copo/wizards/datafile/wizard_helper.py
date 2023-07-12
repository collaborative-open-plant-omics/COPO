__author__ = 'etuka'

import copy
import numpy as np
import pandas as pd
from io import StringIO
from bson import ObjectId
from datetime import datetime
from dal import cursor_to_list
from django.conf import settings
from collections import namedtuple
from pandas.io.json import json_normalize

from dal.copo_da import DataFile, Description, Submission, DAComponent
import web.apps.web_copo.lookup.lookup as lkup
import web.apps.web_copo.templatetags.html_tags as htags
import web.apps.web_copo.schemas.utils.data_utils as d_utils
import web.apps.web_copo.wizards.datafile.wizard_callbacks as wizcb
from web.apps.web_copo.schemas.utils.data_utils import DecoupleFormSubmission
from web.apps.web_copo.wizards.utils.process_wizard_schemas import WizardSchemas

lg = settings.LOGGER


class WizardHelper:
    def __init__(self, description_token, profile_id):
        self.description_token = description_token
        self.profile_id = self.set_profile_id(profile_id)
        self.wiz_message = d_utils.json_to_pytype(lkup.MESSAGES_LKUPS["wizards_messages"])["properties"]

        self.key_split = "___0___"
        self.object_key = settings.DATAFILE_OBJECT_PREFIX + self.description_token
        self.store_name = settings.DATAFILE_OBJECT_STORE
        self.component = 'datafile'

    def set_profile_id(self, profile_id):
        p_id = profile_id
        if not p_id and self.description_token:
            description = Description().GET(self.description_token)
            p_id = description.get("profile_id", str())

        return p_id

    def initiate_description(self):
        """
        function initiates a new description
        :return:
        """

        initiate_result = dict(status="success", message="")

        try:
            description = Description().GET(self.description_token)
        except Exception as e:
            initiate_result['status'] = "error"
            initiate_result['message'] = self.wiz_message["bundle_record_not_found"]["text"]
            lg.exception(e)
            return initiate_result

        stages = description.get("stages", list())
        if not stages:
            # get initial stages - other stages will be dynamically determined along the line
            stages = WizardSchemas().get_wizard_template("start")

            # resolve type and data source for generated stages
            self.sanitise_stages(stages)

        save_dict = dict(stages=stages, created_on=d_utils.get_datetime())
        Description().edit_description(self.description_token, save_dict)

        initiate_result["next_stage"] = self.resolve_next_stage({"current_stage": "intro"})

        return initiate_result

    def add_to_bundle(self, description_targets):
        """
        function adds datafiles to bundle
        :param description_targets:
        :return:
        """

        description_targets = [x for x in description_targets if x]

        trgts_df = pd.DataFrame(description_targets, columns=['id'])
        trgts_df['idsplit'] = trgts_df['id'].apply(lambda x: ObjectId(x.split("row_")[-1]))

        initiate_result = dict(status="success", message="")

        # save description token against bundle items
        update_dict = dict(description_token=self.description_token)

        DataFile().get_collection_handle().update_many(
            {"_id": {"$in": list(trgts_df.idsplit)}},
            {'$set': update_dict})

        return initiate_result

    def validate_description_targets(self, next_stage_dict):
        """
        function validates description bundle against stage for consistency
        :param next_stage_dict:
        :return:
        """

        current_stage = next_stage_dict['stage']['ref']

        # get records in bundle
        records = cursor_to_list(DataFile().get_collection_handle().find({"$and": [
            {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
            {'description.attributes.' + current_stage: {"$exists": True}}]},
            {'description.attributes.' + current_stage: 1}))

        if not records:
            return True

        if len(records) == 1:
            return True

        apply_to_all = next_stage_dict["stage"].get("apply_to_all", False)

        if not apply_to_all:  # no constraint in stage
            return True

        stage_items = dict()
        st = copy.deepcopy(next_stage_dict["stage"])

        for item in st.get("items", list()):
            if str(item.get("hidden", False)).lower() == "false":
                item["id"] = st["ref"] + self.key_split + item["id"]
                stage_items[item["id"]] = item["label"]

        normalized_records = json_normalize(data=records, sep=self.key_split)
        normalized_columns = list(normalized_records.columns)

        # get stage controls to determine consistency in metadata for bundle items
        incompatible_list = set()

        for i in stage_items.keys():
            for j in normalized_columns:
                if i in j:
                    column_series = normalized_records[j].dropna()
                    if len(column_series) > 1:
                        if isinstance(column_series.iloc[0], str):  # string value test
                            if len(list(column_series.unique())) > 1:  # incompatible values
                                incompatible_list.add(stage_items[i])
                        else:  # object value test
                            ref_obj = column_series.iloc[0]
                            compatible_test = []
                            column_series.apply(
                                lambda x: compatible_test.append(True) if x == ref_obj else compatible_test.append(
                                    False))
                            if len(set(compatible_test)) > 1:
                                incompatible_list.add(stage_items[i])

        if incompatible_list:
            next_stage_dict["stage"]["bundle_violation"] = self.wiz_message["bundling_violation_alert_message"][
                "text"].format(", ".join(incompatible_list))

        return True

    def set_stage_data(self, next_stage_dict):
        """
        function tries to resolve stage data from records in description bundle
        :param next_stage_dict:
        :return:
        """

        current_stage = next_stage_dict['stage']['ref']

        # get records in bundle
        records = cursor_to_list(DataFile().get_collection_handle().find({"$and": [
            {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
            {'description.attributes.' + current_stage: {"$exists": True}}]},
            {'description.attributes.' + current_stage: 1}))

        if not records:
            return True

        # set data in the single-record case
        if len(records) == 1:
            next_stage_dict['stage']['data'] = records[0].get("description", dict()).get("attributes", dict()).get(
                current_stage, dict())

            if next_stage_dict['stage']['data']:
                # message to alert the user to how we arrived at data
                next_stage_dict["stage"]["message"] = next_stage_dict["stage"]["message"] + \
                                                      self.wiz_message["pooled_data_message"]["text"]

            return True

        records_df = pd.DataFrame(records)
        data_dict = dict()

        for item in next_stage_dict["stage"].get("items", list()):
            if str(item.get("hidden", False)).lower() == "true":
                continue

            item_id = item["id"]
            item_series = records_df['description'].apply(
                lambda x: x.get('attributes', dict()).get(current_stage, dict()).get(item_id, np.nan))
            item_series = item_series.dropna()

            if not len(item_series):
                continue

            # string instance
            if isinstance(item_series[0], str) and len(item_series[item_series != str()]):
                data_dict[item_id] = list(item_series.value_counts().index)[0]

            # list instance
            elif isinstance(item_series[0], list) and len(item_series[item_series.astype(str) != '[]']):
                new_list = [[]]
                item_series.apply(lambda x: new_list.append(x) if len(x) > len(new_list[-1]) else '')
                data_dict[item_id] = new_list[-1]

            # dict instance
            elif isinstance(item_series[0], dict) and len(item_series[item_series.astype(str) != '{}']):
                data_dict[item_id] = list(item_series[
                                              item_series.astype(str) ==
                                              item_series[item_series.astype(str)].index.value_counts().index[0]])[0]

        next_stage_dict['stage']['data'] = data_dict

        # message to alert the user to how we arrived at data
        if data_dict:
            next_stage_dict["stage"]["message"] = next_stage_dict["stage"]["message"] + \
                                                  self.wiz_message["pooled_data_message"]["text"]

        return True

    def resolve_select_data(self, stages):
        """
        function resolves data source for select-type controls
        :param stages:
        :return:
        """

        for stage in stages:
            for st in stage.get("items", list()):
                if st.get("control", "text") == "copo-lookup":
                    continue
                if st.get("option_values", False) is False:
                    st.pop('option_values', None)
                    continue

                st["option_values"] = htags.get_control_options(st)

        return True

    def set_items_type(self, stages):
        """
        function sets default type and control for all stage item
        :param stages:
        :return:
        """

        for stage in stages:
            for st in stage.get("items", list()):
                if not st.get("type"):
                    st["type"] = "string"

                if not st.get("control"):
                    st["control"] = "text"

                # also get id in the desired format
                st["id"] = st["id"].split(".")[-1]

        return True

    def sanitise_stages(self, stages):
        self.set_items_type(stages)
        self.resolve_select_data(stages)

        return True

    def set_stage_dependency(self, stages):
        """
        for dynamically generated stages, function sets their dependency
        :param stages:
        :return:
        """

        for stage in stages:
            stage['dependency'] = "resolved_stage"

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

    def resolve_defaults(self, stage):
        """
        function sets default values for items that needs resolving to other sources
        :param stages:
        :return:
        """

        Reference = namedtuple('Reference', ['repo', 'stage_ref', 'item_id'])

        # dictionary key take the format - repo, stage ref, and item id mapped to some resolver (e.g., function)
        register_repo_stage_item = {
            Reference("ena", "project_details", "project_name"): self.get_bundle_name,
            Reference("ena", "project_details", "project_title"): self.get_profile_title,
            Reference("ena", "project_details", "project_description"): self.get_profile_description,
            # Reference("ena", "project_details", "project_release_date"): self.get_current_date
        }

        if not self.description_token:
            return False

        description = Description().GET(self.description_token)

        if not description:
            return False

        attributes = description.get("attributes", dict())
        target_repository = attributes.get("target_repository", dict()).get("deposition_context", str())

        if not target_repository:
            return False

        repo_reference = [x for x in register_repo_stage_item.keys() if x.repo == target_repository]

        if not repo_reference:
            return False

        stage_ref = [x for x in repo_reference if x.stage_ref == stage.get("ref", str())]

        if not stage_ref:
            return False

        item_reference = [x for x in stage_ref if x.item_id in [item["id"] for item in stage.get("items", list())]]

        if not item_reference:
            return False

        for ref in stage_ref:
            item = [item for item in stage.get("items", list()) if item["id"] == ref.item_id]

            if item:
                item[0]["default_value"] = register_repo_stage_item[ref]()

        return True

    def remove_stage_dependency(self, indx):
        """
        function removes resolved stages preceding 'indx'
        :param stages:
        :param indx:
        :return:
        """

        description = Description().GET(self.description_token)

        stages = description["stages"]

        indx = indx + 1

        safe_stages = stages[:indx]
        targeted_stages = stages[indx:]
        cleared_stages = [st for st in targeted_stages if not st.get('dependency', str()) == 'resolved_stage']

        return safe_stages + cleared_stages

    def resolve_next_stage(self, auto_fields):
        """
        given data from a stage, function tries to resolve the next stage to be displayed to the user by the wizard
        :param auto_fields:
        :return:
        """

        next_stage_dict = dict(abort=False)
        current_stage = auto_fields.get("current_stage", str())

        if not current_stage:
            # no current stage; send signal to abort the wizard
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
        meta = description.get("meta", dict())
        bundle_name = description.get("name", str())

        # get next stage index
        next_stage_index = [indx for indx, stage in enumerate(stages) if stage['ref'] == current_stage]

        if not next_stage_index and not current_stage == 'intro':  # invalid current stage; send abort signal
            next_stage_dict["abort"] = True
            return next_stage_dict

        next_stage_index = next_stage_index[0] + 1 if len(next_stage_index) else 0

        # save in-coming stage data, check for changes, re-validate wizard, serve next stage
        previous_data = None
        current_data = None

        if next_stage_index > 0:
            current_stage_dict = stages[next_stage_index - 1]
            previous_data = attributes.get(current_stage, dict())
            current_data = DecoupleFormSubmission(auto_fields,
                                                  current_stage_dict['items']).get_schema_fields_updated_dict()

        # save stage data
        if current_data and not (current_data == previous_data):
            attributes[current_stage] = current_data
            save_dict = dict(attributes=attributes)

            Description().edit_description(self.description_token, save_dict)

            # stage data has changed, refresh wizard
            next_stage_dict['refresh_wizard'] = True

            # ...also, update rendered stages list
            if current_stage in meta["rendered_stages"]:
                srch_indx = meta["rendered_stages"].index(current_stage)
                meta["rendered_stages"] = meta["rendered_stages"][:srch_indx + 1]

        # get next stage
        next_stage_dict['stage'] = self.serve_stage(next_stage_index)

        # refresh values from db after obtaining next stage; there's the chance that things may have changed db-side
        description = Description().GET(self.description_token)
        attributes = description["attributes"]
        meta = description.get("meta", dict())

        if not next_stage_dict['stage']:
            # no stage to retrieve, this should signal end
            return next_stage_dict

        # signal to refresh wizard coming from stage resolution overrides previous setting
        if "refresh_wizard" in next_stage_dict['stage']:
            next_stage_dict['refresh_wizard'] = next_stage_dict['stage']['refresh_wizard']

        # build data dictionary for stage
        if next_stage_dict['stage']['ref'] in attributes and "data" not in next_stage_dict['stage']:
            next_stage_dict['stage']['data'] = attributes[next_stage_dict['stage']['ref']]

        if next_stage_dict['stage']['ref']:
            # save reference to rendered stage
            meta["last_rendered_stage"] = next_stage_dict['stage']['ref']

            rendered_stages = meta.get("rendered_stages", list())

            if not next_stage_dict['stage']['ref'] in rendered_stages:
                rendered_stages.append(next_stage_dict['stage']['ref'])
                meta["rendered_stages"] = rendered_stages

                # validate description bundle against this stage
                self.validate_description_targets(next_stage_dict)

                # if we didn't succeed to set stage data from description attributes, try from bundle data
                if "data" not in next_stage_dict['stage']:
                    self.set_stage_data(next_stage_dict)

        Description().edit_description(self.description_token, dict(meta=meta))

        # user feedback: constrained stage
        if next_stage_dict["stage"].get("apply_to_all", False):
            next_stage_dict["stage"]["message"] = next_stage_dict["stage"]["message"] + \
                                                  self.wiz_message["constrained_stage_alert_message"]["text"]
        elif next_stage_dict["stage"].get("is_metadata", True):
            next_stage_dict["stage"]["message"] = next_stage_dict["stage"]["message"] + \
                                                  self.wiz_message["update_stage_alert_message"]["text"]

        # get name of description and pass on
        next_stage_dict["description_label"] = bundle_name

        # check and resolve value for lookup fields
        if "data" in next_stage_dict['stage']:
            self.verify_lookup_items(next_stage_dict['stage'])

        # check and resolve default values
        self.resolve_defaults(next_stage_dict['stage'])

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

                    wizard_callbacks = wizcb.WizardCallbacks(self)  # callbacks are defined in 'WizardCallbacks'
                    stage = getattr(wizard_callbacks, stage["callback"])(next_stage_index)
                except Exception as e:
                    print(stage["ref"])
                    print('Stage resolution error. Next stage index: ' + str(next_stage_index) + ' ' + str(e))
                    stage = dict()
                    lg.exception(e)
                    raise

            # we expect a stage that cannot be directly rendered to return a False, thus prompting
            # progression to the next
            # stage in the sequence of stages (see below). Such non-renderable stages
            # may just be processes or stubs meant for resolving dynamic stages
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

        if stage:  # resolve type and data source for stage
            self.sanitise_stages([stage])

        return stage

    def get_unbundled_datafiles(self):
        """
        function returns datafiles that are not part of any bundle
        :return:
        """

        # get all active bundles in the profile
        existing_bundles = Description().get_all_records_columns(projection=dict(_id=1),
                                                                 filter_by=dict(profile_id=self.profile_id,
                                                                                component=self.component))
        existing_bundles = [str(x["_id"]) for x in existing_bundles]

        data_set = list()

        records = cursor_to_list(DataFile().get_collection_handle().find({"$and": [
            {"profile_id": self.profile_id, 'deleted': d_utils.get_not_deleted_flag()},
            {"$or": [
                {"description_token": {"$in": [None, False, ""]}},
                {"description_token": {"$nin": existing_bundles}}]}]},
            {'name': 1, 'description_token': 1}))

        if len(records):
            df = pd.DataFrame(records)
            df['description_token'] = df['description_token'].fillna('')
            df['_id'] = df._id.astype(str)
            df["DT_RowId"] = df._id
            df["chk_box"] = ''
            df.DT_RowId = 'row_' + df.DT_RowId

            df = df.drop('_id', axis='columns')
            data_set = df.to_dict('records')

        return data_set

    def get_description_bundle(self):
        """
        function returns datafiles in a description bundle
        :return:
        """

        data_set = list()

        # get and filter schema elements based on displayable columns
        schema = [x for x in DataFile().get_schema().get("schema_dict") if x.get("show_in_table", True)]

        # build db column projection
        projection = [(x["id"].split(".")[-1], 1) for x in schema]
        filter_by = dict(description_token=self.description_token)

        records = DataFile().get_all_records_columns(projection=dict(projection), filter_by=filter_by)

        if records:
            df = pd.DataFrame(records)
            df['record_id'] = df._id.astype(str)
            df["DT_RowId"] = df.record_id
            df["chk_box"] = ''
            df.DT_RowId = 'row_' + df.DT_RowId
            df = df.drop('_id', axis='columns')

            for x in schema:
                x["id"] = x["id"].split(".")[-1]
                df[x["id"]] = df[x["id"]].apply(htags.resolve_control_output_apply, args=(x,)).astype(str)

            data_set = df.to_dict('records')

        return data_set

    def generate_discrete_attributes(self):
        """
        function generate discrete attributes for individual datafile editing
        :return:
        """

        description = Description().GET(self.description_token)

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        # data and columns lists
        data = list()

        columns = [dict(title=' ', name='s_n', data="s_n", className='select-checkbox'),
                   dict(title='Name', name='name', data="name")]

        attributes = description["attributes"]
        meta = description["meta"]

        # get rendered stages
        rendered_stages_ref = meta["rendered_stages"]
        rendered_stages = [x for x in description["stages"] if
                           x['ref'] in rendered_stages_ref and x.get("is_metadata", True)]
        rendered_stages_copy = copy.deepcopy(rendered_stages)  # copy for updating individual records

        # aggregate items and data from all rendered stages
        datafile_items = list()
        datafile_attributes = dict()  # will be used for generating tabular data
        df_attributes = dict()  # will be copied to records with no previous description data

        for st in rendered_stages:
            apply_to_all = st.get("apply_to_all", False)
            df_attributes[st["ref"]] = attributes.get(st["ref"], dict())
            for item in st.get("items", list()):
                if str(item.get("hidden", False)).lower() == "false":
                    atrib_val = attributes.get(st["ref"], dict()).get(item["id"], str())
                    item["id"] = st["ref"] + self.key_split + item["id"]
                    item["apply_to_all"] = apply_to_all
                    datafile_attributes[item["id"]] = atrib_val
                    datafile_items.append(item)

        meta["aggregated_items"] = datafile_items
        Description().edit_description(self.description_token, dict(meta=meta))

        schema_df = pd.DataFrame(datafile_items)

        for index, row in schema_df.iterrows():
            resolved_data = htags.resolve_control_output(datafile_attributes, dict(row.dropna()))
            label = row["label"]

            # 'apply_to_all' columns are flagged as non-editable in table view
            column_class = 'locked-column' if row.get("apply_to_all") else ''

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

                        class_name = self.key_split.join((row.id, str(o_indx), object_array_keys[1]))
                        columns.append(dict(title=label + " [{0}]".format(o_row[object_array_keys[0]]), data=class_name,
                                            className=column_class))
                        data.append({class_name: o_row[object_array_keys[1]]})

                        # add other headers/values e.g., unit in material_attribute_value schema
                        for subitem in object_array_keys[2:]:
                            class_name = self.key_split.join((row.id, str(o_indx), subitem))
                            columns.append(dict(
                                title=control_df[control_df.id2.str.lower() == subitem.lower()].iloc[0].label,
                                data=class_name, className=column_class))
                            data.append({class_name: o_row[subitem]})
            elif row["type"] == "array":
                for tt_indx, tt_val in enumerate(resolved_data):
                    shown_keys = (row["id"], str(tt_indx))
                    class_name = self.key_split.join(shown_keys)
                    columns.append(
                        dict(title=label + " [{0}]".format(str(tt_indx + 1)), data=class_name,
                             className=column_class))

                    if isinstance(tt_val, list):
                        tt_val = ', '.join(tt_val)

                    data.append({class_name: tt_val})
            else:
                shown_keys = row["id"]
                class_name = shown_keys
                columns.append(dict(title=label, data=class_name, className=column_class))
                val = resolved_data

                if isinstance(val, list):
                    val = ', '.join(val)

                data.append({class_name: val})

        # get records in bundle
        records = cursor_to_list(
            DataFile().get_collection_handle().find(
                {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
                {'name': 1, 'description.attributes': 1}))

        # 
        if not records:
            return dict(columns=columns, rows=[])

        datafiles_df = pd.DataFrame(records)
        datafiles_df["DT_RowId"] = datafiles_df._id.astype(str)
        datafiles_df.DT_RowId = 'row_' + datafiles_df.DT_RowId

        datafiles_df.index = datafiles_df._id

        # build display dataset
        data_record = dict(pair for d in data for pair in d.items())
        for k, v in data_record.items():
            datafiles_df[k] = v

        datafiles_df.insert(loc=0, column='s_n', value=[''] * len(records))

        no_description_list = list(datafiles_df[datafiles_df.description == {}]['_id'])
        has_description_df = datafiles_df[datafiles_df.description != {}]

        # copy across wizard's data to records without description or single record
        update_dict = dict(description=dict(stages=rendered_stages_copy, attributes=df_attributes))
        if len(has_description_df) == 1:
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": list(has_description_df['_id'])}},
                {'$set': update_dict})

        if len(no_description_list):
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": no_description_list}},
                {'$set': update_dict})

        if len(has_description_df) > 1:
            # update stage list
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": list(has_description_df['_id'])}},
                {'$set': {"description.stages": rendered_stages_copy}})

            for index, row in schema_df.iterrows():
                st_key_split = row.id.split(self.key_split)  # will give [0]: stage ref; [1]: control id

                # keep track of treatments on records
                affected_list = list()

                # any record lacking stage data?
                item_series = has_description_df['description'].apply(
                    lambda x: x.get('attributes', dict()).get(st_key_split[0], np.nan))

                trgt_list = list(item_series[item_series.isna()].index)

                if len(trgt_list):
                    affected_list = affected_list + trgt_list

                    DataFile().get_collection_handle().update_many(
                        {"_id": {"$in": trgt_list}},
                        {'$set': {"description.attributes." + st_key_split[0]: df_attributes[st_key_split[0]]}})

                # any record lacking current item?
                item_series = has_description_df['description'].apply(
                    lambda x: x.get('attributes', dict()).get(st_key_split[0], dict()).get(st_key_split[1], np.nan))

                # filter out already treated records
                item_series = item_series[~item_series.index.isin(affected_list)]
                item_series_copy = item_series.copy()
                trgt_list = list(item_series[item_series.isna()].index)

                if len(trgt_list):
                    affected_list = affected_list + trgt_list

                    DataFile().get_collection_handle().update_many(
                        {"_id": {"$in": list(trgt_list)}},
                        {'$set': {"description.attributes." + st_key_split[0] + "." + st_key_split[1]:
                                      df_attributes[st_key_split[0]][st_key_split[1]]}})

                # get records having different data from wizard's
                item_series = item_series_copy
                item_series = item_series[
                    item_series.astype(str) != str(df_attributes[st_key_split[0]][st_key_split[1]])]

                item_series = item_series.dropna()

                # filter out already treated records
                item_series = item_series[~item_series.index.isin(affected_list)]

                if not len(item_series):
                    continue

                trgt_list = list(item_series.index)

                # check for data consistency if row.apply_to_all
                # since 'apply_to_all' applies to stage rather than individual controls, update entire stage data
                if row.apply_to_all:
                    DataFile().get_collection_handle().update_many(
                        {"_id": {"$in": trgt_list}},
                        {'$set': {"description.attributes." + st_key_split[0]: df_attributes[st_key_split[0]]}})

                    continue

                row_resolved_id = row.id + self.key_split + "_resolved"

                has_description_df_resolved = has_description_df[has_description_df.index.isin(trgt_list)].copy()
                has_description_df_resolved[row_resolved_id] = has_description_df_resolved[
                    'description'].apply(htags.resolve_control_output_description, args=(row,))

                if row.control in object_controls.keys() or row.type == "array":
                    # resolve wizard's data, using it to align data for the records
                    retained_row_id = row.id
                    row.id = st_key_split[1]  # update row id momentarily for data resolution
                    df_resolved_data = htags.resolve_control_output(df_attributes[st_key_split[0]], row)

                    row.id = retained_row_id

                    if not df_resolved_data:
                        continue

                    # align records - i.e., same number of items in records' data as in wizard's
                    # we assume here that items having the same length with the wizard's data capture a consistent
                    # set of features (e.g., host, height in sample characteristics)
                    row_count_val_id = row.id + self.key_split + "_count_val"

                    has_description_df_resolved[row_count_val_id] = has_description_df_resolved[row_resolved_id].apply(
                        lambda x: len(x))
                    has_description_df_resolved_2 = has_description_df_resolved[
                        has_description_df_resolved[row_count_val_id] < len(df_resolved_data)]

                    # align entries, update db, drop column and update resolved dataframe
                    if len(has_description_df_resolved_2):
                        # align resolved items
                        has_description_df_resolved_2[row_resolved_id] = has_description_df_resolved_2[
                            row_resolved_id].apply(lambda x: x + df_resolved_data[len(x):])

                        # ...also align actual data
                        has_description_df_resolved_2['_description'] = has_description_df_resolved_2[
                            'description'].apply(lambda x: x['attributes'][st_key_split[0]][st_key_split[1]] +
                                                           df_attributes[st_key_split[0]][st_key_split[1]][
                                                           len(x['attributes'][st_key_split[0]][st_key_split[1]]):])

                        # ...and save to db
                        bulk = DataFile().get_collection_handle().initialize_unordered_bulk_op()
                        for xindex, xrow in has_description_df_resolved_2.iterrows():
                            bulk.find({'_id': xrow._id}).update({'$set': {
                                "description.attributes." + st_key_split[0] + "." + st_key_split[
                                    1]: xrow._description}})
                        bulk.execute()

                        # merge back to has_description_df_resolved
                        has_description_df_resolved_2 = has_description_df_resolved_2.drop([row_count_val_id],
                                                                                           axis='columns')
                        has_description_df_resolved.loc[
                            has_description_df_resolved_2.index] = has_description_df_resolved_2

                        has_description_df_resolved = has_description_df_resolved.drop([row_count_val_id],
                                                                                       axis='columns')

                    # update ui-bound dataset for object controls
                    if row.control in object_controls.keys():
                        object_array_keys = [list(x.keys())[0] for x in df_resolved_data[0]]

                        for ii in range(0, len(df_resolved_data)):
                            class_name = self.key_split.join((row.id, str(ii), object_array_keys[1]))
                            has_description_df_resolved[class_name] = has_description_df_resolved[
                                row_resolved_id].apply(
                                lambda x: x[ii][1][object_array_keys[1]])

                            datafiles_df.loc[list(has_description_df_resolved.index), class_name] = \
                                has_description_df_resolved.loc[list(has_description_df_resolved.index), class_name]

                            for subitem in object_array_keys[2:]:
                                class_name = self.key_split.join((row.id, str(ii), subitem))
                                sub_index = object_array_keys.index(subitem)

                                has_description_df_resolved[class_name] = has_description_df_resolved[
                                    row_resolved_id].apply(lambda x: x[ii][sub_index][subitem])

                                datafiles_df.loc[list(has_description_df_resolved.index), class_name] = \
                                    has_description_df_resolved.loc[list(has_description_df_resolved.index), class_name]
                    else:
                        #  update ui-bound dataset for arrays
                        for tt_indx in range(len(df_resolved_data)):
                            class_name = self.key_split.join((row.id, str(tt_indx)))
                            has_description_df_resolved[class_name] = has_description_df_resolved[
                                row_resolved_id].apply(
                                lambda x: ', '.join(x[tt_indx]) if isinstance(x[tt_indx], list) else x[tt_indx])

                            datafiles_df.loc[list(has_description_df_resolved.index), class_name] = \
                                has_description_df_resolved.loc[list(has_description_df_resolved.index), class_name]
                else:
                    class_name = row.id
                    has_description_df_resolved[row_resolved_id] = has_description_df_resolved[row_resolved_id].apply(
                        lambda x: ', '.join(x) if isinstance(x, list) else x)
                    has_description_df_resolved[class_name] = has_description_df_resolved[row_resolved_id]

                    datafiles_df.loc[list(has_description_df_resolved.index), class_name] = \
                        has_description_df_resolved.loc[list(has_description_df_resolved.index), class_name]

        # generate dataset for UI
        datafiles_df = datafiles_df.drop(['_id', 'description'], axis='columns')
        data_set = datafiles_df.to_dict('records')

        return dict(columns=columns, rows=data_set)

    def get_cell_control(self, cell_reference, record_id):
        """
        function builds control for a UI data cell
        :param cell_reference:
        :param row_data:
        :return:
        """

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        # get constituent parts of the cell id - use this to determine stage and control of interest
        key = cell_reference.split(self.key_split)

        # get description record and retrieve relevant schema
        description = Description().GET(self.description_token)
        meta = description["meta"]
        schema = meta["aggregated_items"]

        parent_schema = [f for f in schema if f["id"] == key[0] + self.key_split + key[1]]
        parent_schema = parent_schema[0] if parent_schema else {}
        control_schema = parent_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            control_schema = [f for f in object_controls[control_schema['control']] if
                              f["id"].split(".")[-1] == key[3]]
            control_schema = control_schema[0] if control_schema else {}

        # compose return object
        result_dict = dict()

        # get target record
        record_attributes = DataFile().get_record(record_id)['description']['attributes']
        result_dict["schema_data"] = record_attributes[key[0]][key[1]]

        if "option_values" in control_schema:
            control_schema["data"] = result_dict["schema_data"]
            control_schema["option_values"] = htags.get_control_options(control_schema)

        result_dict["control_schema"] = control_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            result_dict["schema_data"] = record_attributes[key[0]][key[1]][int(key[2])][key[3]]
        elif parent_schema["type"] == "array":
            result_dict["control_schema"]["type"] = "string"  # constraints control to be rendered as an non-array
            result_dict["schema_data"] = record_attributes[key[0]][key[1]][int(key[2])]

        # resolve option values for special controls
        if result_dict["control_schema"].get("control", "text") in ["copo-lookup", "copo-lookup2"]:
            result_dict["control_schema"]['data'] = result_dict["schema_data"]
            result_dict["control_schema"]["option_values"] = htags.get_control_options(result_dict["control_schema"])

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

        # get cell schema
        control_schema = dict()

        key = cell_reference.split(self.key_split)

        # gather parameters for validation
        validation_parameters = dict(schema=dict(), data=str())

        # get description record and retrieve relevant schema
        description = Description().GET(self.description_token)
        meta = description["meta"]
        schema = meta["aggregated_items"]

        parent_schema = [f for f in schema if f["id"] == self.key_split.join((key[0], key[1]))]
        parent_schema = parent_schema[0] if parent_schema else {}
        control_schema = parent_schema
        validation_parameters["schema"] = control_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            control_schema = [f for f in object_controls[control_schema['control']] if
                              f["id"].split(".")[-1] == key[3]]
            control_schema = control_schema[0] if control_schema else {}

        # resolve the new entry using the control schema
        resolved_data = DecoupleFormSubmission(auto_fields, [control_schema]).get_schema_fields_updated_dict()

        # get target record
        record = DataFile().get_record(record_id)
        record_attributes = record['description']['attributes']

        if parent_schema.get("control", str()) in object_controls.keys():
            # i.e., [stage-dict][control-dict][index][sub-control-dict]
            record_attributes[key[0]][key[1]][int(key[2])][key[3]] = resolved_data[key[3]]
            validation_parameters["data"] = record_attributes[key[0]][key[1]][int(key[2])]
            result["value"] = htags.get_resolver(resolved_data[key[3]], control_schema)
        elif parent_schema["type"] == "array":
            record_attributes[key[0]][key[1]][int(key[2])] = resolved_data[self.key_split.join((key[0], key[1]))][0]
            validation_parameters["data"] = resolved_data[self.key_split.join((key[0], key[1]))][0]
            result["value"] = htags.get_resolver(resolved_data[self.key_split.join((key[0], key[1]))][0],
                                                 control_schema)
        else:
            record_attributes[key[0]][key[1]] = resolved_data[self.key_split.join((key[0], key[1]))]
            validation_parameters["data"] = resolved_data[self.key_split.join((key[0], key[1]))]
            result["value"] = htags.get_resolver(resolved_data[self.key_split.join((key[0], key[1]))], control_schema)

        # ...this to get lists to render properly
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
            DataFile().get_collection_handle().update(
                {"_id": _id},
                {'$set': record})

        # refresh stored dataset with new display value
        # try:
        #     with pd.HDFStore(self.store_name) as store:
        #         gd_df = store[self.object_key]
        #         gd_df.loc[gd_df.loc[gd_df['DT_RowId'].isin(["row_" + record_id])].index, cell_reference] = result[
        #             "value"]
        #         store[self.object_key] = gd_df
        # except Exception as e:
        #     lg.log('HDF5 Access Error: ' + str(e), level=Loglvl.ERROR, type=Logtype.FILE)

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

        # get description record and retrieve relevant schema
        description = Description().GET(self.description_token)
        meta = description["meta"]
        schema = meta["aggregated_items"]

        parent_schema = [f for f in schema if f["id"] == self.key_split.join((key[0], key[1]))]
        parent_schema = parent_schema[0] if parent_schema else {}
        control_schema = parent_schema
        validation_parameters["schema"] = control_schema

        if parent_schema.get("control", str()) in object_controls.keys():
            control_schema = [f for f in object_controls[control_schema['control']] if
                              f["id"].split(".")[-1] == key[3]]
            control_schema = control_schema[0] if control_schema else {}

        # get target record
        record = DataFile().get_record(record_id)
        record_attributes = record['description']['attributes']

        if parent_schema.get("control", str()) in object_controls.keys():
            # i.e., [stage-dict][control-dict][index][sub-control-dict]
            resolved_data = record_attributes[key[0]][key[1]][int(key[2])][key[3]]
            validation_parameters["data"] = record_attributes[key[0]][key[1]][int(key[2])]
            result["value"] = htags.get_resolver(resolved_data, control_schema)
        elif parent_schema["type"] == "array":
            resolved_data = record_attributes[key[0]][key[1]][int(key[2])]
            validation_parameters["data"] = resolved_data
            result["value"] = htags.get_resolver(resolved_data, control_schema)
        else:
            resolved_data = record_attributes[key[0]][key[1]]
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
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": object_ids}},
                {'$set': {"description" + "." + "attributes" + "." + key[0] + "." + key[1] + "." + key[2] + "." + key[
                    3]: resolved_data}})
        elif parent_schema["type"] == "array":
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": object_ids}},
                {'$set': {
                    "description" + "." + "attributes" + "." + key[0] + "." + key[1] + "." + key[2]: resolved_data}})
        else:
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": object_ids}},
                {'$set': {"description" + "." + "attributes" + "." + key[0] + "." + key[1]: resolved_data}})

        # refresh stored dataset with new display value
        # try:
        #     with pd.HDFStore(self.store_name) as store:
        #         gd_df = store[self.object_key]
        #         gd_df.loc[gd_df.loc[gd_df['DT_RowId'].isin(target_rows)].index, cell_reference] = result["value"]
        #         store[self.object_key] = gd_df
        #
        #         if len(target_rows) > refresh_threshold:
        #             result["data_set"] = gd_df.to_dict('records')
        # except Exception as e:
        #     lg.log('HDF5 Access Error: ' + str(e), level=Loglvl.ERROR, type=Logtype.FILE)

        return result

    def discard_description(self, description_targets):
        """
        function deletes description metadata from target records
        :param description_targets:
        :return:
        """
        object_list = [ObjectId(x.split("row_")[-1]) for x in description_targets]

        DataFile().get_collection_handle().update_many(
            {"_id": {"$in": object_list}}, {"$set": {"description": dict()}}
        )

    def remove_bundle_metadata(self):
        """
        function removes bundle's metadata
        :return:
        """

        result = dict(status="success", message="")

        fields = dict(
            stages=list(),
            attributes=dict(),
            meta=dict(),
            created_on=d_utils.get_datetime(),
        )

        try:
            Description().edit_description(self.description_token, fields)
        except Exception as e:
            result['status'] = "error"
            exception_message = "Error removing bundle's metadata " + " : " + str(e)
            result['message'] = exception_message
            lg.exception(e)
            return result

        return result

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
            if isinstance(data, str) and DataFile().get_collection_handle().find(
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

    def get_description_records(self):
        """
        function returns description bundles
        :return:
        """

        data_set = list()

        projection = dict(name=1, created_on=1)
        filter_by = dict(profile_id=self.profile_id, component=self.component)

        if self.description_token:
            filter_by["_id"] = ObjectId(self.description_token)

        records = Description().get_all_records_columns(sort_by='created_on', sort_direction=1, projection=projection,
                                                        filter_by=filter_by)

        if records:
            df = pd.DataFrame(records)
            df['s_n'] = df.index
            df['id'] = df._id.astype(str)
            df["DT_RowId"] = df._id.astype(str)
            df.DT_RowId = 'row_' + df.DT_RowId
            df['name'] = df['name'].replace('', 'N/A')
            df['created_on'] = df['created_on'].apply(lambda x: htags.resolve_datetime_data(x, dict()))

            # get related submission record
            submission_records = cursor_to_list(
                Submission().get_collection_handle().find(
                    {"description_token": {"$in": list(df['id'])}, 'deleted': d_utils.get_not_deleted_flag()},
                    {'_id': 1, 'complete': 1, 'description_token': 1, 'transcript': 1}))

            submission_map = dict()

            for sub in submission_records:
                submission_map[sub['description_token']] = sub.get('complete', False)

                # todo:  check for errors - need to resolve this
                if str(submission_map[sub['description_token']]).lower() == 'true':
                    submission_map[sub['description_token']] = 'submitted'
                elif sub.get('transcript', dict()).get('status', dict()).get("type", str()) == "error":
                    submission_map[sub['description_token']] = 'error'
                else:
                    submission_map[sub['description_token']] = 'pending'

            df['submission_status'] = df['id'].apply(lambda x: submission_map.get(x, 'not_submitted'))

            data_set = df.to_dict('records')

        return data_set

    def get_bundle_issues(self, description_token=str()):
        """
        function returns errors for incomplete submissions
        :param description_token:
        :return:
        """

        if not description_token:
            description_token = self.description_token

        submission_records = cursor_to_list(
            Submission().get_collection_handle().find(
                {"description_token": {"$in": [description_token]}, 'deleted': d_utils.get_not_deleted_flag()},
                {'_id': 1, 'complete': 1, 'description_token': 1, 'transcript': 1}))

        if not submission_records:
            return list()

        sub = submission_records[0]

        if str(sub.get('complete', False)).lower() == 'true':  # report no issues for completed submission
            return list()

        issues = sub.get('transcript', dict()).get('status', dict()).get("message", list())

        return issues

    def get_bundle_accessions(self, description_token=str()):
        """
        function returns submission accessions for a bundle
        :param description_token:
        :return:
        """

        if not description_token:
            description_token = self.description_token

        submission_records = cursor_to_list(
            Submission().get_collection_handle().find(
                {"description_token": {"$in": [description_token]}, 'deleted': d_utils.get_not_deleted_flag()},
                {'_id': 1, 'complete': 1, 'description_token': 1, 'accessions': 1, 'repository': 1}))

        if not submission_records:
            return list()

        sub = submission_records[0]

        accessions = sub.get("accessions", dict())

        if not accessions:
            return list()

        accessions = htags.generate_submission_accessions_data(submission_id=str(sub["_id"]))

        return accessions

    def get_description_record_details(self, description_token=str()):
        """
        function returns description detail
        :return:
        """

        if not description_token:
            description_token = self.description_token

        description = Description().GET(description_token)

        number_of_datafiles = DataFile().get_collection_handle().count(
            {'description_token': description_token, 'deleted': d_utils.get_not_deleted_flag()})

        name = description.get('name', 'undefined')
        created_on = htags.resolve_datetime_data(description.get('created_on', ''), dict())

        attributes = description.get('attributes', dict())
        meta = description.get("meta", dict())

        # get rendered stages
        rendered_stages_ref = meta.get("rendered_stages", list())
        rendered_stages = [x for x in description.get("stages", list()) if
                           x['ref'] in rendered_stages_ref and x.get("is_metadata", True)]

        datafile_attributes = dict()
        datafile_items = list()

        for st in rendered_stages:
            attributes[st["ref"]] = attributes.get(st["ref"], dict())
            for item in st.get("items", list()):
                if str(item.get("hidden", False)).lower() == "false":
                    atrib_val = attributes.get(st["ref"], dict()).get(item["id"], str())
                    item["id"] = st["ref"] + self.key_split + item["id"]
                    datafile_attributes[item["id"]] = atrib_val
                    datafile_items.append(item)

        data_set = list()
        target_repository = str()

        if datafile_items:
            resolved_element = htags.resolve_display_data(datafile_items, datafile_attributes)
            target_repository = resolved_element.get('data_set', dict()).get(
                'target_repository___0___deposition_context', str())

            for indx, col in enumerate(resolved_element.get('columns', list())):
                data_set.append([indx, col['title'], resolved_element.get('data_set', dict()).get(col['data'], str())])

        return dict(data_set=data_set, name=name, number_of_datafiles=number_of_datafiles, created_on=created_on,
                    target_repository=target_repository)

    def match_to_description(self, target_rows):
        """
        function matches target_rows to their corresponding description record
        :param target_rows:
        :return:
        """

        target_rows = [ObjectId(x.split("row_")[-1]) for x in target_rows]

        if not target_rows:
            return list()

        # get records with description id
        records = cursor_to_list(DataFile().get_collection_handle().find({"$and": [
            {"_id": {"$in": target_rows}},
            {'description_token': {"$exists": True, "$ne": ""}}]},
            {'description_token': 1, '_id': 1}))

        # validate description id
        valid_tokens = list()
        if len(records):
            object_ids = {ObjectId(x["description_token"]) for x in records}
            valid_tokens = cursor_to_list(
                Description().get_description_handle().find(
                    {"_id": {"$in": list(object_ids)}, "profile_id": self.profile_id}, {'_id': 1}))

        valid_tokens = [str(x["_id"]) for x in valid_tokens]
        targets_with_token = list()

        # filter by targets with valid token
        for rec in records:
            if rec["description_token"] in valid_tokens:
                targets_with_token.append('row_' + str(rec["_id"]))

        # if len(records):
        #     all_targets_df = pd.DataFrame(records)
        #     all_targets_df['record'] = all_targets_df['_id'].apply(lambda x: 'row_' + str(x))
        #     targets_with_token = list(all_targets_df['record'])

        return targets_with_token

    def delete_description_bundle(self):
        """
        function removes description bundle - thus unbundling assocoated datafiles
        :return:
        """

        result = dict(status='success')

        # check for dependency before delete
        records = cursor_to_list(
            Submission().get_collection_handle().find(
                {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
                {'_id': 1}))

        if len(records):
            result = dict(status='error', message="Existing dependency with a submission record!")
            return result

        update_dict = dict(description_token=str())

        DataFile().get_collection_handle().update_many(
            {"description_token": self.description_token},
            {'$set': update_dict})

        Description().delete_description([self.description_token])

        return result

    def unbundle_datafiles(self, description_targets):
        """
        function disassociates description_targets from their respective bundles
        :return:
        """

        trgts_df = pd.DataFrame(description_targets, columns=['id'])
        trgts_df['idsplit'] = trgts_df['id'].apply(lambda x: ObjectId(x.split("row_")[-1]))

        result = dict(status='success')

        update_dict = dict(description_token=str())

        DataFile().get_collection_handle().update_many(
            {"_id": {"$in": list(trgts_df.idsplit)}},
            {'$set': update_dict})

        return result

    def initiate_submission(self):
        """
        function initiates submission of datafiles in bundle
        :return:
        """

        # create a new submission record only if none exist for this description

        submission_record = Submission().get_collection_handle().find_one(
            {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()})

        # get attached datafiles
        records = cursor_to_list(
            DataFile().get_collection_handle().find(
                {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
                {'_id': 1, 'file_location': 1}))

        bundle = list()
        bundle_meta = list()

        if len(records):
            df = pd.DataFrame(records)
            df['file_id'] = df._id.astype(str)
            df['file_path'] = df['file_location'].fillna('')
            df['upload_status'] = False

            df = df[['file_id', 'file_path', 'upload_status']]
            bundle = list(df.file_id)
            bundle_meta = df.to_dict('records')

        if submission_record:  # submission record exist
            # update bundle and bundle_meta with new entries
            # we try to maintain 'state' of existing bundle items by not replacing altogether
            new_bundle = [x for x in bundle if x not in submission_record.get("bundle", list())]
            new_bundle_meta = [x for x in bundle_meta if x["file_id"] in new_bundle]
            submission_record["bundle"] = submission_record["bundle"] + new_bundle
            submission_record["bundle_meta"] = submission_record["bundle_meta"] + new_bundle_meta

            submission_id = str(submission_record.pop('_id'))
            Submission().get_collection_handle().update(
                {"_id": ObjectId(submission_id)},
                {'$set': submission_record})

            return dict(submission_id=submission_id, existing=True)

        description = Description().GET(self.description_token)
        target_repository = description["attributes"].get("target_repository", dict()).get("deposition_context", str())

        submission_id = str()

        if len(bundle):
            kwarg = dict(bundle=bundle, bundle_meta=bundle_meta, repository=target_repository,
                         description_token=self.description_token)
            submission_id = str(Submission(profile_id=self.profile_id).save_record(dict(), **kwarg).get("_id", str()))

        return dict(submission_id=submission_id, existing=False)

    def pair_datafiles(self, auto_fields):
        """
        function handles pairing of two datafiles and updating ui display
        :param autofields:
        :return:
        """
        validation_result = dict(status="success", message="")

        description = Description().GET(self.description_token)
        attributes = description["attributes"]

        pairing_targets = [x.split("row_")[-1] for x in auto_fields.get("pairing_targets", list())]
        unpaired_datafiles = [x.split("row_")[-1] for x in auto_fields.get("unpaired_datafiles", list())]

        current_stage = auto_fields.get("current_stage", str())

        # get stored mapping
        saved_mapping = attributes.get(current_stage, list())
        saved_mapping_df = pd.DataFrame(saved_mapping)

        # filter out unpaired files
        filtered_df = saved_mapping_df[(~saved_mapping_df['_id'].isin(unpaired_datafiles)) | (
            ~saved_mapping_df['_id2'].isin(unpaired_datafiles))].copy()

        # append new pair
        filtered_df = filtered_df.append({'_id': pairing_targets[0], '_id2': pairing_targets[1]}, ignore_index=True)

        # remove pairing targets from unpaired datafiles
        unpaired_datafiles = [ObjectId(x) for x in unpaired_datafiles if x not in pairing_targets]

        # generate display datasets
        filtered_df['_idObject'] = filtered_df["_id"].apply(lambda x: ObjectId(x))
        filtered_df['_id2Object'] = filtered_df["_id2"].apply(lambda x: ObjectId(x))
        object_ids = list(filtered_df._idObject) + list(filtered_df._id2Object)

        records = cursor_to_list(DataFile().get_collection_handle().find({"_id": {"$in": object_ids}}, {'name': 1}))
        records_df = pd.DataFrame(records)

        records_df.index = records_df._id
        records_dict = records_df.to_dict()
        records_dict = records_dict["name"]

        filtered_df["name"] = filtered_df['_idObject'].apply(lambda x: str(records_dict[x]))
        filtered_df["name2"] = filtered_df['_id2Object'].apply(lambda x: str(records_dict[x]))

        paired_dataset = filtered_df[['name', 'name2']]
        paired_dataset.columns = ['file1', 'file2']
        validation_result["paired_dataset"] = paired_dataset.to_dict('records')

        validation_result["unpaired_dataset"] = list()

        # prepare pairing dataframe for saving
        filtered_df = filtered_df[['_id', '_id2']]

        if unpaired_datafiles:
            records = cursor_to_list(
                DataFile().get_collection_handle().find({"_id": {"$in": unpaired_datafiles}}, {'name': 1}))
            df = pd.DataFrame(records)
            df['_id'] = df._id.astype(str)
            df["DT_RowId"] = df._id
            df["chk_box"] = ''
            df.DT_RowId = 'row_' + df.DT_RowId
            df = df.drop('_id', axis='columns')
            validation_result["unpaired_dataset"] = df.to_dict('records')

            # save overall pairing information - including unpaired ones. we need to make sure all files are paired!
            chunks = np.array_split(unpaired_datafiles, len(unpaired_datafiles) / 2)
            chunks = pd.DataFrame(chunks, columns=['_id', '_id2'])
            chunks._id = chunks['_id'].astype(str)
            chunks._id2 = chunks['_id2'].astype(str)
            filtered_df = pd.concat([filtered_df, chunks])

        attributes[current_stage] = filtered_df.to_dict('records')

        save_dict = dict(attributes=attributes)
        Description().edit_description(self.description_token, save_dict)

        return validation_result

    def get_unpaired_datafiles(self, auto_fields):
        """
        given name of datafiles that have been unpaired, function return record information
        :param auto_fields:
        :return:
        """

        validation_result = dict(status="success", message="", data_set=list())

        description = Description().GET(self.description_token)
        meta = description.get("meta", dict())

        pairing_info = auto_fields.get("pairing_info", list())
        pairs_df = pd.DataFrame(pairing_info)

        datafile_names = list(pairs_df.file1) + list(pairs_df.file2)

        # get paired candidates
        current_stage = auto_fields.get("current_stage", str())
        paired_candidates = meta.get(current_stage + "_paired_candidates", list())

        object_ids = [ObjectId(x) for x in paired_candidates]

        records = cursor_to_list(DataFile().get_collection_handle().find({"_id": {"$in": object_ids}}, {'name': 1}))
        records_df = pd.DataFrame(records)

        df = records_df[records_df.name.isin(datafile_names)].copy()

        if len(df):
            df['_id'] = df._id.astype(str)
            df["DT_RowId"] = df._id
            df["chk_box"] = ''
            df.DT_RowId = 'row_' + df.DT_RowId
            df = df.drop('_id', axis='columns')
            validation_result["data_set"] = df.to_dict('records')

        return validation_result

    def validate_datafile_pairing(self, auto_fields):
        """
        function validate user supplied pairing map
        :param auto_fields:
        :return:
        """

        validation_result = dict(status="success", message="")

        description = Description().GET(self.description_token)
        meta = description.get("meta", dict())

        pairing_info = auto_fields.get("pairing_info", str())

        if not pairing_info:
            validation_result["status"] = "error"
            validation_result["message"] = "Couldn't find valid pairing information."

            return validation_result

        # get paired candidates
        current_stage = auto_fields.get("current_stage", str())
        paired_candidates = meta.get(current_stage + "_paired_candidates", list())

        object_ids = [ObjectId(x) for x in paired_candidates]

        records = cursor_to_list(DataFile().get_collection_handle().find({"_id": {"$in": object_ids}}, {'name': 1}))

        records_df = pd.DataFrame(records)

        pairing_info = StringIO(pairing_info)
        df = pd.read_csv(pairing_info)

        # remove spaces that could have come with the file name
        try:
            df["File1"] = df.File1.str.strip()
            df["File2"] = df.File2.str.strip()
        except Exception as e:
            exception_message = "Error forming pairs. " + str(e)
            validation_result["status"] = "error"
            validation_result["message"] = exception_message
            lg.exception(e)
            return validation_result

        # get all the file names involved
        revised_file_names = list(df.File1) + list(df.File2)
        stored_file_names = list(records_df["name"])

        revised_file_names.sort()
        stored_file_names.sort()

        # now compare files in revised list and stored files - a mismatch should be reported as error
        if not stored_file_names == revised_file_names:
            validation_result["status"] = "error"
            validation_result[
                "message"] = "Pairing error! Possible cause might be repeated file names, or the introduction of file names not in the exported list."

            return validation_result

        # form the new map - for storing and ui display
        records_df.index = records_df.name
        records_dict = records_df.to_dict()
        records_dict = records_dict["_id"]

        df["_id"] = df['File1'].apply(lambda x: str(records_dict[x]))
        df["_id2"] = df['File2'].apply(lambda x: str(records_dict[x]))

        # save revised pairing
        saved_copy = df[['_id', '_id2']].to_dict('records')

        attributes = description["attributes"]
        attributes[current_stage] = saved_copy
        save_dict = dict(attributes=attributes)

        Description().edit_description(self.description_token, save_dict)

        # ui display
        df = df[['File1', 'File2']]
        df.columns = ['file1', 'file2']

        validation_result["data"] = df.to_dict('records')

        return validation_result

    def get_profile_title(self):
        """
        function returns the title of the parent profile for this description
        :return:
        """

        title = str()
        record = DAComponent(component="profile").get_record(self.profile_id)

        if record:
            title = record.get("title", str())

        return title

    def get_profile_description(self):
        """
        function returns description of the parent profile
        :return:
        """

        description = str()
        record = DAComponent(component="profile").get_record(self.profile_id)

        if record:
            description = record.get("description", str())

        return description

    @staticmethod
    def get_current_date():
        """
        function returns current date
        :return:
        """

        return datetime.today().strftime('%d/%m/%Y')

    def get_bundle_name(self):
        """
        function returns the bundle name
        :return:
        """

        return Description().GET(self.description_token).get("name", str())

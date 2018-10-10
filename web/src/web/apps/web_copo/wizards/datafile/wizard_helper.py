__author__ = 'etuka'

import copy
import difflib
import numpy as np
import pandas as pd
from bson import ObjectId
from dal import cursor_to_list
from operator import itemgetter
from django.conf import settings
from pandas.io.json import json_normalize

from dal.copo_da import DataFile, Description, Submission
import web.apps.web_copo.lookup.lookup as lkup
import web.apps.web_copo.templatetags.html_tags as htags
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from web.apps.web_copo.lookup.copo_enums import Loglvl, Logtype
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

    def initiate_description(self, description_targets):
        """
        using the description targets as basis, function attempts to initiate a new description...
        :param description_targets: datafiles to be described
        :return:
        """

        initiate_result = dict(status="success", message="")
        initiate_result['wiz_message'] = self.wiz_message

        if self.description_token:  # this is a call to reload an existing description
            description = Description().GET(self.description_token)

            if not description:  # validate token
                # description record doesn't exist; flag error
                initiate_result['status'] = "error"
                initiate_result['message'] = self.wiz_message["invalid_token_message"]["text"]
                initiate_result.pop('wiz_message', None)
            else:
                # reset timestamp, which will also reset the 'grace period' for the description
                Description().edit_description(self.description_token, dict(created_on=d_utils.get_datetime()))
                initiate_result['description_token'] = self.description_token

                # get name of description and pass on
                initiate_result["description_label"] = description.get("name", str())

        else:  # this is a call to instantiate a new description; create record, and issue token
            # validate description targets for bundling - based on existing bundle membership
            trgts_df = pd.DataFrame(description_targets, columns=['id'])
            trgts_df['idsplit'] = trgts_df['id'].apply(lambda x: ObjectId(x.split("row_")[-1]))

            records_count = DataFile().get_collection_handle().find({"$and": [
                {"_id": {"$in": list(trgts_df.idsplit)}},
                {'description_token': {"$exists": True, "$ne": ""}},
                {'deleted': d_utils.get_not_deleted_flag()}]}).count()

            if records_count > 0:
                initiate_result['status'] = "error"
                initiate_result['message'] = self.wiz_message["new_bundling_alert"]["text"]
                initiate_result.pop('wiz_message', None)

                return initiate_result

            # get initial stages - other stages will be dynamically determined along the line
            wizard_stages = WizardSchemas().get_wizard_template("start")

            # resolve type and data source for generated stages
            self.sanitise_stages(wizard_stages)

            meta = dict(rendered_stages=list())

            initiate_result['description_token'] = str(
                Description().create_description(stages=wizard_stages, attributes=dict(),
                                                 profile_id=self.profile_id,
                                                 component=self.component, meta=meta)['_id'])

            # save description token against bundle items
            update_dict = dict(description_token=initiate_result['description_token'])

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
                if st["control"] == "copo-lookup":
                    continue
                if st.get("option_values", False) == False:
                    st.pop('option_values', None)
                    continue

                st["option_values"] = htags.get_control_options(st)

        return True

    def set_items_type(self, stages):
        """
        function ensures all stage controls have a type
        :param stages:
        :return:
        """

        for stage in stages:
            for st in stage.get("items", list()):
                if not st.get("type"):
                    st["type"] = "string"

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
            if item.get("control", str()) == "copo-lookup":
                item['data'] = stage['data'].get(item["id"].split(".")[-1], str())
                item["option_values"] = htags.get_control_options(item)

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

        # get next stage index
        next_stage_index = [indx for indx, stage in enumerate(stages) if stage['ref'] == current_stage]

        if not next_stage_index and not current_stage == 'intro':  # invalid current stage; send abort signal
            next_stage_dict["abort"] = True
            return next_stage_dict

        next_stage_index = next_stage_index[0] + 1 if len(next_stage_index) else 0

        # save in-coming stage data, check for changes, re-validate wizard, serve next stage
        current_stage_dict = stages[next_stage_index - 1]
        previous_data = attributes.get(current_stage, dict())
        current_data = DecoupleFormSubmission(auto_fields, current_stage_dict['items']).get_schema_fields_updated_dict()

        # save stage data
        if current_data and not (current_data == previous_data):
            attributes[current_stage] = current_data
            save_dict = dict(attributes=attributes)

            # bundle name saved differently
            if current_stage == "description_bundle_name":
                save_dict["name"] = current_data["description_bundle_name"]

            Description().edit_description(self.description_token, save_dict)

            # stage data has changed, refresh wizard
            next_stage_dict['refresh_wizard'] = True

            # ...also, update rendered stages list
            if current_stage in meta["rendered_stages"]:
                srch_indx = meta["rendered_stages"].index(current_stage)
                meta["rendered_stages"] = meta["rendered_stages"][:srch_indx + 1]

            # generate discrete attributes
            # if current_stage_dict.get("is_metadata", True):
            #     self.generate_discrete_stage_attribute(current_stage)

            # remove store object, if any, associated with this description
            # Description().remove_store_object(store_name=self.store_name, object_key=self.object_key)

            # update meta
            # meta["generated_columns"] = list()

        # get next stage
        next_stage_dict['stage'] = self.serve_stage(next_stage_index)

        # refresh values from db after obtaining next stage; there's the chance that things may have changed db-side
        description = Description().GET(self.description_token)
        attributes = description["attributes"]
        meta = description.get("meta", dict())

        if not next_stage_dict['stage']:
            # no stage to retrieve, this should signal end
            return next_stage_dict

        # build data dictionary for stage
        if next_stage_dict['stage']['ref'] in attributes and "data" not in next_stage_dict['stage']:
            next_stage_dict['stage']['data'] = attributes[next_stage_dict['stage']['ref']]

        # save reference to rendered stage
        if next_stage_dict['stage']['ref']:
            meta["last_rendered_stage"] = next_stage_dict['stage']['ref']

            if not next_stage_dict['stage']['ref'] in meta["rendered_stages"]:
                meta["rendered_stages"].append(next_stage_dict['stage']['ref'])

                # validate description bundle against this stage
                self.validate_description_targets(next_stage_dict)

                # if we didn't succeed to set stage data from description attributes, try from bundle data
                if "data" not in next_stage_dict['stage']:
                    self.set_stage_data(next_stage_dict)

        Description().edit_description(self.description_token, dict(meta=meta))

        if next_stage_dict["stage"].get("apply_to_all", False):  # report constraint in stage
            next_stage_dict["stage"]["message"] = next_stage_dict["stage"]["message"] + \
                                                  self.wiz_message["constrained_stage_alert_message"]["text"]

        # get name of description and pass on
        next_stage_dict["description_label"] = Description().GET(self.description_token).get("name", str())

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
                    wizard_callbacks = wizcb.WizardCallbacks(self)  # callbacks are defined in 'WizardCallbacks'
                    stage = getattr(wizard_callbacks, stage["callback"])(next_stage_index)
                except Exception as e:
                    print('Stage resolution error. Next stage index: ' + str(next_stage_index) + " " + str(e))
                    stage = dict()

            # we expect a stage that cannot be directly rendered to return a False, thus prompting
            # progression to the next
            # stage in the sequence of stages (see below). Such non-renderable stages
            # may just be processes or stubs meant for resolving other dynamic stages
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
        function returns datafiles that are not bundled
        :return:
        """

        data_set = list()

        records = cursor_to_list(DataFile().get_collection_handle().find({"$and": [
            {"profile_id": self.profile_id, 'deleted': d_utils.get_not_deleted_flag()},
            {"description_token": {"$in": [None, False, ""]}}]},
            {'name': 1}))

        if len(records):
            df = pd.DataFrame(records)
            df['_id'] = df._id.astype(str)
            df["DT_RowId"] = df._id
            df["chk_box"] = ''
            df.DT_RowId = 'row_' + df.DT_RowId
            df = df.drop('_id', axis='columns')
            data_set = df.to_dict('records')

        return data_set

    def get_description_bundle(self):
        """
        function returns description bundles
        :return:
        """

        data_set = list()

        records = cursor_to_list(
            DataFile().get_collection_handle().find(
                {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
                {'name': 1}))

        if len(records):
            df = pd.DataFrame(records)
            df['_id'] = df._id.astype(str)
            df["DT_RowId"] = df._id
            df["chk_box"] = ''
            df.DT_RowId = 'row_' + df.DT_RowId
            df = df.drop('_id', axis='columns')
            data_set = df.to_dict('records')

        return data_set

    def generate_discrete_stage_attribute(self, current_stage):
        """
        function generates discrete attribute for stage whose stage_ref is provided
        :param current_stage:
        :return:
        """

        description = Description().GET(self.description_token)

        stage = [x for x in description["stages"] if x['ref'] == current_stage]
        stage = stage[0] if stage else {}
        attributes = description["attributes"].get(current_stage, dict())

        # object type controls and their corresponding schemas
        object_controls = d_utils.get_object_array_schema()

        # data and columns lists
        data = list()

        columns = [dict(title=' ', name='s_n', data="s_n", className='select-checkbox'),
                   dict(title='Name', name='name', data="name")]

        # aggregate items and data from all rendered stages
        datafile_items = list()
        datafile_attributes = dict()  # will be used for generating tabular data

        apply_to_all = stage.get("apply_to_all", False)

        for item in stage.get("items", list()):
            if str(item.get("hidden", False)).lower() == "false":
                atrib_val = attributes.get(item["id"], str())
                item["id"] = stage["ref"] + self.key_split + item["id"]
                item["apply_to_all"] = apply_to_all
                datafile_attributes[item["id"]] = atrib_val
                datafile_items.append(item)

        schema_df = pd.DataFrame(datafile_items)

        for index, row in schema_df.iterrows():
            resolved_data = htags.resolve_control_output(datafile_attributes, row)
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
                {'name': 1, 'description.attributes.' + current_stage: 1}))

        datafiles_df = pd.DataFrame(records)
        datafiles_df["DT_RowId"] = datafiles_df._id.astype(str)
        datafiles_df.DT_RowId = 'row_' + datafiles_df.DT_RowId

        datafiles_df.index = datafiles_df._id

        # build display dataset
        data_record = dict(pair for d in data for pair in d.items())
        for k, v in data_record.items():
            datafiles_df[k] = v

        datafiles_df.insert(loc=0, column='s_n', value=[''] * len(records))

        # any record lacking stage data?
        item_series = datafiles_df['description'].apply(
            lambda x: x.get('attributes', dict()).get(current_stage, np.nan))

        # split records to those with/out data for current_stage
        no_description_list = list(item_series[item_series.isna()].index)
        has_description_series = item_series[~item_series.index.isin(no_description_list)].copy()

        # process datafiles info...
        # get rendered stages
        meta = description["meta"]
        rendered_stages_ref = meta["rendered_stages"]
        rendered_stages = [x for x in description["stages"] if
                           x['ref'] in rendered_stages_ref and x.get("is_metadata", True)]

        df_attributes = dict()  # will be copied to records with no previous description data

        for st in rendered_stages:
            df_attributes[st["ref"]] = description["attributes"].get(st["ref"], dict())

        # copy across wizard's data to records without description or single record case
        if len(no_description_list) or len(has_description_series) == 1:
            update_dict = dict(description=dict(stages=rendered_stages, attributes=df_attributes))
            no_description_list = no_description_list + list(has_description_series.index)
            DataFile().get_collection_handle().update_many(
                {"_id": {"$in": no_description_list}},
                {'$set': update_dict})

        if len(has_description_series) > 1:
            if apply_to_all:
                # check for data consistency if apply_to_all stage, where all records in bundle must have same data
                item_series = has_description_series[has_description_series.astype(str) != str(attributes)]

                if len(item_series):
                    trgt_list = list(item_series.index)

                    DataFile().get_collection_handle().update_many(
                        {"_id": {"$in": trgt_list}},
                        {'$set': {"description.attributes." + current_stage: attributes}})

                # update stage list
                DataFile().get_collection_handle().update_many(
                    {"_id": {"$in": list(has_description_series.index)}},
                    {'$set': {"description.stages": rendered_stages}})

            else:
                for index, row in schema_df.iterrows():
                    st_key_split = row.id.split(self.key_split)  # will give [0]: stage ref; [1]: control id

                    # any record lacking current item?
                    item_series = has_description_series.apply(lambda x: x.get(st_key_split[1], np.nan))

                    trgt_list = list(item_series[item_series.isna()].index)

                    if len(trgt_list):
                        # update our running series by excluding trgt_list; save data for records in trgt_list
                        item_series = item_series[~item_series.index.isin(trgt_list)]

                        DataFile().get_collection_handle().update_many(
                            {"_id": {"$in": list(trgt_list)}},
                            {'$set': {"description.attributes." + st_key_split[0] + "." + st_key_split[1]: attributes[
                                st_key_split[1]]}})

                    if not len(item_series):
                        continue

                    # get records having data different from the wizard's
                    item_series = item_series[item_series.astype(str) != str(attributes[st_key_split[1]])]

                    if not len(item_series):
                        continue

                    # records have data different from the wizard's need to resolve this to the attributes dataframe
                    retained_row_id = row.id
                    row.id = st_key_split[1]  # update row id momentarily for data resolution

                    item_series_resolved = has_description_series[
                        has_description_series.index.isin(item_series.index)].apply(htags.resolve_control_output,
                                                                                    args=(row,))

                    row.id = retained_row_id

                    if row.control in object_controls.keys() or row.type == "array":
                        # resolve wizard's data, using it to align data for the records
                        retained_row_id = row.id
                        row.id = st_key_split[1]  # update row id momentarily for data resolution
                        df_resolved_data = htags.resolve_control_output(attributes, row)

                        row.id = retained_row_id

                        if not df_resolved_data:
                            continue

                        # align records - i.e., same number of items in records' data as in wizard's
                        # we assume here that items having the same length with the wizard's points to a consistent
                        # set of features (e.g., host, height in sample characteristics)

                        item_series_resolved_less = item_series_resolved[
                            item_series_resolved.apply(lambda x: len(x)) < len(df_resolved_data)]

                        # align entries, update db, drop column and update resolved dataframe
                        if len(item_series_resolved_less):
                            # augment _less items
                            item_series_resolved_less = item_series_resolved_less.apply(
                                lambda x: x + df_resolved_data[len(x):])

                            # ...also align actual data and save to db
                            bulk = DataFile().get_collection_handle().initialize_unordered_bulk_op()
                            for ser_indx in list(item_series_resolved_less.index):
                                ser_val = item_series[ser_indx] + attributes[st_key_split[1]][
                                                                  len(item_series[ser_indx]):]
                                bulk.find({'_id': ser_indx}).update({'$set': {
                                    "description.attributes." + st_key_split[0] + "." + st_key_split[
                                        1]: ser_val}})
                            bulk.execute()

                            # merge back to item_series_resolved
                            item_series_resolved = item_series_resolved.loc[
                                item_series_resolved_less.index] = item_series_resolved_less

                        # update ui-bound dataframe for object controls
                        if row.control in object_controls.keys():
                            object_array_keys = [list(x.keys())[0] for x in df_resolved_data[0]]

                            for ii in range(0, len(df_resolved_data)):
                                class_name = self.key_split.join((row.id, str(ii), object_array_keys[1]))
                                item_series_resolved_ui = item_series_resolved.apply(
                                    lambda x: x[ii][1][object_array_keys[1]])

                                datafiles_df.loc[
                                    list(item_series_resolved_ui.index), class_name] = item_series_resolved_ui

                                for subitem in object_array_keys[2:]:
                                    class_name = self.key_split.join((row.id, str(ii), subitem))
                                    sub_index = object_array_keys.index(subitem)

                                    item_series_resolved_ui = item_series_resolved.apply(
                                        lambda x: x[ii][sub_index][subitem])

                                    datafiles_df.loc[
                                        list(item_series_resolved_ui.index), class_name] = item_series_resolved_ui
                        else:
                            #  update ui-bound dataset for arrays
                            for tt_indx in range(len(df_resolved_data)):
                                class_name = self.key_split.join((row.id, str(tt_indx)))
                                item_series_resolved_ui = item_series_resolved.apply(
                                    lambda x: ', '.join(x[tt_indx]) if isinstance(x[tt_indx], list) else x[tt_indx])

                                datafiles_df.loc[
                                    list(item_series_resolved_ui.index), class_name] = item_series_resolved_ui
                    else:
                        class_name = row.id
                        item_series_resolved_ui = item_series_resolved.apply(
                            lambda x: ', '.join(x) if isinstance(x, list) else x)
                        datafiles_df.loc[
                            list(item_series_resolved_ui.index), class_name] = item_series_resolved_ui

        # generate dataset for UI
        datafiles_df = datafiles_df.drop(['_id', 'description'], axis='columns')
        data_set = datafiles_df.to_dict('records')

        return dict(columns=columns, rows=data_set)

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
            resolved_data = htags.resolve_control_output(datafile_attributes, row)
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

        # copy across wizard's data to records without description or single record case
        if len(no_description_list) or len(has_description_df) == 1:
            update_dict = dict(description=dict(stages=rendered_stages_copy, attributes=df_attributes))
            no_description_list = no_description_list + list(has_description_df['_id'])
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
        function returns description records
        :return:
        """

        data_set = list()

        projection = dict(name=1)
        filter_by = dict(profile_id=self.profile_id, component=self.component)

        if self.description_token:
            filter_by["_id"] = ObjectId(self.description_token)

        records = Description().get_all_records_columns(sort_by='created_on', sort_direction=1, projection=projection,
                                                        filter_by=filter_by)

        if records:
            df = pd.DataFrame(records)
            df['id'] = df._id.astype(str)
            df['name'] = df['name'].replace('', 'N/A')

            data_set = df.to_dict('records')

        return data_set

    def get_description_record_details(self):
        """
        function returns description detail
        :return:
        """

        description = Description().GET(self.description_token)

        number_of_datafiles = DataFile().get_collection_handle().count(
            {'description_token': str(description['_id']), 'deleted': d_utils.get_not_deleted_flag()})

        name = description['name']
        created_on = htags.resolve_datetime_data(description['created_on'], dict())

        attributes = description['attributes']
        meta = description["meta"]

        # get rendered stages
        rendered_stages_ref = meta["rendered_stages"]
        rendered_stages = [x for x in description["stages"] if
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

        resolved_element = htags.resolve_display_data(datafile_items, datafile_attributes)
        target_repository = resolved_element['data_set']['target_repository___0___deposition_context']

        data_set = list()

        for indx, col in enumerate(resolved_element['columns']):
            data_set.append([indx, col['title'], resolved_element['data_set'][col['data']]])

        return dict(data_set=data_set, name=name, number_of_datafiles=number_of_datafiles, created_on=created_on,
                    target_repository=target_repository)

    def match_to_description(self, target_rows):
        """
        function matches target_rows to their corresponding description record
        :param target_rows:
        :return:
        """

        trgts_df = pd.DataFrame(target_rows, columns=['id'])
        trgts_df['idsplit'] = trgts_df['id'].apply(lambda x: ObjectId(x.split("row_")[-1]))

        records = cursor_to_list(DataFile().get_collection_handle().find({"$and": [
            {"_id": {"$in": list(trgts_df.idsplit)}},
            {'description_token': {"$exists": True, "$ne": ""}}]}))

        all_targets_series = list()

        if len(records):
            all_targets_df = pd.DataFrame(records)
            all_targets_df['record'] = all_targets_df['_id'].apply(lambda x: 'row_' + str(x))
            all_targets_series = list(all_targets_df['record'])

        return all_targets_series

    def delete_description_record(self):
        """
        function removes description record - datafiles are once more 'free agents'
        :return:
        """

        result = dict(status='success')

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

        records = cursor_to_list(
            DataFile().get_collection_handle().find(
                {"description_token": self.description_token, 'deleted': d_utils.get_not_deleted_flag()},
                {'_id': 1, 'file_location': 1}))

        description = Description().GET(self.description_token)
        target_repository = description["attributes"].get("target_repository", dict()).get("deposition_context", str())

        if len(records):
            df = pd.DataFrame(records)
            df['file_id'] = df._id.astype(str)
            df['file_path'] = df['file_location'].fillna('')
            df['upload_status'] = False

        df = df[['file_id', 'file_path', 'upload_status']]
        bundle = list(df.file_id)
        bundle_meta = df.to_dict('records')
        kwarg = dict(bundle=bundle, bundle_meta=bundle_meta, repository=target_repository)

        submission_id = str(Submission(profile_id=self.profile_id).save_record(dict(), **kwarg).get("_id", str()))

        return submission_id

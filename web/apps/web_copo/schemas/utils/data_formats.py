__author__ = 'etuka'

import json
import os
import re

import web.apps.web_copo.lookup.lookup as lkup
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from web.apps.web_copo.schemas.utils.cg_core.cg_schema_generator import CgCoreSchemas


class DataFormats:
    def __init__(self, schema):
        self.error_messages = list()
        self.generated_controls = list()
        self.resource_objects = list()
        self.schema = schema.upper()

        self.path_to_mappings = lkup.UI_CONFIG_MAPPINGS

        '''
        NB: lkup.UI_CONFIG_MAPPINGS is the path to user interface (UI) schemas.
        Fields assigned in the UI schemas override those assigned elsewhere (e.g., in a mapped configuration).
        Every item under 'properties' in a UI schema must have the required attributes: "id" and "ref" defined:
        "id" - to uniquely identify the item; "ref" - to map to some configuration (e.g., the ISA configuration).
        The "ref" attribute may be left unassigned (i.e., ref: ""), only if no configuration is to be mapped, as is the
        case with most of the schemas defiend under mappings.
        Other attributes (e.g., "label") may be defined to override those defined, say, in some
        configuration elsewhere.

        Also, order matters! That is, the order of items in the properties list is preserved when those items are
        rendered in the UI.
        '''

        self.dispatch = {
            'isa_xml': self.isa_xml_mapping,
            'isa_json': self.isa_json_mapping,
            'copo_json': self.copo_json_mapping
        }

    # generates template for UI rendering
    def generate_ui_template(self):
        # update cg core
        CgCoreSchemas().process_schema()

        new_list = []
        json_files_handle = self.get_mapping_files()
        for file_name in json_files_handle:
            file_dict = d_utils.json_to_pytype(file_name, compatibility_mode=False)
            self.resource_objects.append(dict(file_handle=file_name, file_dict=file_dict))

            mapped_list = self.dispatch[
                file_dict['configuration']['provider'] + "_" + file_dict['configuration']['type']](file_dict)

            if isinstance(mapped_list, list):
                new_list.extend(mapped_list)

        if new_list:
            self.generated_controls = new_list

            # set some default fields
            self.set_type()
            self.set_control_meta()
            self.set_deprecation()
            self.set_versioning()
            self.set_form_display()
            self.set_table_display()
            self.set_ontologies()
            self.set_option_values()

            # self.update_original_resource()
            self.refactor_deprecated_controls()

            out_dict = self.objectify()
            out_dict = {"status": "success", "data": out_dict}
        else:
            out_dict = {}
            out_dict = {"status": "failed", "messages": self.error_messages, "data": out_dict}

        return out_dict

    def isa_xml_mapping(self, arg_dict):
        # get reference to the configuration resource

        new_list = arg_dict['properties']
        current_list = arg_dict['properties']

        output_dict = d_utils.get_isa_schema_xml(arg_dict['configuration']['ref'])

        if output_dict.get("status", str()) == "error":
            self.error_messages.append(output_dict.get("content"))
        else:
            tree = output_dict.get("content")
            root = tree.getroot()

            # get the namespace of the xml document
            ns = self.namespace(root)

            fields = tree.findall(".//{%s}field" % ns)

            attr = lkup.ATTRIBUTE_MAPPINGS["isa_xml"]

            for elem_dict in current_list:
                if "ref" not in elem_dict or "id" not in elem_dict:
                    continue

                # get index and retain for accessing copy element in new_list
                indx = new_list.index(elem_dict)

                # assign attributes defined in lkup, maintain default ones defined in the model
                for k in attr:
                    if k not in elem_dict.keys():
                        new_list[indx][k] = str()

                for f in iter(fields):
                    # 'ref' key in the config is defined to match 'header' attribute in the ISA xml
                    if f.get("header") == elem_dict["ref"]:
                        # modify for file fields
                        if f.get("is-file-field") == "true":
                            new_list[indx]["control"] = "file"

                        # handle list values
                        if f.get("data-type") == "List":
                            try:
                                ls = f.findall(".//{%s}list-values" % ns)
                                options_split = ls[0].text.split(",")
                                new_list[indx]["option_values"] = options_split
                            except IndexError:
                                pass

                        for k, v in attr.items():
                            if not new_list[indx][k]:
                                new_list[indx][k] = f.get(v)

                                if v == "data-type" and f.get(v) in lkup.CONTROL_MAPPINGS["isa_xml"].keys():
                                    new_list[indx][k] = lkup.CONTROL_MAPPINGS["isa_xml"][f.get(v)]

            # clean up controls
            for elem_dict in new_list:
                if "control" in elem_dict and not elem_dict["control"] == "select":
                    if "option_values" in elem_dict:
                        del elem_dict["option_values"]

                # set all null fields to ""
                for k, v in elem_dict.items():
                    if v is None:
                        elem_dict[k] = str()

        return new_list

    def refactor_object_model(self, elem_list):
        all_list = []
        for elem_dict in elem_list:
            key_split = elem_dict["id"].split(".")[:-1]
            all_list.append(key_split)

        object_model = {}
        for path in all_list:
            current_level = object_model
            for part in path:
                if part not in current_level:
                    current_level[part] = {"fields": []}
                current_level = current_level[part]

        return object_model

    def objectify(self):
        out_dict = self.refactor_object_model(self.generated_controls)

        for elem_dict in self.generated_controls:
            key_split = elem_dict["id"].split(".")

            if len(key_split) >= 2:
                out_dict = self.set_model_fields(out_dict, key_split[:-1], elem_dict)

        return out_dict

    def set_model_fields(self, d, keys, val):
        out = d
        for k in keys[:-1]:
            out = out[k]
        out[keys[-1]]["fields"].append(val)
        return d

    def set_form_display(self):
        for elem_dict in self.generated_controls:
            if "show_in_form" not in elem_dict:
                elem_dict["show_in_form"] = True

    def set_table_display(self):
        for elem_dict in self.generated_controls:
            if "show_in_table" not in elem_dict:
                elem_dict["show_in_table"] = True

    def set_deprecation(self):
        for elem_dict in self.generated_controls:
            if "deprecated" not in elem_dict:
                elem_dict["deprecated"] = False

    def refactor_deprecated_controls(self):
        new_list = []

        for elem_dict in self.generated_controls:
            if 'deprecated' in elem_dict and elem_dict['deprecated']:
                pass
            else:
                new_list.append(elem_dict)

        self.generated_controls = new_list

    def set_type(self):
        for elem_dict in self.generated_controls:
            if not elem_dict.get("type"):
                elem_dict["type"] = "string"

    def set_control_meta(self):
        for elem_dict in self.generated_controls:
            if not elem_dict.get("control_meta"):
                elem_dict["control_meta"] = dict()

    def set_versioning(self):
        for elem_dict in self.generated_controls:
            if not elem_dict.get("versions"):
                elem_dict["versions"] = [elem_dict["id"].rsplit(".", 1)[1]]

    def set_ontologies(self):
        for elem_dict in self.generated_controls:
            if elem_dict.get("control", str()).lower() == "ontology term" and "ontology_names" not in elem_dict:
                elem_dict["ontology_names"] = list()

    def set_option_values(self):
        for elem_dict in self.generated_controls:
            if elem_dict.get("control", str()).lower() in ['copo-lookup', 'copo-multi-select', 'copo-select2',
                                                           'copo-lookup2',
                                                           'copo-button-list', 'copo-single-select',
                                                           'copo-multi-select2'] and "option_values" not in elem_dict:
                elem_dict["option_values"] = list()

    def update_original_resource(self):
        """
        writes generated elements to the respective (resource) mapping files
        :return:
        """
        for ro in self.resource_objects:
            prop_dict = list()
            for p in ro["file_dict"]["properties"]:
                prop_dict.append([elem_dict for elem_dict in self.generated_controls if elem_dict['id'] == p['id']][0])

            ro["file_dict"]["properties"] = prop_dict

            with open(ro["file_handle"], 'w') as f:
                json.dump(ro["file_dict"], f)

    def purify(self, out_dict):
        for k, v in out_dict.items():
            if isinstance(v, dict):
                self.purify(v)
            elif isinstance(v, list):
                # de-duplicate fields list
                new_list = v
                found_list = []
                for idx, val in enumerate(new_list):
                    if val["id"] in found_list:
                        del v[idx]
                    else:
                        found_list.append(val["id"])
        return out_dict

    def namespace(self, element):
        match = re.search(r'\{(.+)\}', element.tag)
        return match.group(1) if match else ''

    def get_mapping_files(self):
        json_files = list()

        exclude = set(['additional_attributes'])
        for root, dirs, files in os.walk(self.path_to_mappings):
            dirs[:] = [d for d in dirs if d not in exclude]
            for name in files:
                if name.endswith(".json"):
                    json_files.append(os.path.join(root, name))

        return json_files

    # todo: write a routine for mapping from an jsonschema, i.e., if isa's xml and JSON schemas ever get harmonised
    def isa_json_mapping(self, arg_dict):
        return arg_dict['properties']

    def copo_json_mapping(self, arg_dict):
        # get reference to the configuration resource
        arm = arg_dict['configuration']['ref']
        new_list = arg_dict['properties']

        # is there a configuration resource?
        # basically mappings without a configuration resource is a way of hooking up to the schema grid generated
        # rather than making an actual mapping between schema
        if not arm:
            return new_list

__author__ = 'etuka'

import re
import os
import copy
import threading
import pandas as pd
from bson import ObjectId
from dal import cursor_to_list
import web.apps.web_copo.lookup.lookup as lookup
import web.apps.web_copo.templatetags.html_tags as htags
from web.apps.web_copo.schemas.utils import data_utils as d_utils
from dal.copo_da import Submission, DataFile, DAComponent, Person, Sample, Description
from exceptions_and_logging.logger import Logger


class Investigation:
    def __init__(self, copo_isa_records=dict(), study_schema=dict()):
        self.copo_isa_records = copo_isa_records
        self.study_schema = study_schema
        self.profile_id = str(self.copo_isa_records.get("profile").get("_id"))

    def get_schema(self):
        component = "investigation"

        properties = d_utils.get_db_json_schema(component)

        if properties:
            for k in properties:
                if k == "@id":
                    record = dict(name=self.copo_isa_records.get("submission_token"))
                    properties[k] = ISAHelpers().get_id_field(component=component, record=record)
                else:
                    try:
                        properties[k] = getattr(Investigation, "_" + k)(self, properties[k])
                    except Exception as e:
                        print(e)
                        Logger().exception(e)
                        properties[k] = ISAHelpers().get_schema_key_type(properties.get(k, dict()))

        return properties

    def get_datafilehashes(self):
        return self.copo_isa_records["datafilehashes"]

    def _title(self, spec=dict()):
        return ISAHelpers().get_schema_key_type(spec)

    def _description(self, spec=dict()):
        # this property is set from the Profile record
        return self.copo_isa_records.get("profile").get("description", str())

    def _identifier(self, spec=dict()):
        return self.copo_isa_records.get("submission_token")

    def _studies(self, spec=dict()):
        return self.study_schema

    def _ontologySourceReferences(self, spec=dict()):
        osr = list()

        records = list()
        records = records + list(self.copo_isa_records.get("publication"))
        records = records + list(self.copo_isa_records.get("person"))
        records = records + list(self.copo_isa_records.get("sample"))
        records = records + list(self.copo_isa_records.get("source"))
        records = records + list(self.copo_isa_records.get("datafile"))
        records.append(self.copo_isa_records.get("technology_type"))

        target_record_list = list()
        target_object_keys = set(d_utils.get_db_json_schema("ontology_annotation").keys())

        for record in records:
            target_record_list = ISAHelpers().get_object_instances(record, target_record_list, target_object_keys)

        termsources = [x["termSource"] for x in target_record_list if len(x["termSource"]) > 0]
        termsources = list(set(termsources))

        component = "ontology_source_reference"

        # get ontology base uri
        base_url = lookup.ONTOLOGY_LKUPS.get("ontology_file_uri", str())

        for ts in termsources:
            value_dict = dict(
                name=ts,
                file=base_url + ts
            )

            osr_schema = d_utils.get_db_json_schema(component)
            for k in osr_schema:
                if k == "@id":
                    osr_schema[k] = ISAHelpers().get_id_field(component, dict(name=ts))
                else:
                    osr_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(osr_schema.get(k, dict())))

            osr.append(osr_schema)

        return osr

    def _submissionDate(self, spec=dict()):
        # todo: not decided on a value for this property, return a default type
        return ISAHelpers().get_schema_key_type(spec)

    def _filename(self, spec=dict()):
        filename = 'i_' + self.copo_isa_records.get("submission_token") + '.txt'
        return filename

    def _publicReleaseDate(self, spec=dict()):
        # todo: not decided on a value for this property, return a default type
        return ISAHelpers().get_schema_key_type(spec)

    def _publications(self, spec=dict()):
        # set at the Study level
        return ISAHelpers().get_schema_key_type(spec)

    def _people(self, spec=dict()):
        # set at the Study level
        return ISAHelpers().get_schema_key_type(spec)

    def _comments(self, spec=dict()):
        # todo: not decided on a value for this property, return a default type
        return ISAHelpers().get_schema_key_type(spec)


class Study:
    def __init__(self, copo_isa_records=str(), assay_schema=dict()):
        self.copo_isa_records = copo_isa_records
        self.assay_schema = assay_schema
        self.profile_id = str(self.copo_isa_records.get("profile").get("_id"))

    def get_schema(self):
        component = "study"

        schemas = list()
        properties = d_utils.get_db_json_schema(component)

        if properties:
            for k in properties:
                if k == "@id":
                    record = dict(name=self.copo_isa_records.get("submission_token"))
                    properties[k] = ISAHelpers().get_id_field(component=component, record=record)
                else:
                    try:
                        properties[k] = getattr(Study, "_" + k)(self, properties[k])
                    except Exception as e:
                        print(e)
                        Logger().exception(e)
                        properties[k] = ISAHelpers().get_schema_key_type(properties.get(k, dict()))

            schemas.append(properties)

        return schemas

    def _assays(self, spec):
        return self.assay_schema

    def _publications(self, spec=dict()):
        component = "publication"
        return ISAHelpers().get_isa_records(component, list(self.copo_isa_records.get(component)))

    def _people(self, spec=dict()):
        component = "person"
        return ISAHelpers().get_isa_records(component, list(self.copo_isa_records.get(component)))

    def _studyDesignDescriptors(self, spec=dict()):
        # this property is contingent on the 'study type' associated with a datafile
        sdd = list()

        # this needs to be represented as an ontology annotation
        value_dict = dict(annotationValue=d_utils.lookup_study_type_label(self.copo_isa_records.get("study_type"))
                          )
        component = "ontology_annotation"

        isa_schema = d_utils.get_db_json_schema(component)
        for k in isa_schema:
            isa_schema = ISAHelpers().resolve_schema_key(isa_schema, k, component, value_dict)

        sdd.append(isa_schema)

        return sdd

    def _protocols(self, spec=dict()):
        # this property is contingent on the 'study type' associated with a datafile
        protocols = list()

        # get protocols
        protocol_list = list(self.copo_isa_records["protocol_list"])

        for pr in protocol_list:
            # parameters
            parameters = list()
            for pv in pr.get("parameterValues", list()):
                pv = htags.trim_parameter_value_label(pv).lower()

                ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                for k in ontology_schema:
                    ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k, "ontology_annotation",
                                                                      dict(annotationValue=pv))

                pv_dict = dict(parameterName=ontology_schema)
                pp_schema = d_utils.get_db_json_schema("protocol_parameter")

                for k in pp_schema:
                    if k == "@id":
                        pp_schema[k] = ISAHelpers().get_id_field("parameter", dict(
                            name=pv.replace(" ", "_")))

                    else:
                        pp_schema[k] = pv_dict.get(k,
                                                   ISAHelpers().get_schema_key_type(pp_schema.get(k, dict())))

                parameters.append(pp_schema)

            # components
            components = list()
            if pr.get("name", str()) == "nucleic acid sequencing":
                # get sequencing instrument attached datafiles
                seq_instruments = list(self.copo_isa_records["seq_instruments"])

                for si in seq_instruments:
                    ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                    for k in ontology_schema:
                        ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                          "ontology_annotation",
                                                                          dict(annotationValue="DNA sequencer"))

                    # get components properties
                    component_schema = d_utils.get_db_json_schema("protocol").get("components", dict()).get("items",
                                                                                                            dict()).get(
                        "properties", dict())
                    components_value_dict = dict(componentName=si,
                                                 componentType=ontology_schema)

                    for k in component_schema:
                        component_schema[k] = components_value_dict.get(k, ISAHelpers().get_schema_key_type(
                            component_schema.get(k, dict())))

                    components.append(component_schema)

            # protocolType
            ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
            for k in ontology_schema:
                ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                  "ontology_annotation",
                                                                  dict(annotationValue=pr.get("name", str())))

            protocol_type = ontology_schema

            value_dict = dict(
                name=pr.get("name", str()),
                parameters=parameters,
                components=components,
                protocolType=protocol_type
            )

            protocol_schema = d_utils.get_db_json_schema("protocol")
            for k in protocol_schema:
                if k == "@id":
                    protocol_schema[k] = ISAHelpers().get_id_field("protocol", dict(
                        name=pr.get("name", str()).replace(" ", "_")))
                else:
                    protocol_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(
                        protocol_schema.get(k, dict())))

            protocols.append(protocol_schema)

        return protocols

    def _materials(self, spec=dict()):
        sources = list(self.copo_isa_records["treated_source"])
        samples = list(self.copo_isa_records["treated_sample"])

        materials_value_dict = dict(sources=sources,
                                    samples=samples
                                    )

        materials_properties = spec.get("properties", dict())

        for k in materials_properties:
            materials_properties[k] = materials_value_dict.get(k, ISAHelpers().get_schema_key_type(
                materials_properties.get(k, dict())))

        return materials_properties

    def _processSequence(self, spec=dict()):
        process_sequence = list()

        samples = list(self.copo_isa_records["treated_sample"])

        # get executed protocol
        executes_protocol = [p for p in self._protocols(dict()) if "sample collection" in p.get("name")]
        id_part = str()
        if executes_protocol:
            id_part = (executes_protocol[0]["name"]).replace(" ", "_")
            executes_protocol = {"@id": executes_protocol[0]["@id"]}
        else:
            executes_protocol = dict()

        for indx, sample in enumerate(samples):
            value_dict = dict(
                executesProtocol=executes_protocol,
                inputs=sample.get("derivesFrom", list()),
                outputs=[{"@id": sample["@id"]}]
            )

            process_schema = d_utils.get_db_json_schema("process")
            for k in process_schema:
                if k == "@id":
                    process_schema[k] = ISAHelpers().get_id_field("process", dict(
                        name=id_part + str(indx + 1)))
                else:
                    process_schema[k] = value_dict.get(k,
                                                       ISAHelpers().get_schema_key_type(process_schema.get(k, dict())))

            process_sequence.append(process_schema)

        return process_sequence

    def _factors(self, spec=dict()):
        factors = list()
        seen_list = list()
        components = ["sample"]

        for component in components:
            component_list = list(self.copo_isa_records[component])
            for rec in component_list:
                for fv in rec.get("factorValues", list()):
                    cat_dict = fv.get("category", dict())
                    annotation_value = cat_dict.get("annotationValue", str())
                    if annotation_value and annotation_value.lower() not in seen_list:
                        ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                        for k in ontology_schema:
                            ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                              "ontology_annotation",
                                                                              cat_dict)
                        value_dict = dict(
                            factorName=annotation_value,
                            factorType=ontology_schema)

                        factor_schema = d_utils.get_db_json_schema("factor")
                        for k in factor_schema:
                            if k == "@id":
                                factor_schema[k] = ISAHelpers().get_id_field("factor",
                                                                             dict(
                                                                                 name=annotation_value.replace(
                                                                                     " ", "_")))
                            else:
                                factor_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(
                                    factor_schema.get(k, dict())))

                        factors.append(factor_schema)
                        seen_list.append(annotation_value.lower())

        return factors

    def _characteristicCategories(self, spec=dict()):
        characteristic_categories = list()
        seen_list = list()
        components = ["sample", "source"]

        for component in components:
            component_list = list(self.copo_isa_records[component])
            for rec in component_list:
                # get organism
                if "organism" in rec and "organism" not in seen_list:
                    ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                    for k in ontology_schema:
                        ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                          "ontology_annotation",
                                                                          dict(annotationValue="organism"))

                    value_dict = dict(characteristicType=ontology_schema)

                    material_attribute_schema = d_utils.get_db_json_schema("material_attribute")
                    for k in material_attribute_schema:
                        if k == "@id":
                            material_attribute_schema[k] = ISAHelpers().get_id_field("characteristic_category", dict(
                                name="organism"))
                        else:
                            material_attribute_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(
                                material_attribute_schema.get(k, dict())))

                    characteristic_categories.append(material_attribute_schema)
                    seen_list.append("organism")
                for ch in rec.get("characteristics", list()):
                    cat_dict = ch.get("category", dict())
                    annotation_value = cat_dict.get("annotationValue", str())
                    if annotation_value and annotation_value.lower() not in seen_list:
                        ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                        for k in ontology_schema:
                            ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                              "ontology_annotation",
                                                                              cat_dict)
                        value_dict = dict(characteristicType=ontology_schema)

                        material_attribute_schema = d_utils.get_db_json_schema("material_attribute")
                        for k in material_attribute_schema:
                            if k == "@id":
                                material_attribute_schema[k] = ISAHelpers().get_id_field("characteristic_category",
                                                                                         dict(
                                                                                             name=annotation_value.replace(
                                                                                                 " ", "_")))
                            else:
                                material_attribute_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(
                                    material_attribute_schema.get(k, dict())))

                        characteristic_categories.append(material_attribute_schema)
                        seen_list.append(annotation_value.lower())

        return characteristic_categories

    def _unitCategories(self, spec=dict()):
        unit_categories = list()
        seen_list = list()
        components = ["sample", "source"]

        for component in components:
            component_list = list(self.copo_isa_records[component])
            for rec in component_list:
                # get units from both characteristics and factors
                combined_list = rec.get("characteristics", list()) + rec.get("factorValues", list())
                for ch in combined_list:
                    # value...
                    # called up here mainly to [in]validate the 'unit' property
                    value_dict = ch.get("value", dict())
                    annotation_value = value_dict.get("annotationValue", str())
                    is_numeric = False
                    if annotation_value != "":
                        try:
                            annotation_value = float(annotation_value)
                            is_numeric = True
                        except ValueError:
                            pass

                    if is_numeric:
                        unit_cat = ch.get("unit", dict())
                        annotation_value = unit_cat.get("annotationValue", str())
                        if annotation_value != "" and annotation_value.lower() not in seen_list:
                            ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                            for k in ontology_schema:
                                if k == "@id":
                                    ontology_schema[k] = ISAHelpers().get_id_field("unit",
                                                                                   dict(
                                                                                       name=annotation_value.replace(
                                                                                           " ", "_")))
                                else:
                                    ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                                      "ontology_annotation",
                                                                                      unit_cat)

                            unit_categories.append(ontology_schema)
                            seen_list.append(annotation_value.lower())

        return unit_categories

    def _comments(self, spec=dict()):
        comments = d_utils.json_to_pytype(lookup.SRA_COMMENTS).get("properties", list())
        return comments

    def _publicReleaseDate(self, spec=dict()):
        return ISAHelpers().get_schema_key_type(spec)

    def _submissionDate(self, spec=dict()):
        return ISAHelpers().get_schema_key_type(spec)

    def _description(self, spec=dict()):
        return ISAHelpers().get_schema_key_type(spec)

    def _title(self, spec=dict()):
        # this property is set from the Profile record
        return self.copo_isa_records.get("profile").get("title", str())

    def _identifier(self, spec=dict()):
        return self.copo_isa_records.get("submission_token")

    def _filename(self, spec=dict()):
        filename = 's_' + self.copo_isa_records.get("submission_token") + '.txt'
        return filename


class Assay:
    def __init__(self, copo_isa_records=str()):
        self.copo_isa_records = copo_isa_records
        self.profile_id = str(self.copo_isa_records.get("profile").get("_id"))
        self.process_sequence = list()

    def get_schema(self):
        component = "assay"

        schemas = list()
        properties = d_utils.get_db_json_schema(component)

        if properties:
            for k in properties:
                if k == "@id":
                    record = dict(name=self.copo_isa_records.get("submission_token"))
                    properties[k] = ISAHelpers().get_id_field(component=component, record=record)
                else:
                    try:
                        properties[k] = getattr(Assay, "_" + k)(self, properties[k])
                    except Exception as e:
                        print(e)
                        properties[k] = ISAHelpers().get_schema_key_type(properties.get(k, dict()))

            schemas.append(properties)

        return schemas

    def _comments(self, spec=dict()):
        return ISAHelpers().get_schema_key_type(spec)

    def _filename(self, spec=dict()):
        filename = 'a_' + self.copo_isa_records.get("submission_token") + '.txt'
        return filename

    def _measurementType(self, spec=dict()):
        config_source = ISAHelpers().get_config_source(self.copo_isa_records.get("study_type"))
        measurement_type = ISAHelpers().get_assay_file_measurement(config_source)

        return measurement_type

    def _technologyType(self, spec=dict()):
        return self.copo_isa_records.get("technology_type")

    def _technologyPlatform(self, spec=dict()):
        # todo: need to find out how to set value for this property
        return ISAHelpers().get_schema_key_type(spec)

    def _dataFiles(self, spec=dict()):
        component = "datafile"
        datafiles = list(self.copo_isa_records["datafile"])

        # get datafiles from the submission record
        datafiles = [ISAHelpers().refactor_datafiles(element) for element in datafiles]
        datafiles = ISAHelpers().get_isa_records(component, datafiles)

        df = pd.DataFrame(datafiles)
        remote_path = d_utils.get_ena_remote_path(self.copo_isa_records.get("submission_token"))
        df["name"] = df["name"].apply(ISAHelpers().refactor_datafile_reference, args=(remote_path,))
        datafiles = df.to_dict('records')

        return datafiles

    def _materials(self, spec=dict()):
        samples = list(self.copo_isa_records["sample"])

        samps = list()
        other_materials = list()

        if samples:
            df = pd.DataFrame(samples)
            samps = list(df['name'].apply(ISAHelpers().refactor_sample_reference))
            other_materials = list(df['name'].apply(ISAHelpers().refactor_material))

        value_dict = dict(otherMaterials=other_materials,
                          samples=samps
                          )

        materials_properties = spec.get("properties", dict())

        for k in materials_properties:
            materials_properties[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(
                materials_properties.get(k, dict())))

        return materials_properties

    def _characteristicCategories(self, spec=dict()):
        characteristicCategories = list()
        return characteristicCategories

    def _unitCategories(self, spec=dict()):
        unitCategories = list()
        return unitCategories

    def _processSequence(self, spec=dict()):
        # get relevant protocols
        protocol_list_temp = list(self.copo_isa_records["protocol_list"])
        protocol_list_temp[:] = [d for d in protocol_list_temp if d.get('name') not in ["sample collection"]]

        # get pairing map, if it exists
        description_token = self.copo_isa_records["submission_record"].get("description_token", str())
        pairing_info = list()

        if description_token:
            pairing_info = Description().GET(description_token).get("attributes", dict()).get("datafiles_pairing",
                                                                                              list())
        pairing_info = pd.DataFrame(pairing_info)

        if len(pairing_info):
            pairing_info.columns = ["file1", "file2"]
            pairing_info['combined'] = pairing_info.file1 + "," + pairing_info.file2

        datafiles_df = pd.DataFrame(self.copo_isa_records["datafile"])
        datafiles_df._id = datafiles_df['_id'].astype(str)
        datafiles_df.index = datafiles_df._id
        datafiles_df['treated'] = 'false'
        datafiles_df['paired_status'] = datafiles_df['description'].apply(
            lambda x: x.get('attributes', dict()).get('library_construction', dict()).get('library_layout', str()))

        datafiles_df['paired_status'] = datafiles_df.paired_status.str.upper()

        # to avoid the risk of obfuscation of the file name, modify path to reflect actual saved name
        datafiles_df['file_location'] = datafiles_df['file_location'].apply(lambda x: os.path.split(x)[-1])
        datafiles_df["name"] = datafiles_df['file_location']

        indx = 0
        while True:
            if len(datafiles_df[datafiles_df['treated'] == 'false']) == 0:
                break

            indx = indx + 1
            self.get_assay_process_sequence(protocol_list_temp, indx, pairing_info, datafiles_df)

        return self.process_sequence

    def get_assay_process_sequence(self, protocol_list_temp, indx, pairing_info, datafiles_df):
        # get file...
        datafile = datafiles_df[datafiles_df.treated == 'false'].iloc[0].to_dict()
        datafiles_df.loc[datafile["_id"], 'treated'] = 'true'

        # get description attributes
        attributes = datafile.get("description", dict()).get("attributes", dict())
        datafile_samples = attributes.get("attach_samples", dict()).get("study_samples", list())

        samples = list()
        materials = list()

        if datafile_samples:
            datafile_samples = datafile_samples.split(",") if isinstance(datafile_samples, str) else datafile_samples
            copo_samples = self.copo_isa_records["sample"]
            df = pd.DataFrame(copo_samples)
            df = df[df['_id'].isin([ObjectId(element) for element in datafile_samples])]
            samples = list(df['name'].apply(ISAHelpers().refactor_sample_reference))
            materials = list(df['name'].apply(ISAHelpers().refactor_material_reference))

        protocol_list = list(protocol_list_temp)
        lookup_list = list(protocol_list_temp)
        for pr_indx, pr in enumerate(protocol_list):
            inputs = list()
            outputs = list()
            previous_process = dict()
            next_process = dict()
            comments = list()
            parameter_values = list()
            revised_name = pr.get("name", str()).replace(" ", "_")

            # set sample and extracts
            if revised_name in ["nucleic_acid_extraction"]:
                inputs = samples
                outputs = materials

            # set export
            if revised_name in ["nucleic_acid_sequencing", "library_construction"]:
                comment_schema = d_utils.get_db_json_schema("comment")
                for k in comment_schema:
                    comment_schema = ISAHelpers().resolve_schema_key(comment_schema, k,
                                                                     "comment",
                                                                     dict(name="Export", value="yes"))
                comments.append(comment_schema)

            # set datafile output
            if revised_name in ["nucleic_acid_sequencing"]:
                outputs.append({"@id": ISAHelpers().get_id_field("datafile", datafile)})

                # is this file paired
                if datafile["paired_status"] == "PAIRED" and len(pairing_info):
                    paired_data = [x for x in list(pairing_info['combined']) if datafile["_id"] in x]
                    if paired_data:
                        paired_data = paired_data[0].split(",")
                        paired_data.remove(datafile["_id"])
                        if paired_data[0] in datafiles_df.index:
                            paired_datafile = datafiles_df.loc[paired_data[0]].to_dict()
                            datafiles_df.loc[paired_data[0], 'treated'] = 'true'
                            outputs.append({"@id": ISAHelpers().get_id_field("datafile", paired_datafile)})

            if protocol_list[pr_indx - 1].get("name", str()).replace(" ", "_") == "nucleic_acid_extraction":
                inputs = materials

            # set previous...
            if pr_indx > 0:
                previous_name = lookup_list[pr_indx - 1].get("name", str()).replace(" ", "_")
                previous_process = {"@id": ISAHelpers().get_id_field("process",
                                                                     dict(name=previous_name + str(indx)))}
                # refine input
                if previous_name == "nucleic_acid_extraction":
                    inputs = materials

            # ...and next processes
            if (pr_indx + 1) < len(lookup_list):
                next_name = lookup_list[pr_indx + 1].get("name", str()).replace(" ", "_")

                if next_name == "nucleic_acid_sequencing":
                    # expose the experiment name here
                    next_name = "EXP"

                next_process = {"@id": ISAHelpers().get_id_field("process",
                                                                 dict(name=next_name + str(indx)))}

            # set parameter values
            for pv in pr.get("parameterValues", list()):
                pv = htags.trim_parameter_value_label(pv).lower()
                pv_revised_name = pv.replace(" ", "_")

                pv_value = attributes.get(revised_name, dict()).get(pv_revised_name)

                if pv_value is not None:
                    # represent string values as an ontology object
                    if isinstance(pv_value, str):
                        pv_value = dict(annotationValue=pv_value
                                        )

                    if isinstance(pv_value, dict):
                        ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                        for k in ontology_schema:
                            ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, k,
                                                                              "ontology_annotation",
                                                                              pv_value)

                        pv_value = ontology_schema

                    pv_dict = dict(
                        category={"@id": ISAHelpers().get_id_field("parameter", dict(name=pv_revised_name))},
                        value=pv_value
                    )

                    pp_schema = d_utils.get_db_json_schema("process_parameter_value")

                    for k in pp_schema:
                        pp_schema[k] = pv_dict.get(k,
                                                   ISAHelpers().get_schema_key_type(pp_schema.get(k, dict())))

                    # remove 'unit' from schema
                    if "unit" in pp_schema:
                        del pp_schema["unit"]

                    parameter_values.append(pp_schema)

            # set name
            name = pr.get("name", str()).replace(" ", "_") + str(indx)
            if revised_name == "nucleic_acid_sequencing":
                name = "EXP" + str(indx)

            # set value dictionary
            value_dict = dict(
                executesProtocol={"@id": ISAHelpers().get_id_field("protocol",
                                                                   dict(name=revised_name))},
                inputs=inputs,
                outputs=outputs,
                previousProcess=previous_process,
                nextProcess=next_process,
                parameterValues=parameter_values,
                comments=comments,
                name=name
            )

            # get process schema
            process_schema = d_utils.get_db_json_schema("process")
            for k in process_schema:
                if k == "@id":
                    process_schema[k] = ISAHelpers().get_id_field("process", dict(
                        name=name))
                else:
                    process_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(
                        process_schema.get(k, dict())))

            self.process_sequence.append(process_schema)


class treatedRecordThread(threading.Thread):
    def __init__(self, copo_records, component_name, component_records, all_derived_from=list()):
        threading.Thread.__init__(self)
        self.copo_records = copo_records
        self.component_name = component_name
        self.component_records = component_records
        self.all_derived_from = all_derived_from

    def run(self):
        self.get_treated_records()

    def get_treated_records(self):
        self.copo_records["isa_records_" + self.component_name] = ISAHelpers().get_isa_records(self.component_name,
                                                                                               self.component_records)
        self.copo_records["treated_" + self.component_name] = ISAHelpers().treat_record_characteristics(
            self.copo_records["isa_records_" + self.component_name],
            self.all_derived_from)


class renameRecordThread(threading.Thread):
    def __init__(self, copo_records, component_name, component_records):
        threading.Thread.__init__(self)
        self.copo_records = copo_records
        self.component_name = component_name
        self.component_records = component_records

    def run(self):
        self.get_renamed_records()

    def get_renamed_records(self):
        if self.component_records:
            df = pd.DataFrame(self.component_records)
            df["name"] = df["name"].apply(ISAHelpers().rename_it, args=(self.component_name,))
            records = df.to_dict('records')
            self.copo_records[self.component_name] = list(records)


class ISAHelpers:
    def broker_copo_records(self, submission_token=str()):
        profile_id = Submission().get_record(submission_token).get("profile_id", str())
        copo_records = dict()

        # submission_token
        copo_records["submission_token"] = submission_token
        copo_records["submission_record"] = DAComponent(component="submission").get_record(submission_token)

        # profile
        copo_records["profile"] = DAComponent(component="profile").get_record(profile_id)

        # publication
        copo_records["publication"] = DAComponent(profile_id=profile_id, component="publication").get_all_records()

        # person
        # check for sra person
        Person(profile_id=profile_id).create_sra_person()
        copo_records["person"] = DAComponent(profile_id=profile_id, component="person").get_all_records()

        # datafile and samples, sources, study_type and seq_instruments
        df_ids_list = copo_records["submission_record"].pop("bundle", list())

        df_ids_object_list = [ObjectId(element) for element in df_ids_list]
        datafiles = cursor_to_list(
            DataFile().get_collection_handle().find({"_id": {"$in": df_ids_object_list}},
                                                    {"file_location": 1,
                                                     "description.attributes": 1,
                                                     "name": 1,
                                                     "type": 1,
                                                     "file_hash": 1}))

        # ...this, to correct file names being modified by the system
        df = pd.DataFrame(datafiles)
        df["name"] = df["file_location"].apply(ISAHelpers().refactor_datafile_name)
        copo_records["datafile"] = df.to_dict('records')

        copo_records["datafilehashes"] = self.get_datafilehashes(copo_records["datafile"],
                                                                 submission_token)

        # sample... contingent on datafiles
        attach_samples = list()
        for x in copo_records["datafile"]:
            samp = x.get("description", dict()).get("attributes", dict()).get('attach_samples', dict()).get(
                'study_samples', list())
            if isinstance(samp, str):
                attach_samples.extend(samp.split(","))
            elif isinstance(samp, list):
                attach_samples.extend(samp)

        attach_samples = set(attach_samples)  # get unique samples
        object_list = [ObjectId(sample_id) for sample_id in attach_samples]

        copo_records["sample"] = list()
        samples = cursor_to_list(Sample().get_collection_handle().find({"_id": {"$in": object_list}}))

        # source
        # source...dependent on samples
        derived_list = list()
        for s in samples:
            derived_list = derived_list + s.get("derivesFrom", list())

        derived_list = list(set(derived_list))  # unique elements
        derived_list = [ObjectId(element) for element in derived_list]
        copo_records["source"] = list()
        sources = cursor_to_list(
            DAComponent(component="source").get_collection_handle().find({"_id": {"$in": derived_list}}))

        # rename sample and sources
        thread_rename_sample = renameRecordThread(copo_records, "sample", samples)
        thread_rename_source = renameRecordThread(copo_records, "source", sources)

        thread_rename_sample.start()
        thread_rename_source.start()
        thread_rename_sample.join()
        thread_rename_source.join()

        # study_type
        copo_records["study_type"] = self.get_study_type(df_ids_list)

        # seq_instruments
        seq_instruments = [
            x.get("description", dict()).get("attributes", dict()).get('nucleic_acid_sequencing', dict()).get(
                'sequencing_instrument',
                str()) for x in
            copo_records["datafile"]]
        copo_records["seq_instruments"] = list(set(seq_instruments))

        # technology_type
        copo_records["technology_type"] = self.get_assay_file_technology(
            self.get_config_source(copo_records["study_type"]))

        # protocol_list
        protocol_list = self.get_protocols_parameter_values(copo_records["study_type"])

        # remove non-relevant protocols from the list
        protocol_list[:] = [d for d in protocol_list if d.get('name') not in ["dummy", "sequence assembly",
                                                                              "sequence analysis data transformation"]]
        copo_records["protocol_list"] = protocol_list

        # treated records...
        # make a copy of the dictionary before embarking on treated records to preserve their originality
        copo_records_temp = copy.deepcopy(copo_records)

        thread_treated_sample = treatedRecordThread(copo_records, "sample", copo_records["sample"],
                                                    copo_records["source"])
        thread_treated_source = treatedRecordThread(copo_records, "source", copo_records["source"],
                                                    copo_records["source"])

        thread_treated_sample.start()
        thread_treated_source.start()
        thread_treated_sample.join()
        thread_treated_source.join()

        copo_records["sample"] = copo_records_temp["sample"]
        copo_records["source"] = copo_records_temp["source"]
        copo_records["datafile"] = copo_records_temp["datafile"]

        return copo_records

    def get_datafilehashes(self, datafiles, submission_token):
        datafilehashes = dict()

        df = pd.DataFrame(datafiles)
        remote_path = d_utils.get_ena_remote_path(submission_token)
        df["name"] = df["name"].apply(ISAHelpers().refactor_datafile_reference, args=(remote_path,))
        datafiles = df.to_dict('records')

        for df in datafiles:
            datafilehashes[df["name"]] = df["file_hash"]

        return datafilehashes

    def get_study_type(self, datafile_ids=list()):
        study_type = str()

        if datafile_ids:
            study_type = DataFile().get_record_property(datafile_ids[0], "study_type")

        if study_type:
            return study_type
        else:
            raise KeyError("Study type not found!")

    def get_assay_file_technology(self, config_source=str()):
        properties = dict()

        output_dict = d_utils.get_isa_schema_xml(config_source)

        if output_dict.get("status", str()) == "success":
            tree = output_dict.get("content")
            root = tree.getroot()

            # get the namespace of the xml document
            ns = self.namespace(root)

            # get technology details
            fields = tree.findall(".//{%s}technology" % ns)

            for t in iter(fields):
                value_dict = dict(annotationValue=t.get("term-label", str()),
                                  termAccession=t.get("term-accession", str()),
                                  termSource=t.get("source-abbreviation", str())
                                  )

                if value_dict:
                    component = "ontology_annotation"

                    isa_schema = d_utils.get_db_json_schema(component)
                    for k in isa_schema:
                        isa_schema = ISAHelpers().resolve_schema_key(isa_schema, k, component, value_dict)

                    properties = isa_schema

        return properties

    def get_assay_file_measurement(self, config_source=str()):
        properties = dict()

        output_dict = d_utils.get_isa_schema_xml(config_source)

        if output_dict.get("status", str()) == "success":
            tree = output_dict.get("content")
            root = tree.getroot()

            # get the namespace of the xml document
            ns = self.namespace(root)

            # get measurement details
            fields = tree.findall(".//{%s}measurement" % ns)

            value_dict = dict()

            for t in iter(fields):
                value_dict = dict(annotationValue=t.get("term-label", str()),
                                  termAccession=t.get("term-accession", str()),
                                  termSource=t.get("source-abbreviation", str())
                                  )

            if value_dict:
                component = "ontology_annotation"

                isa_schema = d_utils.get_db_json_schema(component)
                for k in isa_schema:
                    isa_schema = ISAHelpers().resolve_schema_key(isa_schema, k, component, value_dict)

                properties = isa_schema

        return properties

    def namespace(self, element):
        match = re.search(r'\{(.+)\}', element.tag)
        return match.group(1) if match else ''

    def get_config_source(self, study_type):
        config_source = None
        v = [x for x in lookup.DROP_DOWNS['STUDY_TYPES'] if x["value"].lower() == study_type.lower()]

        if v:
            v = v[0]
            if "config_source" in v:
                config_source = v.get("config_source")

        if config_source:
            return config_source
        else:
            raise KeyError("Couldn't get config source for study_type: " + study_type)

    def get_protocols_parameter_values(self, study_type=str()):
        # filters protocols based on the presence of parameter values

        protocols = ISAHelpers().get_study_protocols() + ISAHelpers().get_assay_protocols(study_type)

        for pr in protocols:
            for pv in list(pr["parameterValues"]):
                if not pv.startswith("Parameter Value"):
                    pr["parameterValues"].remove(pv)

        return protocols

    def get_all_protocols(self, study_type=str()):
        all_protocols = self.get_study_protocols() + self.get_assay_protocols(study_type)

        return all_protocols

    def get_assay_protocols(self, study_type=str()):
        protocol_list = []

        # get configuration, given study type
        config_source = str()
        if study_type:
            config_source = ISAHelpers().get_config_source(study_type)

        output_dict = d_utils.get_isa_schema_xml(config_source)

        if output_dict.get("status", str()) == "success":
            tree = output_dict.get("content")
            root = tree.getroot()

            # create a dummy protocol and add to the list, a work-around for dealing with dangling parameters
            dummy_protocol = dict(name="dummy", parameterValues=list())
            protocol_list.append(dummy_protocol)

            for child in list(root[0]):
                tag = child.tag.split("}")[-1]
                if tag == "protocol-field":
                    protocol_list.append(dict(name=child.attrib.get("protocol-type", str()), parameterValues=list()))
                elif tag == "field":
                    # get parent protocol
                    protocol_list[-1].get("parameterValues").append(child.attrib.get("header", str()))

            # remove dummy protocol
            protocol_list[:] = [d for d in protocol_list if d.get('name') != "dummy"]

        return protocol_list

    def get_study_protocols(self):
        protocol_list = []

        config_source = "study_sample.xml"

        output_dict = d_utils.get_isa_schema_xml(config_source)

        if output_dict.get("status", str()) == "success":
            tree = output_dict.get("content")
            root = tree.getroot()

            # create a dummy protocol and add to the list, a work-around for dealing with dangling parameters
            dummy_protocol = dict(name="dummy", parameterValues=list())
            protocol_list.append(dummy_protocol)

            for child in list(root[0]):
                tag = child.tag.split("}")[-1]
                if tag == "protocol-field":
                    protocol_list.append(dict(name=child.attrib.get("protocol-type", str()), parameterValues=list()))
                elif tag == "field":
                    # get parent protocol
                    protocol_list[-1].get("parameterValues").append(child.attrib.get("header", str()))

        return protocol_list

    def get_isa_records(self, component, records=list()):
        isa_records = list()

        for rec in records:
            isa_schema = d_utils.get_db_json_schema(component)

            # handle organism property in source
            if component == "source":
                # get organism and add to characteristics
                ontology_schema = d_utils.get_db_json_schema("ontology_annotation")
                for onto in ontology_schema:
                    ontology_schema = ISAHelpers().resolve_schema_key(ontology_schema, onto,
                                                                      "ontology_annotation",
                                                                      dict(annotationValue="organism"))

                # conform to the ontology schema
                value_dict = dict(category=ontology_schema, value=rec.get("organism", dict()))

                material_attribute_schema = d_utils.get_db_json_schema("material_attribute_value")
                for onto in material_attribute_schema:
                    material_attribute_schema = ISAHelpers().resolve_schema_key(material_attribute_schema, onto,
                                                                                "material_attribute_value",
                                                                                value_dict)

                rec["characteristics"].append(material_attribute_schema)

            for k in isa_schema:
                isa_schema = ISAHelpers().resolve_schema_key(isa_schema, k, component, rec)

            isa_records.append(isa_schema)

        return isa_records

    def treat_record_characteristics(self, records, all_derived_from=list()):
        """
        given records with associated characteristics, factorValues, derivesFrom properties, make such are isa-record-ready
        :param records:
        :return: treated records
        """
        ch_records = records
        for rec in ch_records:
            attributes_dict = dict()
            if "characteristics" in rec:
                attributes_dict["characteristics"] = dict(component="characteristic_category",
                                                          records=rec.get("characteristics", list()))

            if "factorValues" in rec:
                attributes_dict["factorValues"] = dict(component="factor", records=rec.get("factorValues", list()))

            for k in attributes_dict:
                for ch in attributes_dict[k]["records"]:
                    # category
                    cat_dict = ch.get("category", dict())
                    annotation_value = cat_dict.get("annotationValue", str())
                    if annotation_value != "":
                        # reference category by ID
                        annotation_value = ISAHelpers().get_id_field(attributes_dict[k]["component"],
                                                                     dict(name=annotation_value.replace(" ", "_")))
                        ch["category"] = {"@id": annotation_value}

                    # unit
                    unit_dict = ch.get("unit", dict())
                    if unit_dict:
                        if not bool([a for a in unit_dict.values() if a]):
                            ch["unit"] = dict()
                        else:
                            annotation_value = unit_dict.get("annotationValue", str())
                            if annotation_value != "":
                                # reference unit by ID
                                annotation_value = ISAHelpers().get_id_field("unit",
                                                                             dict(name=annotation_value.replace(" ",
                                                                                                                "_")))
                                ch["unit"] = {"@id": annotation_value}

                    # value...
                    # called up here mainly to [in]validate 'unit' property
                    value_dict = ch.get("value", dict())
                    annotation_value = value_dict.get("annotationValue", str())
                    is_numeric = False

                    if annotation_value != "":
                        try:
                            annotation_value = float(annotation_value)
                            is_numeric = True
                        except ValueError:
                            pass

                    if is_numeric:
                        ch["value"] = annotation_value
                    else:
                        if "unit" in ch:
                            del ch["unit"]

                rec[k] = attributes_dict[k]["records"]

            # treat derivesFrom
            derived_list = rec.get("derivesFrom", list())
            if derived_list:
                df = pd.DataFrame(all_derived_from)
                df = df[df['_id'].isin([ObjectId(element) for element in derived_list])]
                rec["derivesFrom"] = list(df['name'].apply(ISAHelpers().refactor_source_reference))

        return ch_records

    def get_object_instances(self, obj=None, target_record_list=list(), target_object_keys=set()):
        if isinstance(obj, dict) and set(obj.keys()) == target_object_keys:
            target_record_list.append(obj)
        else:
            if isinstance(obj, dict):
                for k_dict in obj:
                    ISAHelpers().get_object_instances(obj[k_dict], target_record_list, target_object_keys)
            elif isinstance(obj, list):
                for k_list in obj:
                    ISAHelpers().get_object_instances(k_list, target_record_list, target_object_keys)

        return target_record_list

    def get_key_instances(self, obj=None, target_record_list=list(), target_object_key=str()):
        if isinstance(obj, dict) and target_object_key in obj:
            obj = copy.deepcopy(obj)
            target_record_list.append(obj.pop(target_object_key))

        if isinstance(obj, dict) or isinstance(obj, list):
            for k in obj:
                if isinstance(obj, dict):
                    new_obj = obj[k]
                else:
                    new_obj = k
                ISAHelpers().get_key_instances(new_obj, target_record_list, target_object_key)

        return target_record_list

    def get_schema_key_type(self, fragment):
        json_type = "string"
        keywords = ["anyOf", "allOf", "oneOf"]

        if isinstance(fragment, dict):
            if "type" in fragment:
                json_type = fragment["type"]
            elif "$ref" in fragment:
                json_type = "object"
            else:
                for kw in keywords:
                    if kw in fragment:
                        kw_type = fragment[kw]
                        if len(kw_type) > 0:
                            kw_type = kw_type[0]
                            if isinstance(kw_type, dict):
                                if "type" in kw_type:
                                    json_type = kw_type["type"]
                                    break

        return d_utils.default_jsontype(json_type)

    def resolve_schema_key(self, schema_dict=dict(), schema_field=str(), component=str(), record=dict()):
        """
        function resolve schema attributes, making sure the provided record conforms to the specification of the schema
        NB: this function assumes the schema_dict is JSON Schema compliant
        :param schema_dict: schema 'properties' that informs the record resolution. must be JSON Schema compliant!
        :param schema_field: field to be resolved to
        :param component: e.g., publication, source, sample
        :param record: associated record to component
        :return: resolved_value: value of schema_field resolved
        """

        copo_schema = d_utils.get_copo_schema(component)
        isa_schema = d_utils.get_db_json_schema(component)
        default_value = self.get_schema_key_type(isa_schema.get(schema_field, dict()))
        resolved_value = default_value

        if schema_field == "@id":
            schema_dict[schema_field] = ISAHelpers().get_id_field(component, record)
            return schema_dict
        else:
            for f in copo_schema:
                if schema_field == f["versions"][-1]:
                    static_id = f["id"].split(".")[-1]  # the field known and stored in COPO
                    resolved_value = record.get(static_id)

                    # handle object type fields e.g., ontology term, comment
                    if resolved_value:
                        object_type_control = d_utils.object_type_control_map().get(f["control"].lower(), str())
                        if object_type_control:
                            if f["type"] == "array":
                                for indx, val_dict in enumerate(resolved_value):
                                    isa_schema_2 = d_utils.get_db_json_schema(object_type_control)
                                    for k_2 in isa_schema_2:
                                        isa_schema_2 = ISAHelpers().resolve_schema_key(isa_schema_2, k_2,
                                                                                       object_type_control,
                                                                                       val_dict)
                                    resolved_value[indx] = isa_schema_2
                            else:
                                isa_schema = d_utils.get_db_json_schema(object_type_control)
                                for k in isa_schema:
                                    isa_schema = ISAHelpers().resolve_schema_key(isa_schema, k,
                                                                                 object_type_control,
                                                                                 resolved_value)

                                resolved_value = isa_schema
            schema_dict[schema_field] = resolved_value if resolved_value else default_value

            return schema_dict

    def rename_it(self, x, args):
        return args + "-" + x

    def refactor_sample_reference(self, x):
        return {"@id": self.get_id_field("sample", dict(name=x))}

    def refactor_datafile_reference(self, x, args):
        return os.path.join(args, x)

    def refactor_datafile_name(self, x):
        return os.path.join(os.path.split(x)[-1])

    def refactor_source_reference(self, x):
        return {"@id": self.get_id_field("source", dict(name=x))}

    def refactor_ontology_source_references(self, x):
        component = "ontology_source_reference"
        # get ontology base uri
        base_url = lookup.ONTOLOGY_LKUPS.get("ontology_file_uri", str())

        value_dict = dict(
            name=x,
            file=base_url + x
        )

        osr_schema = d_utils.get_db_json_schema(component)
        for k in osr_schema:
            if k == "@id":
                osr_schema[k] = ISAHelpers().get_id_field(component, dict(
                    name=x))
            else:
                osr_schema[k] = value_dict.get(k, ISAHelpers().get_schema_key_type(osr_schema.get(k, dict())))

        return osr_schema

    def refactor_material(self, x):
        x = x[7:] if x[:7] == "sample-" else x

        material_name = "extract-" + x

        other_material_properties = d_utils.get_db_json_schema("material")

        material_type = other_material_properties.get("type", dict()).get("enum", list())
        if isinstance(material_type, list) and len(material_type) > 0:
            material_type = material_type[0]

        other_material_value_dict = {
            "@id": self.get_id_field(component="material", record=dict(name=material_name)),
            "name": material_name,
            "type": material_type
        }

        for k in other_material_properties:
            other_material_properties[k] = other_material_value_dict.get(k, self.get_schema_key_type(
                other_material_properties.get(k, dict())))

        return other_material_properties

    def refactor_material_reference(self, x):
        x = x[7:] if x[:7] == "sample-" else x

        material_name = "extract-" + x
        return {"@id": self.get_id_field("material", dict(name=material_name))}

    def refactor_datafiles(self, datafile):
        # set export flag
        comment_schema = d_utils.get_db_json_schema("comment")
        for k in comment_schema:
            comment_schema = ISAHelpers().resolve_schema_key(comment_schema, k,
                                                             "comment",
                                                             dict(name="Export", value="yes"))

        datafile.get("comments", list()).append(comment_schema)
        return datafile

    def get_id_field(self, component, record=dict()):
        _id = str(record.get("_id", str()))
        name = str(record.get("name", str())).lower()

        id_dict = dict(
            publication="#" + component + "/" + _id,
            person="#" + component + "/" + _id,
            sample="#" + component + "/" + name,
            source="#" + component + "/" + name,
            material="#" + component + "/" + name,
            investigation="#" + component + "/" + name,
            ontology_annotation=str(),
            study="#" + component + "/" + name,
            assay="#" + component + "/" + name,
            protocol="#" + component + "/" + name,
            parameter="#" + component + "/" + name,
            characteristic_category="#" + component + "/" + name,
            unit="#" + component + "/" + name,
            factor="#" + component + "/" + name,
            process="#" + component + "/" + name,
            datafile="#" + "data/rawdatafile" + "-" + name,
            ontology_source_reference=str()
        )

        return id_dict.get(component, str())

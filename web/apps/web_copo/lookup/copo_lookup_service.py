__author__ = 'etuka'

import os
import pandas as pd
from bson import ObjectId
from dal import cursor_to_list
from dal.copo_da import Sample, Source, CGCore, Submission
from dal.mongo_util import get_collection_ref
from web.apps.web_copo.lookup.resolver import RESOLVER
import web.apps.web_copo.schemas.utils.data_utils as d_utils

"""
class is a service for the resolution of search terms to local objects in COPO. 
Each resolver should provide a mechanism for:
1. resolving a search term to valid objects
2. resolving accessions (i.e., id, values, etc.) to obtain matching or corresponding objects
"""

Lookups = get_collection_ref("Lookups")


class COPOLookup:
    def __init__(self, **kwargs):
        self.param_dict = kwargs
        self.search_term = self.param_dict.get("search_term", str()).lower()
        self.accession = self.param_dict.get("accession", dict())
        self.data_source = self.param_dict.get("data_source", str())
        self.profile_id = self.param_dict.get("profile_id", str())
        self.referenced_field = self.param_dict.get("referenced_field", str())
        self.drop_downs_pth = RESOLVER['copo_drop_downs']

    def broker_component_search(self):
        dispatcher = {
            'agrovoclabels': self.get_lookup_type,
            'countrieslist': self.get_lookup_type,
            'mediatypelabels': self.get_lookup_type,
            'fundingbodies': self.get_lookup_type,
            'cg_dependency_lookup': self.cg_dependency_lookup,
            'isa_samples_lookup': self.get_isasamples,
            'sample_source_lookup': self.get_samplesource,
            'all_samples_lookup': self.get_allsamples,
            'run_lookup': self.get_runs,
            'study_lookup': self.get_studies,
            'experiment_lookup': self.get_experiments,
            'sample_lookup': self.get_samples
        }

        result = []
        message = 'error'

        if self.data_source in dispatcher:
            try:
                result = dispatcher[self.data_source]()
                message = 'success'
            except Exception as e:
                exception_message = "Error brokering component search. " + str(e)
                print(exception_message)
                raise

        return dict(result=result, message=message)

    def broker_data_source(self):
        """
        function resolves dropdown list given a data source handle
        :return:
        """

        pths_map = dict(
            select_yes_no=os.path.join(self.drop_downs_pth, 'select_yes_no.json'),
            select_start_end=os.path.join(self.drop_downs_pth, 'select_start_end.json'),
            cgiar_centres=os.path.join(self.drop_downs_pth, 'cgiar_centres.json'),
            crp_list=os.path.join(self.drop_downs_pth, 'crp_list.json'),
            languagelist=os.path.join(self.drop_downs_pth, 'language_list.json'),
            library_strategy=os.path.join(self.drop_downs_pth, 'library_strategy.json'),
            library_source=os.path.join(self.drop_downs_pth, 'library_source.json'),
            library_selection=os.path.join(self.drop_downs_pth, 'library_selection.json'),
            sequencing_instrument=os.path.join(self.drop_downs_pth, 'sequencing_instrument.json'),
            figshare_category_options=d_utils.get_figshare_category_options(),
            figshare_article_options=d_utils.get_figshare_article_options(),
            figshare_publish_options=d_utils.get_figshare_publish_options(),
            figshare_license_options=d_utils.get_figshare_license_options(),
            study_type_options=d_utils.get_study_type_options(),
            rooting_medium_options=d_utils.get_rooting_medium_options(),
            growth_area_options=d_utils.get_growth_area_options(),
            nutrient_control_options=d_utils.get_nutrient_control_options(),
            watering_control_options=d_utils.get_watering_control_options(),
            dataverse_subject_dropdown=d_utils.get_dataverse_subject_dropdown(),
            repository_options=os.path.join(self.drop_downs_pth, 'metadata_template_types.json'),
            repository_types_list=os.path.join(self.drop_downs_pth, 'repository_types.json'),
            sample_type_options=os.path.join(self.drop_downs_pth, 'sample_types.json'),
        )

        data = pths_map.get(self.data_source, str())

        if isinstance(data, str) and data:  # it's only a path, resolve to get actual data
            data = d_utils.json_to_pytype(data)

        return data

    def get_lookup_type(self):
        projection = dict(label=1, accession=1, description=1)
        filter_by = dict(type=self.data_source)

        records = list()

        if self.accession or self.search_term:
            if self.accession:
                bn = list()
                bn.append(self.accession) if isinstance(self.accession, str) else bn.extend(self.accession)
                filter_by["accession"] = {'$in': bn}
            elif self.search_term:
                filter_by["label"] = {'$regex': self.search_term, "$options": 'i'}

            records = cursor_to_list(Lookups.find(filter_by, projection))

            if not records and self.search_term:
                del filter_by["label"]
                records = cursor_to_list(Lookups.find(filter_by, projection))

        return records

    def get_samplesource(self):
        """
        lookup sources related to a sample
        :return:
        """
        import web.apps.web_copo.templatetags.html_tags as htags

        df = pd.DataFrame()

        if self.accession:
            if isinstance(self.accession, str):
                self.accession = self.accession.split(",")

            object_ids = [ObjectId(x) for x in self.accession if x.strip()]
            records = cursor_to_list(Source().get_collection_handle().find({"_id": {"$in": object_ids}}))

            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df['name']
                df['desc'] = df['accession'].apply(lambda x: htags.generate_attributes("source", x))
                df['description'] = df['desc'].apply(lambda x: self.format_description(x))
                df['server-side'] = True  # ...to request callback to server for resolving item description
        elif self.search_term:
            projection = dict(name=1)
            filter_by = dict()
            filter_by["name"] = {'$regex': self.search_term, "$options": 'i'}

            sort_by = 'name'
            sort_direction = -1

            records = Source(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                 projection=projection,
                                                                                 sort_by=sort_by,
                                                                                 sort_direction=sort_direction)

            if not records:
                # try getting all records
                del filter_by["name"]
                records = Source(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                     projection=projection,
                                                                                     sort_by=sort_by,
                                                                                     sort_direction=sort_direction)

            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df['name']
                df['description'] = ''
                df['server-side'] = True  # ...to request callback to server for resolving item description

        result = list()

        if not df.empty:
            df = df[['accession', 'label', 'description', 'server-side']]
            result = df.to_dict('records')

        return result

    def cg_dependency_lookup(self):
        """
        lookup for cgcore dependent components
        :return:
        """
        import web.apps.web_copo.templatetags.html_tags as htags

        result = list()
        df = pd.DataFrame()
        dependent_record_label = 'copo_name'

        if self.accession:
            if isinstance(self.accession, str):
                self.accession = self.accession.split(",")

            object_ids = [ObjectId(x) for x in self.accession if x.strip()]
            records = cursor_to_list(CGCore().get_collection_handle().find({"_id": {"$in": object_ids}}))
            result = list()

            if records:
                for record in records:
                    referenced_field = record.get("dependency_id", str())
                    kwargs = dict()
                    kwargs["referenced_field"] = referenced_field
                    schema = CGCore().get_component_schema(**kwargs)

                    label = record.get(dependent_record_label, str())

                    # modify schema before generating description
                    schema = [x for x in schema if
                              'dependency' in x and x['dependency'] == referenced_field and x.get("show_in_table",
                                                                                                  True)]
                    resolved = htags.resolve_display_data(schema, record)
                    description = self.format_description(resolved)

                    item_dict = dict(accession=str(record["_id"]),
                                     label=label,
                                     description=description)
                    item_dict['server-side'] = True  # ...to request callback to server for resolving item description

                    result.append(item_dict)
        elif self.search_term:
            referenced_field = self.referenced_field
            filter_name = dependent_record_label
            projection = {filter_name: 1}
            filter_by = dict(dependency_id=referenced_field)
            filter_by[filter_name] = {'$regex': self.search_term, "$options": 'i'}

            sort_by = filter_name
            sort_direction = -1

            records = CGCore(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                 projection=projection,
                                                                                 sort_by=sort_by,
                                                                                 sort_direction=sort_direction)

            if not records:
                # try getting all records
                del filter_by[filter_name]
                records = CGCore(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                     projection=projection,
                                                                                     sort_by=sort_by,
                                                                                     sort_direction=sort_direction)
            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df[filter_name]
                df['description'] = ''
                df['server-side'] = True  # ...to request callback to server for resolving item description

        if not df.empty:
            df = df[['accession', 'label', 'description', 'server-side']]
            result = df.to_dict('records')

        return result

    def get_isasamples(self):
        """
        lookup for ISA-based (COPO standard) samples
        :return:
        """

        import web.apps.web_copo.templatetags.html_tags as htags

        df = pd.DataFrame()

        if self.accession:
            if isinstance(self.accession, str):
                self.accession = self.accession.split(",")

            object_ids = [ObjectId(x) for x in self.accession if x.strip()]
            records = cursor_to_list(Sample().get_collection_handle().find({"_id": {"$in": object_ids}}))

            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df['name']
                df['desc'] = df['accession'].apply(lambda x: htags.generate_attributes("sample", x))
                df['description'] = df['desc'].apply(lambda x: self.format_description(x))
                df['server-side'] = True  # ...to request callback to server for resolving item description

        elif self.search_term:
            projection = dict(name=1)
            filter_by = dict(sample_type="isasample")
            filter_by["name"] = {'$regex': self.search_term, "$options": 'i'}

            sort_by = 'name'
            sort_direction = -1

            records = Sample(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                 projection=projection,
                                                                                 sort_by=sort_by,
                                                                                 sort_direction=sort_direction)
            if not records:
                # try getting all records
                del filter_by['name']
                records = Sample(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                     projection=projection,
                                                                                     sort_by=sort_by,
                                                                                     sort_direction=sort_direction)
            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df['name']
                df['description'] = ''
                df['server-side'] = True  # ...to request callback to server for resolving item description

        result = list()

        if not df.empty:
            df = df[['accession', 'label', 'description', 'server-side']]
            result = df.to_dict('records')

        return result

    def get_allsamples(self):
        """
        lookup for all samples irrespective of sample type
        :return:
        """

        import web.apps.web_copo.templatetags.html_tags as htags

        df = pd.DataFrame()

        if self.accession:
            if isinstance(self.accession, str):
                self.accession = self.accession.split(",")

            object_ids = [ObjectId(x) for x in self.accession if x.strip()]
            records = cursor_to_list(Sample().get_collection_handle().find({"_id": {"$in": object_ids}}))

            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df['name']
                df['desc'] = df['accession'].apply(lambda x: htags.generate_attributes("sample", x))
                df['description'] = df['desc'].apply(lambda x: self.format_description(x))
                df['server-side'] = True  # ...to request callback to server for resolving item description
        elif self.search_term:
            projection = dict(name=1)
            filter_by = dict()
            filter_by["name"] = {'$regex': self.search_term, "$options": 'i'}

            sort_by = 'name'
            sort_direction = -1

            records = Sample(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                 projection=projection,
                                                                                 sort_by=sort_by,
                                                                                 sort_direction=sort_direction)
            if not records:
                # try getting all records
                del filter_by['name']
                records = Sample(profile_id=self.profile_id).get_all_records_columns(filter_by=filter_by,
                                                                                     projection=projection,
                                                                                     sort_by=sort_by,
                                                                                     sort_direction=sort_direction)

            if records:
                df = pd.DataFrame(records)
                df['accession'] = df._id.astype(str)
                df['label'] = df['name']
                df['description'] = ''
                df['server-side'] = True  # ...to request callback to server for resolving item description

        result = list()

        if not df.empty:
            df = df[['accession', 'label', 'description', 'server-side']]
            result = df.to_dict('records')

        return result

    def format_description(self, desc):
        html = """<table style="width:100%">"""
        for col in desc['columns']:
            html += "<tr><td>{}</td>".format(col['title'])
            html += "<td>{}</td>".format(desc['data_set'][col['data']])
            html += "</tr>"
        html += "</table>"

        return html

    def get_runs(self):
        existing_sub = Submission().get_records_by_field("profile_id", self.profile_id)
        df = pd.DataFrame()


        existing_accessions = ""
        accession_set = []
        if existing_sub:
            existing_accessions = existing_sub[0].get("accessions", "")
        if  existing_accessions:
            runs = existing_accessions.get("run", "")
            if runs:
                for run in runs:
                    if run.get("accession", ""):
                       accession_set.append(run.get("accession", ""))
                        
        if accession_set:
            df = pd.DataFrame(accession_set)
            df['accession'] = accession_set
            df['label'] = accession_set
            df['description'] = ''
            df['server-side'] = False  # ...to request callback to server for resolving item description

        result = df.to_dict('records')
        return result


    def get_studies(self):
        existing_sub = Submission().get_records_by_field("profile_id", self.profile_id)
        df = pd.DataFrame()

        existing_accessions = ""
        accession_set = []
        study_accession = ""
        if existing_sub:
            existing_accessions = existing_sub[0].get("accessions", "")
        if  existing_accessions:
            study = existing_accessions.get("project", "")
            if study:
                if isinstance(study, dict):
                    study_accession = study.get("accession", "")
                elif isinstance(study, list):
                    study_accession = study[0].get("accession", "")          
        accession_set.append(study_accession)                
        if accession_set:
            df = pd.DataFrame(accession_set)
            df['label'] = df["accession"]
            df['description'] = ''
            df['server-side'] = False  # ...to request callback to server for resolving item description

        result = df.to_dict('records')
        return result
    
    def get_experiments(self):
        existing_sub = Submission().get_records_by_field("profile_id", self.profile_id)
        df = pd.DataFrame()
        existing_accessions = ""
        accession_set = []
        if existing_sub:
            existing_accessions = existing_sub[0].get("accessions", "")
        if  existing_accessions:
            experiments = existing_accessions.get("experiment", "")
            if experiments:
                for experiment in experiments:
                    if experiment.get("accession", ""):
                       accession_set.append(experiment.get("accession", ""))
                        
        if accession_set:
            df = pd.DataFrame(accession_set)
            df['label'] = df["accession"]
            df['description'] = ''
            df['server-side'] = False  # ...to request callback to server for resolving item description

        result = df.to_dict('records')
        return result

    def get_samples(self):
        existing_sub = Submission().get_records_by_field("profile_id", self.profile_id)
        df = pd.DataFrame()

        existing_accessions = ""
        accession_set = []
        if existing_sub:
            samples = existing_accessions.get("sample", "")
            if samples:
                for sample in samples:
                    if sample.get("sample_accession", ""):
                        accession_set.append(sample.get("sample_accession", ""))
                        
        if accession_set:
            df = pd.DataFrame(accession_set)
            df['label'] = df["accession"]
            df['description'] = ''
            df['server-side'] = False  # ...to request callback to server for resolving item description

        result = df.to_dict('records')
        return result
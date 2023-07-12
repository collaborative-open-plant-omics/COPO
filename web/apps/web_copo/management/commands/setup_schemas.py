""" module generates schemas and lookups used in dropdowns """
__author__ = 'etuka'
__updated__ = 'fshaw'

import glob
import json
import os
import xml.etree.ElementTree as ET
import pandas as pd
import web.apps.web_copo.schemas.utils.data_utils as d_utils
from django.core.management.base import BaseCommand
from exceptions_and_logging.logger import Logger
from dal.copo_base_da import DataSchemas
from dal.mongo_util import get_collection_ref
from web.apps.web_copo.lookup.resolver import RESOLVER
from web.apps.web_copo.schemas.utils.data_formats import DataFormats

Schemas = get_collection_ref("Schemas")
Lookups = get_collection_ref("Lookups")

drop_downs_pth = RESOLVER['copo_drop_downs']


class Command(BaseCommand):
    help = 'Generate UI schemas and dropdown lookups'

    def handle(self, *args, **options):
        # generate ui schemas
        self.generate_ui_schemas()

        self.convert_crp_list()

        self.generate_lookup_datasource()

        self.stdout.write(self.style.SUCCESS('Successfully generated schemas'))

    def generate_ui_schemas(self):
        """
        function generates ui schemas
        :return:
        """
        # instantiate data schema
        data_schema = DataSchemas("COPO")

        # generate core schemas
        temp_dict = DataFormats("COPO").generate_ui_template()

        # store schemas in DB
        if temp_dict["status"] == "success" and temp_dict["data"]:
            data_schema.add_ui_template(temp_dict["data"])

        return True

    def convert_crp_list(self):
        """
        converts cgiar crp from csv to json
        :return:
        """

        try:
            df = pd.read_csv(os.path.join(drop_downs_pth, 'crp_list.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error retrieving schema resource: ' + str(e)))
            Logger().exception(e)
            return False

        # ﻿'Platform_no', 'Operating_name', 'Official_name', 'Standard_reference', 'Lead_center', 'Class'
        df.columns = [x.lower() for x in df.columns]
        df['label'] = df['official_name']
        df['value'] = df['operating_name']
        df['description'] = "<div>Platform number: " + df['platform_no'].astype(str) + \
                            "</div><div>Standard reference: " + df['standard_reference'].astype(str) + \
                            "</div><div>Operating name: " + df['operating_name'].astype(str) + \
                            "</div><div>Lead center: " + df['lead_center'].astype(str) + \
                            "</div>Class: " + df['class'].astype(str)

        df = df[['label', 'value', 'description']]
        result = df.to_dict('records')

        try:
            with open(os.path.join(drop_downs_pth, 'crp_list.json'), 'w') as fout:
                json.dump(result, fout)
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error writing crp_list.json: ' + str(e)))
            Logger().exception(e)
            return False

        return True

    def generate_lookup_datasource(self):

        dispatcher = {
            'agrovoclabels': self.agrovoc_datasource,
            'countrieslist': self.countrieslist_datasource,
            'mediatypelabels': self.mediatype_datasource,
            'fundingbodies': self.fundingbodies_datasource
        }

        for k in dispatcher.keys():
            # drop existing records of type
            Lookups.remove({"type": k})
            try:
                result_df = dispatcher[k]()
                result_df['type'] = k
                result_df = result_df[['accession', 'label', 'description', 'type', 'tags']]
                Lookups.insert_many(result_df.to_dict('records'))
            except Exception as e:
                print(e)
                Logger().exception(e)

    def agrovoc_datasource(self):
        """
        function generates data source for Agrovoc terms lookup
        :return:
        """

        data = d_utils.json_to_pytype(os.path.join(drop_downs_pth, 'agrovocLabels.json'))["bindings"]
        data_df = pd.DataFrame(data)

        data_df['accession'] = data_df['uri'].apply(lambda x: x.get('value', str()))
        data_df['label'] = data_df['label'].apply(lambda x: x.get('value', str()))
        data_df['description'] = '<table style="width:100%"><tr><td>Label</td><td>' + data_df[
            'label'] + '</td></tr><tr><td>Accession</td><td>' + data_df['accession'] + '</td></table>'
        data_df['tags'] = [''] * len(data_df)

        return data_df

    def countrieslist_datasource(self):
        """
        function generates data source for lookup of countries
        :return:
        """

        data = d_utils.json_to_pytype(os.path.join(drop_downs_pth, 'countries.json'))["bindings"]
        data_df = pd.DataFrame(data)

        data_df['accession'] = data_df['name']
        data_df['label'] = data_df['name']

        data_df['description'] = '<table style="width:100%"><tr><td>Code</td><td>' + data_df[
            'country-code'] + '</td></tr><tr><td>Region</td><td>' + data_df[
                                     'region'] + '</td></tr><tr><td>Sub-region</td><td>' + data_df[
                                     'sub-region'] + '</td></tr></table>'

        data_df['tags'] = [''] * len(data_df)

        return data_df

    def mediatype_datasource(type):
        """
        :param type: is the 'datasource' used in the ui control element
        :return:
        """

        # get all mediatype files
        pth = os.path.join(drop_downs_pth, 'media_types')
        all_files = glob.glob(os.path.join(pth, "*.csv"))

        all_list = list()
        for f in all_files:
            df = pd.read_csv(f)
            df['type'] = df['Template'].str.split("/").str.get(0)
            stem_part = set(df['type'][~df['type'].isna()]).pop()
            df['type'] = stem_part
            vv = df['Template'][df['Template'].isna()].index
            tt = df['Name'][vv]
            df.loc[list(vv), 'Template'] = stem_part + '/' + tt
            df = df[['Name', 'Template', 'type']]
            all_list = all_list + df.to_dict('records')

        data_df = pd.DataFrame(all_list)
        data_df['accession'] = data_df['Template']
        data_df['label'] = data_df['Template']
        data_df['description'] = '<table style="width:100%"><tr><td>Category</td><td>' + data_df[
            'type'] + '</td></tr></table>'

        data_df['tags'] = [''] * len(data_df)

        return data_df

    def fundingbodies_datasource(type):
        """
        function generates data source for lookup of funding bodies
        see: https://github.com/CrossRef/open-funder-registry/releases/tag/v1.22
        :return:
        """

        xml_pth = os.path.join(drop_downs_pth, 'open-funder-registry', 'registry.rdf')
        tree = ET.parse(xml_pth)
        root = tree.getroot()

        namespaces = {'skos': 'http://www.w3.org/2004/02/skos/core#',
                      'skosxl': 'http://www.w3.org/2008/05/skos-xl#',
                      'svf': 'http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/'}

        tags = []

        for child in root.findall('skos:Concept', namespaces):
            label = child.find('skosxl:prefLabel', namespaces).find('skosxl:Label', namespaces).find(
                'skosxl:literalForm',
                namespaces).text
            accession = list(child.attrib.values())[0]
            fundingBodyType = child.find('svf:fundingBodyType', namespaces).text
            fundingBodySubType = child.find('svf:fundingBodySubType', namespaces).text

            altLabels = list()

            for altLabel in child.findall('skosxl:altLabel', namespaces):
                altlabel = altLabel.find('skosxl:Label', namespaces).find('skosxl:literalForm', namespaces).text
                altLabels.append(altlabel)

            tags.append(dict(label=label, accession=accession, fundingBodyType=fundingBodyType,
                             fundingBodySubType=fundingBodySubType, altLabels=altLabels))

        data_df = pd.DataFrame(tags)

        data_df['tags'] = data_df['altLabels']

        data_df['description'] = '<table style="width:100%"><tr><td>Funding body type:</td><td><div>' + data_df[
            'fundingBodyType'] + '</div><div>' + data_df['fundingBodySubType'] + '</div></td></tr></table>'

        return data_df

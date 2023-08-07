__author__ = 'felix.shaw@tgac.ac.uk - 20/01/2016'

import json
import bson.json_util as jsonb
from django.http import HttpResponse
import pandas as pd
from django_tools.middlewares import ThreadLocal

from web.apps.web_copo.lookup.lookup import API_RETURN_TEMPLATES


def get_return_template(type):
    """
    Method to return a python object representation of the given api template return type
    :param type: a string naming the template type
    :return: an python object representation of the json contained in the template
    """
    path = API_RETURN_TEMPLATES[type.upper()]
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def extract_to_template(object=None, template=None):
    """
    Method to examine fields in object and extract those which match the field names in template along with their values
    :param object: the object to search
    :param template: the fields to look for
    :return: the template with the values completed
    """
    for f in object:
        for t in template:
            if f == t:
                template[t] = object[t]

    return template


def finish_request(template=None, error=None, num_found=None, return_http_response=True):
    """
    Method to tidy up data before returning API caller
    :param template: completed template of resource data
    :param error_info: error created if any
    :return: the complete API return
    """
    request = ThreadLocal.get_current_request()
    return_type = request.GET.get('return_type', "json").lower()

    '''
    if is_csv == 'True' or is_csv == 'true' or is_csv == '1' or is_csv == 1 :
        is_csv = True
    else:
        is_csv = False
    '''
    wrapper = get_return_template('WRAPPER')
    if error is None:
        if num_found == None:
            if template == None:
                wrapper["number_found"] = 0
            if type(template) == type(list()):
                wrapper['number_found'] = len(template)
            else:
                wrapper['number_found'] = 1
        else:
            wrapper['number_found'] = num_found
        wrapper['data'] = template
        wrapper['status'] = "OK"
    else:
        wrapper['status']['error'] = True
        wrapper['status']['error_detail'] = error
        wrapper['number_found'] = None
        wrapper['data'] = None
    output = jsonb.dumps(wrapper)
    if return_http_response:
        if return_type == "csv":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=export.csv'
            df = pd.DataFrame(template)
            df.to_csv(response, index=False) 
            return response
        elif return_type == "rocrate":
            rocrate_objs = generate_rocrate_response(template)
            return HttpResponse(content=jsonb.dumps(rocrate_objs),content_type="application/json" )
        else:    
            return HttpResponse(output, content_type="application/json")

    else: 
        return output

def generate_rocrate_response(data):
    result_list = ["Not Implemented"]
    return result_list


def generate_rocrate_response_experiment(data):
    result_list = []
    manifest_map = dict()
    for samples in data:
        manifest_id = samples.get("manifest_id","")
        if manifest_id:
            if manifest_id not in manifest_map:
                manifest_map[manifest_id] = []
            manifest_map[manifest_id].append(samples)

    for key, samples in manifest_map.items():
        rocrate_list = list()

        context = dict()
        context["@context"] = [
                    "https://w3id.org/ro/crate/1.1/context",
                    "https://w3id.org/ro/terms/sample",
                    "https://w3id.org/ro/terms/copo"
                ],

        item_list = list()
        #create creativework
        creativeWork = dict(id="ro-crate-metadata.json", type="CreativeWork")
        conformsTo = {"@id": "https://w3id.org/ro/crate/1.1", "about": {"@id":f"https://copo-project.org/api/manifest/{key}" }}
        creativeWork.update(conformsTo)
        item_list.append(creativeWork)

        df = pd.DataFrame(samples)
        dateCreated = df["time_created"].min()
        dateModifed = df["time_updated"].max()
        author = df["created_by"].unique()
        item = {"@id":f"https://copo-project.org/api/manifest/{key}", "@type":"Dataset", "dateCreated": dateCreated, "datedModified":dateModifed} 
        item["author"] = author
        item["contributor"] = df["updated_by"].unique()
        item["hasPart"] = [ { "@id": f"https://copo-project.org/api/sample/copo_id/{x['copo_id']}"} for x in samples ] 
        item["about"] = [ { "@id": f"https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={x}"} for x in df["TAXON_ID"].unique() ] 
        item_list.append(item)       


        for x in df["TAXON_ID"].unique():
             item = {"@id": f"https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={x}"}
             item["@type"] = "TAXON"
             item["name"] = df[df["TAXON_ID"]== x ]["SCIENTIFIC_NAME"][0]
             item["parentTaxon"] = {"@id": f"https://copo-project.org/api/sample_field/ORDER_OR_GROUP/{df[df['TAXON_ID']== x ]['ORDER_OR_GROUP'][0]}"}    
             item_list.append(item)


        context["@graph"] = item_list
        rocrate_list.append(context)

        result_list.append(rocrate_list)
    return result_list


'''
    response = """
 {
 	"@context": "https://w3id.org/ro/crate/1.1/context",
 	"@graph": [{
 			"@type": "CreativeWork",
 			"@id": "ro-crate-metadata.json",
 			"conformsTo": {
 				"@id": "https://w3id.org/ro/crate/1.1%22%7D",
 				"about": {
 					"@id": "./"
 				}
 			}
 		},

 		{
 			"@id": "./",
 			"identifier": "https://doi.org/10.4225/59/59672c09f4a4b",
 			"@type": "Dataset",
 			"datePublished": "2017",
 			"name": "Data files associated with the manuscript:Effects of facilitated family case conferencing for ...",
 			"description": "Palliative care planning for nursing home residents with advanced dementia ...",
 			"license": {
 				"@id": "https://creativecommons.org/licenses/by-nc-sa/3.0/au/%22%7D"
 			}
 		},
 		{
 			"@id": "https://creativecommons.org/licenses/by-nc-sa/3.0/au/",
 			"@type": "CreativeWork",
 			"description": "This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Australia License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/au/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.",
 			"identifier": "https://creativecommons.org/licenses/by-nc-sa/3.0/au/",
 			"name": "Attribution-NonCommercial-ShareAlike 3.0 Australia (CC BY-NC-SA 3.0 AU)"
 		}
 	]
 }
    """
    return response
'''

def map_to_dict(x, y):
    # method to make output dict using keys from array x and values from array y
    out = dict()
    for idx, el in enumerate(x):
        out[el] = y[idx]
    return out


'''
class Rocrate_obj:
    def __init__(self, id=str(), type=str(), description=str(), name=str(), identifier=str()):
        self.data = dict()
        if id:
            self.data["@id"] = id
        if type:
            self.data["@type"] = type
        if description:
            self.data["description"] = description
        if identifier:
            self.data["identifier"] = identifier
        if name:
            self.data["name"] = name
    
    def set_values(self, dict):
        self.data.update(dict)
'''

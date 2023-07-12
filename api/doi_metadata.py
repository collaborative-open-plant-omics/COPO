__author__ = 'etuka'

import ast
from urllib.request import Request, urlopen

import rdflib
from django.conf import settings
from exceptions_and_logging.logger import Logger
import web.apps.web_copo.lookup.lookup as lkup
from dal.copo_da import DAComponent
import web.apps.web_copo.schemas.utils.data_utils as d_utils

ds = settings.DOI_SERVICES
ncbi = settings.NCBI_SERVICES


# class handles both DOI and PubMed Id resolutions
class DOI2Metadata:
    def __init__(self, id_handle, id_type=None):
        # id_handle could resolve to either an DOI or PubMed ID
        self.error_messages = list()

        self.id_handle = id_handle
        self.id_type = id_type

        self.resolved_data = dict()
        self.failed_flag = "failed"
        self.success_flag = "success"

    def get_esummary(self, pmid):
        r = ncbi.get("PMC_APIS").get("pmid_doi_esummary").format(**locals())
        q = Request(r)

        try:
            request = urlopen(q)
            result_dict = request.read().decode("utf-8")
            result_dict = ast.literal_eval(result_dict)

            if result_dict.get("error"):
                self.error_messages.append(result_dict.get("error"))
                return

            pmid_data = result_dict.get("result", dict()).get(pmid)

            if pmid_data:
                if pmid_data.get("error"):
                    self.error_messages.append("Could not resolve PubMed ID: " + pmid + "!")
                    return

                # get title
                title = pmid_data.get("title")
                if title:
                    self.resolved_data["title"] = title

                # get status
                recordstatus = pmid_data.get("recordstatus")
                if recordstatus:
                    self.resolved_data["status"] = recordstatus

                # get authors
                authors = pmid_data.get("authors")
                if authors and len(self.resolved_data["authorList"]) == 0:
                    for author in authors:
                        if author["authtype"] == "Author":
                            self.resolved_data["authorList"].append(author["name"])

                # resolve doi
                articleids = pmid_data.get("articleids")
                if articleids:
                    for article_id in articleids:
                        if article_id["idtype"] == "doi":
                            self.resolved_data["doi"] = article_id["value"]
                            break

                # add the pmid
                self.resolved_data["pubMedID"] = pmid
        except Exception as e:
            print(str(e))
            Logger().exception(e)
            self.error_messages.append("Could not resolve PubMed ID: " + pmid + "!")

        return

    def get_publication_metadata_pmid(self):
        # NB: if needed, other NCBI PMC APIs could potentially be called in place of esummary, e.g., "E-Fetch",
        # to obtain richer metadata context
        self.get_esummary(self.id_handle)

        return

    def pmid_from_doi(self, doi):
        # given doi, resolve pmid
        pmid = str()

        r = ncbi.get("PMC_APIS").get("doi_pmid_idconv").format(**locals())
        q = Request(r)
        q.add_header('Accept', 'application/json')
        try:
            request = urlopen(q)
            result_dict = request.read().decode("utf-8")
            result_dict = ast.literal_eval(result_dict)
            if result_dict.get("records"):
                records = result_dict.get("records")[0]
                if records.get("pmid"):
                    pmid = records.get("pmid")
        except:
            pass

        return pmid

    def get_publication_metadata_doi(self):
        # strip doi of base, if supplied along
        doi = self.id_handle
        if ds["base_url"] in doi:
            doi = doi.split(ds["base_url"])[1]

        stored_doi = doi  # this will be returned if resolution is successful

        doi = doi.strip("/")  # parsers don't like trailing slashes
        doi = ds["base_url"] + doi

        graph = rdflib.Graph()
        try:
            graph.parse(doi)
        except:
            self.error_messages.append("Could not resolve DOI: " + self.id_handle + "!")
            return

        # define relevant namespaces
        FOAF = rdflib.Namespace(ds["namespaces"]["FOAF"])
        DC = rdflib.Namespace(ds["namespaces"]["DC"])

        # get title
        for triple in graph.triples((None, DC["title"], None)):
            if isinstance(triple[2], rdflib.term.Literal):
                if str(doi) == str(triple[0]):
                    self.resolved_data["title"] = str(triple[2])

        # get authors
        for triple in graph.triples((None, DC["creator"], None)):
            if isinstance(triple[2], rdflib.term.Literal):
                self.resolved_data.get("authorList").append(str(triple[2]))
            elif isinstance(triple[2], rdflib.term.URIRef):
                for x in graph.triples((triple[2], FOAF['name'], None)):
                    self.resolved_data.get("authorList").append(str(x[2]))

        # set doi
        self.resolved_data["doi"] = stored_doi

        # resolve pmid from doi
        pmid = self.pmid_from_doi(stored_doi)
        if pmid:
            self.resolved_data["pubMedID"] = pmid

            # now, resolving a pmid currently seems to provide richer information than doi...
            self.get_esummary(pmid)

        return

    def publication_metadata(self):
        pub_meta = dict(title=str(),
                        authorList=list(),
                        doi=str(),
                        pubMedID=str(),
                        status=str())

        self.resolved_data = pub_meta

        if self.id_type == "doi":
            self.get_publication_metadata_doi()
        elif self.id_type == "pmid":
            self.get_publication_metadata_pmid()

        if len(self.error_messages):
            return dict(status=self.failed_flag,
                        error=self.error_messages,
                        data=dict())
        else:
            return dict(status=self.success_flag,
                        error=self.error_messages,
                        data=self.resolved_data)

    def get_resolve(self, component=str()):
        da_object = DAComponent(component=component)

        message_display_templates = d_utils.json_to_pytype(lkup.MESSAGES_LKUPS["message_templates"])["templates"]
        lookup_messages = d_utils.json_to_pytype(lkup.MESSAGES_LKUPS["lookup_messages"])["properties"]
        component_dict = dict()
        message_dict = dict()

        resolved_dict = self.publication_metadata()

        if resolved_dict.get("status") == "success":
            message_dict = message_display_templates.get("success", dict())
            message_dict["text"] = lookup_messages.get("doi_metadata_crosscheck", str()).get("text", str())
            for f in da_object.get_schema().get("schema"):
                data_dict = resolved_dict.get("data", dict())
                key = f.id.split(".")[-1]
                if key in data_dict:
                    val = data_dict[key]
                    # reconcile schema type mismatch
                    if isinstance(val, list) and f.type == "string":
                        val = ','.join(str(e) for e in val)  # account for numbers
                    if isinstance(val, str) and f.type == "object":
                        object_type_control = d_utils.object_type_control_map().get(f.control.lower(), str())
                        if object_type_control == "ontology_annotation":
                            object_schema = d_utils.get_db_json_schema(object_type_control)
                            value_dict = dict(annotationValue=val
                                              )
                            for k in object_schema:
                                object_schema[k] = value_dict.get(k, d_utils.default_jsontype(
                                    object_schema.get(k, dict()).get("type", "object")))

                            val = object_schema
                    component_dict[key] = val

                if key not in component_dict:  # set default values based on type
                    component_dict[key] = d_utils.default_jsontype(f.type)
        else:
            error_list = resolved_dict.get("error", list())
            message_dict = message_display_templates.get("danger", dict())
            message_dict["text"] = '; '.join(
                str(e) for e in error_list) + lookup_messages.get("doi_metadata_error", str()).get("text", str())

        return dict(component_dict=component_dict,
                    message_dict=message_dict
                    )

    # todo: will handle resolution of metadata for datasets
    def dataset_metadata(self):
        pass

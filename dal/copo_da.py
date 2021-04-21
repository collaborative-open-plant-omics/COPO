__author__ = 'felix.shaw@tgac.ac.uk - 22/10/15'

import copy
import os
from datetime import datetime, timezone, date

import pandas as pd
import pymongo
import pymongo.errors as pymongo_errors
from bson import ObjectId, json_util
from bson.errors import InvalidId
from chunked_upload.models import ChunkedUpload
from django.conf import settings
from django.contrib.auth.models import User
from django_tools.middlewares import ThreadLocal

import web.apps.web_copo.utils.EnaUtils as u
from dal import cursor_to_list, cursor_to_list_str, cursor_to_list_no_ids
from dal.copo_base_da import DataSchemas
from dal.mongo_util import get_collection_ref
from web.apps.web_copo.lookup.copo_enums import Loglvl, Logtype
from web.apps.web_copo.lookup.lookup import DB_TEMPLATES
from web.apps.web_copo.models import UserDetails
from web.apps.web_copo.schemas.utils import data_utils
from web.apps.web_copo.schemas.utils.cg_core.cg_schema_generator import CgCoreSchemas
from web.apps.web_copo.schemas.utils.data_utils import DecoupleFormSubmission
from web.apps.web_copo.utils.dtol.Dtol_Helpers import make_tax_from_sample

lg = settings.LOGGER

PubCollection = 'PublicationCollection'
PersonCollection = 'PersonCollection'
DataCollection = 'DataCollection'
SampleCollection = 'SampleCollection'
SubmissionCollection = 'SubmissionCollection'
SourceCollection = 'SourceCollection'
DataFileCollection = 'DataFileCollection'
RemoteFileCollection = 'RemoteFileCollection'
DescriptionCollection = 'DescriptionCollection'
ProfileCollection = 'Profiles'
AnnotationReference = 'AnnotationCollection'
GroupCollection = 'GroupCollection'
RepositoryCollection = 'RepositoryCollection'
CGCoreCollection = 'CGCoreCollection'
TextAnnotationCollection = 'TextAnnotationCollection'
SubmissionQueueCollection = 'SubmissionQueueCollection'
MetadataTemplateCollection = 'MetadataTemplateCollection'
FileTransferQueueCollection = 'FileTransferQueueCollection'
StatsCollection = 'StatsCollection'

handle_dict = dict(publication=get_collection_ref(PubCollection),
                   person=get_collection_ref(PersonCollection),
                   sample=get_collection_ref(SampleCollection),
                   source=get_collection_ref(SourceCollection),
                   profile=get_collection_ref(ProfileCollection),
                   submission=get_collection_ref(SubmissionCollection),
                   datafile=get_collection_ref(DataFileCollection),
                   annotation=get_collection_ref(AnnotationReference),
                   group=get_collection_ref(GroupCollection),
                   repository=get_collection_ref(RepositoryCollection),
                   cgcore=get_collection_ref(CGCoreCollection),
                   textannotation=get_collection_ref(TextAnnotationCollection),
                   metadata_template=get_collection_ref(MetadataTemplateCollection),
                   stats=get_collection_ref(StatsCollection)
                   )


def to_object_id(id):
    return ObjectId(id)


class ProfileInfo:
    def __init__(self, profile_id=None):
        self.profile_id = profile_id

    def get_counts(self):
        """
        Method to return current numbers of Publication, Person, Data,
        Sample and Submission objects in the given profile
        :return: Dictionary containing the data
        """
        num_dict = dict(num_pub="publication",
                        num_person="person",
                        num_data="datafile",
                        num_sample="sample",
                        num_submission="submission",
                        num_annotation="annotation",
                        num_temp="metadata_template"
                        )

        status = dict()

        for k, v in num_dict.items():
            if handle_dict.get(v, None):
                status[k] = handle_dict.get(v).count(
                    {'profile_id': self.profile_id, 'deleted': data_utils.get_not_deleted_flag()})

        return status

    def source_count(self):
        return handle_dict.get("source").count(
            {'profile_id': self.profile_id, 'deleted': data_utils.get_not_deleted_flag()})


class DAComponent:
    def __init__(self, profile_id=None, component=str()):
        self.profile_id = profile_id
        self.component = component

    def get_number(self):
        return self.get_collection_handle().count({})

    def get_record(self, oid) -> object:
        """

        :rtype: object
        """
        doc = None
        if self.get_collection_handle():
            try:
                doc = self.get_collection_handle().find_one({"_id": ObjectId(oid)})
            except InvalidId as e:
                return e
        if not doc:
            pass

        return doc

    def get_records(self, oids: list) -> list:

        # return list of objects from the given oids list
        if not isinstance(oids, list):
            raise TypeError("Method requires a list")
        # make sure we have ObjectIds
        try:
            oids = list(map(lambda x: ObjectId(x), oids))
        except InvalidId as e:
            return e
        handle = self.get_collection_handle()
        if handle:
            cursor = self.get_collection_handle().find({"_id": {"$in": oids}})

        return cursor_to_list(cursor)

    def get_component_count(self):
        count = 0
        if self.get_collection_handle():
            count = self.get_collection_handle().count(
                {'profile_id': self.profile_id, 'deleted': data_utils.get_not_deleted_flag()})

        return count

    def get_collection_handle(self):
        return handle_dict.get(self.component, None)

    def get_id_base(self):
        base_dict = dict(
            publication="copo.publication",
            person="copo.person",
            datafile="copo.datafile",
            sample="copo.sample",
            source="copo.source",
            profile="copo.profile",
            submission="copo.submission",
            repository="copo.repository",
            annotation="copo.annotation",
            investigation="i_",
            study="s_",
            assay="a_",
        )

        return base_dict.get(self.component, str())

    def get_qualified_field(self, elem=str()):
        return self.get_id_base() + "." + elem

    def get_schema(self):
        schema_base = DataSchemas("COPO").get_ui_template().get("copo")
        x = data_utils.json_to_object(schema_base.get(self.component, dict()))

        return dict(schema_dict=schema_base.get(self.component, dict()).get("fields", list()),
                    schema=x.fields
                    )

    def get_component_schema(self, **kwargs):
        return DataSchemas("COPO").get_ui_template_node(self.component)

    def validate_record(self, auto_fields=dict(), validation_result=dict(), **kwargs):
        """
        validates record, could be overriden by sub-classes to perform component
        specific validation of a record before saving
        :param auto_fields:
        :param validation_result:
        :param kwargs:
        :return:
        """

        local_result = dict(status=validation_result.get("status", True),
                            message=validation_result.get("message", str()))

        return local_result

    def save_record(self, auto_fields=dict(), **kwargs):
        fields = dict()
        schema = kwargs.get("schema", list()) or self.get_component_schema()

        # set auto fields
        if auto_fields:
            fields = DecoupleFormSubmission(auto_fields, schema).get_schema_fields_updated_dict()

        # should have target_id for updates and return empty string for inserts
        target_id = kwargs.pop("target_id", str())

        # set system fields
        system_fields = dict(
            date_modified=data_utils.get_datetime(),
            deleted=data_utils.get_not_deleted_flag()
        )

        if not target_id:
            system_fields["date_created"] = data_utils.get_datetime()
            system_fields["profile_id"] = self.profile_id

        # extend system fields
        for k, v in kwargs.items():
            system_fields[k] = v

        # add system fields to 'fields' and set default values - insert mode only
        for f in schema:
            f_id = f["id"].split(".")[-1]
            try:
                v_id = f["versions"][0]
            except:
                v_id = ""
            if f_id in system_fields:
                fields[f_id] = system_fields.get(f_id)
            elif v_id in system_fields:
                fields[f_id] = system_fields.get(v_id)

            if not target_id and f_id not in fields:
                fields[f_id] = data_utils.default_jsontype(f["type"])

        # if True, then the database action (to save/update) is never performed, but validated 'fields' are returned
        validate_only = kwargs.pop("validate_only", False)
        fields["date_modified"] = datetime.now()
        # check if there is attached profile then update date modified
        if "profile_id" in fields:
            self.update_profile_modified(fields["profile_id"])
        if validate_only is True:
            return fields
        else:
            if target_id:
                self.get_collection_handle().update(
                    {"_id": ObjectId(target_id)},
                    {'$set': fields})
            else:
                doc = self.get_collection_handle().insert(fields)
                target_id = str(doc)

            # return saved record
            rec = self.get_record(target_id)

            return rec

    def update_profile_modified(self, profile_id):
        handle_dict["profile"].update_one({"_id": ObjectId(profile_id)}, {"$set": {"date_modified": datetime.now()}})

    def get_all_records(self, sort_by='_id', sort_direction=-1, **kwargs):
        doc = dict(deleted=data_utils.get_not_deleted_flag())
        if self.profile_id:
            doc["profile_id"] = self.profile_id

        return cursor_to_list(self.get_collection_handle().find(doc).sort([[sort_by, sort_direction]]))

    def get_all_records_columns(self, sort_by='_id', sort_direction=-1, projection=dict(), filter_by=dict()):
        filter_by["deleted"] = data_utils.get_not_deleted_flag()
        if self.profile_id:
            filter_by["profile_id"] = self.profile_id

        return cursor_to_list(
            self.get_collection_handle().find(filter_by, projection).sort([[sort_by, sort_direction]]))

    def get_all_records_columns_server(self, sort_by='_id', sort_direction=-1, projection=dict(), filter_by=dict(),
                                       search_term=str(),
                                       limit=0, skip=0):

        filter_by["deleted"] = data_utils.get_not_deleted_flag()

        # 'name' seems to be the only reasonable field to restrict searching; others fields are resolved
        filter_by["name"] = {'$regex': search_term, "$options": 'i'}

        if self.profile_id:
            filter_by["profile_id"] = self.profile_id

        if skip > 0:
            records = self.get_collection_handle().find(filter_by, projection).sort([[sort_by, sort_direction]]).skip(
                skip).limit(limit)
        else:
            records = self.get_collection_handle().find(filter_by, projection).sort([[sort_by, sort_direction]]).limit(
                limit)

        return cursor_to_list(records)

    def execute_query(self, query_dict=dict()):
        if self.profile_id:
            query_dict["profile_id"] = self.profile_id

        return cursor_to_list(self.get_collection_handle().find(query_dict))


class Publication(DAComponent):
    def __init__(self, profile_id=None):
        super(Publication, self).__init__(profile_id, "publication")


class TextAnnotation(DAComponent):
    def __init__(self, profile_id=None):
        super(TextAnnotation, self).__init__(profile_id, "textannotation")

    def add_term(self, data):
        data["file_id"] = ObjectId(data["file_id"])
        id = self.get_collection_handle().insert(data)
        return id

    def get_all_for_file_id(self, file_id):
        records = self.get_collection_handle().find({"file_id": ObjectId(file_id)})
        return cursor_to_list_str(records, use_underscore_in_id=False)

    def remove_text_annotation(self, id):
        done = self.get_collection_handle().delete_one({"_id": ObjectId(id)})
        return done

    def update_text_annotation(self, id, data):
        data["file_id"] = ObjectId(data["file_id"])
        done = self.get_collection_handle().update_one({"_id": ObjectId(id)}, {"$set": data})
        return done

    def get_file_level_metadata_for_pdf(self, file_id):
        docs = self.get_collection_handle().find({"file_id": ObjectId(file_id)})
        if docs:
            return cursor_to_list_str(docs)


class MetadataTemplate(DAComponent):
    def __init__(self, profile_id=None):
        super(MetadataTemplate, self).__init__(profile_id, "metadata_template")

    def update_name(self, template_name, template_id):
        record = self.get_collection_handle().update({"_id": ObjectId(template_id)},
                                                     {"$set": {"template_name": template_name}})
        record = self.get_by_id(template_id)
        return record

    def get_by_id(self, id):
        record = self.get_collection_handle().find_one({"_id": ObjectId(id)})
        return record

    def update_template(self, template_id, data):
        record = self.get_collection_handle().update_one({"_id": ObjectId(template_id)}, {"$set": {"terms": data}})
        return record

    def get_terms_by_template_id(self, template_id):
        terms = self.get_collection_handle().find_one({"_id": ObjectId(template_id)}, {"terms": 1, "_id": 0})
        return terms


class Annotation(DAComponent):
    def __init__(self, profile_id=None):
        super(Annotation, self).__init__(profile_id, "annotation")

    def add_or_increment_term(self, data):
        # check if annotation is already present
        a = self.get_collection_handle().find_one({"uid": data["uid"], "iri": data["iri"], "label": data["label"]})
        if a:
            # increment
            return self.get_collection_handle().update({"_id": a["_id"]}, {"$inc": {"count": 1}})
        else:
            data["count"] = 1
            return self.get_collection_handle().insert(data)

    def decrement_or_delete_annotation(self, uid, iri):
        a = self.get_collection_handle().find_one({"uid": uid, "iri": iri})
        if a:
            if a["count"] > 1:
                # decrement
                return self.get_collection_handle().update({"_id": a["_id"]}, {"$inc": {"count": -1}})
            else:
                return self.get_collection_handle().delete_one({"_id": a["_id"]})
        else:
            return False

    def get_terms_for_user_alphabetical(self, uid):
        a = self.get_collection_handle().find({"uid": uid}).sort("label", pymongo.ASCENDING)
        return cursor_to_list(a)

    def get_terms_for_user_ranked(self, uid):
        a = self.get_collection_handle().find({"uid": uid}).sort("count", pymongo.DESCENDING)
        return cursor_to_list(a)

    def get_terms_for_user_by_dataset(self, uid):
        docs = self.get_collection_handle().aggregate(
            [
                {"$match": {"uid": uid}},
                {"$group": {"_id": "$file_id", "annotations": {"$push": "$$ROOT"}}}
            ])
        data = cursor_to_list(docs)
        return data


class Person(DAComponent):
    def __init__(self, profile_id=None):
        super(Person, self).__init__(profile_id, "person")

    def get_people_for_profile(self):
        docs = self.get_collection_handle().find({'profile_id': self.profile_id})
        if docs:
            return docs
        else:
            return False

    def create_sra_person(self):
        """
        creates an (SRA) person record and attach to profile
        Returns:
        """

        people = self.get_all_records()
        sra_roles = list()
        for record in people:
            for role in record.get("roles", list()):
                sra_roles.append(role.get("annotationValue", str()))

        # has sra roles?
        has_sra_roles = all(x in sra_roles for x in ['SRA Inform On Status', 'SRA Inform On Error'])

        if not has_sra_roles:
            try:
                user = data_utils.get_current_user()

                auto_fields = {
                    'copo.person.roles.annotationValue': 'SRA Inform On Status',
                    'copo.person.lastName': user.last_name,
                    'copo.person.firstName': user.first_name,
                    'copo.person.roles.annotationValue___0___1': 'SRA Inform On Error',
                    'copo.person.email': user.email
                }
            except Exception as e:
                pass
            else:
                kwargs = dict()
                self.save_record(auto_fields, **kwargs)
        return


class CGCore(DAComponent):
    def __init__(self, profile_id=None):
        super(CGCore, self).__init__(profile_id, "cgcore")

    def get_component_schema(self, **kwargs):
        """
        function returns sub schema for a composite attribute
        :param kwargs:
        :return:
        """
        schema_fields = super(CGCore, self).get_component_schema()

        if not schema_fields:
            return list()

        referenced_field = kwargs.get("referenced_field", str())
        referenced_type = kwargs.get("referenced_type", str())

        if referenced_field:  # resolve dependencies
            schema_fields = [x for x in schema_fields if 'dependency' in x and x['dependency'] == referenced_field]

            if not schema_fields:
                return list()

            # add an attribute to capture the referenced field - mark this as hidden for UI purposes
            dependent_record_label = 'dependency_id'
            new_attribute = copy.deepcopy(schema_fields[-1])
            new_attribute["id"] = new_attribute["id"].split(".")
            new_attribute["id"][-1] = dependent_record_label
            new_attribute["id"] = ".".join(new_attribute["id"])
            new_attribute["control"] = 'text'
            new_attribute["hidden"] = 'true'
            new_attribute["required"] = True
            new_attribute["help_tip"] = ''
            new_attribute["label"] = ''
            new_attribute["default_value"] = referenced_field
            new_attribute["show_in_form"] = True
            new_attribute["show_in_table"] = False
            new_attribute["versions"] = [dependent_record_label]
            schema_fields = [new_attribute] + schema_fields

        if referenced_type:  # set field constraints
            schema_df = CgCoreSchemas().resolve_field_constraint(schema=schema_fields, type_name=referenced_type)
            columns = list(schema_df.columns)

            for col in columns:
                schema_df[col].fillna('n/a', inplace=True)

            schema_fields = schema_df.sort_values(by=['field_constraint_rank']).to_dict('records')

            # delete non-relevant attributes
            for item in schema_fields:
                for k in columns:
                    if item[k] == 'n/a':
                        del item[k]

        for item in schema_fields:
            # set array types to string - child array types are accounted for by the parent
            item["type"] = "string"

        if schema_fields:
            # add a mandatory label field - for lookups and uniquely identifying a sub-record
            dependent_record_label = 'copo_name'
            new_attribute = copy.deepcopy(schema_fields[-1])
            new_attribute["id"] = new_attribute["id"].split(".")
            new_attribute["id"][-1] = dependent_record_label
            new_attribute["id"] = ".".join(new_attribute["id"])
            new_attribute["control"] = 'text'
            new_attribute["hidden"] = 'false'
            new_attribute["field_constraint"] = 'required'
            new_attribute["required"] = True
            new_attribute["unique"] = True
            new_attribute["help_tip"] = 'Please provide a unique label for this dependent record.'
            new_attribute["label"] = 'Label'
            new_attribute["show_in_form"] = True
            new_attribute["show_in_table"] = True
            new_attribute["versions"] = [dependent_record_label]
            new_attribute["field_constraint_rank"] = 1
            schema_fields = [new_attribute] + schema_fields

        return schema_fields

    def get_all_records(self, sort_by='_id', sort_direction=-1, **kwargs):
        doc = dict(deleted=data_utils.get_not_deleted_flag())
        if self.profile_id:
            doc["profile_id"] = self.profile_id

        referenced_field = kwargs.get("referenced_field", str())

        if referenced_field:
            doc["dependency_id"] = referenced_field

        return cursor_to_list(self.get_collection_handle().find(doc).sort([[sort_by, sort_direction]]))

    def save_record(self, auto_fields=dict(), **kwargs):
        all_keys = [x.lower() for x in auto_fields.keys() if x]
        schema_fields = self.get_component_schema()
        schema_fields = [x for x in schema_fields if x["id"].lower() in all_keys]

        schema_fields.append(dict(id="dependency_id", type="string", control="text"))
        schema_fields.append(dict(id="date_modified", type="string", control="text"))
        schema_fields.append(dict(id="deleted", type="string", control="text"))
        schema_fields.append(dict(id="date_created", type="string", control="text"))
        schema_fields.append(dict(id="profile_id", type="string", control="text"))

        # get dependency id
        dependency_id = [v for k, v in auto_fields.items() if k.split(".")[-1] == "dependency_id"]
        kwargs["dependency_id"] = dependency_id[0] if dependency_id else ''
        kwargs["schema"] = schema_fields

        return super(CGCore, self).save_record(auto_fields, **kwargs)


class Source(DAComponent):
    def __init__(self, profile_id=None):
        super(Source, self).__init__(profile_id, "source")

    def get_from_profile_id(self, profile_id):
        return self.get_collection_handle().find({'profile_id': profile_id})

    def get_specimen_biosample(self, value):
        return cursor_to_list(self.get_collection_handle().find({"sample_type": "dtol_specimen",
                                                                 "SPECIMEN_ID": value}))

    def add_accession(self, biosample_accession, sra_accession, submission_accession, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$set":
                {
                    'biosampleAccession': biosample_accession,
                    'sraAccession': sra_accession,
                    'submissionAccession': submission_accession,
                    'status': 'accepted'}
            })

    def get_by_specimen(self, value):
        return cursor_to_list(self.get_collection_handle().find({"SPECIMEN_ID": value}))  # todo can this be find one

    def add_fields(self, fieldsdict, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$set":
                 fieldsdict
             }
        )

    def add_rejected_status(self, status, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$set":
                 {'error': status["msg"],
                  'status': "rejected"}
             }
        )


class Sample(DAComponent):
    def __init__(self, profile_id=None):
        super(Sample, self).__init__(profile_id, "sample")

    def get_sample_by_specimen_id(self, specimen_id):
        return self.get_collection_handle().find({"SPECIMEN_ID": specimen_id})

    def count_samples_by_specimen_id_for_barcoding(self, specimen_id):
        # specimens must not have already been submitted to ENA so should have status of pending
        return self.get_collection_handle().count(
            {"SPECIMEN_ID": specimen_id, "status": {"$nin": ["rejected", "accepted", "processing"]}})

    def find_incorrectly_rejected_samples(self):
        # TODO - for some reason, some dtol samples end up rejected even though the have accessions, so find these and
        # flip them to accepted
        self.get_collection_handle().update_many(
            {"biosampleAccession": {"$ne": ""}},
            {"$set": {"status": "accepted"}}
        )

    def update_public_name(self, name):
        self.get_collection_handle().update_many(
            {"SPECIMEN_ID": name['specimen']["specimenId"], "species_list" : {
                '$elemMatch' : {"TAXON_ID": str(name['species']["taxonomyId"]), "SYMBIONT": "target"}}},
            {"$set": {"public_name": name.get("tolId", "")}})

    def delete_sample(self, sample_id):
        sample = self.get_record(sample_id)
        # check if sample has already been accepted
        if sample["status"] in ["accepted", "processing"]:
            return "Sample {} with accession {} cannot be deleted as it has already been submitted to ENA.".format(
                sample.get("SPECIMEN_ID", ""), sample.get("biosampleAccession", "X"))
        else:
            # delete sample from mongo
            self.get_collection_handle().remove({"_id": ObjectId(sample_id)})
            message = "Sample {} was deleted".format(sample.get("SPECIMEN_ID", ""))
            # check if the parent source to see if it can also be delete
            if self.get_collection_handle().count({"SPECIMEN_ID": sample.get("SPECIMEN_ID", "")}) < 1:
                handle_dict["source"].remove({"SPECIMEN_ID": sample.get("SPECIMEN_ID", "")})
                message = message + "Specimen with id {} was deleted".format(sample.get("SPECIMEN_ID", ""))
            return message

    def check_dtol_unique(self, rack_tube):
        rt = list(rack_tube)
        return cursor_to_list(self.get_collection_handle().find(
            {"rack_tube": {"$in": rt}},
            {"RACK_OR_PLATE_ID": 1, "TUBE_OR_WELL_ID": 1}
        ))

    def get_all_dtol_samples(self):
        return cursor_to_list(self.get_collection_handle().find(
            {"sample_type": "dtol"},
            {"_id": 1}
        ))

    def get_number_of_dtol_samples(self):
        return self.get_collection_handle().count(
            {"sample_type": "dtol"}
        )

    def get_number_of_samples(self):
        return self.get_collection_handle().count({

        })

    def get_dtol_type(self, id):
        return self.get_collection_handle().find_one(
            {"$or": [{"biosampleAccession": id}, {"sraAccession": id}, {"biosampleAccession": id}]})

    def get_from_profile_id(self, profile_id):
        return self.get_collection_handle().find({'profile_id': profile_id})

    def timestamp_dtol_sample_created(self, sample_id):
        email = ThreadLocal.get_current_user().email
        sample = self.get_collection_handle().update({"_id": ObjectId(sample_id)},
                                                     {"$set": {"time_created": datetime.now(timezone.utc).replace(
                                                         microsecond=0), "created_by": email}})

    def timestamp_dtol_sample_updated(self, sample_id):

        try:
            email = ThreadLocal.get_current_user().email
        except:
            email = "copo@earlham.ac.uk"
        sample = self.get_collection_handle().update({"_id": ObjectId(sample_id)},
                                                     {"$set": {"time_updated": datetime.now(timezone.utc).replace(
                                                         microsecond=0),
                                                         "date_modified": datetime.now(timezone.utc).replace(
                                                             microsecond=0),
                                                         "updated_by": email}})

    def add_accession(self, biosample_accession, sra_accession, submission_accession, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$set":
                {
                    'biosampleAccession': biosample_accession,
                    'sraAccession': sra_accession,
                    'submissionAccession': submission_accession,
                    'status': 'accepted'}
            })

    def add_field(self, field, value, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$set":
                {
                    field: value}
            })

    def remove_field(self, field, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$unset":
                {
                    field: ""
                }}
        )

    def add_rejected_status(self, status, oid):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(oid)
            },
            {"$set":
                 {'error': status["msg"],
                  'status': "rejected"}
             }
        )

    def get_dtol_from_profile_id(self, profile_id, filter):
        if filter == "pending":
            # $nin will return where status neq to values in array, or status is absent altogether
            cursor = self.get_collection_handle().find(
                {'profile_id': profile_id, "status": {"$nin": ["rejected", "accepted", "processing"]}, "barcoding": {
                    "$exists": True}})
        elif filter == "pending_barcode":
            cursor = self.get_collection_handle().find(
                {'profile_id': profile_id, "status": {"$nin": ["rejected", "accepted", "processing"]}, "barcoding": {
                    "$exists": False}})
        elif filter == "conflicting_barcode":
            cursor = self.get_collection_handle().find(
                {'profile_id': profile_id, "status": "conflicting"})
        else:
            # else return samples who's status simply mathes the filter
            cursor = self.get_collection_handle().find({'profile_id': profile_id, "status": filter})
        out = list()
        # get schema
        sc = self.get_component_schema()
        out = list()
        for i in cursor_to_list(cursor):
            sam = dict()
            for cell in i:
                for field in sc:
                    if cell == field.get("id", "").split(".")[-1] or cell == "_id":
                        if "dtol" in field.get("specifications", "") or "asg" in field.get("specifications", ""):
                            if field.get("show_in_table", ""):
                                sam[cell] = i[cell]
            out.append(sam)
        return out

    def mark_rejected(self, sample_id, reason="Sample rejected by curator."):
        return self.get_collection_handle().update({"_id": ObjectId(sample_id)},
                                                   {"$set": {"status": "rejected", "error": reason}})

    def mark_processing(self, sample_id):
        return self.get_collection_handle().update({"_id": ObjectId(sample_id)}, {"$set": {"status": "processing"}})

    def get_by_manifest_id(self, manifest_id):
        samples = cursor_to_list(self.get_collection_handle().find({"manifest_id": manifest_id}))
        for s in samples:
            s["copo_profile_title"] = Profile().get_name(s["profile_id"])
        return samples

    def get_statuses_by_manifest_id(self, manifest_id):
        return cursor_to_list(self.get_collection_handle().find({"manifest_id": manifest_id},
                                                                {"status": 1, "copo_id": 1, "manifest_id": 1,
                                                                 "time_created": 1, "time_updated": 1}))

    def get_by_biosample_ids(self, biosample_ids):
        return cursor_to_list(self.get_collection_handle().find({"biosampleAccession": {"$in": biosample_ids}}))

    def get_by_field(self, dtol_field, value):
        return cursor_to_list(self.get_collection_handle().find({dtol_field: {"$in": value}}))

    def get_specimen_biosample(self, value):
        return cursor_to_list(self.get_collection_handle().find({"sample_type": "dtol_specimen",
                                                                 "SPECIMEN_ID": value}))

    def get_manifests(self):
        cursor = self.get_collection_handle().aggregate(
            [
                {
                    "$match": {
                        "sample_type": "dtol"
                    }
                },
                {"$sort":
                     {"time_created": -1}
                 },
                {"$group":
                    {
                        "_id": "$manifest_id",
                        "created": {"$first": "$time_created"}
                    }
                }
            ])
        return cursor_to_list_no_ids(cursor)

    def get_manifests_by_date(self, d_from, d_to):
        ids = self.get_collection_handle().aggregate(
            [
                {"$match": {"sample_type": "dtol", "time_created": {"$gte": d_from, "$lt": d_to}}},
                {"$sort": {"time_created": -1}},
                {"$group":
                    {
                        "_id": "$manifest_id",
                        "created": {"$first": "$time_created"}
                    }
                }
            ])
        out = cursor_to_list_no_ids(ids)
        return out

    def check_and_add_symbiont(self, s):
        sample = self.get_collection_handle().find_one(
            {"RACK_OR_PLATE_ID": s["RACK_OR_PLATE_ID"], "TUBE_OR_WELL_ID": s["TUBE_OR_WELL_ID"]})
        if sample:
            out = make_tax_from_sample(s)
            self.add_symbiont(sample, out)
            return True
        return False

    def add_symbiont(self, s, out):
        self.get_collection_handle().update(
            {"RACK_OR_PLATE_ID": s["RACK_OR_PLATE_ID"], "TUBE_OR_WELL_ID": s["TUBE_OR_WELL_ID"]},
            {"$push": {"species_list": out}}
        )
        return True


class Submission(DAComponent):
    def __init__(self, profile_id=None):
        super(Submission, self).__init__(profile_id, "submission")

    def dtol_sample_processed(self, sub_id, sam_ids):
        # when dtol sample has been processed, pull id from submission and check if there are remaining
        # samples left to go. If not, make submission complete. This will stop celery processing the this submission.
        sub_handle = self.get_collection_handle()
        for sam_id in sam_ids:
            sub_handle.update({"_id": ObjectId(sub_id)}, {"$pull": {"dtol_samples": sam_id}})
        sub = sub_handle.find_one({"_id": ObjectId(sub_id)}, {"dtol_samples": 1})

        if len(sub["dtol_samples"]) < 1:
            sub_handle.update({"_id": ObjectId(sub_id)}, {"$set": {"dtol_status": "complete"}})

    def get_dtol_samples_in_biostudy(self, study_ids):
        sub = self.get_collection_handle().find(
            {"accessions.study_accessions.bioProjectAccession": {"$in": study_ids}},
            {"accessions": 1, "_id": 0}
        )
        return cursor_to_list(sub)

    def get_pending_dtol_samples(self):
        REFRESH_THRESHOLD = 3600  # time in seconds to retry stuck submission
        # called by celery to get samples the supeprvisor has set to be sent to ENA
        # those not yet sent should be in pending state. Occasionally there will be
        # stuck submissions in sending state, so get both types
        sub = self.get_collection_handle().find({"type": "dtol", "dtol_status": {"$in": ["sending", "pending"]}},
                                                {"dtol_samples": 1, "dtol_status": 1, "profile_id": 1,
                                                 "date_modified": 1})
        sub = cursor_to_list(sub)
        out = list()

        for s in sub:
            # calculate whether a submission is an old one
            recorded_time = s.get("date_modified", datetime.now())
            current_time = datetime.now()
            time_difference = current_time - recorded_time
            if s.get("dtol_status", "") == "sending" and time_difference.seconds > (REFRESH_THRESHOLD):
                # submission retry time has elapsed so re-add to list
                out.append(s)
                self.update_submission_modified_timestamp(s["_id"])
                print("ADDING STALLED SUBMISSION BACK INTO QUEUE")
                # no need to change status
            elif s.get("dtol_status", "") == "pending":
                out.append(s)
                self.update_submission_modified_timestamp(s["_id"])
                self.get_collection_handle().update({"_id": ObjectId(s["_id"])}, {"$set": {"dtol_status": "sending"}})
        return out

    def get_incomplete_submissions_for_user(self, user_id, repo):
        doc = self.get_collection_handle().find(
            {"user_id": user_id,
             "repository": repo,
             "complete": "false"}
        )
        return doc

    def make_dtol_status_pending(self, sub_id):
        doc = self.get_collection_handle().update({"_id": ObjectId(sub_id)}, {
            "$set": {"dtol_status": "pending", "date_modified": data_utils.get_datetime()}})

    def save_record(self, auto_fields=dict(), **kwargs):
        if not kwargs.get("target_id", str()):
            repo = kwargs.pop("repository", str())
            for k, v in dict(
                    repository=repo,
                    status=False,
                    complete='false',
                    user_id=data_utils.get_current_user().id,
                    date_created=data_utils.get_datetime()
            ).items():
                auto_fields[self.get_qualified_field(k)] = v

        return super(Submission, self).save_record(auto_fields, **kwargs)

    def validate_and_delete(self, target_id=str()):
        """
        function deletes a submission record, but first checks for dependencies
        :param target_id:
        :return:
        """

        submission_id = str(target_id)

        result = dict(status='success', message="")

        if not submission_id:
            return dict(status='error', message="Submission record identifier not found!")

        # get submission record
        submission_record = self.get_collection_handle().find_one({"_id": ObjectId(submission_id)})

        # check completion status - can't delete a completed submission
        if str(submission_record.get("complete", False)).lower() == 'true':
            return dict(status='error', message="Submission record might be tied to a remote or public record!")

        # check for accession - can't delete record with accession
        if submission_record.get("accessions", dict()):
            return dict(status='error', message="Submission record has associated accessions or object identifiers!")

        # ..and other checks as they come up

        # delete record
        self.get_collection_handle().remove({"_id": ObjectId(submission_id)})

        return result

    def get_submission_metadata(self, submission_id=str()):
        """
        function returns the metadata associated with this submission
        :param submission_id:
        :return:
        """

        result = dict(status='error', message="Metadata not found or unspecified procedure.", meta=list())

        if not submission_id:
            return dict(status='error', message="Submission record identifier not found!", meta=list())

        try:
            repository_type = self.get_repository_type(submission_id=submission_id)
        except Exception as error:
            repository_type = str()

        if not repository_type:
            return dict(status='error', message="Submission repository unknown!", meta=list())

        if repository_type in ["dataverse", "ckan", "dspace"]:
            query_projection = dict()

            for x in self.get_schema().get("schema_dict"):
                query_projection[x["id"].split(".")[-1]] = 0

            query_projection["bundle"] = {"$slice": 1}

            submission_record = self.get_collection_handle().find_one({"_id": ObjectId(submission_id)},
                                                                      query_projection)

            if len(submission_record["bundle"]):
                items = CgCoreSchemas().extract_repo_fields(str(submission_record["bundle"][0]), repository_type)

                if repository_type == "dataverse":
                    items.append({"dc": "dc.relation", "copo_id": "submission_id", "vals": "copo:" + str(submission_id),
                                  "label": "COPO Id"})

                return dict(status='success', message="", meta=items)
        else:
            pass  # todo: if required for other repo, can use metadata from linked bundle

        return result

    def lift_embargo(self, submission_id=str()):
        """
        function attempts to lift the embargo on the submission, releasing to the public
        :param submission_id:
        :return:
        """

        result = dict(status='info', message="Release status unknown or unspecified procedure.")

        if not submission_id:
            return dict(status='error', message="Submission record identifier not found!")

        # this process is repository-centric...
        # so every repository type should provide its own implementation if needed

        try:
            repository_type = self.get_repository_type(submission_id=submission_id)
        except Exception as error:
            repository_type = str()

        if not repository_type:
            return dict(status='error', message="Submission repository unknown!")

        if repository_type == "ena":
            from submission import enareadSubmission
            return enareadSubmission.EnaReads(submission_id=submission_id).process_study_release(force_release=True)

        return result

    def get_repository_type(self, submission_id=str()):
        """
        function returns the repository type for this submission
        :param submission_id:
        :return:
        """

        # specify filtering
        filter_by = dict(_id=ObjectId(str(submission_id)))

        # specify projection
        query_projection = {
            "_id": 1,
            "repository_docs.type": 1,
        }

        doc = self.get_collection_handle().aggregate(
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

        try:
            repository = records[0]['repository_docs'][0]['type']
        except (IndexError, AttributeError) as error:
            message = "Error retrieving submission repository " + str(error)
            lg.log(message, level=Loglvl.ERROR, type=Logtype.FILE)
            raise

        return repository

    def get_repository_details(self, submission_id=str()):
        """
        function returns the repository details for this submission
        :param submission_id:
        :return:
        """

        # specify filtering
        filter_by = dict(_id=ObjectId(str(submission_id)))

        # specify projection
        query_projection = {
            "_id": 1,
        }

        for x in Repository().get_schema().get("schema_dict"):
            query_projection["repository_docs." + x["id"].split(".")[-1]] = 1

        doc = self.get_collection_handle().aggregate(
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

        try:
            repository_details = records[0]['repository_docs'][0]
        except (IndexError, AttributeError) as error:
            message = "Error retrieving submission repository details " + str(error)
            lg.log(message, level=Loglvl.ERROR, type=Logtype.FILE)
            raise

        return repository_details

    def mark_all_token_obtained(self, user_id):

        # mark all submissions for profile with type figshare as token obtained
        return self.get_collection_handle().update_many(
            {
                'user_id': user_id,
                'repository': 'figshare'
            },
            {
                "$set": {
                    "token_obtained": True
                }
            }
        )

    def mark_figshare_article_published(self, article_id):
        return self.get_collection_handle().update_many(
            {
                'accessions': article_id
            },
            {
                "$set": {
                    "status": 'published'
                }
            }
        )

    def clear_submission_metadata(self, sub_id):
        return self.get_collection_handle().update({"_id": ObjectId(sub_id)}, {"$set": {"meta": {}}})

    def isComplete(self, sub_id):
        doc = self.get_collection_handle().find_one({"_id": ObjectId(sub_id)})

        return doc.get("complete", False)

    def insert_dspace_accession(self, sub, accessions):
        # check if submission accessions are not a list, if not delete as multiple accessions cannot be added to object
        doc = self.get_collection_handle().find_one({"_id": ObjectId(sub["_id"])})
        if type(doc['accessions']) != type(list()):
            self.get_collection_handle().update(
                {"_id": ObjectId(sub["_id"])},
                {"$unset": {"accessions": ""}}
            )

        doc = self.get_collection_handle().update(
            {"_id": ObjectId(sub["_id"])},
            {"$push": {"accessions": accessions}}
        )
        return doc

    def insert_ckan_accession(self, sub, accessions):

        try:
            doc = self.get_collection_handle().update(
                {"_id": ObjectId(sub)},
                {"$push": {"accessions": accessions}}
            )
        except pymongo_errors.WriteError:
            self.get_collection_handle().update({"_id": ObjectId(sub)}, {"$unset": {"accessions": ""}})
            doc = self.get_collection_handle().update({"_id": ObjectId(sub)}, {"$push": {"accessions": accessions}})
        return doc

    def mark_submission_complete(self, sub_id, article_id=None):
        if article_id:
            if not type(article_id) is list:
                article_id = [article_id]
            f = {
                "$set": {
                    "complete": "true",
                    "completed_on": datetime.now(),
                    "accessions": article_id
                }
            }
        else:
            f = {
                "$set": {
                    "complete": "true",
                    "completed_on": datetime.now()
                }
            }
        doc = self.get_collection_handle().update_one(
            {
                '_id': ObjectId(sub_id)
            },
            f

        )

    def mark_figshare_article_id(self, sub_id, article_id):
        if not type(article_id) is list:
            article_id = [article_id]
        doc = self.get_collection_handle().update_one(
            {
                '_id': ObjectId(sub_id)
            },
            {
                "$set": {
                    "accessions": article_id,
                }
            }
        )

    def get_file_accession(self, sub_id):
        doc = self.get_collection_handle().find_one(
            {
                '_id': ObjectId(sub_id)
            },
            {
                'accessions': 1,
                'bundle': 1,
                'repository': 1
            }
        )
        if doc['repository'] == 'figshare':
            return {'accessions': doc['accessions'], 'repo': 'figshare'}
        else:
            filenames = list()
            for file_id in doc['bundle']:
                f = DataFile().get_by_file_name_id(file_id=file_id)
                filenames.append(f['name'])
            if isinstance(doc['accessions'], str):
                doc['accessions'] = None
            return {'accessions': doc['accessions'], 'filenames': filenames, 'repo': doc['repository']}

    def get_file_accession_for_dataverse_entry(self, mongo_file_id):
        return self.get_collection_handle().find_one({'accessions.mongo_file_id': mongo_file_id},
                                                     {'_id': 0, 'accessions.$': 1})

    def get_complete(self):
        complete_subs = self.get_collection_handle().find({'complete': True})
        return complete_subs

    def get_ena_type(self):
        subs = self.get_collection_handle().find({'repository': {'$in': ['ena-ant', 'ena', 'ena-asm']}})
        return subs

    def update_destination_repo(self, submission_id, repo_id):
        if repo_id == 'default':
            return self.get_collection_handle().update(
                {'_id': ObjectId(submission_id)}, {'$set': {'destination_repo': 'default'}}
            )
        r = Repository().get_record(ObjectId(repo_id))
        dest = {"url": r.get('url'), 'apikey': r.get('apikey', ""), "isCG": r.get('isCG', ""), "repo_id": repo_id,
                "name": r.get('name', ""),
                "type": r.get('type', ""), "username": r.get('username', ""), "password": r.get('password', "")}
        self.get_collection_handle().update(
            {'_id': ObjectId(submission_id)},
            {'$set': {'destination_repo': dest, 'repository': r['type'], 'date_modified': data_utils.get_datetime()}}
        )

        return r

    def update_meta(self, submission_id, meta):
        return self.get_collection_handle().update(
            {'_id': ObjectId(submission_id)}, {'$set': {'meta': json_util.loads(meta)}}
        )

    def get_dataverse_details(self, submission_id):
        doc = self.get_collection_handle().find_one(
            {'_id': ObjectId(submission_id)}, {'destination_repo': 1}
        )
        default_dataverse = {'url': settings.DATAVERSE["HARVARD_TEST_API"],
                             'apikey': settings.DATAVERSE["HARVARD_TEST_TOKEN"]}
        if 'destination_repo' in doc:
            if doc['destination_repo'] == 'default':
                return default_dataverse
            else:
                return doc['destination_repo']
        else:
            return default_dataverse

    def mark_as_published(self, submission_id):
        return self.get_collection_handle().update(
            {'_id': ObjectId(submission_id)}, {'$set': {'published': True}}
        )

    def get_dtol_submission_for_profile(self, profile_id):
        return self.get_collection_handle().find_one({
            "profile_id": profile_id, "type": {"$in": ["dtol"]}
        })

    def add_accession(self, biosample_accession, sra_accession, submission_accession, oid, collection_id):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(collection_id)
            },
            {"$set":
                {
                    'accessions.sample_accessions.' + str(oid): {
                        'biosampleAccession': biosample_accession,
                        'sraAccession': sra_accession,
                        'submissionAccession': submission_accession,
                        'status': 'accepted'}
                }})

    def add_study_accession(self, bioproject_accession, sra_study_accession, study_accession, collection_id):
        return self.get_collection_handle().update(
            {
                "_id": ObjectId(collection_id)
            },
            {"$set":
                {
                    'accessions.study_accessions': {
                        'bioProjectAccession': bioproject_accession,
                        'sraStudyAccession': sra_study_accession,
                        'submissionAccession': study_accession,
                        'status': 'accepted'}
                }}
        )

    def get_study(self, collection_id):
        # return if study has been already submitted
        return self.get_collection_handle().count(
            {'$and': [{'_id': ObjectId(collection_id)}, {'accessions.study_accessions': {'$exists': 'true'}}]})

    def update_submission_modified_timestamp(self, sub_id):
        return self.get_collection_handle().update(
            {"_id": ObjectId(sub_id)}, {"$set": {"modified": datetime.utcnow()}}
        )

    def get_submission_from_sample_id(self, s_id):
        query = "accessions.sample_accessions." + s_id
        projection = "accessions.study_accessions"
        return cursor_to_list(self.get_collection_handle().find({query: {"$exists": True}}, {projection: 1}))


class DataFile(DAComponent):
    def __init__(self, profile_id=None):
        super(DataFile, self).__init__(profile_id, "datafile")

    def get_for_profile(self, profile_id):
        docs = self.get_collection_handle().find({
            "profile_id": profile_id
        })
        return docs

    def get_by_file_id(self, file_id=None):
        docs = None
        if file_id:
            docs = self.get_collection_handle().find_one(
                {"file_id": file_id, "deleted": data_utils.get_not_deleted_flag()})

        return docs

    def get_by_file_name_id(self, file_id=None):
        docs = None
        if file_id:
            docs = self.get_collection_handle().find_one(
                {
                    "_id": ObjectId(file_id), "deleted": data_utils.get_not_deleted_flag()
                },
                {
                    "name": 1
                }
            )

        return docs

    def get_relational_record_for_id(self, datafile_id):
        chunked_upload = ChunkedUpload.objects.get(id=int(datafile_id))
        return chunked_upload

    def get_record_property(self, datafile_id=str(), elem=str()):
        """
        eases the access to deeply nested properties
        :param datafile_id: record id
        :param elem: schema property(key)
        :return: requested property or some default value
        """

        datafile = self.get_record(datafile_id)
        description = datafile.get("description", dict())
        description_attributes = description.get("attributes", dict())
        description_stages = description.get("stages", list())

        property_dict = dict(
            target_repository=description_attributes.get("target_repository", dict()).get("deposition_context", str()),
            attach_samples=description_attributes.get("attach_samples", dict()).get("study_samples", str()),
            sequencing_instrument=description_attributes.get("nucleic_acid_sequencing", dict()).get(
                "sequencing_instrument", str()),
            study_type=description_attributes.get("study_type", dict()).get("study_type", str()),
            description_attributes=description_attributes,
            description_stages=description_stages
        )

        return property_dict.get(elem, str())

    def add_fields_to_datafile_stage(self, target_ids, fields, target_stage_ref):

        for target_id in target_ids:
            # for each file in target_ids retrieve the datafile object
            df = self.get_record(target_id)
            # get the stage using list comprehension and add new fields
            for idx, stage in enumerate(df['description']['stages']):
                if 'ref' in stage and stage['ref'] == target_stage_ref:
                    for field in fields:
                        df['description']['stages'][idx]['items'].append(field)

            # now update datafile record
            self.get_collection_handle().update({'_id': ObjectId(target_id)},
                                                {'$set': {'description.stages': df['description']['stages']}})

    def update_file_level_metadata(self, file_id, data):
        self.get_collection_handle().update({"_id": ObjectId(file_id)}, {"$push": {"file_level_annotation": data}})
        return self.get_file_level_metadata_for_sheet(file_id, data["sheet_name"])

    def insert_sample_id(self, file_id, sample_id):
        self.get_collection_handle().update({"_id": ObjectId(file_id)}, {
            "$push": {"description.attributes.attach_samples.study_samples": sample_id}})

    def get_file_level_metadata_for_sheet(self, file_id, sheetname):

        docs = self.get_collection_handle().aggregate(
            [
                {"$match": {"_id": ObjectId(file_id)}},
                {"$unwind": "$file_level_annotation"},
                {"$match": {"file_level_annotation.sheet_name": sheetname}},
                {"$project": {"file_level_annotation": 1, "_id": 0}},
                {"$sort": {"file_level_annotation.column_idx": 1}}
            ])
        return cursor_to_list(docs)

    def delete_annotation(self, col_idx, sheet_name, file_id):
        docs = self.get_collection_handle().update({"_id": ObjectId(file_id)},
                                                   {"$pull": {"file_level_annotation": {"sheet_name": sheet_name,
                                                                                        "column_idx": str(col_idx)}}})
        return docs


class Profile(DAComponent):
    def __init__(self, profile=None):
        super(Profile, self).__init__(None, "profile")

    def get_num(self):
        return self.get_collection_handle().count({})

    def get_all_profiles(self, user=None):
        mine = list(self.get_for_user(user))
        shared = list(self.get_shared_for_user(user))
        return shared + mine

    def get_type(self, profile_id):
        p = self.get_collection_handle().find_one({"_id": ObjectId(profile_id)})
        if p:
            return p["type"]
        else:
            return False

    def get_for_user(self, user=None):
        if not user:
            user = data_utils.get_current_user().id
        docs = self.get_collection_handle().find({"user_id": user, "deleted": data_utils.get_not_deleted_flag()}).sort(
            [['_id', -1]])

        if docs:
            return docs
        else:
            return None

    def get_shared_for_user(self, user=None):
        # get profiles shared with user
        if not user:
            user = data_utils.get_current_user().id
        groups = CopoGroup().Group.find({'member_ids': str(user)})

        p_list = list()
        for g in groups:
            gp = dict(g)
            p_list.extend(gp['shared_profile_ids'])
        # remove duplicates
        # p_list = list(set(p_list))
        docs = self.get_collection_handle().find(
            {
                "_id": {"$in": p_list},
                "deleted": data_utils.get_not_deleted_flag()
            }
        )
        out = list(docs)
        for d in out:
            d['shared'] = True

        return out

    def save_record(self, auto_fields=dict(), **kwargs):
        if not kwargs.get("target_id", str()):
            for k, v in dict(
                    copo_id=data_utils.get_copo_id(),
                    user_id=data_utils.get_user_id()
            ).items():
                auto_fields[self.get_qualified_field(k)] = v

        rec = super(Profile, self).save_record(auto_fields, **kwargs)

        # trigger after save actions
        if not kwargs.get("target_id", str()):
            Person(profile_id=str(rec["_id"])).create_sra_person()
        return rec

    def add_dataverse_details(self, profile_id, dataverse):
        handle_dict['profile'].update_one({'_id': ObjectId(profile_id)}, {'$set': {'dataverse': dataverse}})

    def check_for_dataverse_details(self, profile_id):
        p = self.get_record(ObjectId(profile_id))
        if 'dataverse' in p:
            return p['dataverse']

    def add_dataverse_dataset_details(self, profile_id, dataset):

        handle_dict['profile'].update_one({'_id': ObjectId(profile_id)}, {'$push': {'dataverse.datasets': dataset}})
        return [dataset]

    def check_for_dataset_details(self, profile_id):
        p = self.get_record(ObjectId(profile_id))
        if 'dataverse' in p:
            if 'datasets' in p['dataverse']:
                return p['dataverse']['datasets']

    def get_dtol_profiles(self):
        p = self.get_collection_handle().find(
            {"type": {"$in": ["Darwin Tree of Life (DTOL)", "Aquatic Symbiosis Genomics (ASG)"]}}).sort("date_modified",
                                                                                                        pymongo.DESCENDING)
        return cursor_to_list(p)

    def get_name(self, profile_id):
        p = self.get_record(ObjectId(profile_id))
        return p["title"]


class CopoGroup(DAComponent):
    def __init__(self):
        super(CopoGroup, self).__init__(None, "group")
        self.Group = get_collection_ref(GroupCollection)

    def get_by_owner(self, owner_id):
        doc = self.Group.find({'owner_id': owner_id})
        if not doc:
            return list()
        return doc

    def create_shared_group(self, name, description, owner_id=None):
        group_fields = data_utils.json_to_pytype(DB_TEMPLATES['COPO_GROUP'])
        if not owner_id:
            owner_id = data_utils.get_user_id()
        group_fields['owner_id'] = owner_id
        group_fields['name'] = name
        group_fields['description'] = description
        group_fields['data_created'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        uid = self.Group.insert(group_fields)
        if uid:
            return uid
        else:
            return False

    def delete_group(self, group_id):
        result = self.Group.delete_one({'_id': ObjectId(group_id)})
        return result.deleted_count > 0

    def add_profile(self, group_id, profile_id):
        return self.Group.update({'_id': ObjectId(group_id)}, {'$push': {'shared_profile_ids': ObjectId(profile_id)}})

    def remove_profile(self, group_id, profile_id):
        return self.Group.update(
            {'_id': ObjectId(group_id)},
            {'$pull': {'shared_profile_ids': ObjectId(profile_id)}}
        )

    def get_profiles_for_group_info(self, group_id):
        p_list = cursor_to_list(Profile().get_for_user(data_utils.get_user_id()))
        group = CopoGroup().get_record(ObjectId(group_id))
        for p in p_list:
            if p['_id'] in group['shared_profile_ids']:
                p['selected'] = True
            else:
                p['selected'] = False
        return p_list

    def get_repos_for_group_info(self, uid, group_id):
        g = CopoGroup().get_record(ObjectId(group_id))
        docs = cursor_to_list(Repository().Repository.find({'users.uid': uid}))
        for d in docs:
            if d['_id'] in g['repo_ids']:
                d['selected'] = True
            else:
                d['selected'] = False
        return list(docs)

    def get_users_for_group_info(self, group_id):
        group = CopoGroup().get_record(ObjectId(group_id))
        member_ids = group['member_ids']
        user_list = list()
        for u in member_ids:
            usr = User.objects.get(pk=u)
            x = {'id': usr.id, 'first_name': usr.first_name, 'last_name': usr.last_name, 'email': usr.email,
                 'username': usr.username}
            user_list.append(x)
        return user_list

    def add_user_to_group(self, group_id, user_id):
        return self.Group.update(
            {'_id': ObjectId(group_id)},
            {'$push': {'member_ids': user_id}})

    def remove_user_from_group(self, group_id, user_id):
        return self.Group.update(
            {'_id': ObjectId(group_id)},
            {'$pull': {'member_ids': user_id}}
        )

    def add_repo(self, group_id, repo_id):
        return self.Group.update({'_id': ObjectId(group_id)}, {'$push': {'repo_ids': ObjectId(repo_id)}})

    def remove_repo(self, group_id, repo_id):
        return self.Group.update(
            {'_id': ObjectId(group_id)},
            {'$pull': {'repo_ids': ObjectId(repo_id)}}
        )


class Repository(DAComponent):
    def __init__(self, profile=None):
        super(Repository, self).__init__(None, "repository")

    def get_by_uid(self, uid):
        doc = self.get_collection_handle().find({"uid": uid}, {"name": 1, "type": 1, "url": 1})
        return doc

    def get_from_list(self, repo_list):
        oids = list(map(lambda x: ObjectId(x), repo_list))
        docs = self.get_collection_handle().find({"_id": {"$in": oids}, "personal": True}, {"apikey": 0})
        return cursor_to_list_str(docs, use_underscore_in_id=False)

    def get_by_ids(self, uids):
        doc = list()
        if (uids):
            oids = list(map(lambda x: ObjectId(x), uids))
            doc = self.get_collection_handle().find({"_id": {"$in": oids}})
        return cursor_to_list(doc)

    def get_by_username(self, username):
        doc = self.get_collection_handle().find({"username": username})
        return doc

    def get_users(self, repo_id):
        doc = self.get_collection_handle().find_one({"_id": ObjectId(repo_id)})
        return doc['users']

    def push_user(self, repo_id, uid, first_name, last_name, username, email):
        args = {'uid': uid, "first_name": first_name, "last_name": last_name, "username": username, "email": email}
        return self.get_collection_handle().update(
            {'_id': ObjectId(repo_id)},
            {'$push': {'users': args}}
        )

    def pull_user(self, repo_id, user_id):
        doc = self.get_collection_handle().update({'_id': ObjectId(repo_id)},
                                                  {'$pull': {'users': {'uid': user_id}}})

        return doc

    def add_personal_dataverse(self, url, name, apikey, type, username, password):
        u = ThreadLocal.get_current_user()
        doc = self.get_collection_handle().insert(
            {"isCG": False, "url": url, "name": name, "apikey": apikey, "personal": True, "uid": u.id, "type": type,
             "username": username, "password": password})
        udetails = u.userdetails
        udetails.repo_submitter.append(str(doc))
        udetails.save()
        return doc

    def validate_record(self, auto_fields=dict(), validation_result=dict(), **kwargs):
        """
        validates record. useful before CRUD actions
        :param auto_fields:
        :param validation_result:
        :param kwargs:
        :return:
        """

        if validation_result.get("status", True) is False:  # no need continuing with validation, propagate error
            return super(Repository, self).validate_record(auto_fields, result=validation_result, **kwargs)

        local_result = dict(status=True, message="")
        kwargs["validate_only"] = True  # causes the subsequent call to save_record to do everything else but save

        new_record = super(Repository, self).save_record(auto_fields, **kwargs)
        new_record_id = kwargs.get("target_id", str())

        existing_records = cursor_to_list(
            self.get_collection_handle().find({}, {"name": 1, "type": 1, "visibility": 1}))

        # check for uniqueness of name - repository names must be unique!
        same_name_records = [str(x["_id"]) for x in existing_records if
                             x.get("name", str()).strip().lower() == new_record.get("name", str()).strip().lower()]

        uniqueness_error = "Action error: duplicate repository name is not allowed."
        if len(same_name_records) > 1:
            # multiple duplicate names, shouldn't be
            local_result["status"] = False
            local_result["message"] = uniqueness_error

            return super(Repository, self).validate_record(auto_fields, validation_result=local_result, **kwargs)
        elif len(same_name_records) == 1 and new_record_id != same_name_records[0]:
            local_result["status"] = False
            local_result["message"] = uniqueness_error

            return super(Repository, self).validate_record(auto_fields, validation_result=local_result, **kwargs)

        # check repo visibility constraint - i.e. one public repository per repository type
        if new_record.get("visibility", str()).lower() == 'public':
            same_visibility_records = [str(x["_id"]) for x in existing_records if
                                       x.get("type", str()).strip().lower() == new_record.get("type",
                                                                                              str()).strip().lower()
                                       and x.get("visibility", str()).lower() == 'public']

            visibility_error = "Action error: multiple public instances of the same repository type is not allowed."
            if len(same_visibility_records) > 1:
                local_result["status"] = False
                local_result[
                    "message"] = visibility_error
                return super(Repository, self).validate_record(auto_fields, validation_result=local_result, **kwargs)
            elif len(same_visibility_records) == 1 and new_record_id != same_visibility_records[0]:
                local_result["status"] = False
                local_result[
                    "message"] = visibility_error
                return super(Repository, self).validate_record(auto_fields, validation_result=local_result, **kwargs)

        return super(Repository, self).validate_record(auto_fields, validation_result=local_result, **kwargs)

    def delete(self, repo_id):
        # have to delete repo id from UserDetails model as well as remove mongo record
        uds = UserDetails.objects.filter(repo_manager__contains=[repo_id])
        for ud in uds:
            ud.repo_manager.remove(repo_id)
            ud.save()
        uds = UserDetails.objects.filter(repo_submitter__contains=[repo_id])
        for ud in uds:
            ud.repo_submitter.remove(repo_id)
            ud.save()
        doc = self.get_collection_handle().remove({"_id": ObjectId(repo_id)})
        return doc

    def validate_and_delete(self, target_id=str()):
        """
        function deletes repository only if there are no dependent records
        :param target_id:
        :return:
        """

        repository_id = target_id

        result = dict(status='success', message="")

        if not repository_id:
            return dict(status='error', message="Repository record identifier not found!")

        # any dependent submission record?

        count_submissions = Submission().get_collection_handle().find(
            {"destination_repo": repository_id, 'deleted': data_utils.get_not_deleted_flag()}).count()

        if count_submissions > 0:
            return dict(status='error', message="Action not allowed: dependent records exist!")

        uds = UserDetails.objects.filter(repo_manager__contains=[repository_id])
        for ud in uds:
            ud.repo_manager.remove(repository_id)
            ud.save()

        uds = UserDetails.objects.filter(repo_submitter__contains=[repository_id])
        for ud in uds:
            ud.repo_submitter.remove(repository_id)
            ud.save()
        self.get_collection_handle().remove({"_id": ObjectId(repository_id)})

        return result


class RemoteDataFile:
    def __init__(self, profile_id=None):
        self.RemoteFileCollection = get_collection_ref(RemoteFileCollection)
        self.profile_id = profile_id

    def GET(self, id):
        doc = self.RemoteFileCollection.find_one({"_id": ObjectId(id)})
        if not doc:
            pass
        return doc

    def get_by_sub_id(self, sub_id):
        doc = self.RemoteFileCollection.find_one({"submission_id": sub_id})
        return doc

    def create_transfer(self, submission_id, file_path=None):
        # before creating a new transfer record for this submission, remove all others
        remote_record = self.get_by_sub_id(submission_id)
        if remote_record:
            self.delete_transfer(str(remote_record["_id"]))

        fields = data_utils.json_to_pytype(DB_TEMPLATES['REMOTE_FILE_COLLECTION'])
        fields['submission_id'] = submission_id
        fields['profile_id'] = self.profile_id
        fields['file_path'] = file_path
        transfer_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        fields["commenced_on"] = transfer_time
        fields["current_time"] = transfer_time
        fields["transfer_rate"] = ""

        if file_path:
            d = DataFile().GET(submission_id)
            chunked_upload = ChunkedUpload.objects.get(id=int(d['file_id']))
            fields["file_size_bytes"] = u.filesize_toString(chunked_upload.offset)

        doc = self.RemoteFileCollection.insert(fields)

        # return inserted record
        df = self.GET(str(doc))
        return df

    def delete_transfer(self, transfer_id):
        self.RemoteFileCollection.delete_one({'_id': ObjectId(transfer_id)})

    def update_transfer(self, transfer_id, fields, delete="0"):

        fields["deleted"] = delete
        if 'transfer_rate' in fields:
            # speed = fields.pop("transfer_rate")

            self.RemoteFileCollection.update(
                {
                    "_id": ObjectId(transfer_id)
                },
                {
                    # '$push': {"transfer_rate": float(speed)},
                    '$set': fields
                }
            )
        else:
            self.RemoteFileCollection.update(
                {
                    "_id": ObjectId(transfer_id)
                },
                {
                    '$set': fields
                }
            )

    def get_all_records(self):
        doc = {'profile_id': self.profile_id, 'deleted': data_utils.get_not_deleted_flag()}
        return cursor_to_list(self.RemoteFileCollection.find(doc))

    def get_by_datafile(self, datafile_id):
        doc = {'datafile_id': ObjectId(datafile_id), 'deleted': data_utils.get_not_deleted_flag()}
        return cursor_to_list(self.RemoteFileCollection.find(doc))

    def sanitise_remote_files(self):
        pass


class Stats:
    def update_stats(self):
        datafiles = handle_dict["datafile"].count({})
        profiles = handle_dict["profile"].count({})
        samples = Sample().get_number_of_samples()
        users = users = len(User.objects.all())
        out = {"datafiles": datafiles, "profiles": profiles, "samples": samples, "users": users,
               "date": str(date.today())}
        get_collection_ref(StatsCollection).insert(out)


class Description:
    def __init__(self, profile_id=None):
        self.DescriptionCollection = get_collection_ref(DescriptionCollection)
        self.profile_id = profile_id
        self.component = str()

    def GET(self, id):
        doc = self.DescriptionCollection.find_one({"_id": ObjectId(id)})
        if not doc:
            pass
        return doc

    def get_description_handle(self):
        return self.DescriptionCollection

    def create_description(self, stages=list(), attributes=dict(), profile_id=str(), component=str(), meta=dict(),
                           name=str()):
        self.component = component

        fields = dict(
            stages=stages,
            attributes=attributes,
            profile_id=profile_id,
            component=component,
            meta=meta,
            name=name,
            created_on=data_utils.get_datetime(),
        )

        doc = self.DescriptionCollection.insert(fields)

        # return inserted record
        df = self.GET(str(doc))
        return df

    def edit_description(self, description_id, fields):
        self.DescriptionCollection.update(
            {"_id": ObjectId(description_id)},
            {'$set': fields})

    def delete_description(self, description_ids=list()):
        object_ids = []
        for id in description_ids:
            object_ids.append(ObjectId(id))

        self.DescriptionCollection.remove({"_id": {"$in": object_ids}})

    def get_all_descriptions(self):
        return cursor_to_list(self.DescriptionCollection.find())

    def get_all_records_columns(self, sort_by='_id', sort_direction=-1, projection=dict(), filter_by=dict()):
        return cursor_to_list(self.DescriptionCollection.find(filter_by, projection).sort([[sort_by, sort_direction]]))

    def is_valid_token(self, description_token):
        is_valid = False

        if description_token:
            if self.DescriptionCollection.find_one({"_id": ObjectId(description_token)}):
                is_valid = True

        return is_valid

    def get_elapsed_time_dataframe(self):
        pipeline = [{"$project": {"_id": 1, "diff_days": {
            "$divide": [{"$subtract": [data_utils.get_datetime(), "$created_on"]}, 1000 * 60 * 60 * 24]}}}]
        description_df = pd.DataFrame(cursor_to_list(self.DescriptionCollection.aggregate(pipeline)))

        return description_df

    def remove_store_object(self, object_path=str()):
        if os.path.exists(object_path):
            import shutil
            shutil.rmtree(object_path)

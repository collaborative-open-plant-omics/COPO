# module provides a lookup service for various resources

import os
from .resolver import RESOLVER

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# DB_TEMPLATES dictionary provides paths to database templates
DB_TEMPLATES = {
    'COPO_COLLECTION_HEAD_FILE': os.path.join(RESOLVER['schemas_copo'], 'collection_head_model.json'),
    'REMOTE_FILE_COLLECTION': os.path.join(RESOLVER['schemas_copo'], 'aspera_db_model.json'),
    'PERSON': os.path.join(RESOLVER['isa_json_db_models'], 'person_schema.json'),
    'PUBLICATION': os.path.join(RESOLVER['isa_json_db_models'], 'publication_schema.json'),
    'SAMPLE': os.path.join(RESOLVER['isa_json_db_models'], 'sample_schema.json'),
    'DATA': os.path.join(RESOLVER['isa_json_db_models'], 'data_schema.json'),
    'SUBMISSION': os.path.join(RESOLVER['isa_json_db_models'], 'copo_submission.json'),
    'ONTOLOGY_ANNOTATION': os.path.join(RESOLVER['isa_json_db_models'], 'ontology_annotation_schema.json'),
    'COMMENT': os.path.join(RESOLVER['isa_json_db_models'], 'comment_schema.json'),
    'COPO_GROUP': os.path.join(RESOLVER['schemas_copo'], 'copo_group.json')
}

# SRA_SETTINGS PATHS
SRA_SETTINGS = os.path.join(RESOLVER['schemas_generic'], 'sra_settings.json')
SRA_COMMENTS = os.path.join(RESOLVER['schemas_generic'], 'sra_comments.json')
SRA_SUBMISSION_TEMPLATE = os.path.join(RESOLVER['schemas_generic'], 'submission.xml')
SRA_SUBMISSION_MODIFY_TEMPLATE = os.path.join(RESOLVER['schemas_generic'], 'submission_modify.xml')
SRA_PROJECT_TEMPLATE = os.path.join(RESOLVER['schemas_generic'], 'project.xml')
SRA_SAMPLE_TEMPLATE = os.path.join(RESOLVER['schemas_generic'], 'sample.xml')
SRA_EXPERIMENT_TEMPLATE = os.path.join(RESOLVER['schemas_generic'], 'experiment.xml')
SRA_RUN_TEMPLATE = os.path.join(RESOLVER['schemas_generic'], 'run.xml')

# ENA CLI PATH
ENA_CLI = os.path.join(RESOLVER['ena_cli'], 'webin-cli.jar')

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# API_RETURN_TEMPLATES dictionary provides paths to api return templates
API_RETURN_TEMPLATES = {
    'WRAPPER': os.path.join(RESOLVER['api_return_templates'], 'template_wrapper.json'),
    'PERSON': os.path.join(RESOLVER['api_return_templates'], 'person.json'),
    'SAMPLE': os.path.join(RESOLVER['api_return_templates'], 'sample.json'),
    'SOURCE': os.path.join(RESOLVER['api_return_templates'], 'source.json')
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# API_ERRORS dictionary provides paths to api return templates
API_ERRORS = {
    'NOT_FOUND': 'resource not found',
    'CONNECTION_ERROR': 'internal error, please try later',
    'INVALID_PARAMETER': 'badly formed parameter',
    'UNKNOWN_ERROR': 'unknown error - please contact the administrator'
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#

# path to UI mapping schemas:
UI_CONFIG_MAPPINGS = os.path.join(RESOLVER['uimodels_copo'], 'mappings')

# path to mapping based on schema version:
UI_CONFIG_MAPPINGS_BASED_ON_SCHEMA_VERSION = os.path.join(RESOLVER['isa_mappings'])

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# X_FILES dictionary holds paths other (non-categorised) schemas
X_FILES = {
    'ISA_JSON_REFACTOR_TYPES': '',
    'SAMPLE_ATTRIBUTES': ''
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# ATTRIBUTE_MAPPINGS dictionary holds mappings from one schema element to another
ATTRIBUTE_MAPPINGS = {
    'isa_xml': {
        'label': 'header',
        'control': 'data-type',
        'required': 'is-required',
        'hidden': 'is-hidden',
        'default_value': '',
        'option_values': '',
        'help_tip': ''
    },
    'ENA_DOI_PUBLICATION_MAPPINGS': {
        'title': 'dc:title',
        'authorList': 'dc:creator',
        'doi': 'dc:identifier_doi',
        'pubMedID': 'dc:identifier_pmid',
        'status': 'dc:status'
    }
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# CONTROL_MAPPINGS dictionary holds mappings between elements in different schemas
CONTROL_MAPPINGS = {
    'isa_xml': {
        'String': 'text',
        'Long String': 'textarea',
        'List': 'select'
        # 'Ontology term':?
    }
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# Repository file types - extensions suitable for different repositories
REPO_FILE_EXTENSIONS = {
    'ena': ['bam', 'fastq', 'sam'],
    'figshare': ['gif', 'jpeg', 'pdf', 'png', 'py', 'doc', 'ppt', 'docx']
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# define options for drop-downs
# wrapping items up in lists to maintain order
# for upgrades, only update the label, but the 'value' field should remain intact
# for referencing in codes.


# !!!!!   MAKE SURE VOCAB REPO NAMES AND DROPDOWN REPOSITORIES ARE IN SYNC
DROP_DOWNS = {
    'COLLECTION_TYPES': [
        {
            'value': 'dummy',
            'label': 'Select Collection Type...',
            'description': 'dummy item'
        },
        {
            'value': 'ENA Submission',
            'label': 'ENA Submission',
            'description': 'Submission to the ENA repository'
        },
        {
            'value': 'Figshare',
            'label': 'PDF File',
            'description': ''
        },
        {
            'value': 'Figshare',
            'label': 'Image',
            'description': ''
        },
        {
            'value': 'Movie',
            'label': 'Movie',
            'description': ''
        },
        {
            'value': 'Other',
            'label': 'Other',
            'description': 'Miscellaneous data file'
        }
    ],
    'STUDY_TYPES': [
        {
            'value': 'genomeSeq',  # this matches the value defined in the object_model.py
            'label': 'Whole Genome Sequencing',
            'description': '',
            'config_source': 'genome_seq.xml'
        },
        {
            'value': 'metagenomeSeq',
            'label': 'Metagenomics',
            'description': '',
            'config_source': 'metagenome_seq.xml'
        },
        {
            'value': 'transcriptomeAnalysis',
            'label': 'Transcriptome Analysis',
            'description': '',
            'config_source': 'transcription_seq.xml'
        },
        {
            'value': 'resequencing',
            'label': 'Resequencing',
            'description': '',
            'config_source': 'genome_seq.xml'
        },
        # {
        #     'value': 'epigenetics',
        #     'label': 'Epigenetics',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'syntheticGenomics',
        #     'label': 'Synthetic Genomics',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'forensicOrPaleo-genomics',
        #     'label': 'Forensic or Paleo-genomics',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'geneRegulationStudy',
        #     'label': 'Gene Regulation Study',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'cancerGenomics',
        #     'label': 'Cancer Genomics',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'populationGenomics',
        #     'label': 'Population Genomics',
        #     'description': '',
        #     'config_source': ''
        # },
        {
            'value': 'rNASeq',
            'label': 'RNA-seq',
            'description': '',
            'config_source': 'transcription_seq.xml'
        },
        # {
        #     'value': 'exomeSequencing',
        #     'label': 'Exome Sequencing',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'pooledCloneSequencing',
        #     'label': 'Pooled Clone Sequencing',
        #     'description': '',
        #     'config_source': ''
        # },
        # {
        #     'value': 'Other',
        #     'label': 'Other',
        #     'description': 'Some random study',
        #     'config_source': ''
        # }
    ],
    'FIGSHARE_CATEGORIES': [
        {
            'value': 'Cell Biology',
            'label': 'Cell Biology',
            'description': ''
        },
        {
            'value': 'Molecular Biology',
            'label': 'Molecular Biology',
            'description': ''
        },
        {
            'value': 'Cancer',
            'label': 'Cancer',
            'description': ''
        },
        {
            'value': 'Bioinformatics',
            'label': 'Bioinformatics',
            'description': ''
        },
        {
            'value': 'Computational Biology',
            'label': 'Computational Biology',
            'description': ''
        },
        {
            'value': 'Proteomics',
            'label': 'Proteomics',
            'description': ''
        },
        {
            'value': 'Synthetic Biology',
            'label': 'Synthetic Biology',
            'description': ''
        },
        {
            'value': 'Genomics',
            'label': 'Genomics',
            'description': ''
        },
        {
            'value': 'Genetically Modified Field and Crop Pasture',
            'label': 'Genetically Modified Field and Crop Pasture',
            'description': ''
        }
    ],
    "FIGSHARE_ARTICLE_TYPES": [
        {
            'value': 'figure',
            'label': 'Figure (Figures, Images)'
        },
        {
            'value': 'media',
            'label': 'Media (Videos, Audio)'
        },
        {
            'value': 'dataset',
            'label': 'Dataset (Tables, Statistics)'
        },
        {
            'value': 'poster',
            'label': 'Poster (Illustrations, Diagrams)'
        },
        {
            'value': 'paper',
            'label': 'Paper (Publication, Documents)'
        },
        {
            'value': 'presentation',
            'label': 'Presentation (Slides)'
        },
        {
            'value': 'thesis',
            'label': 'Thesis (Essays, Dissertations)'
        },
        {
            'value': 'code',
            'label': 'Code (Scripts, Classes, Binaries)'
        }

    ],
    "DATAVERSE_SUBJECTS": [
        {
            'value': 'Arts and Humanities',
            'label': 'Arts and Humanities',
        },
        {
            'value': 'Computer and Information Science',
            'label': 'Computer and Information Science',
        },
        {
            'value': 'Law',
            'label': 'Law',
        },
        {
            'value': 'Engineering',
            'label': 'Engineering',
        },
        {
            'value': 'Social Sciences',
            'label': 'Social Sciences',
        },
        {
            'value': 'Medicine, Health and Life Sciences',
            'label': 'Medicine, Health and Life Sciences',
        },
        {
            'value': 'Agricultural Sciences',
            'label': 'Agricultural Sciences',
        },
        {
            'value': 'Astronomy and Astrophysics',
            'label': 'Astronomy and Astrophysics',
        },
        {
            'value': 'Business and Management',
            'label': 'Business and Management',
        },
        {
            'value': 'Chemistry',
            'label': 'Chemistry',
        },
        {
            'value': 'Earth and Environmental Sciences',
            'label': 'Earth and Environmental Sciences',
        },
        {
            'value': 'Mathematical Sciences',
            'label': 'Mathematical Sciences',
        },
        {
            'value': 'Physics',
            'label': 'Physics',
        },
        {
            'value': 'Other',
            'label': 'Other',
        }
    ],
    "REPO_TYPE_OPTIONS": [
        {
            "value": "dataverse",
            "label": "Dataverse",
            "abbreviation": "dv"
        },
        {
            "value": "dspace",
            "label": "dSPACE",
            "abbreviation": "ds"
        },
        {
            "value": "ckan",
            "label": "CKAN",
            "abbreviation": "ck"
        }
    ],
    "LICENSE_TYPES": [
        {
            'value': 'Apache-2.0',
            'label': 'Apache-2.0'
        },
        {
            'value': 'CC-0',
            'label': 'CC-0'
        },
        {
            'value': 'CC-BY',
            'label': 'CC-BY'
        },
        {
            'value': 'GPL',
            'label': 'GPL'
        },
        {
            'value': 'GPL-2.0',
            'label': 'GPL-2.0'
        },
        {
            'value': 'GPL-3.0',
            'label': 'GPL-3.0'
        },
        {
            'value': 'MIT',
            'label': 'MIT'
        },
    ],
    "YES_NO": [
        {
            'value': 'True',
            'label': 'Yes'
        },
        {
            'value': 'False',
            'label': 'No'
        }
    ],
    "REPOSITORIES": [  # !!! this is deprecated. moved to lookup/drop_downs/metadata_templates_types.json
        {
            'value': 'cg_core',
            'label': 'CG Core',
            'description': 'Template for describing CG-compliant data objects'
        },
        {
            'value': "dtol",
            'label': 'Darwin Tree of Life / Sanger',
            'description': 'Template for descripbing samples created for the Darwin Tree of Life Project'
        },
        {
            'value': 'ena',
            'label': 'ENA - Sequence Reads',
            'description': 'This repository option defines metadata for submission of <strong>raw sequence reads</strong> to the European '
                           'Nucleotide Archive (ENA)'
        },
        {
            'value': 'ena-asm',
            'label': 'ENA - Sequence Assemblies',
            'description': 'This repository option defines metadata for submission of <strong>sequence assemblies</strong> to the European '
                           'Nucleotide Archive (ENA)'
        },
        {
            'value': 'ena-ant',
            'label': 'ENA - Sequence Annotations',
            'description': 'This repository option defines metadata for submission of <strong>sequence annotations</strong> to the European '
                           'Nucleotide Archive (ENA)'
        },
        {
            'value': 'figshare',
            'label': 'Figshare',
            'description': 'Figshare accepts many file formats, and can be used to submit file types including PDFs, image, audio, and video files'
        },
        {
            'value': 'miappe',
            'label': 'MIAPPE Compliant',
            'description': 'MIAPPE is a Minimum Information (MI) standard for plant phenotyping. This repository option defines a list of '
                           'attributes for describing a phenotyping experiment'
        },
        {
            'value': 'dcterms',
            'label': 'Dublin Core',
            'description': 'Dublin Core is a generic community stardard metadata set for describing digital objects (such as images, video, pdfs, '
                           'webpages) and physical objects (such as books or CDs). Items described with this schema can be submitted to Dataverse '
                           'or dSpace instances'
        },

        # {
        #     'value': 'MetaboLights',
        #     'label': 'MetaboLights'
        # },
        # {
        #     'value': 'unknown',
        #     'label': 'Unknown'
        # }
    ],
    "OMICS_TYPES": [
        {
            "value": 1,
            "label": "Sequence Reads",
            "description": "Use this option to submit raw data from various sequencing platforms"
        },
        {
            "value": 2,
            "label": "Sequence Assemblies",
            "description": "Use this option to submit assembled scaffolds",
        },
        {
            "value": 3,
            "label": "Annotations",
            "description": "Use this option to submit Annotations of objects already submitted"
        }
    ],
    "SAMPLE_TYPES": [  # !!! this is deprecated. moved to lookup/drop_downs/sample_types.json
        {
            "value": "biosample",
            "label": "Biosample Standard",
            "description": "Biosmaple samples are based on <a href='https://www.ebi.ac.uk/biosamples/' target='_blank'>BioSamples</a>. They are "
                           "<strong>repository agnostic</strong>, and are better suited for describing samples in a generic manner or in contexts "
                           "where the target repository isn't known in advance."
        },
        {
            "value": "isasample",
            "label": "COPO Standard",
            "description": "COPO samples are based on the <a href='http://isa-tools.org/' target='_blank'>Investigation, Study and Assay </a> (ISA) "
                           "specifications, and are better tailored for describing samples that will subsequently become part of data submissions "
                           "to repositories such as <strong>ENA</strong> and <strong>Metabolights</strong>."
        },
        {
            "value": "dtol",
            "label": "Sanger / Darwin Tree of Life",
            "description": "Samples to be entered for the Darwin Tree of Life Project"
        }
    ],
    "GROWTH_AREAS": [
        {
            "value": "growth_chamber_GC",
            "label": "Growth Chamber"
        },
        {
            "value": "greenhouse_rooting",
            "label": "Greenhouse",
            "schema": "miappe_rooting_greenhouse"
        },
        {
            "label": "Open_Top_Chamber",
            "value": "open top chamber"
        },
        {
            "value": "experimental_garden",
            "label": "Experimental Garden"
        },
        {
            "label": "Experimental_Field",
            "value": "field_rooting",
            "schema": "miappe_rooting_field"
        }
    ],
    "ROOTING_MEDIUM": [
        {
            "value": "aeroponics",
            "label": "Aeroponics"
        },
        {
            "value": "hydroponics_water_based",
            "label": "Hydroponics (water based)"
        },
        {
            "value": "hydroponics_solid-media_based",
            "label": "Hydroponics (solid-media based)"
        },
        {
            "value": "soil_sand",
            "label": "Soil (sandy)"
        },
        {
            "value": "soil_peat",
            "label": "Soil (peat)"
        },
        {
            "value": "soil_clay",
            "label": "Soil (clay)"
        },
        {
            "value": "soil_mixed",
            "label": "Soil (mixed)"
        },
        {
            "value": "other",
            "label": "Other"
        }
    ],
    "GROWTH_NUTRIENTS": [
        {
            "value": "hydroponics",
            "label": "Hydroponics",
            "schema": "hydroponics"
        },
        {
            "value": "soil",
            "label": "Soil",
            "schema": "soil"
        }
    ],
    "WATERING_OPTIONS": [
        {
            "value": "top",
            "label": "Top"
        },
        {
            "value": "bottom",
            "label": "Bottom"
        },
        {
            "value": "drip",
            "label": "Drip"
        }
    ]
}

# !!!!!   MAKE SURE VOCAB REPO NAMES AND DROPDOWN REPOSITORIES ARE IN SYNC
VOCAB = {
    "REPO_NAMES": {
        "figshare": {"value": "figshare",
                     "label": "Figshare"},
        "ena": {"value": "ena",
                "label": "European Nucleotide Archive (ENA)"
                },
        "metab": {"value": "metabolights",
                  "label": "metabolights"},
        "bip": {"value": "bip",
                "label": "Brassica Information Portal"}
    },
    "DA_COMPONENTS": {
        "submission": {
            "value": "submission"
        },
        "source": {
            "value": "source"
        },
        "sample": {
            "value": "sample"
        },
        "profile": {
            "value": "profile"
        },
        "datafile": {
            "value": "datafile"
        },
        "publication": {
            "value": "publication"
        },
        "person": {
            "value": "person"
        },

    },

}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# tags for generating html elements
HTML_TAGS = {
    "oauth_required": '<a href="/rest/forward_to_figshare/"> Grant COPO access to your Figshare account </a>',
    "bootstrap_button": '<button type="button" id="{btn_id!s}" class="btn btn-{btn_type!s}">{btn_text!s}</button>',
    "bootstrap_button_right": '<button type="button" id="{btn_id!s}" class="btn btn-{btn_type!s} pull-right">{btn_text!s}</button>',
    "bootstrap_button_small": '<button type="button" id="{btn_id!s}" class="btn btn-{btn_type!s} btn-sm">{btn_text!s}</button>',
    "bootstrap_button_small_right": '<button type="button" id="{btn_id!s}" class="btn btn-{btn_type!s} btn-sm pull-right">{btn_text!s}</button>',

    "action_buttons": ''

}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# for displaying information/guidance mostly via tooltips
UI_INFO = {
    'study_type_add_info': "Use this form to add new study types",
    'study_type_clone_info': "Use this form to clone existing study types",
    'sample_add_info': "Use this form to add/edit study sample and assign to studies",
    'sample_assign_info': "View allows for assigning samples to current study",
    'sample_unassign_warning': 'Assigned samples about to be deleted!.',
    'add_form_title': "<h4 class='modal-title'>Add New <span style='text-transform: capitalize;'>{component_name!s}</span></h4>",
    'edit_form_title': "<h4 class='modal-title'>Edit <span style='text-transform: capitalize;'>{component_name!s}</span></h4>",
    'publication_doi_resolution': 'Enter a DOI or PubMed ID to be resolved',
    'user_defined_attribute_message': "This will be treated as a user-defined attribute",
    'files_add_info': 'Use this dialog to specify the specific details of the file you just uploaded',
    'system_suggested_attribute_message': "This is a system-suggested attribute",
    'component_delete_body': "<p>You are about to delete the highlighted {component_name!s} record.</p> <p>Do you want to proceed?</p>",
    'component_delete_title': "<h4 class='modal-title'>Confirm Delete Action</h4>",
    'component_unassign_body': "<p>You are about to unassign the highlighted {component_name!s}.</p> <p>Do you want to proceed?</p>",
    'component_unassign_title': "<h4 class='modal-title'>Confirm <span style='text-transform: capitalize;'>{component_name!s}</span> "
                                "Unassignment</h4>"

}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# specifies file paths holding the configs for wizard stages:
WIZARD_FILES = {
    'start': os.path.join(RESOLVER['wizards_datafile'], 'start_stages.json'),
    'ena': os.path.join(RESOLVER['wizards_datafile'], 'ena_stages_seq.json'),
    'ena-asm': os.path.join(RESOLVER['wizards_datafile'], 'ena_stages_asm.json'),
    'ena-ant': os.path.join(RESOLVER['wizards_datafile'], 'ena_stages_ant.json'),
    'figshare': os.path.join(RESOLVER['wizards_datafile'], 'figshare_stages.json'),
    'miappe': os.path.join(RESOLVER['wizards_datafile'], 'miappe_stages.json'),
    'sample_start': os.path.join(RESOLVER['wizards_sample'], 'start_stages.json'),
    'sample_attributes': os.path.join(RESOLVER['wizards_sample'], 'attributes_stages.json'),
    'dataverse': os.path.join(RESOLVER['wizards_datafile'], 'dc_stages.json'),
    'dcterms': os.path.join(RESOLVER['wizards_datafile'], 'dc_stages.json'),
    'cg_core': os.path.join(RESOLVER['wizards_datafile'], 'cg_core_stages.json'),
    'dtol_mappings': os.path.join(RESOLVER['wizards_sample'], 'dtol_field_mapping.json'),
    'dtol_manifests': os.path.join(RESOLVER['wizards_sample'], 'dtol_manifests'),
    'sample_details': os.path.join(RESOLVER['isa_mappings'], 'sample.json'),
    'ena_seq_manifest': os.path.join(RESOLVER['isa_mappings'], "ena_seq.json"),
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# strings used in creating requests to ontology services
# fieldList={fields!s}
# ontology={ontologies!s}
# size=50&r&
ONTOLOGY_LKUPS = {
    'ontologies_to_search': 'go,co,po',
    'fields_to_search': 'label,description,short_form',
    'ebi_ols_autocomplete': 'http://www.ebi.ac.uk/ols/api/select?q={term!s}&ontology={'
                            'ontology_names!s}&rows=50&local=true&type=class&fieldList=iri,label,short_form,obo_id,ontology_name,ontology_prefix,'
                            'description,type,id',
    'ontology_file_uri': 'http://data.bioontology.org/ontologies/',
    'copo_ontologies': os.path.join(RESOLVER['lookup'], "ontology_references.json")
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# path to different message configurations across the system
MESSAGES_LKUPS = {
    'HELP_MESSAGES': {
        'datafile': os.path.join(RESOLVER['lookup'], 'help_messages', 'datafile_help.json'),
        'sample': os.path.join(RESOLVER['lookup'], 'help_messages', 'sample_help.json'),
        'group': os.path.join(RESOLVER['lookup'], 'help_messages', 'group_help.json'),
        'global': os.path.join(RESOLVER['lookup'], 'help_messages', 'global_help.json'),
        'context_help': os.path.join(RESOLVER['lookup'], 'help_messages', 'context_help.json'),
    },
    'wizards_messages': os.path.join(RESOLVER['wizards_messages'], 'wizard_messages.json'),
    'lookup_messages': os.path.join(RESOLVER['lookup'], 'messages.json'),
    'message_templates': os.path.join(RESOLVER['lookup'], 'message_templates.json'),
    'exception_messages': os.path.join(RESOLVER['copo_exceptions'], 'messages.json')
}

# help messages

# path to rating templates for rating description metadata
METADATA_RATING_TEMPLATE_LKUPS = {
    'rating_template': os.path.join(RESOLVER['schemas_utils'], 'metadata_rating_templates', 'rating_template_v1.json')
}

FIGSHARE_API_URLS = {
    'base_url': 'https://api.figshare.com/v2/{endpoint}',
    'access_token': 'https://figshare.com/account/applications/authorize?client_id=978ec401ab6ad6c1d66f0b6cef3015d71a4734d7&scope=all&response_type'
                    '=code&redirect_uri={redirect_url}/',
    'login_return': '{return_url}?figshare_oauth=true',
    'authorization_token': 'https://api.figshare.com/v2/token'
}

# THIS IS DEPRECATED!!! SEE data_utils.get_db_json_schema()
ISA_SCHEMAS = {
    'investigation_schema': '/schemas/copo/dbmodels/investigation_schema.json',
    'publication_schema': '/schemas/copo/dbmodels/publication_schema.json',
    'person_schema': '/schemas/copo/dbmodels/person_schema.json',
    'ontology_annotation_schema': '/schemas/copo/dbmodels/ontology_annotation_schema.json',
    'organization_schema': '/schemas/copo/dbmodels/organization_schema.json',
    'study_schema': '/schemas/copo/dbmodels/study_schema.json',
    'assay_schema': '/schemas/copo/dbmodels/assay_schema.json',
    'data_schema': '/schemas/copo/dbmodels/data_schema.json',
    'comment_schema': '/schemas/copo/dbmodels/comment_schema.json',
    'material_schema': '/schemas/copo/dbmodels/material_schema.json',
    'sample_schema': '/schemas/copo/dbmodels/sample_schema.json',
    'source_schema': '/schemas/copo/dbmodels/source_schema.json',
    'material_attribute_value_schema': '/schemas/copo/dbmodels/material_attribute_value_schema.json',
    'protocol_schema': '/schemas/copo/dbmodels/protocol_schema.json',
    'protocol_parameter_schema': '/schemas/copo/dbmodels/protocol_parameter_schema.json',
}

# •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••#
# templates for composing reusable UI buttons - This is getting deprecated!!! Moved to components_templates.html
BUTTON_TEMPLATES = {
    "title": "Button templates",
    "description": "Provides templates for composing reusable buttons. 'btnType' can either be: "
                   "(1) 'single' - if the button's action is intended to impact just a single record (e.g., edit), "
                   "(2) 'multi' - if the buttons's action is intended to impact one or more records,"
                   "(3) 'all' - always true, and none dependent of row selections e.g., add button",
    "templates": {
        "edit_record_single": {
            "text": "Edit",
            "className": " green button copo-dt",
            "iconClass": "fa fa-pencil-square-o",
            "btnAction": "edit",
            "btnType": "single",
            "btnMessage": "Edit selected"
        },
        "delete_record_multi": {
            "text": "Delete",
            "className": " red button copo-dt",
            "iconClass": "fa fa-trash-o",
            "btnAction": "delete",
            "btnType": "multi",
            "btnMessage": "Delete selected"
        },
        "summarise_record_single": {
            "text": "Summarise",
            "className": " teal button copo-dt",
            "iconClass": "fa fa-info",
            "btnAction": "summarise",
            "btnType": "single",
            "btnMessage": "Summarise selected"
        },
        "add_record_single": {
            "text": "Add",
            "className": " blue button copo-dt",
            "iconClass": "fa fa-plus",
            "btnAction": "add",
            "btnType": "all",
            "btnMessage": "Add new record"
        },
        "edit_row": {
            "text": "Edit",
            "className": "copo-dt btn btn-success",
            "iconClass": "fa fa-pencil-square-o",
            "btnAction": "edit",
            "btnType": "single"
        },
        "delete_row": {
            "text": "Delete",
            "className": "copo-dt btn btn-danger",
            "iconClass": "fa fa-trash-o",
            "btnAction": "delete"
        },
        "describe_row": {
            "text": "Describe",
            "className": "copo-dt btn btn-primary",
            "iconClass": "fa fa-tags",
            "btnAction": "describe"
        },
        "add_new_samples_global": {
            "text": "Add New Samples",
            "className": "copo-dt btn btn-success",
            "iconClass": "fa fa-plus-circle",
            "btnAction": "new_samples"
        },
        "info_row": {
            "text": "Info",
            "className": "copo-dt btn btn-info",
            "iconClass": "fa fa-info-circle",
            "btnAction": "info"
        },
        "convert_row": {
            "text": "Convert",
            "className": "copo-dt btn btn-custom",
            "iconClass": "fa fa-superpowers",
            "btnAction": "convert"
        },
        "delete_global": {
            "text": "Delete selected",
            "className": "copo-dt btn btn-danger",
            "iconClass": "fa fa-trash-o",
            "btnAction": "delete"
        },
        "describe_global": {
            "text": "Describe",
            "className": "copo-dt btn btn-primary",
            "iconClass": "fa fa-tags",
            "btnAction": "describe"
        },
        "undescribe_global": {
            "text": "[Un]Describe",
            "className": "copo-dt btn btn-danger",
            "iconClass": "fa fa-tags",
            "btnAction": "undescribe"
        },
        "submit_assembly_multi": {
            "text": "Submit",
            "className": "copo-dt btn btn-danger",
            "iconClass": "fa fa-tags",
            "btnAction": "submit_assembly"
        },        
        "submit_annotation_multi": {
            "text": "Submit",
            "className": "copo-dt btn btn-danger",
            "iconClass": "fa fa-tags",
            "btnAction": "submit_annotation"
        },   
        "submit_read_multi": {
            "text": "Submit",
            "className": "copo-dt btn btn-danger",
            "iconClass": "fa fa-tags",
            "btnAction": "submit_read"
        },    
        "delete_read_multi": {
            "text": "Delete",
            "className": " red button copo-dt",
            "iconClass": "fa fa-trash-o",
            "btnAction": "delete",
            "btnType": "multi",
            "btnMessage": "Delete selected"
        },      
    }
}
REPO_NAME_LOOKUP = {
    'ena-ant': 'Sequence Annotation',
    'ena-asm': 'Sequence Assembly',
    'ena': 'Sequence Reads',
    'figshare': 'Figshare',
    'dataverse': 'Dataverse'
}

'''
primer fields template
Here we are referencing json configs which are found in web/apps/web_copo/wizards/datafile/
adding here will make the schema importable as primer fields in a new experimatal template
'''
TEMPLATES_TO_APPEAR_IN_EDITOR = ["dc_stages", "miappe", "dcterms"]

DTOL_SAMPLE_COLLECTION_LOCATION_STATEMENT = {
    "__SPAIN__" : "The biological material collected in Spain, and used to generate digital sequences, was retrieved from \
wildlife taxa regulated by the Spanish Royal Decree 124/2017 (https://www.boe.es/eli/es/rd/2017/02/24/124)."

}

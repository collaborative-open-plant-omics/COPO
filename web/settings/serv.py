# define parameters for repositories
from tools import resolve_env

REPOSITORIES = {
    'ASPERA': {
        'resource_path': 'tools/reposit/aspera/Aspera Connect.app/Contents/Resources/' + resolve_env.get_env(
            'ASPERA_PLUGIN_DIRECTORY') + '/',
        'user_token': resolve_env.get_env('WEBIN_USER'),
        'password': resolve_env.get_env('WEBIN_USER_PASSWORD'),
        'remote_path': ''

    },
    'IRODS': {
        'api': 'irods',
        'resource_path': '/tempZone/home/rods/copo-data',
        'credentials': {
            'user_token': '',
            'host_token': '',
            'program': 'python',
            'password': '',
            'script': 'myptest.py'
        }
    },
    'ORCID': {
        'api': 'orcid',
        'client_id': '0000-0002-4011-2520',
        'client_secret': '634ce113-2768-40bf-a4a7-20e8fbf8aa10',  # TODO: put in secret_settings
        'urls': {
            'ouath/token': 'https://api.sandbox.orcid.org/oauth/token?',
            'base_url': 'https://sandbox.orcid.org',
            'authorise_url': resolve_env.get_env('ORCID_REDIRECT'),
            'redirect': 'copo',
        }
    },
    'ENA': {
        'urls': {
            'submission': {
                'test': 'https://www-test.ebi.ac.uk/ena/submit/drop-box/submit/',
                'production': 'https://www.ebi.ac.uk/ena/submit/drop-box/submit/'
            }
        }
    }
}

UI_CONFIG_SOURCES = {
    'INVESTIGATION_FILE_XML': 'https://raw.githubusercontent.com/ISA-tools/Configuration-Files/master'
                              '/isaconfig-default_v2014-01-16/investigation.xml',
    'STUDY_SAMPLE_FILE_XML': 'https://raw.githubusercontent.com/ISA-tools/Configuration-Files/master'
                             '/isaconfig-default_v2014-01-16/studySample.xml',

    'STUDY_ASSAY_GENOME_SEQ_FILE_XML': 'https://raw.githubusercontent.com/ISA-tools/Configuration-Files/master'
                                       '/isaconfig-default_v2014-01-16/genome_seq.xml',
    'STUDY_ASSAY_METAGENOME_SEQ_FILE_XML': 'https://raw.githubusercontent.com/ISA-tools/Configuration-Files/master'
                                           '/isaconfig-default_v2014-01-16/metagenome_seq.xml',
    'STUDY_ASSAY_TRANSCRIPTOME_ANALYSIS_FILE_XML': 'https://raw.githubusercontent.com/ISA-tools/Configuration-Files/master'
                                                   '/isaconfig-default_v2014-01-16/transcription_seq.xml'
}

WEB_SERVICES = {
    'COPO': {
        'get_id': 'http://v0514.nbi.ac.uk:1025/id/'
    }
}

DOI_SERVICES = {
    "base_url": "http://dx.doi.org/",
    "namespaces": {
        "DC": "http://purl.org/dc/terms/",
        "FOAF": "http://xmlns.com/foaf/0.1/"
    }
}

NCBI_SERVICES = {
    "PMC_APIS": {
        "doi_pmid_idconv": "http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi!s}&format=json",
        "pmid_doi_esummary": "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={"
                             "pmid!s}&retmode=json"
    }
}

EXPORT_LOCATIONS = {
    'ENA': {
        'export_path': '~/Desktop/'
    }
}

ENA_TYPES = ["ena", "ena-asm"]

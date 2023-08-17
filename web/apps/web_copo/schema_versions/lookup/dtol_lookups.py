# FS - 18/8/2020
# this module contains lookups and mappings pertaining to DTOL functionality
# such as validation enumerations and mappings between different field names
from tools import resolve_env


def get_collection_location_1(str):
    return str.split('|')[0].strip()


def get_collection_location_2(str):
    return "|".join(str.split('|')[1:])


def get_default_data_function(str):
    return str.lower().replace("_", " ").strip()


def exec_function(func=get_default_data_function, str=str()):
    return func(str)


DTOL_ENA_MAPPINGS = {
    'ASSOCIATED_BIOGENOME_PROJECTS': {
        'ena': 'associated biogenome projects'
    },
    'BARCODE_HUB': {
        'ena': 'barcoding center'
    },
    'COLLECTED_BY': {
        'ena': 'collected_by'
    },
    'COLLECTION_LOCATION_1': {
        'info': "split COLLECTION_LOCATION on first '|' and put left hand side here (should be country)",
        'ena': 'geographic location (country and/or sea)',
        'ena_data_function': get_collection_location_1
    },
    'COLLECTION_LOCATION_2': {
        'info': "split COLLECTION_LOCATION on first '|' and put right hand side here (should be a list of '|' separated locations)",
        'ena': 'geographic location (region and locality)',
        'ena_data_function': get_collection_location_2
    },
    'COLLECTOR_AFFILIATION': {
        'ena': 'collecting institution'
    },
    'COLLECTOR_ORCID_ID': {
        'ena': 'collector ORCID ID'
    },
    'CULTURE_OR_STRAIN_ID': {
        'ena': 'culture_or_strain_id'
    },
    'DATE_OF_COLLECTION': {
        'ena': 'collection date'
    },
    'DECIMAL_LATITUDE': {
        'ena': 'geographic location (latitude)'
    },
    'DECIMAL_LONGITUDE': {
        'ena': 'geographic location (longitude)'
    },
    'DEPTH': {
        'ena': 'geographic location (depth)'
    },
    'DESCRIPTION_OF_COLLECTION_METHOD': {
        'ena': 'sample collection device or method'
    },
    'DNA_VOUCHER_ID_FOR_BIOBANKING': {
        'ena': 'bio_material'
    },
    'ELEVATION': {
        'ena': 'geographic location (elevation)'
    },
    'GAL': {
        'ena': 'GAL'
    },
    'GAL_SAMPLE_ID': {
        'ena': 'GAL_sample_id'
    },
    'HABITAT': {
        'ena': 'habitat'
    },
    'IDENTIFIED_BY': {
        'ena': 'identified_by'
    },
    'IDENTIFIER_AFFILIATION': {
        'ena': 'identifier_affiliation'
    },
    'LATITUDE_END': {
        'ena': 'geographic location end (latitude_end)'
    },
    'LATITUDE_START': {
        'ena': 'geographic location start (latitude_start)'
    },
    'LIFESTAGE': {
        'ena': 'lifestage'
    },
    'LONGITUDE_END': {
        'ena': 'geographic location end (longitude_end)'
    },
    'LONGITUDE_START': {
        'ena': 'geographic location start (longitude_start)'
    },
    'ORGANISM_PART': {
        'ena': 'organism part'
    },
    'ORIGINAL_COLLECTION_DATE': {
        'ena': 'original collection date'
    },
    'ORIGINAL_DECIMAL_LATITUDE': {
        'ena': 'original geographic location (latitude)'
    },
    'ORIGINAL_DECIMAL_LONGITUDE': {
        'ena': 'original geographic location (longitude)'
    },
    'ORIGINAL_GEOGRAPHIC_LOCATION': {
        'ena': 'original collection location'
    },
    'PARTNER': {
        'ena': 'GAL'
    },
    'PARTNER_SAMPLE_ID': {
        'ena': 'GAL_sample_id'
    },
    'PROXY_TISSUE_VOUCHER_ID_FOR_BIOBANKING': {
        'ena': 'proxy biomaterial'
    },
    'PROXY_VOUCHER_ID': {
        'ena': 'proxy voucher'
    },
    'PROXY_VOUCHER_LINK': {
        'ena': 'proxy voucher url'
    },
    'RELATIONSHIP': {
        'ena': 'relationship'
    },
    'SAMPLE_COORDINATOR': {
        'ena': 'sample coordinator'
    },
    'SAMPLE_COORDINATOR_AFFILIATION': {
        'ena': 'sample coordinator affiliation'
    },
    'SAMPLE_COORDINATOR_ORCID_ID': {
        'ena': 'sample coordinator ORCID ID'
    },
    'SEX': {
        'ena': 'sex'
    },
    'SPECIMEN_ID': {
        'ena': 'specimen_id'
    },
    'TIME_OF_COLLECTION': {
        'ena': 'time of collection'
    },
    'TISSUE_VOUCHER_ID_FOR_BIOBANKING': {
        'ena': 'bio_material'
    },
    'VOUCHER_ID': {
        'ena': 'specimen_voucher'
    },
    'VOUCHER_INSTITUTION': {
        'ena': 'voucher institution url'
    },
    'VOUCHER_LINK': {
        'ena': 'specimen voucher url'
    },
    'public_name': {
        'ena': 'tolid'
    },
    'sampleDerivedFrom': {
        'ena': 'sample derived from'
    },
    'sampleSameAs': {
        'ena': 'sample same as'
    },
    'sampleSymbiontOf': {
        'ena': 'sample symbiont of'
    }
}

DTOL_ENUMS = {
    'ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_RIGHTS_APPLICABLE':
        [
            'Y',
            'N'
        ],
    'BARCODE_HUB': [
        'MARINE BIOLOGICAL ASSOCIATION',
        'NATURAL HISTORY MUSEUM',
        'ROYAL BOTANIC GARDEN EDINBURGH',
        'ROYAL BOTANIC GARDENS KEW/NATURAL HISTORY MUSEUM',
        'UNIVERSITY OF OXFORD',
        'NOT_COLLECTED',
        'NOT_PROVIDED'
    ],
    'BARCODING_STATUS': [
        'DNA_BARCODE_EXEMPT',
        'DNA_BARCODING_COMPLETED',
        'DNA_BARCODING_FAILED',
        'DNA_BARCODING_TO_BE_PERFORMED_GAL'
    ],
    'CELL_NUMBER': [
        '1',
        '2-10',
        '11-50',
        '51-100',
        '101-10000',
        '10001-50000',
        '50001-100000',
        '100001-500000',
        '500001-1000000',
        '1000000+'
    ],
    'COLLECTION_LOCATION':
        [
            'AFGHANISTAN',
            'ALBANIA',
            'ALGERIA',
            'AMERICAN SAMOA',
            'ANDORRA',
            'ANGOLA',
            'ANGUILLA',
            'ANTARCTICA',
            'ANTIGUA AND BARBUDA',
            'ARCTIC OCEAN',
            'ARGENTINA',
            'ARMENIA',
            'ARUBA',
            'ASHMORE AND CARTIER ISLANDS',
            'ATLANTIC OCEAN',
            'AUSTRALIA',
            'AUSTRIA',
            'AZERBAIJAN',
            'BAHAMAS',
            'BAHRAIN',
            'BAKER ISLAND',
            'BALTIC SEA',
            'BANGLADESH',
            'BARBADOS',
            'BASSAS DA INDIA',
            'BELARUS',
            'BELGIUM',
            'BELIZE',
            'BENIN',
            'BERMUDA',
            'BHUTAN',
            'BOLIVIA',
            'BORNEO',
            'BOSNIA AND HERZEGOVINA',
            'BOTSWANA',
            'BOUVET ISLAND',
            'BRAZIL',
            'BRITISH VIRGIN ISLANDS',
            'BRUNEI',
            'BULGARIA',
            'BURKINA FASO',
            'BURUNDI',
            'CAMBODIA',
            'CAMEROON',
            'CANADA',
            'CAPE VERDE',
            'CAYMAN ISLANDS',
            'CENTRAL AFRICAN REPUBLIC',
            'CHAD',
            'CHILE',
            'CHINA',
            'CHRISTMAS ISLAND',
            'CLIPPERTON ISLAND',
            'COCOS ISLANDS',
            'COLOMBIA',
            'COMOROS',
            'COOK ISLANDS',
            'CORAL SEA ISLANDS',
            'COSTA RICA',
            "COTE D'IVOIRE",
            'CROATIA',
            'CUBA',
            'CURACAO',
            'CYPRUS',
            'CZECH REPUBLIC',
            'DEMOCRATIC REPUBLIC OF THE CONGO',
            'DENMARK',
            'DJIBOUTI',
            'DOMINICA',
            'DOMINICAN REPUBLIC',
            'EAST TIMOR',
            'ECUADOR',
            'EGYPT',
            'EL SALVADOR',
            'EQUATORIAL GUINEA',
            'ERITREA',
            'ESTONIA',
            'ETHIOPIA',
            'EUROPA ISLAND',
            'FALKLAND ISLANDS (ISLAS MALVINAS)',
            'FAROE ISLANDS',
            'FIJI',
            'FINLAND',
            'FRANCE',
            'FRENCH GUIANA',
            'FRENCH POLYNESIA',
            'FRENCH SOUTHERN AND ANTARCTIC LANDS',
            'GABON',
            'GAMBIA',
            'GAZA STRIP',
            'GEORGIA',
            'GERMANY',
            'GHANA',
            'GIBRALTAR',
            'GLORIOSO ISLANDS',
            'GREECE',
            'GREENLAND',
            'GRENADA',
            'GUADELOUPE',
            'GUAM',
            'GUATEMALA',
            'GUERNSEY',
            'GUINEA',
            'GUINEA-BISSAU',
            'GUYANA',
            'HAITI',
            'HEARD ISLAND AND MCDONALD ISLANDS',
            'HONDURAS',
            'HONG KONG',
            'HOWLAND ISLAND',
            'HUNGARY',
            'ICELAND',
            'INDIA',
            'INDIAN OCEAN',
            'INDONESIA',
            'IRAN',
            'IRAQ',
            'IRELAND',
            'ISLE OF MAN',
            'ISRAEL',
            'ITALY',
            'JAMAICA',
            'JAN MAYEN',
            'JAPAN',
            'JARVIS ISLAND',
            'JERSEY',
            'JOHNSTON ATOLL',
            'JORDAN',
            'JUAN DE NOVA ISLAND',
            'KAZAKHSTAN',
            'KENYA',
            'KERGUELEN ARCHIPELAGO',
            'KINGMAN REEF',
            'KIRIBATI',
            'KOSOVO',
            'KUWAIT',
            'KYRGYZSTAN',
            'LAOS',
            'LATVIA',
            'LEBANON',
            'LESOTHO',
            'LIBERIA',
            'LIBYA',
            'LIECHTENSTEIN',
            'LITHUANIA',
            'LUXEMBOURG',
            'MACAU',
            'MACEDONIA',
            'MADAGASCAR',
            'MALAWI',
            'MALAYSIA',
            'MALDIVES',
            'MALI',
            'MALTA',
            'MARSHALL ISLANDS',
            'MARTINIQUE',
            'MAURITANIA',
            'MAURITIUS',
            'MAYOTTE',
            'MEDITERRANEAN SEA',
            'MEXICO',
            'MICRONESIA',
            'MIDWAY ISLANDS',
            'MOLDOVA',
            'MONACO',
            'MONGOLIA',
            'MONTENEGRO',
            'MONTSERRAT',
            'MOROCCO',
            'MOZAMBIQUE',
            'MYANMAR',
            'NAMIBIA',
            'NAURU',
            'NAVASSA ISLAND',
            'NEPAL',
            'NETHERLANDS',
            'NEW CALEDONIA',
            'NEW ZEALAND',
            'NICARAGUA',
            'NIGER',
            'NIGERIA',
            'NIUE',
            'NORFOLK ISLAND',
            'NORTH KOREA',
            'NORTH SEA',
            'NORTHERN MARIANA ISLANDS',
            'NORWAY',
            'OMAN',
            'PACIFIC OCEAN',
            'PAKISTAN',
            'PALAU',
            'PALMYRA ATOLL',
            'PANAMA',
            'PAPUA NEW GUINEA',
            'PARACEL ISLANDS',
            'PARAGUAY',
            'PERU',
            'PHILIPPINES',
            'PITCAIRN ISLANDS',
            'POLAND',
            'PORTUGAL',
            'PUERTO RICO',
            'QATAR',
            'REPUBLIC OF THE CONGO',
            'REUNION',
            'ROMANIA',
            'ROSS SEA',
            'RUSSIA',
            'RWANDA',
            'SAINT HELENA',
            'SAINT KITTS AND NEVIS',
            'SAINT LUCIA',
            'SAINT PIERRE AND MIQUELON',
            'SAINT VINCENT AND THE GRENADINES',
            'SAMOA',
            'SAN MARINO',
            'SAO TOME AND PRINCIPE',
            'SAUDI ARABIA',
            'SENEGAL',
            'SERBIA',
            'SEYCHELLES',
            'SIERRA LEONE',
            'SINGAPORE',
            'SINT MAARTEN',
            'SLOVAKIA',
            'SLOVENIA',
            'SOLOMON ISLANDS',
            'SOMALIA',
            'SOUTH AFRICA',
            'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS',
            'SOUTH KOREA',
            'SOUTHERN OCEAN',
            'SPAIN',
            'SPRATLY ISLANDS',
            'SRI LANKA',
            'SUDAN',
            'SURINAME',
            'SVALBARD',
            'SWAZILAND',
            'SWEDEN',
            'SWITZERLAND',
            'SYRIA',
            'TAIWAN',
            'TAJIKISTAN',
            'TANZANIA',
            'TASMAN SEA',
            'THAILAND',
            'TOGO',
            'TOKELAU',
            'TONGA',
            'TRINIDAD AND TOBAGO',
            'TROMELIN ISLAND',
            'TUNISIA',
            'TURKEY',
            'TURKMENISTAN',
            'TURKS AND CAICOS ISLANDS',
            'TUVALU',
            'UGANDA',
            'UKRAINE',
            'UNITED ARAB EMIRATES',
            'UNITED KINGDOM',
            'URUGUAY',
            'USA',
            'UZBEKISTAN',
            'VANUATU',
            'VENEZUELA',
            'VIET NAM',
            'VIRGIN ISLANDS',
            'WAKE ISLAND',
            'WALLIS AND FUTUNA',
            'WEST BANK',
            'WESTERN SAHARA',
            'YEMEN',
            'ZAMBIA',
            'ZIMBABWE',
            'NOT APPLICABLE',
            'NOT COLLECTED',
            'NOT PROVIDED'
        ],
    'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE':
        [
            'DIFFICULT',
            'FULL_CURATION',
            'HIGH_PRIORITY',
            'NOT_APPLICABLE',
            'NOT_COLLECTED',
            'NOT_PROVIDED'
        ],
    'DNA_REMOVED_FOR_BIOBANKING':
        [
            'Y',
            'N'
        ],
    'ETHICS_PERMIT_REQUIRED':
        [
            'Y',
            'N'
        ],
    'GAL': {
        'DTOL': [
            'EARLHAM INSTITUTE',
            'MARINE BIOLOGICAL ASSOCIATION',
            'NATURAL HISTORY MUSEUM',
            'ROYAL BOTANIC GARDEN EDINBURGH',
            'ROYAL BOTANIC GARDENS KEW',
            'SANGER INSTITUTE',
            'UNIVERSITY OF OXFORD'
        ],
        'DTOL_ENV': [
            'EARLHAM INSTITUTE',
            'MARINE BIOLOGICAL ASSOCIATION',
            'NATURAL HISTORY MUSEUM',
            'ROYAL BOTANIC GARDEN EDINBURGH',
            'ROYAL BOTANIC GARDENS KEW',
            'SANGER INSTITUTE',
            'UNIVERSITY OF OXFORD'
        ],
        'ERGA':
            [
                'CENTRO NACIONAL DE ANÁLISIS GENÓMICO',
                'DNA SEQUENCING AND GENOMICS LABORATORY, HELSINKI GENOMICS CORE FACILITY',
                'DRESDEN-CONCEPT',
                'EARLHAM INSTITUTE',
                'FUNCTIONAL GENOMIC CENTER ZURICH',
                'GENOSCOPE',
                'GIGA-GENOMICS CORE FACILITY UNIVERSITY OF LIEGE',
                'HANSEN LAB, DENMARK',
                'INDUSTRY PARTNER',
                'LAUSANNE GENOMIC TECHNOLOGIES FACILITY',
                'LEIBNIZ INSTITUTE FOR THE ANALYSIS OF BIODIVERSITY CHANGE, MUSEUM KOENIG, BONN',
                'NEUROMICS SUPPORT FACILITY, UANTWERP, VIB',
                'NGS BERN',
                'NGS COMPETENCE CENTER TÜBINGEN',
                'NORWEGIAN SEQUENCING CENTRE',
                'SANGER INSTITUTE',
                'SCILIFELAB',
                'SVARDAL LAB, ANTWERP',
                'UNIVERSITY OF BARI',
                'UNIVERSITY OF FLORENCE',
                'WEST GERMAN GENOME CENTRE',
                'Other_ERGA_Associated_GAL'
            ]
    },
    'HAZARD_GROUP': {
        'DTOL':
            [
                'HG1',
                'HG2',
                'HG3'
            ],
        'ASG':
            [
                'HG1',
                'HG2',
                'HG3'],
        'ERGA':
            [
                '1',
                '2',
                '3',
                '4'
            ]
    },
    'LIFESTAGE':
        [
            'ADULT',
            'EGG',
            'EMBRYO',
            'GAMETOPHYTE',
            'JUVENILE',
            'LARVA',
            'PUPA',
            'SPORE_BEARING_STRUCTURE',
            'SPOROPHYTE',
            'VEGETATIVE_CELL',
            'VEGETATIVE_STRUCTURE',
            'ZYGOTE',
            'NOT_APPLICABLE',
            'NOT_COLLECTED',
            'NOT_PROVIDED'
        ],
    'MIXED_SAMPLE_RISK':
        [
            'Y',
            'N'
        ],
    'NAGOYA_PERMITS_REQUIRED':
        [
            'Y',
            'N'
        ],
    'ORGANISM_PART':
        [
            '**OTHER_FUNGAL_TISSUE**',
            '**OTHER_PLANT_TISSUE**',
            '**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**',
            '**OTHER_SOMATIC_ANIMAL_TISSUE**',
            'ABDOMEN',
            'ANTERIOR_BODY',
            'BLADE',
            'BLOOD',
            'BODYWALL',
            'BRACT',
            'BRAIN',
            'BUD',
            'CAP',
            'CEPHALOTHORAX',
            'EGG',
            'EGGSHELL',
            'ENDOCRINE_TISSUE',
            'EYE',
            'FAT_BODY',
            'FIN',
            'FLOWER',
            'GILL_ANIMAL',
            'GILL_FUNGI',
            'GONAD',
            'HAIR',
            'HEAD',
            'HEART',
            'HEPATOPANCREAS',
            'HOLDFAST_FUNGI',
            'INTESTINE',
            'KIDNEY',
            'LEAF',
            'LEG',
            'LIVER',
            'LUNG',
            'MID_BODY',
            'MODULAR_COLONY',
            'MOLLUSC_FOOT',
            'MULTICELLULAR_ORGANISMS_IN_CULTURE',
            'MUSCLE',
            'MYCELIUM',
            'MYCORRHIZA',
            'OVARY_ANIMAL',
            'OVIDUCT',
            'PANCREAS',
            'PETIOLE',
            'POSTERIOR_BODY',
            'ROOT',
            'SCALES',
            'SCAT',
            'SEED',
            'SEEDLING',
            'SHOOT',
            'SKIN',
            'SPERM_SEMINAL_FLUID',
            'SPLEEN',
            'SPORE',
            'SPORE_BEARING_STRUCTURE',
            'STEM',
            'STIPE',
            'STOMACH',
            'TENTACLE',
            'TERMINAL_BODY',
            'TESTIS',
            'THALLUS_FUNGI',
            'THALLUS_PLANT',
            'THORAX',
            'UNICELLULAR_ORGANISMS_IN_CULTURE',
            'WHOLE_ORGANISM',
            'WHOLE_PLANT',
            'NOT_APPLICABLE',
            'NOT_COLLECTED',
            'NOT_PROVIDED',
        ],
    'PARTNER':
        [
            'DALHOUSIE UNIVERSITY',
            'GEOMAR HELMHOLTZ CENTRE',
            'NOVA SOUTHEASTERN UNIVERSITY',
            'PORTLAND STATE UNIVERSITY',
            'QUEEN MARY UNIVERSITY OF LONDON',
            'SENCKENBERG RESEARCH INSTITUTE',
            'THE SAINSBURY LABORATORY',
            'UNIVERSITY OF BRITISH COLUMBIA',
            'UNIVERSITY OF CALIFORNIA',
            'UNIVERSITY OF DERBY',
            'UNIVERSITY OF ORGEON',
            'UNIVERSITY OF RHODE ISLAND',
            'UNIVERSITY OF VIENNA (CEPHALOPOD)',
            'UNIVERSITY OF VIENNA (MOLLUSC)'
        ],
    'PRIMARY_BIOGENOME_PROJECT': [
        'ERGA-associated'
        'ERGA-BGE',
        'ERGA-Pilot',
    ],
    'PURPOSE_OF_SPECIMEN': {
        'ASG':
            [
                'DNA_BARCODING_ONLY',
                'R&D',
                'REFERENCE_GENOME',
                'RNA_SEQUENCING',
                'SHORT_READ_SEQUENCING'
            ],
        'DTOL':
            [
                'DNA_BARCODING_ONLY',
                'R&D',
                'REFERENCE_GENOME',
                'RNA_SEQUENCING',
                'SHORT_READ_SEQUENCING'
            ],

        'ERGA':
            [
                'DNA_BARCODING_ONLY',
                'R&D',
                'REFERENCE_GENOME',
                'RNA_SEQUENCING',
                'SHORT_READ_SEQUENCING'
            ]
    },
    'REGULATORY_COMPLIANCE':
        [
            'Y',
            'N',
            'NOT_APPLICABLE'
        ],
    'SAMPLE_FORMAT': [
        'DNA',
        'RNA',
        'biological sample/tissue from non-infectious organism',
        'inactivated biological sample from infectious organism'
        'live biological sample from infectious organism'
    ],
    'SAMPLING_PERMITS_REQUIRED':
        [
            'Y',
            'N'
        ],
    'SEQUENCING_CENTRE':
        [
            'EARLHAM INSTITUTE',
            'SANGER INSTITUTE'
        ],
    'SEX':
        [
            'ASEXUAL_MORPH',
            'HERMAPHRODITE_MONOECIOUS',
            'FEMALE',
            'MALE',
            'NOT_APPLICABLE',
            'NOT_COLLECTED',
            'NOT_PROVIDED',
            'SEXUAL_MORPH'
        ],
    'SIZE_OF_TISSUE_IN_TUBE':
        [
            'VS',
            'S',
            'M',
            'L',
            'SINGLE_CELL',
            'NOT_APPLICABLE',
            'NOT_COLLECTED',
            'NOT_PROVIDED'
        ],
    'SORTER_AFFILIATION':
        [
            'EARLHAM INSTITUTE',
            'UNIVERSITY OF OXFORD'
        ],
    'SPECIMEN_IDENTITY_RISK':
        [
            'Y',
            'N'
        ],
    'SYMBIONT':
        [
            'TARGET',
            'SYMBIONT'
        ],
    'TISSUE_FOR_BARCODING':
        [
            '**OTHER_FUNGAL_TISSUE**',
            '**OTHER_PLANT_TISSUE**',
            '**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**',
            '**OTHER_SOMATIC_ANIMAL_TISSUE**',
            'ABDOMEN',
            'ANTERIOR_BODY',
            'BLADE',
            'BLOOD',
            'BODYWALL',
            'BRACT',
            'BRAIN',
            'BUD',
            'CAP',
            'CEPHALOTHORAX',
            'DNA_EXTRACT',
            'EGG',
            'EGGSHELL',
            'ENDOCRINE_TISSUE',
            'EYE',
            'FAT_BODY',
            'FIN',
            'FLOWER',
            'GILL_ANIMAL',
            'GILL_FUNGI',
            'GONAD',
            'HAIR',
            'HEAD',
            'HEART',
            'HEPATOPANCREAS',
            'HOLDFAST_FUNGI',
            'INTESTINE',
            'KIDNEY',
            'LEAF',
            'LEG',
            'LIVER',
            'LUNG',
            'MID_BODY',
            'MODULAR_COLONY',
            'MOLLUSC_FOOT',
            'MULTICELLULAR_ORGANISMS_IN_CULTURE',
            'MUSCLE',
            'MYCELIUM',
            'MYCORRHIZA',
            'NOT_APPLICABLE',
            'NOT_COLLECTED',
            'NOT_PROVIDED',
            'OVARY_ANIMAL',
            'OVIDUCT',
            'PANCREAS',
            'PETIOLE',
            'POSTERIOR_BODY',
            'ROOT',
            'SCALES',
            'SCAT',
            'SEED',
            'SEEDLING',
            'SHOOT',
            'SKIN',
            'SPERM_SEMINAL_FLUID',
            'SPLEEN',
            'SPORE',
            'SPORE_BEARING_STRUCTURE',
            'STEM',
            'STIPE',
            'STOMACH',
            'TENTACLE',
            'TERMINAL_BODY',
            'TESTIS',
            'THALLUS_FUNGI',
            'THALLUS_PLANT',
            'THORAX',
            'UNICELLULAR_ORGANISMS_IN_CULTURE',
            'WHOLE_ORGANISM',
            'WHOLE_PLANT'
        ],
    'TISSUE_FOR_BIOBANKING': [
        '**OTHER_FUNGAL_TISSUE**',
        '**OTHER_PLANT_TISSUE**',
        '**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**',
        '**OTHER_SOMATIC_ANIMAL_TISSUE**',
        'ABDOMEN',
        'ANTERIOR_BODY',
        'BLADE',
        'BLOOD',
        'BODYWALL',
        'BRACT',
        'BRAIN',
        'BUD',
        'CAP',
        'CEPHALOTHORAX',
        'EGG',
        'EGGSHELL',
        'ENDOCRINE_TISSUE',
        'EYE',
        'FAT_BODY',
        'FIN',
        'FLOWER',
        'GILL_ANIMAL',
        'GILL_FUNGI',
        'GONAD',
        'HAIR',
        'HEAD',
        'HEART',
        'HEPATOPANCREAS',
        'HOLDFAST_FUNGI',
        'INTESTINE',
        'KIDNEY',
        'LEAF',
        'LEG',
        'LIVER',
        'LUNG',
        'MID_BODY',
        'MODULAR_COLONY',
        'MOLLUSC_FOOT',
        'MULTICELLULAR_ORGANISMS_IN_CULTURE',
        'MUSCLE',
        'MYCELIUM',
        'MYCORRHIZA',
        'OVARY_ANIMAL',
        'OVIDUCT',
        'PANCREAS',
        'PETIOLE',
        'POSTERIOR_BODY',
        'ROOT',
        'SCALES',
        'SCAT',
        'SEED',
        'SEEDLING',
        'SHOOT',
        'SKIN',
        'SPERM_SEMINAL_FLUID',
        'SPLEEN',
        'SPORE',
        'SPORE_BEARING_STRUCTURE',
        'STEM',
        'STIPE',
        'STOMACH',
        'TENTACLE',
        'TERMINAL_BODY',
        'TESTIS',
        'THALLUS_FUNGI',
        'THALLUS_PLANT',
        'THORAX',
        'UNICELLULAR_ORGANISMS_IN_CULTURE',
        'WHOLE_ORGANISM',
        'WHOLE_PLANT',
        'NOT_APPLICABLE',
        'NOT_COLLECTED',
        'NOT_PROVIDED',
    ],
    'TISSUE_REMOVED_FOR_BARCODING':
        [
            'Y',
            'N'
        ],
    'TISSUE_REMOVED_FOR_BIOBANKING':
        [
            'Y',
            'N'
        ],
    'TO_BE_USED_FOR':
        [
            'BARCODING ONLY',
            'REFERENCE GENOME',
            'RESEQUENCING(POPGEN)',
            'RNAseq'
        ],
    'WATER_BODY_TYPE':
        [
            'COASTAL',
            'ESTUARY',
            'LAKE',
            'OPEN SEA',
            'POND',
            'RIVER',
            'STREAM'
        ],
    'WATER_TYPE':
        [
            'BRACKISH_WATER',
            'FRESH_WATER',
            'SALT_WATER'
        ]
}

DTOL_EXPORT_TO_STS_FIELDS = {
    'asg': [
        'SERIES',
        'RACK_OR_PLATE_ID',
        'TUBE_OR_WELL_ID',
        'SPECIMEN_ID',
        'ORDER_OR_GROUP',
        'FAMILY',
        'GENUS',
        'TAXON_ID',
        'SCIENTIFIC_NAME',
        'TAXON_REMARKS',
        'INFRASPECIFIC_EPITHET',
        'CULTURE_OR_STRAIN_ID',
        'COMMON_NAME',
        'LIFESTAGE',
        'SEX',
        'ORGANISM_PART',
        'SYMBIONT',
        'RELATIONSHIP',
        'PARTNER',
        'PARTNER_SAMPLE_ID',
        'COLLECTOR_SAMPLE_ID',
        'COLLECTED_BY',
        'COLLECTOR_AFFILIATION',
        'DATE_OF_COLLECTION',
        'COLLECTION_LOCATION',
        'DECIMAL_LATITUDE',
        'DECIMAL_LONGITUDE',
        'GRID_REFERENCE',
        'HABITAT',
        'DEPTH',
        'ELEVATION',
        'ORIGINAL_COLLECTION_DATE',
        'ORIGINAL_GEOGRAPHIC_LOCATION',
        'ORIGINAL_DECIMAL_LATITUDE',
        'ORIGINAL_DECIMAL_LONGITUDE',
        'TIME_OF_COLLECTION',
        'DESCRIPTION_OF_COLLECTION_METHOD',
        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
        'IDENTIFIED_BY',
        'IDENTIFIER_AFFILIATION',
        'IDENTIFIED_HOW',
        'SPECIMEN_IDENTITY_RISK',
        'MIXED_SAMPLE_RISK',
        'PRESERVED_BY',
        'PRESERVER_AFFILIATION',
        'PRESERVATION_APPROACH',
        'PRESERVATIVE_SOLUTION',
        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
        'DATE_OF_PRESERVATION',
        'SIZE_OF_TISSUE_IN_TUBE',
        'BARCODE_HUB',
        'TISSUE_REMOVED_FOR_BARCODING',
        'TISSUE_REMOVED_FROM_BARCODING',
        'PLATE_ID_FOR_BARCODING',
        'TUBE_OR_WELL_ID_FOR_BARCODING',
        'TISSUE_FOR_BARCODING',
        'BARCODE_PLATE_PRESERVATIVE',
        'BARCODING_STATUS',
        'PURPOSE_OF_SPECIMEN',
        'SAMPLE_FORMAT',
        'HAZARD_GROUP',
        'REGULATORY_COMPLIANCE',
        'VOUCHER_ID',
        'PROXY_VOUCHER_ID',
        'VOUCHER_LINK',
        'PROXY_VOUCHER_LINK',
        'VOUCHER_INSTITUTION',
        'OTHER_INFORMATION',
        'associated_tol_project',
        'biosampleAccession',
        'boldAccession',
        'copo_profile_title',
        'created_by',
        'manifest_id',
        'public_name',
        'sampleDerivedFrom',
        'sampleSameAs',
        'sampleSymbiontOf',
        'sraAccession',
        'status',
        'submissionAccession',
        'time_created',
        'time_updated',
        'tol_project',
        'updated_by'
    ],
    'dtol': [
        'SERIES',
        'RACK_OR_PLATE_ID',
        'TUBE_OR_WELL_ID',
        'SPECIMEN_ID',
        'ORDER_OR_GROUP',
        'FAMILY',
        'GENUS',
        'TAXON_ID',
        'SCIENTIFIC_NAME',
        'TAXON_REMARKS',
        'INFRASPECIFIC_EPITHET',
        'CULTURE_OR_STRAIN_ID',
        'COMMON_NAME',
        'LIFESTAGE',
        'SEX',
        'ORGANISM_PART',
        'SYMBIONT',
        'RELATIONSHIP',
        'GAL',
        'GAL_SAMPLE_ID',
        'COLLECTOR_SAMPLE_ID',
        'COLLECTED_BY',
        'COLLECTOR_AFFILIATION',
        'DATE_OF_COLLECTION',
        'COLLECTION_LOCATION',
        'DECIMAL_LATITUDE',
        'DECIMAL_LONGITUDE',
        'GRID_REFERENCE',
        'HABITAT',
        'DEPTH',
        'ELEVATION',
        'ORIGINAL_COLLECTION_DATE',
        'ORIGINAL_GEOGRAPHIC_LOCATION',
        'ORIGINAL_DECIMAL_LATITUDE',
        'ORIGINAL_DECIMAL_LONGITUDE',
        'TIME_OF_COLLECTION',
        'DESCRIPTION_OF_COLLECTION_METHOD',
        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
        'IDENTIFIED_BY',
        'IDENTIFIER_AFFILIATION',
        'IDENTIFIED_HOW',
        'SPECIMEN_IDENTITY_RISK',
        'MIXED_SAMPLE_RISK',
        'PRESERVED_BY',
        'PRESERVER_AFFILIATION',
        'PRESERVATION_APPROACH',
        'PRESERVATIVE_SOLUTION',
        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
        'DATE_OF_PRESERVATION',
        'SIZE_OF_TISSUE_IN_TUBE',
        'BARCODE_HUB',
        'TISSUE_REMOVED_FOR_BARCODING',
        'TISSUE_REMOVED_FROM_BARCODING',
        'PLATE_ID_FOR_BARCODING',
        'TUBE_OR_WELL_ID_FOR_BARCODING',
        'TISSUE_FOR_BARCODING',
        'BARCODE_PLATE_PRESERVATIVE',
        'BARCODING_STATUS',
        'PURPOSE_OF_SPECIMEN',
        'SAMPLE_FORMAT',
        'HAZARD_GROUP',
        'REGULATORY_COMPLIANCE',
        'VOUCHER_ID',
        'PROXY_VOUCHER_ID',
        'VOUCHER_LINK',
        'PROXY_VOUCHER_LINK',
        'VOUCHER_INSTITUTION',
        'OTHER_INFORMATION',
        'associated_tol_project',
        'biosampleAccession',
        'boldAccession',
        'copo_profile_title',
        'created_by',
        'manifest_id',
        'public_name',
        'sampleDerivedFrom',
        'sampleSameAs',
        'sampleSymbiontOf',
        'sraAccession',
        'status',
        'submissionAccession',
        'time_created',
        'time_updated',
        'tol_project',
        'updated_by'
    ],
    'env': [],
    'erga': [
        'TUBE_OR_WELL_ID',
        'SPECIMEN_ID',
        'PURPOSE_OF_SPECIMEN',
        'SAMPLE_COORDINATOR',
        'SAMPLE_COORDINATOR_AFFILIATION',
        'SAMPLE_COORDINATOR_ORCID_ID',
        'ORDER_OR_GROUP',
        'FAMILY',
        'GENUS',
        'TAXON_ID',
        'SCIENTIFIC_NAME',
        'TAXON_REMARKS',
        'INFRASPECIFIC_EPITHET',
        'CULTURE_OR_STRAIN_ID',
        'COMMON_NAME',
        'LIFESTAGE',
        'SEX',
        'ORGANISM_PART',
        'SYMBIONT',
        'RELATIONSHIP',
        'GAL',
        'GAL_SAMPLE_ID',
        'COLLECTOR_SAMPLE_ID',
        'COLLECTED_BY',
        'COLLECTOR_AFFILIATION',
        'COLLECTOR_ORCID_ID',
        'DATE_OF_COLLECTION',
        'TIME_OF_COLLECTION',
        'COLLECTION_LOCATION',
        'DECIMAL_LATITUDE',
        'DECIMAL_LONGITUDE',
        'LATITUDE_START',
        'LONGITUDE_START',
        'LATITUDE_END',
        'LONGITUDE_END',
        'HABITAT',
        'DEPTH',
        'ELEVATION',
        'ORIGINAL_COLLECTION_DATE',
        'ORIGINAL_GEOGRAPHIC_LOCATION',
        'DESCRIPTION_OF_COLLECTION_METHOD',
        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
        'IDENTIFIED_BY',
        'IDENTIFIER_AFFILIATION',
        'IDENTIFIED_HOW',
        'SPECIMEN_IDENTITY_RISK',
        'PRESERVED_BY',
        'PRESERVER_AFFILIATION',
        'PRESERVATION_APPROACH',
        'PRESERVATIVE_SOLUTION',
        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
        'DATE_OF_PRESERVATION',
        'SIZE_OF_TISSUE_IN_TUBE',
        'TISSUE_REMOVED_FOR_BARCODING',
        'TUBE_OR_WELL_ID_FOR_BARCODING',
        'TISSUE_FOR_BARCODING',
        'BARCODE_PLATE_PRESERVATIVE',
        'TISSUE_REMOVED_FOR_BIOBANKING',
        'TISSUE_VOUCHER_ID_FOR_BIOBANKING',
        'TISSUE_FOR_BIOBANKING',
        'DNA_REMOVED_FOR_BIOBANKING',
        'DNA_VOUCHER_ID_FOR_BIOBANKING',
        'VOUCHER_ID',
        'PROXY_VOUCHER_ID',
        'VOUCHER_LINK',
        'PROXY_VOUCHER_LINK',
        'VOUCHER_INSTITUTION',
        'REGULATORY_COMPLIANCE',
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_APPLICABLE',
        'INDIGENOUS_RIGHTS_DEF',
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_CONTACT',
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_LABEL',
        'ETHICS_PERMITS_MANDATORY',
        'ETHICS_PERMITS_DEF',
        'ETHICS_PERMITS_FILENAME',
        'SAMPLING_PERMITS_MANDATORY',
        'SAMPLING_PERMITS_DEF',
        'SAMPLING_PERMITS_FILENAME'
        'NAGOYA_PERMITS_MANDATORY',
        'NAGOYA_PERMITS_DEF',
        'NAGOYA_PERMITS_FILENAME',
        'HAZARD_GROUP',
        'OTHER_INFORMATION',
        'BARCODE_HUB',
        'INDIGENOUS_RIGHTS_APPLICABLE',
        'PLATE_ID_FOR_BARCODING',
        'RACK_OR_PLATE_ID',
        'SERIES',
        'TISSUE_REMOVED_FROM_BARCODING',
        'BIOBANKED_TISSUE_PRESERVATIVE',
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID',
        'NAGOYA_PERMITS_REQUIRED',
        'PROXY_TISSUE_VOUCHER_ID_FOR_BIOBANKING',
        'BARCODING_STATUS',
        'ORIGINAL_DECIMAL_LONGITUDE',
        'PRIMARY_BIOGENOME_PROJECT',
        'SAMPLING_PERMITS_REQUIRED',
        'ETHICS_PERMITS_REQUIRED',
        'ORIGINAL_DECIMAL_LATITUDE',
        'MIXED_SAMPLE_RISK',
        'ASSOCIATED_PROJECT_ACCESSIONS',
        'associated_tol_project',
        'biosampleAccession',
        'boldAccession',
        'copo_profile_title',
        'created_by',
        'manifest_id',
        'public_name',
        'sampleDerivedFrom',
        'sampleSameAs',
        'sampleSymbiontOf',
        'sraAccession',
        'status',
        'submissionAccession',
        'time_created',
        'time_updated',
        'tol_project',
        'updated_by'
    ]}

# allow updates to fields in the list by hand of the user pre-approval
DTOL_NO_COMPLIANCE_FIELDS = {
    "asg": [
        'BARCODE_HUB',
        'BARCODE_PLATE_PRESERVATIVE',
        'COLLECTOR_SAMPLE_ID',
        'CULTURE_OR_STRAIN_ID',
        'DATE_OF_PRESERVATION',
        'DEPTH',
        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
        'ELEVATION',
        'HAZARD_GROUP',
        'IDENTIFIED_BY',
        'IDENTIFIED_HOW',
        'IDENTIFIER_AFFILIATION',
        'INFRASPECIFIC_EPITHET',
        'LIFESTAGE',
        'PARTNER_SAMPLE_ID',
        'PLATE_ID_FOR_BARCODING',
        'PRESERVED_BY',
        'PRESERVER_AFFILIATION',
        'PURPOSE_OF_SPECIMEN',
        'RELATIONSHIP',
        'SEX',
        'SIZE_OF_TISSUE_IN_TUBE',
        'SPECIMEN_ID_RISK',
        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
        'TIME_OF_COLLECTION',
        'TISSUE_FOR_BARCODING',
        'TISSUE_REMOVED_FOR_BARCODING',
        'TUBE_OR_WELL_ID_FOR_BARCODING',
        'VOUCHER_ID'
    ],
    "dtol": [
        'BARCODE_HUB',
        'BARCODE_PLATE_PRESERVATIVE',
        'COLLECTOR_SAMPLE_ID',
        'CULTURE_OR_STRAIN_ID',
        'DATE_OF_PRESERVATION',
        'DEPTH',
        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
        'ELEVATION',
        'GAL_SAMPLE_ID',
        'HAZARD_GROUP',
        'IDENTIFIED_BY',
        'IDENTIFIED_HOW',
        'IDENTIFIER_AFFILIATION',
        'INFRASPECIFIC_EPITHET',
        'LIFESTAGE',
        'PLATE_ID_FOR_BARCODING',
        'PRESERVED_BY',
        'PRESERVER_AFFILIATION',
        'PURPOSE_OF_SPECIMEN',
        'RELATIONSHIP',
        'SEX',
        'SIZE_OF_TISSUE_IN_TUBE',
        'SPECIMEN_IDENTITY_RISK',
        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
        'TIME_OF_COLLECTION',
        'TISSUE_FOR_BARCODING',
        'TISSUE_REMOVED_FOR_BARCODING',
        'TUBE_OR_WELL_ID_FOR_BARCODING',
        'VOUCHER_ID'
    ],
    "erga": [
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_CONTACT',
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID',
        'ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_RIGHTS_APPLICABLE',
        'BARCODE_HUB',
        'BARCODE_PLATE_PRESERVATIVE',
        'COLLECTED_BY',
        'COLLECTION_LOCATION',
        'COLLECTOR_AFFILIATION',
        'COLLECTOR_SAMPLE_ID',
        'COMMON_NAME',
        'CULTURE_OR_STRAIN_ID',
        'DATE_OF_COLLECTION',
        'DATE_OF_PRESERVATION',
        'DECIMAL_LATITUDE',
        'DECIMAL_LONGITUDE',
        'DEPTH',
        'DESCRIPTION_OF_COLLECTION_METHOD',
        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
        'DNA_REMOVED_FOR_BIOBANKING',
        'DNA_VOUCHER_FOR_BIOBANKING',
        'ELEVATION',
        'ETHICS_PERMITS_DEF',
        'ETHICS_PERMITS_FILENAME',
        'ETHICS_PERMITS_REQUIRED',
        'FAMILY',
        'GAL',
        'GAL_SAMPLE_ID',
        'GENUS',
        'GRID_REFERENCE',
        'HABITAT',
        'HAZARD_GROUP',
        'IDENTIFIED_BY',
        'IDENTIFIED_HOW',
        'IDENTIFIER_AFFILIATION',
        'IDENTIFIER_AFFILIATION',
        'INDIGENOUS_RIGHTS_APPLICABLE',
        'INDIGENOUS_RIGHTS_DEF',
        'INDIGENOUS_RIGHTS_DEF',
        'INFRASPECIFIC_EPITHET',
        'LIFESTAGE',
        'NAGOYA_PERMITS_DEF',
        'NAGOYA_PERMITS_FILENAME',
        'NAGOYA_PERMITS_REQUIRED',
        'ORDER_OR_GROUP',
        'ORGANISM_PART',
        'ORIGINAL_COLLECTION_DATE',
        'ORIGINAL_GEOGRAPHIC_LOCATION',
        'OTHER_INFORMATION',
        'PRESERVATION_APPROACH',
        'PRESERVATIVE_SOLUTION',
        'PRESERVED_BY',
        'PRESERVER_AFFILIATION',
        'PURPOSE_OF_SPECIMEN',
        'REGULATORY_COMPLIANCE',
        'RELATIONSHIP',
        'SAMPLE_COORDINATOR',
        'SAMPLE_COORDINATOR_AFFILIATION',
        'SAMPLE_COORDINATOR_ORCID_ID',
        'SAMPLING_PERMITS_FILENAME',
        'SAMPLING_PERMITS_REQUIRED',
        'SCIENTIFIC_NAME',
        'SEX',
        'SIZE_OF_TISSUE_IN_TUBE',
        'SPECIMEN_IDENTITY_RISK',
        'TAXON_ID',
        'TAXON_REMARKS',
        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
        'TIME_OF_COLLECTION',
        'TISSUE_FOR_BARCODING',
        'TISSUE_FOR_BIOBANKING',
        'TISSUE_REMOVED_FOR_BARCODING',
        'TISSUE_REMOVED_FOR_BIOBANKING',
        'TISSUE_REMOVED_FROM_BARCODING',
        'TISSUE_VOUCHER_ID_FOR_BIOBANKING',
        'TUBE_OR_WELL_ID_FOR_BARCODING',
        'VOUCHER_ID'
    ]
}

DTOL_RULES = {
    'ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID':
        {
            "strict_regex": "^[a-z0-9]{8}-([a-z0-9]{4}-){3}[a-z0-9]{12}$",
            "human_readable": "[ID provided by the local context hub]"
        },
    'CHLOROPHYL_A':
        {
            "strict_regex": "^\d+$",
            "human_readable": "integer"
        },
    'COLLECTOR_ORCID_ID':
        {
            "strict_regex": "^((\d{4}-){3}\d{3}(\d|X))(\|(\d{4}-){3}\d{3}(\d|X))*|(^not provided$)|(^not applicable$)",
            "human_readable": "16-digit number that is compatible with the ISO Standard (ISO 27729),  if multiple IDs separate with a | and no spaces"
        },
    'DATE_OF_COLLECTION':
        {
            "ena_regex": "(^[12][0-9]{3}(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01])(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?"
                         "([+-][0-9]{1,2})?)?)?)?(/[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?"
                         "([+-][0-9]{1,2})?)?)?)?)?$)|(^not collected$)|(^not provided$)|(^restricted access$) ",
            "human_readable": "YYYY-MM-DD, YYYY-MM, YYYY, NOT_COLLECTED or NOT_PROVIDED"
        },
    'DECIMAL_LATITUDE':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$)",
            "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"
        },
    'DECIMAL_LATITUDE_ERGA':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)",
            "human_readable": "numeric, or NOT_COLLECTED"

        },
    'DECIMAL_LONGITUDE':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$)",
            "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"

        },
    'DECIMAL_LONGITUDE_ERGA':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)",
            "human_readable": "numeric, or NOT_COLLECTED"

        },
    'DEPTH':
        {
            "ena_regex": "(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?",
            "human_readable": "numeric, or empty string"
        },
    'DISSOLVED_OXYGEN':
        {
            "strict_regex": "^\d+$",
            "human_readable": "integer"
        },
    'ELEVATION':
        {
            "ena_regex": "[+-]?(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?",
            "human_readable": "numeric, or empty string"
        },
    'ETHICS_PERMITS_FILENAME':
        {
            "optional_regex": "^.+\.pdf$",
            "human_readable": "filename (including '.pdf' extension) if permit is required or NOT_APPLICABLE if permit is not required"
        },
    'LATITUDE_END':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$)",
            "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"
        },
    'LATITUDE_END_ERGA':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)",
            "human_readable": "numeric, or NOT_COLLECTED"

        },
    'LATITUDE_START':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$)",
            "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"

        },
    'LATITUDE_START_ERGA':
        {

            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)",
            "human_readable": "numeric, or NOT_COLLECTED"

        },
    'LONGITUDE_END':
        {

            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$)",
            "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"

        },
    'LONGITUDE_END_ERGA':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)",
            "human_readable": "numeric, or NOT_COLLECTED"

        },
    'LONGITUDE_START':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$)",
            "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"
        },
    'LONGITUDE_START_ERGA':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)",
            "human_readable": "numeric, or NOT_COLLECTED"

        },
    'NAGOYA_PERMITS_FILENAME':
        {
            "optional_regex": "^.+\.pdf$",
            "human_readable": "filename (including '.pdf' extension) if permit is required or NOT_APPLICABLE if permit is not required"
        },
    'ORIGINAL_COLLECTION_DATE':
        {
            "ena_regex": "^[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?(/[0-9]{"
                         "4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?)?$",
            "human_readable": "Date as YYYY, YYYY-MM or YYYY-MM-DD"
        },
    'ORIGINAL_DECIMAL_LATITUDE':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]{0,8}$)",
            "human_readable": "numeric with 8 decimal places"
        },
    'ORIGINAL_DECIMAL_LONGITUDE':
        {
            "ena_regex": "(^[+-]?[0-9]+.?[0-9]{0,8}$)",
            "human_readable": "numeric with 8 decimal places"
        },
    'RACK_OR_PLATE_ID':
        {
            "optional_regex": "^[a-zA-Z]{2}\d{8}$"
        },
    'SALINITY':
        {
            "strict_regex": "^\d+$",
            "human_readable": "integer"
        },
    'SAMPLE_COORDINATOR_ORCID_ID':
        {
            "strict_regex": "^((\d{4}-){3}\d{3}(\d|X))(\|(\d{4}-){3}\d{3}(\d|X))*$",
            "human_readable": "16-digit number that is compatible with the ISO Standard (ISO 27729), if multiple IDs separate with a | and no spaces"
        },
    'SAMPLE_DERIVED_FROM':
        {
            "ena_regex": "(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{"
                         "11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END]["
                         "AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)",
            "human_readable": "Specimen accession"
        },
    'SAMPLE_SAME_AS':
        {
            "ena_regex": "(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{"
                         "11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END]["
                         "AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)",
            "human_readable": "Specimen accession"
        },
    'SAMPLE_SYMBIONT_OF':
        {
            "ena_regex": "(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{"
                         "11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END]["
                         "AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)",
            "human_readable": "Specimen accession"
        },
    'SAMPLING_PERMITS_FILENAME':
        {
            "optional_regex": "^.+\.pdf$",
            "human_readable": "filename (including '.pdf' extension) if permit is required or NOT_APPLICABLE if permit is not required"
        },
    'SAMPLING_WATER_BODY_DEPTH':
        {
            "strict_regex": "^\d+$",
            "human_readable": "integer"
        },
    'TEMPERATURE':
        {
            "strict_regex": "^\d+$",
            "human_readable": "integer"
        },
    'TIME_OF_COLLECTION':
        {
            "strict_regex": "^([0-1][0-9]|2[0-4]):[0-5]\d$",
            "human_readable": "24-hour format with hours and minutes separated by colon"
        },
    'TUBE_OR_WELL_ID':
        {
            "optional_regex": "^[a-zA-Z]{2}\d{8}$"
        },
    'WATER_SPEED':
        {
            "strict_regex": "^\d+$",
            "human_readable": "integer"
        }
}

DTOL_UNITS = {
    'DECIMAL_LATITUDE': {'ena_unit': 'DD'},
    'DECIMAL_LONGITUDE': {'ena_unit': 'DD'},
    'DEPTH': {'ena_unit': 'm'},
    'ELEVATION': {'ena_unit': 'm'},
    'LATITUDE_END': {'ena_unit': 'DD'},
    'LATITUDE_START': {'ena_unit': 'DD'},
    'LONGITUDE_END': {'ena_unit': 'DD'},
    'LONGITUDE_START': {'ena_unit': 'DD'},
    'ORIGINAL_DECIMAL_LATITUDE': {'ena_unit': 'DD'},
    'ORIGINAL_DECIMAL_LONGITUDE': {'ena_unit': 'DD'}
}

GAL_MAP_LOCATION_COORDINATES = {
    "CENTRO NACIONAL DE ANÁLISIS GENÓMICO": {"latitude": 41.29322842500072, "longitude": 2.112447951213345},
    "DNA SEQUENCING AND GENOMICS LABORATORY": {"latitude": 52.604080415603875, "longitude": 1.322325116120334},
    "HELSINKI GENOMICS CORE FACILITY": {"latitude": 60.17217434637327, "longitude": 24.76174956537578},
    "DRESDEN-CONCEPT": {"latitude": 50.953555072066706, "longitude": 13.765873443664715},
    "EARLHAM INSTITUTE": {"latitude": 52.62318280716785, "longitude": 1.2555952213587074},
    "FUNCTIONAL GENOMIC CENTER ZURICH": {"latitude": 47.29317744028429, "longitude": 8.630075015560141},
    "GENOSCOPE": {"latitude": 48.57242945075802, "longitude": 2.440779473998219},
    "GIGA-GENOMICS CORE FACILITY UNIVERSITY OF LIEGE": {"latitude": 50.49505310219335,
                                                        "longitude": 5.469583675188101},
    "HANSEN LAB, DENMARK": {"latitude": 55.85342233870096, "longitude": 12.580689191025195},
    "INDUSTRY PARTNER": {"latitude": 53.415313884089315, "longitude": 14.621839848348806},
    "LAUSANNE GENOMIC TECHNOLOGIES FACILITY": {"latitude": 46.43785938836717, "longitude": 6.720611497418699},
    "LEIBNIZ INSTITUTE FOR THE ANALYSIS OF BIODIVERSITY CHANGE, MUSEUM KOENIG, BONN": {"latitude": 50.662300290436946,
                                                                                       "longitude": 7.1815164845562895},
    "MARINE BIOLOGICAL ASSOCIATION": {"latitude": 50.24306793085285, "longitude": -4.077733915519119},
    "NGS BERN": {"latitude": 46.79965448973021, "longitude": 7.576577902102794},
    "NGS COMPETENCE CENTER TÜBINGEN": {"latitude": 48.48522057082666, "longitude": 9.090980002697727},
    "NATURAL HISTORY MUSEUM": {"latitude": 51.4486310061879, "longitude": -0.06127617046297753},
    "NEUROMICS SUPPORT FACILITY, UANTWERP, VIB": {"latitude": 51.11917170838246, "longitude": 4.416086561730746},
    "NORWEGIAN SEQUENCING CENTRE": {"latitude": 63.43527653315388, "longitude": 10.605382103292664},
    "ROYAL BOTANIC GARDEN EDINBURGH": {"latitude": 55.96501818957333, "longitude": -3.209092180629166},
    "ROYAL BOTANIC GARDENS KEW": {"latitude": 51.478500987462645, "longitude": -0.2952321886064486},
    "SANGER INSTITUTE": {"latitude": 52.078851760344094, "longitude": 0.1833635227184019},
    "SCILIFELAB": {"latitude": 59.35025588644969, "longitude": 18.02342940480995},
    "SVARDAL LAB, ANTWERP": {"latitude": 51.204388155984645, "longitude": 4.383337520422855},
    "UNIVERSITY OF BARI": {"latitude": 41.09506928572348, "longitude": 16.88037847340563},
    "UNIVERSITY OF FLORENCE": {"latitude": 43.7443574368754, "longitude": 11.222120017904818},
    "UNIVERSITY OF OXFORD": {"latitude": 51.75111553102938, "longitude": -1.242828944684545},
    "WEST GERMAN GENOME CENTRE": {"latitude": 51.51577076977291, "longitude": -0.058774328461889375},
}

PARTNER_MAP_LOCATION_COORDINATES = {
    "DALHOUSIE UNIVERSITY": {"latitude": 44.6356351, "longitude": -63.5977486},
    "GEOMAR HELMHOLTZ CENTRE": {"latitude": 54.31473535017579, "longitude": 10.202507477880662},
    "NOVA SOUTHEASTERN UNIVERSITY": {"latitude": 25.9036859889384, "longitude": -80.08505409832087},
    "PORTLAND STATE UNIVERSITY": {"latitude": 45.06625034918671, "longitude": -122.26178879087954},
    "QUEEN MARY UNIVERSITY OF LONDON": {"latitude": 51.52408461103592, "longitude": -0.040097483705069534},
    "SENCKENBERG RESEARCH INSTITUTE": {"latitude": 50.980247934669954, "longitude": 11.319421517872232},
    "THE SAINSBURY LABORATORY": {"latitude": 52.62229597053812, "longitude": 1.2228178153758562},
    "UNIVERSITY OF BRITISH COLUMBIA": {"latitude": 49.10593106507127, "longitude": -123.55137019649796},
    "UNIVERSITY OF RHODE ISLAND": {"latitude": 41.30562478960331, "longitude": -71.55357021967731},
    "UNIVERSITY OF CALIFORNIA": {"latitude": 32.59728946736694, "longitude": -117.16274620316563},
    "UNIVERSITY OF DERBY": {"latitude": 52.937887605383885, "longitude": -1.4956414943590064},
    "UNIVERSITY OF ORGEON": {"latitude": 44.19293642050486, "longitude": -122.7208166347002},
    "UNIVERSITY OF VIENNA (CEPHALOPOD)": {"latitude": 48.213401869226296, "longitude": 16.364048156381596},
    "UNIVERSITY OF VIENNA (MOLLUSC)": {"latitude": 48.21189890585992, "longitude": 16.364341481491362},
}

# Default values for columns that are mandatory in ERGA manifests but are
# optional for 'POP_GENOMICS' associated tol project type for ERGA manifests
POP_GENOMICS_OPTIONAL_COLUMNS_DEFAULT_VALUES_MAPPING = {
    'BARCODE_PLATE_PRESERVATIVE': 'NOT_APPLICABLE',
    'BARCODING_STATUS': 'DNA_BARCODING_TO_BE_PERFORMED_GAL',
    'BIOBANKED_TISSUE_PRESERVATIVE': 'NOT_APPLICABLE',
    'COLLECTOR_ORCID_ID': 'NOT_PROVIDED',
    'DATE_OF_PRESERVATION': 'NOT_COLLECTED',
    'DESCRIPTION_OF_COLLECTION_METHOD': 'NOT_COLLECTED',
    'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': 'NOT_COLLECTED',
    'DNA_REMOVED_FOR_BIOBANKING': 'N',
    'DNA_VOUCHER_ID_FOR_BIOBANKING': 'NOT_APPLICABLE',
    'GAL': 'INDUSTRY PARTNER',
    'GAL_SAMPLE_ID': '',  # Default value is value of 'COLLECTOR_SAMPLE_ID' column
    'IDENTIFIED_BY': 'NOT_COLLECTED',
    'IDENTIFIED_HOW': 'NOT_COLLECTED',
    'IDENTIFIER_AFFILIATION': 'NOT_COLLECTED',
    'LATITUDE_START': 'NOT_COLLECTED',
    'LATITUDE_END': 'NOT_COLLECTED',
    'LONGITUDE_START': 'NOT_COLLECTED',
    'LONGITUDE_END': 'NOT_COLLECTED',
    'LIFESTAGE': 'NOT_COLLECTED',
    'PRESERVATION_APPROACH': 'NOT_COLLECTED',
    'PRESERVED_BY': 'NOT_COLLECTED',
    'PRESERVER_AFFILIATION': 'NOT_COLLECTED',
    'SIZE_OF_TISSUE_IN_TUBE': 'NOT_COLLECTED',
    'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': 'NOT_COLLECTED',
    'TISSUE_FOR_BARCODING': 'NOT_APPLICABLE',
    'TISSUE_FOR_BIOBANKING': 'NOT_APPLICABLE',
    'TISSUE_REMOVED_FOR_BARCODING': 'N',
    'TISSUE_REMOVED_FOR_BIOBANKING': 'N',
    'TISSUE_VOUCHER_ID_FOR_BIOBANKING': 'NOT_APPLICABLE',
    'TUBE_OR_WELL_ID_FOR_BARCODING': 'NOT_APPLICABLE',
    'VOUCHER_ID': 'NOT_PROVIDED'
}

SPECIMEN_PREFIX = {
    'GAL': {
        'dtol': {
            'EARLHAM INSTITUTE': 'EI_',
            'MARINE BIOLOGICAL ASSOCIATION': 'MBA',
            'NATURAL HISTORY MUSEUM': 'NHMUK',
            'ROYAL BOTANIC GARDEN EDINBURGH': 'EDTOL',
            'ROYAL BOTANIC GARDENS KEW': 'KDTOL',
            'SANGER INSTITUTE': 'SAN',
            'UNIVERSITY OF OXFORD': 'Ox'
        },
        'erga': {
            'default': 'ERGA_'
        },
        'dtol_env': {
            'EARLHAM INSTITUTE': 'EI_',
            'MARINE BIOLOGICAL ASSOCIATION': 'MBA',
            'NATURAL HISTORY MUSEUM': 'NHMUK',
            'ROYAL BOTANIC GARDEN EDINBURGH': 'EDTOL',
            'ROYAL BOTANIC GARDENS KEW': 'KDTOL',
            'SANGER INSTITUTE': 'SAN',
            'UNIVERSITY OF OXFORD': 'Ox'
        }
    },
    'PARTNER': {
        'DALHOUSIE UNIVERSITY': 'DU',
        'GEOMAR HELMHOLTZ CENTRE': 'GHC',
        'NOVA SOUTHEASTERN UNIVERSITY': 'NSU',
        'PORTLAND STATE UNIVERSITY': 'PORT',
        'QUEEN MARY UNIVERSITY OF LONDON': 'QMOUL',
        'SENCKENBERG RESEARCH INSTITUTE': 'SENCK',
        'THE SAINSBURY LABORATORY': 'SL',
        'UNIVERSITY OF BRITISH COLUMBIA': 'UOBC',
        'UNIVERSITY OF CALIFORNIA': 'UCALI',
        'UNIVERSITY OF DERBY': 'UDUK',
        'UNIVERSITY OF OREGON': 'UOREG',
        'UNIVERSITY OF RHODE ISLAND': 'URI',
        'UNIVERSITY OF VIENNA (CEPHALOPOD)': 'VIEC',
        'UNIVERSITY OF VIENNA (MOLLUSC)': 'VIEM'
    }
}

SPECIMEN_SUFFIX = {
    "GAL": {
        "dtol": {
            'EARLHAM INSTITUTE': '\d{5}',
            'MARINE BIOLOGICAL ASSOCIATION': '-\d{6}-\d{3}[A-Z]',
            'NATURAL HISTORY MUSEUM': '\d{9}',
            'ROYAL BOTANIC GARDEN EDINBURGH': '\d{5}',
            'ROYAL BOTANIC GARDENS KEW': '\d{5}',
            'SANGER INSTITUTE': '\d{7}',
            'UNIVERSITY OF OXFORD': '\d{6}'
        },
        "dtol_env": {
            'EARLHAM INSTITUTE': '\d{5}',
            'MARINE BIOLOGICAL ASSOCIATION': '-\d{5}-\d{3}[A-Z]',
            'NATURAL HISTORY MUSEUM': '\d{9}',
            'ROYAL BOTANIC GARDEN EDINBURGH': '\d{5}',
            'ROYAL BOTANIC GARDENS KEW': '\d{5}',
            'SANGER INSTITUTE': '\d{7}',
            'UNIVERSITY OF OXFORD': '\d{6}'
        },
        "erga": {
            "default": "([A-Z]{1,10}_\d{3}(\d|X)_\d{2,3})"
        }
    }
}

##################

API_KEY = resolve_env.get_env("PUBLIC_NAME_SERVICE_API_KEY")

BLANK_VALS = ['NOT_APPLICABLE', 'NOT_COLLECTED', 'NOT_PROVIDED']

DATE_FIELDS = ["DATE_OF_PRESERVATION"]

PERMIT_FILENAME_COLUMN_NAMES = ["SAMPLING_PERMITS_FILENAME", "ETHICS_PERMITS_FILENAME",
                                "NAGOYA_PERMITS_FILENAME"]

PERMIT_REQUIRED_COLUMN_NAMES = ["SAMPLING_PERMITS_REQUIRED", "ETHICS_PERMITS_REQUIRED",
                                "NAGOYA_PERMITS_REQUIRED"]

PERMIT_COLUMN_NAMES_PREFIX = ["SAMPLING_PERMITS", "ETHICS_PERMITS", "NAGOYA_PERMITS"]

NA_VALS = ['#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NULL',
           'NaN', 'n/a', 'nan', 'NaT']

NIH_API_KEY = resolve_env.get_env("NIH_API_KEY")

REQUIRED_MEMBER_GROUPS = ['dtol_users', 'dtol_sample_managers', 'dtolenv_users', 'dtolenv_sample_managers',
                          'erga_users', 'erga_sample_managers']

SANGER_TOL_PROFILE_TYPES = ["asg", "dtol", "dtol_env", "erga"]

SPECIES_LIST_FIELDS = ["SYMBIONT", "TAXON_ID", "ORDER_OR_GROUP", "FAMILY", "GENUS", "SCIENTIFIC_NAME",
                       "INFRASPECIFIC_EPITHET", "CULTURE_OR_STRAIN", "COMMON_NAME", "TAXON_REMARKS"]

STANDALONE_ACCESSION_TYPES = ["project", "sample", "assembly", "seq_annotation", "experiment", "run"]

SYMBIONT_FIELDS = ["ORDER_OR_GROUP", "FAMILY", "GENUS", "TAXON_ID", "SCIENTIFIC_NAME", "TAXON_REMARKS",
                   "INFRASPECIFIC_EPITHET", "CULTURE_OR_STRAIN_ID", "COMMON_NAME", "LIFESTAGE", "SEX", "SYMBIONT",
                   "species_list", "characteristics", "profile_id", "manifest_id", "sample_type", "biosampleAccession",
                   "sraAccession", "submissionAccession", "status", "tol_project", "manifest_version", "public_name",
                   "factorValues"]

SYMBIONT_VALS = ["TARGET", "SYMBIONT"]

TOL_PROFILE_TYPES = ["asg", "dtol", "dtol_env", "erga"]

# FS - 18/8/2020
# this module contains lookups and mappings pertaining to DTOL functionality
# such as validation enumerations and mappings between different field names
from tools import resolve_env
# from django.conf.global_settings import DEBUG
from web.settings.all import DEBUG

DTOL_EXPORT_TO_STS_FIELDS = {
    "dtol": [
        "SERIES",
        "RACK_OR_PLATE_ID",
        "TUBE_OR_WELL_ID",
        "SPECIMEN_ID",
        "TAXON_ID",
        "ORDER_OR_GROUP",
        "FAMILY",
        "GENUS",
        "SCIENTIFIC_NAME",
        "INFRASPECIFIC_EPITHET",
        "CULTURE_OR_STRAIN_ID",
        "COMMON_NAME",
        "TAXON_REMARKS",
        "LIFESTAGE",
        "SEX",
        "ORGANISM_PART",
        "GAL",
        "GAL_SAMPLE_ID",
        "COLLECTOR_SAMPLE_ID",
        "COLLECTED_BY",
        "COLLECTOR_AFFILIATION",
        "DATE_OF_COLLECTION",
        "COLLECTION_LOCATION",
        "DECIMAL_LATITUDE",
        "DECIMAL_LONGITUDE",
        "HABITAT",
        "DESCRIPTION_OF_COLLECTION_METHOD",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION",
        "IDENTIFIED_HOW",
        "SPECIMEN_IDENTITY_RISK",
        "MIXED_SAMPLE_RISK",
        "PRESERVED_BY",
        "PRESERVER_AFFILIATION",
        "PRESERVATION_APPROACH",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUES_IN_TUBE",
        "TISSUE_REMOVED_FROM_BARCODING",
        "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP",
        "REGULATORY_COMPLIANCE",
        "VOUCHER_ID",
        "RELATIONSHIP",
        "GRID_REFERENCE",
        "DEPTH",
        "ELEVATION",
        "TIME_OF_COLLECTION",
        "IDENTIFIER_AFFILIATION",
        "PRESERVATIVE_SOLUTION",
        "SIZE_OF_TISSUE_IN_TUBE",
        "TISSUE_REMOVED_FOR_BARCODING",
        "OTHER_INFORMATION",
        "SYMBIONT",
        "BARCODE_HUB",
        "ORIGINAL_GEOGRAPHIC_LOCATION",
        "ORIGINAL_COLLECTION_DATE",
        "ORIGINAL_DECIMAL_LATITUDE",
        "ORIGINAL_DECIMAL_LONGITUDE",
        "SAMPLE_FORMAT",
        "BARCODING_STATUS",
        "boldAccession",
        "public_name",
        "biosampleAccession",
        "created_by",
        "time_created",
        "submissionAccession",
        "sraAccession",
        "manifest_id",
        "time_updated",
        "updated_by",
        "status",
        "sampleDerivedFrom",
        "sampleSameAs",
        "sampleSymbiontOf",
        "copo_profile_title",
        "tol_project"

    ],
    "erga": [
        "SERIES",
        "RACK_OR_PLATE_ID",
        "TUBE_OR_WELL_ID",
        "SPECIMEN_ID",
        "TAXON_ID",
        "ORDER_OR_GROUP",
        "FAMILY",
        "GENUS",
        "SCIENTIFIC_NAME",
        "INFRASPECIFIC_EPITHET",
        "CULTURE_OR_STRAIN_ID",
        "COMMON_NAME",
        "TAXON_REMARKS",
        "LIFESTAGE",
        "SEX",
        "ORGANISM_PART",
        "GAL",
        "GAL_SAMPLE_ID",
        "COLLECTOR_SAMPLE_ID",
        "COLLECTED_BY",
        "COLLECTOR_AFFILIATION",
        "DATE_OF_COLLECTION",
        "COLLECTION_LOCATION",
        "DECIMAL_LATITUDE",
        "DECIMAL_LONGITUDE",
        "HABITAT",
        "DESCRIPTION_OF_COLLECTION_METHOD",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION",
        "IDENTIFIED_HOW",
        "SPECIMEN_IDENTITY_RISK",
        "PRESERVED_BY",
        "PRESERVER_AFFILIATION",
        "PRESERVATION_APPROACH",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUES_IN_TUBE",
        "TISSUE_REMOVED_FROM_BARCODING",
        "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP",
        "REGULATORY_COMPLIANCE",
        "VOUCHER_ID",
        "RELATIONSHIP",
        "GRID_REFERENCE",
        "DEPTH",
        "ELEVATION",
        "TIME_OF_COLLECTION",
        "IDENTIFIER_AFFILIATION",
        "PRESERVATIVE_SOLUTION",
        "SIZE_OF_TISSUE_IN_TUBE",
        "TISSUE_REMOVED_FOR_BARCODING",
        "OTHER_INFORMATION",
        "SYMBIONT",
        "BARCODE_HUB",
        "ORIGINAL_GEOGRAPHIC_LOCATION",
        "ORIGINAL_COLLECTION_DATE",
        "SAMPLE_COORDINATOR",
        "SAMPLE_COORDINATOR_AFFILIATION",
        "SAMPLE_COORDINATOR_ORCID_ID",
        "INDIGENOUS_RIGHTS_APPLICABLE",
        "INDIGENOUS_RIGHTS_DEF",
        "ASSOCIATED_TRADITIONAL_KNOWLEDGE_APPLICABLE",
        "ASSOCIATED_TRADITIONAL_KNOWLEDGE_LABEL",
        "ASSOCIATED_TRADITIONAL_KNOWLEDGE_CONTACT",
        "ETHICS_PERMITS_MANDATORY",
        "ETHICS_PERMITS_DEF",
        "SAMPLING_PERMITS_MANDATORY",
        "SAMPLING_PERMITS_DEF",
        "NAGOYA_PERMITS_MANDATORY",
        "NAGOYA_PERMITS_DEF",
        "TISSUE_REMOVED_FOR_BIOBANKING",
        "TISSUE_REMOVED_FOR_BIOBANKING",
        "TISSUE_VOUCHER_ID_FOR_BIOBANKING",
        "TISSUE_FOR_BIOBANKING",
        "DNA_REMOVED_FOR_BIOBANKING",
        "DNA_VOUCHER_ID_FOR_BIOBANKING",
        "COLLECTOR_ORCID_ID",
        "PRESERVATION_APPROACH",
        "boldAccession",
        "public_name",
        "biosampleAccession",
        "created_by",
        "time_created",
        "submissionAccession",
        "sraAccession",
        "manifest_id",
        "time_updated",
        "updated_by",
        "status",
        "sampleDerivedFrom",
        "sampleSameAs",
        "sampleSymbiontOf",
        "copo_profile_title",
        "tol_project",

    ],
    "asg": [
        "SERIES",
        "RACK_OR_PLATE_ID",
        "TUBE_OR_WELL_ID",
        "SPECIMEN_ID",
        "TAXON_ID",
        "ORDER_OR_GROUP",
        "FAMILY",
        "GENUS",
        "SCIENTIFIC_NAME",
        "INFRASPECIFIC_EPITHET",
        "CULTURE_OR_STRAIN_ID",
        "COMMON_NAME",
        "TAXON_REMARKS",
        "LIFESTAGE",
        "SEX",
        "ORGANISM_PART",
        "PARTNER",
        "PARTNER_SAMPLE_ID",
        "COLLECTOR_SAMPLE_ID",
        "COLLECTED_BY",
        "COLLECTOR_AFFILIATION",
        "DATE_OF_COLLECTION",
        "COLLECTION_LOCATION",
        "DECIMAL_LATITUDE",
        "DECIMAL_LONGITUDE",
        "HABITAT",
        "DESCRIPTION_OF_COLLECTION_METHOD",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION",
        "IDENTIFIED_HOW",
        "SPECIMEN_ID_RISK",
        "MIXED_SAMPLE_RISK",
        "PRESERVED_BY",
        "PRESERVER_AFFILIATION",
        "PRESERVATION_APPROACH",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUES_IN_TUBE",
        "TISSUE_REMOVED_FROM_BARCODING",
        "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP",
        "REGULATORY_COMPLIANCE",
        "VOUCHER_ID",
        "RELATIONSHIP",
        "GRID_REFERENCE",
        "DEPTH",
        "ELEVATION",
        "TIME_OF_COLLECTION",
        "IDENTIFIER_AFFILIATION",
        "PRESERVATIVE_SOLUTION",
        "SIZE_OF_TISSUE_IN_TUBE",
        "TISSUE_REMOVED_FOR_BARCODING",
        "OTHER_INFORMATION",
        "SYMBIONT",
        "BARCODE_HUB",
        "ORIGINAL_COLLECTION_DATE",
        "ORIGINAL_GEOGRAPHIC_LOCATION",
        "ORIGINAL_DECIMAL_LATITUDE",
        "ORIGINAL_DECIMAL_LONGITUDE",
        "BARCODING_STATUS",
        "boldAccession",
        "public_name",
        "biosampleAccession",
        "created_by",
        "time_created",
        "submissionAccession",
        "sraAccession",
        "manifest_id",
        "time_updated",
        "updated_by",
        "status",
        "sampleDerivedFrom",
        "sampleSameAs",
        "sampleSymbiontOf",
        "copo_profile_title",
        "tol_project"
    ],
    "env": []
}
DTOL_ENUMS = {

    "GAL": {
        "DTOL": [
            "SANGER INSTITUTE",
            "UNIVERSITY OF OXFORD",
            "MARINE BIOLOGICAL ASSOCIATION",
            "ROYAL BOTANIC GARDENS KEW",
            "ROYAL BOTANIC GARDEN EDINBURGH",
            "EARLHAM INSTITUTE",
            "NATURAL HISTORY MUSEUM"],

        "DTOL_ENV": [
            "SANGER INSTITUTE",
            "UNIVERSITY OF OXFORD",
            "MARINE BIOLOGICAL ASSOCIATION",
            "ROYAL BOTANIC GARDENS KEW",
            "ROYAL BOTANIC GARDEN EDINBURGH",
            "EARLHAM INSTITUTE",
            "NATURAL HISTORY MUSEUM"
        ],
        "ERGA": [
            "SANGER INSTITUTE",
            "EARLHAM INSTITUTE",
            "CENTRO NACIONAL DE ANÁLISIS GENÓMICO",
            "SCILIFELAB",
            "WEST GERMAN GENOME CENTRE",
            "NGS COMPETENCE CENTER TÜBINGEN",
            "DRESDEN-CONCEPT",
            "FUNCTIONAL GENOMIC CENTER ZURICH",
            "GENOSCOPE",
            "LAUSANNE GENOMIC TECHNOLOGIES FACILITY",
            "DNA SEQUENCING AND GENOMICS LABORATORY, HELSINKI GENOMICS CORE FACILITY",
            "NGS BERN",
            "NORWEGIAN SEQUENCING CENTRE",
            "UNIVERSITY OF BARI",
            "UNIVERSITY OF FLORENCE",
            "NEUROMICS SUPPORT FACILITY, UANTWERP, VIB",
            "GIGA-GENOMICS CORE FACILITY UNIVERSITY OF LIEGE",
            "SVARDAL LAB, ANTWERP",
            "HANSEN LAB, DENMARK",
            "INDUSTRY PARTNER",
            "LEIBNIZ INSTITUTE FOR THE ANALYSIS OF BIODIVERSITY CHANGE, MUSEUM KOENIG, BONN",
            "other ERGA associated GAL"
        ]},
    "PARTNER": [
        "UNIVERSITY OF DERBY",
        "DALHOUSIE UNIVERSITY",
        "GEOMAR HELMHOLTZ CENTRE",
        "NOVA SOUTHEASTERN UNIVERSITY",
        "UNIVERSITY OF BRITISH COLUMBIA",
        "UNIVERSITY OF VIENNA (MOLLUSC)",
        "QUEEN MARY UNIVERSITY OF LONDON",
        "THE SAINSBURY LABORATORY",
        "PORTLAND STATE UNIVERSITY",
        "UNIVERSITY OF RHODE ISLAND",
        "SENCKENBERG RESEARCH INSTITUTE",
        "UNIVERSITY OF VIENNA (CEPHALOPOD)",
        "UNIVERSITY OF ORGEON",
        "UNIVERSITY OF CALIFORNIA"
    ],
    "SYMBIONT": [
        "TARGET",
        "SYMBIONT"
    ],
    "SPECIMEN_ID_RISK": [
        "Y",
        "N"
    ],
    "SEX": [
        "FEMALE",
        "MALE",
        "HERMAPHRODITE_MONOECIOUS",
        "NOT_COLLECTED",
        "NOT_APPLICABLE",
        "NOT_PROVIDED",
        "ASEXUAL_MORPH",
        "SEXUAL_MORPH"
    ],
    "LIFESTAGE": [
        "ADULT",
        "EGG",
        "JUVENILE",
        "LARVA",
        "PUPA",
        "SPOROPHYTE",
        "GAMETOPHYTE",
        "EMBRYO",
        "ZYGOTE",
        "SPORE_BEARING_STRUCTURE",
        "VEGETATIVE_STRUCTURE",
        "VEGETATIVE_CELL",
        "NOT_COLLECTED",
        "NOT_APPLICABLE",
        "NOT_PROVIDED"
    ],
    "HAZARD_GROUP": {
        "DTOL": [
            "HG1",
            "HG2",
            "HG3"
        ],
        "ASG": [
            "HG1",
            "HG2",
            "HG3"
        ],
        "ERGA": [
            "1",
            "2",
            "3",
            "4"
        ]
    },
    "REGULATORY_COMPLIANCE": [
        "Y",
        "N",
        "NOT_APPLICABLE"
    ],
    "MIXED_SAMPLE_RISK": [
        "Y",
        "N"
    ],
    "ORGANISM_PART": [
        "**OTHER_FUNGAL_TISSUE**",
        "**OTHER_PLANT_TISSUE**",
        "**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**",
        "**OTHER_SOMATIC_ANIMAL_TISSUE**",
        "ABDOMEN",
        "ANTERIOR_BODY",
        "BLADE",
        "BLOOD",
        "BODYWALL",
        "BRACT",
        "BRAIN",
        "BUD",
        "CAP",
        "CEPHALOTHORAX",
        "EGG",
        "EGGSHELL",
        "ENDOCRINE_TISSUE",
        "EYE",
        "FAT_BODY",
        "FIN",
        "FLOWER",
        "GILL_ANIMAL",
        "GILL_FUNGI",
        "GONAD",
        "HAIR",
        "HEAD",
        "HEART",
        "HEPATOPANCREAS",
        "HOLDFAST_FUNGI",
        "KIDNEY",
        "INTESTINE",
        "LEAF",
        "LEG",
        "LIVER",
        "LUNG",
        "MID_BODY",
        "MODULAR_COLONY",
        "MUSCLE",
        "MYCELIUM",
        "MYCORRHIZA",
        "NOT_COLLECTED",
        "NOT_APPLICABLE",
        "NOT_PROVIDED",
        "OVARY_ANIMAL",
        "OVIDUCT",
        "PANCREAS",
        "PETIOLE",
        "POSTERIOR_BODY",
        "ROOT",
        "SCALES",
        "SCAT",
        "SEEDLING",
        "SEED",
        "SHOOT",
        "SKIN",
        "SPERM_SEMINAL_FLUID",
        "SPLEEN",
        "SPORE",
        "SPORE_BEARING_STRUCTURE",
        "STEM",
        "STIPE",
        "STOMACH",
        "TENTACLE",
        "TERMINAL_BODY",
        "TESTIS",
        "THALLUS_FUNGI",
        "THALLUS_PLANT",
        "THORAX",
        "WHOLE_ORGANISM",
        "WHOLE_PLANT",
        "MOLLUSC_FOOT",
        "UNICELLULAR_ORGANISMS_IN_CULTURE",
        "MULTICELLULAR_ORGANISMS_IN_CULTURE"
    ],
    "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE": [
        "HIGH_PRIORITY",
        "NOT_APPLICABLE",
        "DIFFICULT",
        "NOT_PROVIDED",
        "NOT_COLLECTED",
        "FULL_CURATION"
    ],
    "TO_BE_USED_FOR": [
        "RNAseq",
        "REFERENCE GENOME",
        "RESEQUENCING(POPGEN)",
        "BARCODING ONLY"
    ],
    "PURPOSE_OF_SPECIMEN": {
        "DTOL": [
            "REFERENCE_GENOME",
            "SHORT_READ_SEQUENCING",
            "DNA_BARCODING_ONLY",
            "RNA_SEQUENCING",
            "R&D"],
        "ASG": [
            "REFERENCE_GENOME",
            "SHORT_READ_SEQUENCING",
            "DNA_BARCODING_ONLY",
            "RNA_SEQUENCING",
            "R&D"],
        "ERGA": [
            "REFERENCE_GENOME",
            "SHORT_READ_SEQUENCING",
            "DNA_BARCODING_ONLY",
            "RNA_SEQUENCING",
            "R&D"
        ]
    },
    "SIZE_OF_TISSUE_IN_TUBE": [
        "VS",
        "S",
        "M",
        "L",
        "SINGLE_CELL",
        "NOT_APPLICABLE",
        "NOT_COLLECTED",
        "NOT_PROVIDED"
    ],
    "TISSUE_FOR_BARCODING": [
        "**OTHER_FUNGAL_TISSUE**",
        "**OTHER_PLANT_TISSUE**",
        "**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**",
        "**OTHER_SOMATIC_ANIMAL_TISSUE**",
        "ABDOMEN",
        "ANTERIOR_BODY",
        "BLADE",
        "BLOOD",
        "BODYWALL",
        "BRACT",
        "BRAIN",
        "BUD",
        "CAP",
        "CEPHALOTHORAX",
        "DNA_EXTRACT",
        "EGG",
        "EGGSHELL",
        "ENDOCRINE_TISSUE",
        "EYE",
        "FAT_BODY",
        "FIN",
        "FLOWER",
        "GILL_ANIMAL",
        "GILL_FUNGI",
        "GONAD",
        "HAIR",
        "HEAD",
        "HEART",
        "HEPATOPANCREAS",
        "HOLDFAST_FUNGI",
        "KIDNEY",
        "INTESTINE",
        "LEAF",
        "LEG",
        "LIVER",
        "LUNG",
        "MID_BODY",
        "MODULAR_COLONY",
        "MUSCLE",
        "MYCELIUM",
        "MYCORRHIZA",
        "NOT_COLLECTED",
        "NOT_APPLICABLE",
        "NOT_PROVIDED",
        "OVARY_ANIMAL",
        "OVIDUCT",
        "PANCREAS",
        "PETIOLE",
        "POSTERIOR_BODY",
        "ROOT",
        "SCALES",
        "SCAT",
        "SEEDLING",
        "SEED",
        "SHOOT",
        "SKIN",
        "SPERM_SEMINAL_FLUID",
        "SPLEEN",
        "SPORE",
        "SPORE_BEARING_STRUCTURE",
        "STEM",
        "STIPE",
        "STOMACH",
        "TENTACLE",
        "TERMINAL_BODY",
        "TESTIS",
        "THALLUS_FUNGI",
        "THALLUS_PLANT",
        "THORAX",
        "WHOLE_ORGANISM",
        "WHOLE_PLANT",
        "MOLLUSC_FOOT",
        "UNICELLULAR_ORGANISMS_IN_CULTURE",
        "MULTICELLULAR_ORGANISMS_IN_CULTURE"
    ],
    "TISSUE_REMOVED_FOR_BARCODING": [
        "Y",
        "N"
    ],
    "COLLECTION_LOCATION": [
        "AFGHANISTAN",
        "ALBANIA",
        "ALGERIA",
        "AMERICAN SAMOA",
        "ANDORRA",
        "ANGOLA",
        "ANGUILLA",
        "ANTARCTICA",
        "ANTIGUA AND BARBUDA",
        "ARCTIC OCEAN",
        "ARGENTINA",
        "ARMENIA",
        "ARUBA",
        "ASHMORE AND CARTIER ISLANDS",
        "ATLANTIC OCEAN",
        "AUSTRALIA",
        "AUSTRIA",
        "AZERBAIJAN",
        "BAHAMAS",
        "BAHRAIN",
        "BAKER ISLAND",
        "BALTIC SEA",
        "BANGLADESH",
        "BARBADOS",
        "BASSAS DA INDIA",
        "BELARUS",
        "BELGIUM",
        "BELIZE",
        "BENIN",
        "BERMUDA",
        "BHUTAN",
        "BOLIVIA",
        "BORNEO",
        "BOSNIA AND HERZEGOVINA",
        "BOTSWANA",
        "BOUVET ISLAND",
        "BRAZIL",
        "BRITISH VIRGIN ISLANDS",
        "BRUNEI",
        "BULGARIA",
        "BURKINA FASO",
        "BURUNDI",
        "CAMBODIA",
        "CAMEROON",
        "CANADA",
        "CAPE VERDE",
        "CAYMAN ISLANDS",
        "CENTRAL AFRICAN REPUBLIC",
        "CHAD",
        "CHILE",
        "CHINA",
        "CHRISTMAS ISLAND",
        "CLIPPERTON ISLAND",
        "COCOS ISLANDS",
        "COLOMBIA",
        "COMOROS",
        "COOK ISLANDS",
        "CORAL SEA ISLANDS",
        "COSTA RICA",
        "COTE D'IVOIRE",
        "CROATIA",
        "CUBA",
        "CURACAO",
        "CYPRUS",
        "CZECH REPUBLIC",
        "DEMOCRATIC REPUBLIC OF THE CONGO",
        "DENMARK",
        "DJIBOUTI",
        "DOMINICA",
        "DOMINICAN REPUBLIC",
        "EAST TIMOR",
        "ECUADOR",
        "EGYPT",
        "EL SALVADOR",
        "EQUATORIAL GUINEA",
        "ERITREA",
        "ESTONIA",
        "ETHIOPIA",
        "EUROPA ISLAND",
        "FALKLAND ISLANDS (ISLAS MALVINAS)",
        "FAROE ISLANDS",
        "FIJI",
        "FINLAND",
        "FRANCE",
        "FRENCH GUIANA",
        "FRENCH POLYNESIA",
        "FRENCH SOUTHERN AND ANTARCTIC LANDS",
        "GABON",
        "GAMBIA",
        "GAZA STRIP",
        "GEORGIA",
        "GERMANY",
        "GHANA",
        "GIBRALTAR",
        "GLORIOSO ISLANDS",
        "GREECE",
        "GREENLAND",
        "GRENADA",
        "GUADELOUPE",
        "GUAM",
        "GUATEMALA",
        "GUERNSEY",
        "GUINEA",
        "GUINEA-BISSAU",
        "GUYANA",
        "HAITI",
        "HEARD ISLAND AND MCDONALD ISLANDS",
        "HONDURAS",
        "HONG KONG",
        "HOWLAND ISLAND",
        "HUNGARY",
        "ICELAND",
        "INDIA",
        "INDIAN OCEAN",
        "INDONESIA",
        "IRAN",
        "IRAQ",
        "IRELAND",
        "ISLE OF MAN",
        "ISRAEL",
        "ITALY",
        "JAMAICA",
        "JAN MAYEN",
        "JAPAN",
        "JARVIS ISLAND",
        "JERSEY",
        "JOHNSTON ATOLL",
        "JORDAN",
        "JUAN DE NOVA ISLAND",
        "KAZAKHSTAN",
        "KENYA",
        "KERGUELEN ARCHIPELAGO",
        "KINGMAN REEF",
        "KIRIBATI",
        "KOSOVO",
        "KUWAIT",
        "KYRGYZSTAN",
        "LAOS",
        "LATVIA",
        "LEBANON",
        "LESOTHO",
        "LIBERIA",
        "LIBYA",
        "LIECHTENSTEIN",
        "LITHUANIA",
        "LUXEMBOURG",
        "MACAU",
        "MACEDONIA",
        "MADAGASCAR",
        "MALAWI",
        "MALAYSIA",
        "MALDIVES",
        "MALI",
        "MALTA",
        "MARSHALL ISLANDS",
        "MARTINIQUE",
        "MAURITANIA",
        "MAURITIUS",
        "MAYOTTE",
        "MEDITERRANEAN SEA",
        "MEXICO",
        "MICRONESIA",
        "MIDWAY ISLANDS",
        "MOLDOVA",
        "MONACO",
        "MONGOLIA",
        "MONTENEGRO",
        "MONTSERRAT",
        "MOROCCO",
        "MOZAMBIQUE",
        "MYANMAR",
        "NAMIBIA",
        "NAURU",
        "NAVASSA ISLAND",
        "NEPAL",
        "NETHERLANDS",
        "NEW CALEDONIA",
        "NEW ZEALAND",
        "NICARAGUA",
        "NIGER",
        "NIGERIA",
        "NIUE",
        "NORFOLK ISLAND",
        "NORTH KOREA",
        "NORTH SEA",
        "NORTHERN MARIANA ISLANDS",
        "NORWAY",
        "OMAN",
        "PACIFIC OCEAN",
        "PAKISTAN",
        "PALAU",
        "PALMYRA ATOLL",
        "PANAMA",
        "PAPUA NEW GUINEA",
        "PARACEL ISLANDS",
        "PARAGUAY",
        "PERU",
        "PHILIPPINES",
        "PITCAIRN ISLANDS",
        "POLAND",
        "PORTUGAL",
        "PUERTO RICO",
        "QATAR",
        "REPUBLIC OF THE CONGO",
        "REUNION",
        "ROMANIA",
        "ROSS SEA",
        "RUSSIA",
        "RWANDA",
        "SAINT HELENA",
        "SAINT KITTS AND NEVIS",
        "SAINT LUCIA",
        "SAINT PIERRE AND MIQUELON",
        "SAINT VINCENT AND THE GRENADINES",
        "SAMOA",
        "SAN MARINO",
        "SAO TOME AND PRINCIPE",
        "SAUDI ARABIA",
        "SENEGAL",
        "SERBIA",
        "SEYCHELLES",
        "SIERRA LEONE",
        "SINGAPORE",
        "SINT MAARTEN",
        "SLOVAKIA",
        "SLOVENIA",
        "SOLOMON ISLANDS",
        "SOMALIA",
        "SOUTH AFRICA",
        "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS",
        "SOUTH KOREA",
        "SOUTHERN OCEAN",
        "SPAIN",
        "SPRATLY ISLANDS",
        "SRI LANKA",
        "SUDAN",
        "SURINAME",
        "SVALBARD",
        "SWAZILAND",
        "SWEDEN",
        "SWITZERLAND",
        "SYRIA",
        "TAIWAN",
        "TAJIKISTAN",
        "TANZANIA",
        "TASMAN SEA",
        "THAILAND",
        "TOGO",
        "TOKELAU",
        "TONGA",
        "TRINIDAD AND TOBAGO",
        "TROMELIN ISLAND",
        "TUNISIA",
        "TURKEY",
        "TURKMENISTAN",
        "TURKS AND CAICOS ISLANDS",
        "TUVALU",
        "USA",
        "UGANDA",
        "UKRAINE",
        "UNITED ARAB EMIRATES",
        "UNITED KINGDOM",
        "URUGUAY",
        "UZBEKISTAN",
        "VANUATU",
        "VENEZUELA",
        "VIET NAM",
        "VIRGIN ISLANDS",
        "WAKE ISLAND",
        "WALLIS AND FUTUNA",
        "WEST BANK",
        "WESTERN SAHARA",
        "YEMEN",
        "ZAMBIA",
        "ZIMBABWE",
        "NOT APPLICABLE",
        "NOT COLLECTED",
        "NOT PROVIDED"
    ],
    "BARCODE_HUB": [
        "UNIVERSITY OF OXFORD",
        "MARINE BIOLOGICAL ASSOCIATION",
        "ROYAL BOTANIC GARDEN EDINBURGH",
        "NATURAL HISTORY MUSEUM",
        "ROYAL BOTANIC GARDENS KEW/NATURAL HISTORY MUSEUM",
        "NOT_COLLECTED",
        "NOT_PROVIDED"
    ],
    "TISSUE_FOR_BIOBANKING": [
        "**OTHER_FUNGAL_TISSUE**",
        "**OTHER_PLANT_TISSUE**",
        "**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**",
        "**OTHER_SOMATIC_ANIMAL_TISSUE**",
        "ABDOMEN",
        "ANTERIOR_BODY",
        "BLADE",
        "BLOOD",
        "BODYWALL",
        "BRACT",
        "BRAIN",
        "BUD",
        "CAP",
        "CEPHALOTHORAX",
        "EGG",
        "EGGSHELL",
        "ENDOCRINE_TISSUE",
        "EYE",
        "FAT_BODY",
        "FIN",
        "FLOWER",
        "GILL_ANIMAL",
        "GILL_FUNGI",
        "GONAD",
        "HAIR",
        "HEAD",
        "HEART",
        "HEPATOPANCREAS",
        "HOLDFAST_FUNGI",
        "KIDNEY",
        "INTESTINE",
        "LEAF",
        "LEG",
        "LIVER",
        "LUNG",
        "MID_BODY",
        "MODULAR_COLONY",
        "MUSCLE",
        "MYCELIUM",
        "MYCORRHIZA",
        "NOT_COLLECTED",
        "NOT_APPLICABLE",
        "NOT_PROVIDED",
        "OVARY_ANIMAL",
        "OVIDUCT",
        "PANCREAS",
        "PETIOLE",
        "POSTERIOR_BODY",
        "ROOT",
        "SCALES",
        "SCAT",
        "SEEDLING",
        "SEED",
        "SHOOT",
        "SKIN",
        "SPERM_SEMINAL_FLUID",
        "SPLEEN",
        "SPORE",
        "SPORE_BEARING_STRUCTURE",
        "STEM",
        "STIPE",
        "STOMACH",
        "TENTACLE",
        "TERMINAL_BODY",
        "TESTIS",
        "THALLUS_FUNGI",
        "THALLUS_PLANT",
        "THORAX",
        "WHOLE_ORGANISM",
        "WHOLE_PLANT",
        "MOLLUSC_FOOT",
        "UNICELLULAR_ORGANISMS_IN_CULTURE",
        "MULTICELLULAR_ORGANISMS_IN_CULTURE"
    ],
    "TISSUE_REMOVED_FOR_BIOBANKING": [
        "Y",
        "N"
    ],
    "DNA_REMOVED_FOR_BIOBANKING": [
        "Y",
        "N"
    ],
    "ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_RIGHTS_APPLICABLE": [
        "Y",
        "N"
    ],
    "ETHICS_PERMIT_REQUIRED": [
        "Y",
        "N"
    ],
    "SAMPLING_PERMITS_REQUIRED": [
        "Y",
        "N"
    ],
    "NAGOYA_PERMITS_REQUIRED": [
        "Y",
        "N"
    ],
    "SEQUENCING_CENTRE": [
        "EARLHAM INSTITUTE",
        "SANGER INSTITUTE"
    ],
    "WATER_BODY_TYPE": [
        "STREAM",
        "RIVER",
        "POND",
        "LAKE",
        "COASTAL",
        "ESTUARY",
        "OPEN SEA"
    ],
    "WATER_TYPE": [
        "FRESH_WATER",
        "SALT_WATER",
        "BRACKISH_WATER"
    ],
    "SORTER_AFFILIATION": [
        "EARLHAM INSTITUTE",
        "UNIVERSITY OF OXFORD"
    ],
    "CELL_NUMBER": [
        "1",
        "2-10",
        "11-50",
        "51-100",
        "101-10000",
        "10001-50000",
        "50001-100000",
        "100001-500000",
        "500001-1000000",
        "1000000+"
    ],
    "BARCODING_STATUS": [
        "DNA_BARCODING_COMPLETED",
        "DNA_BARCODE_EXEMPT",
        "DNA_BARCODING_FAILED"
    ],
    "SAMPLE_FORMAT": [
        "live biological sample from infectious organism",
        "inactivated biological sample from infectious organism",
        "biological sample/tissue from non-infectious organism",
        "DNA",
        "RNA"
    ]
}
DTOL_RULES = {
    "DATE_OF_COLLECTION": {
        "ena_regex": "(^[12][0-9]{3}(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01])(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?"
                     "([+-][0-9]{1,2})?)?)?)?(/[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?"
                     "([+-][0-9]{1,2})?)?)?)?)?$)|(^not collected$)|(^not provided$)|(^restricted access$) ",
        "human_readable": "YYYY-MM-DD, NOT_COLLECTED or NOT_PROVIDED"
    },
    "DECIMAL_LATITUDE": {
        "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$) ",
        "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"
    },
    "DECIMAL_LONGITUDE": {
        "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$) ",
        "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"

    },
    "DEPTH": {
        "ena_regex": "(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?",
        "human_readable": "numeric, or empty string"

    },
    "ELEVATION": {
        "ena_regex": "[+-]?(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?",
        "human_readable": "numeric, or empty string"
    },
    "SAMPLE_DERIVED_FROM": {
        "ena_regex": "(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{"
                     "11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END]["
                     "AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)",
        "human_readable": "Specimen accession"
    },
    "SAMPLE_SAME_AS": {
        "ena_regex": "(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{"
                     "11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END]["
                     "AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)",
        "human_readable": "Specimen accession"
    },
    "SAMPLE_SYMBIONT_OF": {
        "ena_regex": "(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{"
                     "11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END]["
                     "AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)",
        "human_readable": "Specimen accession"
    },
    "RACK_OR_PLATE_ID": {
        "optional_regex": "^[a-zA-Z]{2}\d{8}$"
    },
    "TUBE_OR_WELL_ID": {
        "optional_regex": "^[a-zA-Z]{2}\d{8}$"
    },
    "TIME_OF_COLLECTION": {
        "strict_regex": "^([0-1][0-9]|2[0-4]):[0-5]\d$",
        "human_readable": "24-hour format with hours and minutes separated by colon"
    },
    "ORIGINAL_COLLECTION_DATE": {
        "ena_regex": "^[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?(/[0-9]{"
                     "4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?)?$",
        "strict_regex": "^(1\d{3}(-0\d(-[0-2]\d|-3[0-1])?|-1[0-2](-[0-2]\d|-3[0-1])?)?)|(20[0-2]\d{1}(-0\d(-["
                        "0-2]\d|-3[0-1])?|-1[0-2](-[0-2]\d|-3[0-1])?)?)$",
        "human_readable": "Date as YYYY, YYYY-MM or YYYY-MM-DD"
    },
    "SAMPLE_COORDINATOR_ORCID_ID": {
        "strict_regex": "^((\d{4}-){3}\d{3}(\d|X))(\|(\d{4}-){3}\d{3}(\d|X))*$",
        "human_readable": "16-digit number that is compatible with the ISO Standard (ISO 27729), if multiple IDs separate with a | and no spaces"
    },
    "COLLECTOR_ORCID_ID": {
        "strict_regex": "^((\d{4}-){3}\d{3}(\d|X))(\|(\d{4}-){3}\d{3}(\d|X))*|(^not provided$)|(^not applicable$)",
        "human_readable": "16-digit number that is compatible with the ISO Standard (ISO 27729),  if multiple IDs separate with a | and no spaces"
    },
    "SAMPLING_WATER_BODY_DEPTH": {
        "strict_regex": "^\d+$",
        "human_readable": "integer"
    },
    "WATER_SPEED": {
        "strict_regex": "^\d+$",
        "human_readable": "integer"
    },
    "CHLOROPHYL_A": {
        "strict_regex": "^\d+$",
        "human_readable": "integer"
    },
    "SALINITY": {
        "strict_regex": "^\d+$",
        "human_readable": "integer"
    },
    "DISSOLVED_OXYGEN": {
        "strict_regex": "^\d+$",
        "human_readable": "integer"
    },
    "TEMPERATURE": {
        "strict_regex": "^\d+$",
        "human_readable": "integer"
    },
    "ORIGINAL_DECIMAL_LATITUDE": {
        "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$) ",
        "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"
    },
    "ORIGINAL_DECIMAL_LONGITUDE": {
        "ena_regex": "(^[+-]?[0-9]+.?[0-9]*$)|(^not collected$)|(^not provided$)|(^restricted access$) ",
        "human_readable": "numeric, NOT_COLLECTED or NOT_PROVIDED"
    },
    "ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID": {
        "strict_regex": "^[a-z0-9]{8}-([a-z0-9]{4}-){3}[a-z0-9]{12}$",
        "human_readable": "[ID provided by the local conatext hub]"
    }
}
DTOL_UNITS = {
    "DECIMAL_LATITUDE": {
        "ena_unit": "DD"
    },
    "DECIMAL_LONGITUDE": {
        "ena_unit": "DD"
    },
    "DEPTH": {
        "ena_unit": "m"
    },
    "ELEVATION": {
        "ena_unit": "m"
    }
}
DTOL_ENA_MAPPINGS = {
    "ORGANISM_PART": {
        "ena": "organism part"
    },
    "LIFESTAGE": {
        "ena": "lifestage"
    },
    "COLLECTED_BY": {
        "ena": "collected_by"
    },
    "DATE_OF_COLLECTION": {
        "ena": "collection date"
    },
    "COLLECTION_LOCATION_1": {
        "info": "split COLLECTION_LOCATION on first '|' and put left hand side here (should be country)",
        "ena": "geographic location (country and/or sea)"
    },
    "DECIMAL_LATITUDE": {
        "ena": "geographic location (latitude)"
    },
    "DECIMAL_LONGITUDE": {
        "ena": "geographic location (longitude)"
    },
    "COLLECTION_LOCATION_2": {
        "info": "split COLLECTION_LOCATION on first '|' and put right hand side here (should be a list of '|' "
                "separated locations)",
        "ena": "geographic location (region and locality)"
    },
    "IDENTIFIED_BY": {
        "ena": "identified_by"
    },
    "DEPTH": {
        "ena": "geographic location (depth)"
    },
    "ELEVATION": {
        "ena": "geographic location (elevation)"
    },
    "HABITAT": {
        "ena": "habitat"
    },
    "IDENTIFIER_AFFILIATION": {
        "ena": "identifier_affiliation"
    },
    "SEX": {
        "ena": "sex"
    },
    "RELATIONSHIP": {
        "ena": "relationship"
    },
    "COLLECTOR_AFFILIATION": {
        "ena": "collecting institution"
    },
    "GAL": {
        "ena": "GAL"
    },
    "PARTNER": {
        "ena": "GAL"
    },
    "VOUCHER_ID": {
        "ena": "specimen_voucher"
    },
    "SPECIMEN_ID": {
        "ena": "specimen_id"
    },
    "GAL_SAMPLE_ID": {
        "ena": "GAL_sample_id"
    },
    "PARTNER_SAMPLE_ID": {
        "ena": "GAL_sample_id"
    },
    "CULTURE_OR_STRAIN_ID": {
        "ena": "culture_or_strain_id"
    },
    "sampleDerivedFrom": {
        "ena": "sample derived from"
    },
    "sampleSameAs": {
        "ena": "sample same as"
    },
    "sampleSymbiontOf": {
        "ena": "sample symbiont of"
    },
    "public_name": {
        "ena": "tolid"
    },
    "ORIGINAL_COLLECTION_DATE": {
        "ena": "original collection date"
    },
    "ORIGINAL_GEOGRAPHIC_LOCATION": {
        "ena": "original collection location"
    },
    "BARCODE_HUB": {
        "ena": "barcoding center"
    },
    "SAMPLE_COORDINATOR": {
        "ena": "sample coordinator"
    },
    "SAMPLE_COORDINATOR_AFFILIATION": {
        "ena": "sample coordinator affiliation"
    },
    # this is a custom field extra to the checklist
    "SAMPLE_COORDINATOR_ORCID_ID": {
        "ena": "sample coordinator ORCID ID"
    },
    "TISSUE_VOUCHER_ID_FOR_BIOBANKING": {
        "ena": "bio_material"
    },
    "DNA_VOUCHER_ID_FOR_BIOBANKING": {
        "ena": "bio_material"
    },
    "DESCRIPTION_OF_COLLECTION_METHOD": {
        "ena": "sample collection device or method"
    },
    "ORIGINAL_DECIMAL_LATITUDE": {
        "ena": "original geographic location (latitude)"
    },
    "ORIGINAL_DECIMAL_LONGITUDE": {
        "ena": "original geographic location (longitude)"
    },
    "PROXY_VOUCHER_ID": {
        "ena": "proxy voucher"
    },
    "VOUCHER_LINK": {
        "ena": "specimen voucher url"
    },
    "PROXY_VOUCHER_LINK": {
        "ena": "proxy voucher url"
    },
    "VOUCHER_INSTITUTION": {
        "ena": "voucher institution url"
    },
    "COLLECTOR_ORCID_ID": {
        "ena": "collector ORCID ID"
    }
}

SPECIMEN_PREFIX = {
    "GAL": {
        "dtol": {
            "UNIVERSITY OF OXFORD": "Ox",
            "MARINE BIOLOGICAL ASSOCIATION": "MBA",
            "ROYAL BOTANIC GARDENS KEW": "KDTOL",
            "ROYAL BOTANIC GARDEN EDINBURGH": "EDTOL",
            "EARLHAM INSTITUTE": "EI_",
            "NATURAL HISTORY MUSEUM": "NHMUK",
            "SANGER INSTITUTE": "SAN"
        },
        "erga": {
            "default": "ERGA_"
        },
        "dtol_env": {
            "UNIVERSITY OF OXFORD": "Ox",
            "MARINE BIOLOGICAL ASSOCIATION": "MBA",
            "ROYAL BOTANIC GARDENS KEW": "KDTOL",
            "ROYAL BOTANIC GARDEN EDINBURGH": "EDTOL",
            "EARLHAM INSTITUTE": "EI_",
            "NATURAL HISTORY MUSEUM": "NHMUK",
            "SANGER INSTITUTE": "SAN"
        }
    },
    "PARTNER": {
        "UNIVERSITY OF DERBY": "UDUK",
        "DALHOUSIE UNIVERSITY": "DU",
        "NOVA SOUTHEASTERN UNIVERSITY": "NSU",
        "GEOMAR HELMHOLTZ CENTRE": "GHC",
        "UNIVERSITY OF BRITISH COLUMBIA": "UOBC",
        "UNIVERSITY OF VIENNA (MOLLUSC)": "VIEM",
        "QUEEN MARY UNIVERSITY OF LONDON": "QMOUL",
        "THE SAINSBURY LABORATORY": "SL",
        "PORTLAND STATE UNIVERSITY": "PORT",
        "UNIVERSITY OF RHODE ISLAND": "URI",
        "UNIVERSITY OF CALIFORNIA": "UCALI",
        "SENCKENBERG RESEARCH INSTITUTE": "SENCK",
        "UNIVERSITY OF VIENNA (CEPHALOPOD)": "VIEC",
        "UNIVERSITY OF OREGON": "UOREG",
    }
}

SPECIMEN_SUFFIX = {
    "GAL": {
        "dtol": {
            "UNIVERSITY OF OXFORD": '\d{6}',
            "MARINE BIOLOGICAL ASSOCIATION": '-\d{6}-\d{3}[A-Z]',
            "ROYAL BOTANIC GARDENS KEW": '\d{5}',
            "ROYAL BOTANIC GARDEN EDINBURGH": '\d{5}',
            "EARLHAM INSTITUTE": '\d{5}',
            "NATURAL HISTORY MUSEUM": '\d{9}',
            "SANGER INSTITUTE": '\d{7}'
        },
        "dtol_env": {
            "UNIVERSITY OF OXFORD": '\d{6}',
            "MARINE BIOLOGICAL ASSOCIATION": '-\d{5}-\d{3}[A-Z]',
            "ROYAL BOTANIC GARDENS KEW": '\d{5}',
            "ROYAL BOTANIC GARDEN EDINBURGH": '\d{5}',
            "EARLHAM INSTITUTE": '\d{5}',
            "NATURAL HISTORY MUSEUM": '\d{9}',
            "SANGER INSTITUTE": '\d{7}'
        },
        "erga": {
            "default": "([A-Z]{1,10}_\d{3}(\d|X)_\d{2,3})"
        }
    }
}

# allow updates to fields in the list by hand of the user pre-approval
DTOL_NO_COMPLIANCE_FIELDS = {
    "dtol": [
        "INFRASPECIFIC_EPITHET",
        "CULTURE_OR_STRAIN_ID",
        "LIFESTAGE",
        "SEX",
        "RELATIONSHIP",
        "GAL_SAMPLE_ID",
        "COLLECTOR_SAMPLE_ID",
        "DEPTH",
        "ELEVATION",
        "TIME_OF_COLLECTION",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION",
        "IDENTIFIED_HOW",
        "SPECIMEN_ID_RISK",
        "PRESERVED_BY",
        "PRESERVER_AFFILIATION",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUE_IN_TUBE",
        "BARCODE_HUB",
        "TISSUE_REMOVED_FOR_BARCODING",
        "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP",
        "VOUCHER_ID"
    ],
    "asg": [
        "INFRASPECIFIC_EPITHET",
        "CULTURE_OR_STRAIN_ID",
        "LIFESTAGE",
        "SEX",
        "RELATIONSHIP",
        "PARTNER_SAMPLE_ID",
        "COLLECTOR_SAMPLE_ID",
        "DEPTH",
        "ELEVATION",
        "TIME_OF_COLLECTION",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION",
        "IDENTIFIED_HOW",
        "SPECIMEN_ID_RISK",
        "PRESERVED_BY",
        "PRESERVER_AFFILIATION",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUE_IN_TUBE",
        "BARCODE_HUB",
        "TISSUE_REMOVED_FOR_BARCODING",
        "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP",
        "VOUCHER_ID"
    ],
    "erga": [
        "SAMPLE_COORDINATOR",
        "SAMPLE_COORDINATOR_AFFILIATION",
        "SAMPLE_COORDINATOR_ORCID_ID",
        "TAXON_ID",
        "ORDER_OR_GROUP",
        "FAMILY",
        "GENUS",
        "SCIENTIFIC_NAME",
        "INFRASPECIFIC_EPITHET",
        "CULTURE_OR_STRAIN_ID",
        "COMMON_NAME",
        "TAXON_REMARKS",
        "LIFESTAGE",
        "SEX",
        "ORGANISM_PART",
        "GAL",
        "GAL_SAMPLE_ID",
        "COLLECTOR_SAMPLE_ID",
        "COLLECTED_BY",
        "COLLECTOR_AFFILIATION",
        "DATE_OF_COLLECTION",
        "COLLECTION_LOCATION",
        "DECIMAL_LATITUDE",
        "DECIMAL_LONGITUDE",
        "HABITAT",
        "DESCRIPTION_OF_COLLECTION_METHOD",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION",
        "IDENTIFIED_HOW",
        "SPECIMEN_ID_RISK",
        "PRESERVED_BY",
        "PRESERVER_AFFILIATION",
        "PRESERVATION_APPROACH",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUES_IN_TUBE",
        "TISSUE_REMOVED_FROM_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE",
        "TISSUE_REMOVED_FOR_BIOBANKING",
        "TISSUE_VOUCHER_ID_FOR_BIOBANKING",
        "TISSUE_FOR_BIOBANKING",
        "DNA_REMOVED_FOR_BIOBANKING",
        "DNA_VOUCHER_FOR_BIOBANKING",
        "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP",
        "REGULATORY_COMPLIANCE",
        "VOUCHER_ID",
        "INDIGENOUS_RIGHTS_APPLICABLE",
        "INDIGENOUS_RIGHTS_DEF",
        "ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_RIGHTS_APPLICABLE",
        "INDIGENOUS_RIGHTS_DEF",
        "ASSOCIATED_TRADITIONAL_KNOWLEDGE_OR_BIOCULTURAL_PROJECT_ID",
        "ASSOCIATED_TRADITIONAL_KNOWLEDGE_CONTACT",
        "ETHICS_PERMITS_REQUIRED",
        "ETHICS_PERMITS_DEF",
        "SAMPLING_PERMITS_REQUIRED",
        "NAGOYA_PERMITS_REQUIRED",
        "NAGOYA_PERMITS_DEF",
        "RELATIONSHIP",
        "GRID_REFERENCE",
        "DEPTH",
        "ELEVATION",
        "TIME_OF_COLLECTION",
        "IDENTIFIER_AFFILIATION",
        "PRESERVATIVE_SOLUTION",
        "SIZE_OF_TISSUE_IN_TUBE",
        "TISSUE_REMOVED_FOR_BARCODING",
        "OTHER_INFORMATION",
        "BARCODE_HUB",
        "ORIGINAL_GEOGRAPHIC_LOCATION",
        "ORIGINAL_COLLECTION_DATE"
    ]
}

API_KEY = resolve_env.get_env("PUBLIC_NAME_SERVICE_API_KEY")
NIH_API_KEY = resolve_env.get_env("NIH_API_KEY")

BLANK_VALS = ['NOT_COLLECTED', 'NOT_PROVIDED', 'NOT_APPLICABLE']
SYMBIONT_VALS = ["TARGET", "SYMBIONT"]
NA_VALS = ['#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A',
           'NULL', 'NaN', 'n/a', 'nan']
DATE_FIELDS = ["DATE_OF_COLLECTION", "DATE_OF_PRESERVATION"]
SPECIES_LIST_FIELDS = ["SYMBIONT", "TAXON_ID", "ORDER_OR_GROUP", "FAMILY", "GENUS", "SCIENTIFIC_NAME",
                       "INFRASPECIFIC_EPITHET", "CULTURE_OR_STRAIN", "COMMON_NAME", "TAXON_REMARKS"]
SYMBIONT_FIELDS = ["ORDER_OR_GROUP", "FAMILY", "GENUS", "TAXON_ID", "SCIENTIFIC_NAME", "TAXON_REMARKS",
                   "INFRASPECIFIC_EPITHET", "CULTURE_OR_STRAIN_ID", "COMMON_NAME", "LIFESTAGE", "SEX", "SYMBIONT",
                   "species_list", "characteristics", "profile_id", "manifest_id", "sample_type", "biosampleAccession",
                   "sraAccession", "submissionAccession", "status", "tol_project", "manifest_version", "public_name",
                   "factorValues"]
TOL_PROFILE_TYPES = ["asg", "dtol", "dtol_env", "erga"]
SANGER_TOL_PROFILE_TYPES = ["asg", "dtol", "dtol_env", "erga"]

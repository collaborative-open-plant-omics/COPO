ENA_MAPPING = {
    #barcoding loci to ENA marker sequence checklist
    "ITS" : "ITS rDNA",
    "rbcL" : "Single CDS genomic DNA",
    "ITS2" : "ITS rDNA",
    "psbA-trnH" : "Multi-Locus Marker",
    "COI" : "COI gene",
    "16S" : "rRNA Gene",
    "CO1" : "COI gene",
    "18S (V4, V9)" : "rRNA gene",
    "LSU D2/D3" : "rRNA Gene",
    "tufA" : "Single CDS genomic DNA",
    "psaA" : "Single CDS genomic DNA",
    "18S V4" : "rRNA Gene",
    "18S V9" : "rRNA Gene",
    "18S" : "rRNA Gene"

}

CHECKLISTS = {
    "rRNA gene" : {
        "checklist_code" : "ERT000002",
        "mandatory" : [
            "organism", #is your oranism blablabla?
            "sedimentation coefficient", #selected from blablabla?
            "sequence"
        ],
        "optional" : [
            "strain name",
            "clone identifier",
            "isolate name",
            "isolation source",
            "sex of organism",
            "mating type",
            "haplotype",
            "organelle",
            "tissue type",
            "specimen voucher",
            "biomaterial",
            "culture collection",
            "variety",
            "cultivar",
            "ecotype",
            "breed",
            "natural host",
            "laboratory host",
            "country",
            "geographic area",
            "locality",
            "latitude/longitude",
            "collection date",
            "forward primer name",
            "forward primer sequence",
            "reverse primer name",
            "reverse primer sequence",
            "2nd forward primer name",
            "2nd forward primer sequence",
            "2nd reverse primer name",
            "2nd reverse primer sequence"

        ]
    },
    "Single CDS genomic DNA" : {
        "checklist_code" : "ERT000029",
        "mandatory" : [
            "organism", #is your organism from blabla?
            "gene",
            "5' cds location",
            "3' cds location",
            "partial at 5'",
            "partial at 3'",
            "product",
            "translation table",
            "sequence"
        ],
        "optional" : [
            "strain name",
            "clone identifier",
            "isolate name",
            "isolation source",
            "sex of organism",
            "mating type",
            "haplotype",
            "plasmid",
            "organelle",
            "tissue type",
            "specimen voucher",
            "biomaterial",
            "culture collection",
            "variety",
            "cultivar",
            "ecotype",
            "breed",
            "natural host",
            "laboratory host",
            "country",
            "geographic area",
            "locality",
            "latitude/longitude",
            "collection date",
            "reading frame",
            "inference type",
            "inference accession",
            "experiment",
            "map",
            "allele",
            "chromosome",
            "function",
            "forward primer name",
            "forward primer sequence",
            "reverse primer name",
            "reverse primer sequence",
            "2nd forward primer name",
            "2nd forward primer sequence",
            "2nd reverse primer name",
            "2nd reverse primer sequence"
        ]
    },
    "ITS rDNA" : {
        "checklist_code" : "ERT000009",
        "mandatory" : [
            "organism", #is your organism blabla ?
            "18s rrna present",
            "its1 present",
            "5.8s rrna present",
            "its2 present",
            "28s rrna present",
            "sequence"
        ],
        "optional" : [
            "strain name",
            "clone identifier",
            "isolate name",
            "isolation source",
            "specimen voucher",
            "culture collection",
            "variety",
            "cultivar",
            "ecotype",
            "natural host",
            "country",
            "geographic area",
            "locality",
            "latitude/longitude",
            "collection date",
            "identified by",
            "forward primer name",
            "forward primer sequence",
            "reverse primer name",
            "reverse primer sequence",
            "2nd forward primer name",
            "2nd forward primer sequence",
            "2nd reverse primer name",
            "2nd reverse primer sequence"
        ]
    },
    "Multi-Locus Marker" : {
        "checklist_code": "ERT000058",
        "mandatory" : [
            "organism", #is your organism from blablabla?
            "region name",
            "sequence"
        ],
        "optional" : [
            "strain name",
            "clone identifier",
            "isolate name",
            "isolation source",
            "development stage",
            "sex of organism",
            "mating type",
            "haplotype",
            "organelle",
            "cell type",
            "tissue type",
            "specimen voucher",
            "biomaterial",
            "culture collection",
            "variety",
            "cultivar",
            "ecotype",
            "breed",
            "natural host",
            "laboratory host",
            "country",
            "geographic area",
            "locality",
            "latitude/longitude",
            "collection date",
            "forward primer name",
            "forward primer sequence",
            "reverse primer name",
            "reverse primer sequence",
            "2nd forward primer name",
            "2nd forward primer sequence",
            "2nd reverse primer name",
            "2nd reverse primer sequence"
        ]
    },
    "COI gene" : {
        "checklist_code" : "ERT000020",
        "mandatory" : [
            "organism",
            "5' cds location",
            "3' cds location",
            "partial at 5'",
            "partial at 3'",
            "translation table",
            "sequence"
        ],
        "optional" : [
            "strain name",
            "clone identifier",
            "isolate name",
            "isolation source",
            "development stage",
            "sex",
            "haplotype",
            "cell type",
            "tissue type",
            "specimen voucher",
            "variety",
            "cultivar",
            "ecotype",
            "breed",
            "natural host",
            "country",
            "geographic area",
            "locality",
            "latitude/longitude",
            "collection date",
            "identified by",
            "reading frame",
            "forward primer name",
            "forward primer sequence",
            "reverse primer name",
            "reverse primer sequence",
            "2nd forward primer name",
            "2nd forward primer sequence",
            "2nd reverse primer name",
            "2nd reverse primer sequence"
        ]
    }
}

BARCODING_VOCABULARY = {
    "marker product": [
        "actin",
        "alpha tubulin",
        "beta tubulin",
        "translation elongation factor 1 alpha",
        "calmodulin",
        "RNA polymerase II large subunit 1",
        "RNA polymerase II large subunit 2",
        "Glyceraldehyde 3-phosphate dehydrogenase",
        "Histone H3"
    ],
    "organelle": [
        "mitochondrion",
        "plastid",
        "chromatophore",
        "hydrogenosome",
        "nucleomorph",
        "mitochondrion:kinetoplast",
        "plastid:apicoplast",
        "plastid:chromoplast",
        "plastid:cyanelle",
        "plastid:leucoplast",
        "plastid:proplastid",
        "plastid:chloroplast"
    ],
    "ets type": [
        "5'",
        "3'"
    ],
    "reading frame" : [
        "1",
        "2",
        "3"
    ],
    "sediment coeficient" : [
        "5S",
        "5.8S",
        "12S",
        "16S",
        "18S",
        "23S",
        "26S",
        "28S"
    ],
    "inference type": [
        "similar to sequence",
        "similar to AA sequence",
        "similar to DNA sequence",
        "similar to RNA sequence",
        "similar to RNA sequence, mRNA",
        "similar to RNA sequence, EST",
        "similar to RNA sequence other RNA"        
        "profile",
        "nucleotide motif",
        "ab inito prediction",
        "alignment"
    ]
}
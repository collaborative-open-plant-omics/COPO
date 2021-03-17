MESSAGES = {
    "validation_msg_missing_symbiont": "Missing data detected in column <strong>%s</strong> at row "
                                       "<strong>%s</strong>. All required fields must have a value. There must be no "
                                       "empty rows. Values of <strong>%s</strong> are allowed.",
    "validation_msg_missing_data": "Missing data detected in column <strong>%s</strong> at row <strong>%s</strong>. "
                                   "All required fields must have a value. There must be no empty rows. Values of "
                                   "<strong>%s</strong> are allowed.",
    "validation_msg_missing_scientific_name": "Missing data detected in column <strong>%s</strong> at row "
                                              "<strong>%s</strong>. "
                                              "All required fields must have a value. There must be no empty rows.",
    "validation_msg_rack_tube_both_na": "NOT_APPLICABLE, NOT_PROVIDED or NOT_COLLECTED found in both RACK_OR_PLATE_ID "
                                        " and TUBE_OR_WELL_ID at row <strong>%s</strong>.",
    "validation_msg_duplicate_tube_or_well_id_in_copo": "Duplicate RACK_OR_PLATE_ID and TUBE_OR_WELL_ID already in "
                                                        "COPO: <strong>%s</strong>",
    "validation_msg_duplicate_without_target": "Duplicate RACK_OR_PLATE_ID and TUBE_OR_WELL_ID <strong>%s</strong> "
                                               "found without TARGET in SYMBIONT field. One of these duplicates must "
                                               "be listed as TARGET",
    "validation_msg_duplicate_tube_or_well_id": "Duplicate RACK_OR_PLATE_ID and TUBE_OR_WELL_ID found in this "
                                                "Manifest: <strong>%s</strong>",
    "validation_msg_invalid_data": "Invalid data: <strong>%s</strong> in column <strong>%s</strong> at row "
                                   "<strong>%s</strong>. Allowed values are <strong>%s</strong>",
    "validation_msg_invalid_list": "Invalid data: <strong>%s</strong> in column <strong>%s</strong> at row "
                                   "<strong>%s</strong>. If this is a location, start with the Country, adding more "
                                   "specific details separated with '|'. See list of allowed Country entries at <a "
                                   "href='https://www.ebi.ac.uk/ena/browser/view/ERC000053'>https://www.ebi.ac.uk/ena"
                                   "/browser/view/ERC000053</a>",
    "validation_msg_invalid_taxonomy": "Invalid data: <strong>%s</strong> in column <strong>%s</strong> at row "
                                       "<strong>%s</strong>. Expected value is <strong>%s</strong>",
    "validation_msg_synonym": "Invalid scientific name: <strong>%s</strong> at row <strong>%s</strong> is a synonym "
                              "of <strong>%s</strong>. Please provide the official scientific name.",
    "validation_msg_missing_taxon": "Missing TAXON_ID at row <strong>%s</strong>. For <strong>%s</strong> TAXON_ID "
                                    "should be <strong>%s</strong>",
    "validation_msg_used_whole_organism": "Duplicate SPECIMEN_ID and ORGANISM_PART <strong>'WHOLE ORGANISM'</strong> "
                                          "pair found for specimen: <strong>%s</strong>",
    "validation_warning_synonym": "Synonym warning: <strong>%s</strong> at row <strong>%s</strong> is a synonym of "
                                  "<strong>%s</strong>. COPO will substitute the official scientific name.",
    "validation_warning_field": "Missing <strong>%s</strong>: row <strong>%s</strong> - <strong>%s</strong> for "
                                "<strong>%s</strong> will be filled with <strong>%s</strong>",
    "validation_msg_invalid_rank": "Invalid scientific name or taxon ID: row <strong>%s</strong> - rank of scientific "
                                   "name and taxon id should be species.",

    "validation_msg_invalid_date": "Invalid date: <strong>%s</strong> in column <strong>%s</strong> at row "
                                   "<strong>%s</strong>. Dates should be in format YYYY-MM-DD",
    "barcode_msg_missing_specimen": "Samples not for found specimen <strong>%s</strong>. Barcodes can only be "
                                    "uploaded for previously registered TOL samples."

}

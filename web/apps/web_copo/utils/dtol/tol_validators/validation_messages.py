MESSAGES = {
    "validation_msg_missing_symbiont": "Missing data detected in column <strong>%s</strong> at row "
                                       "<strong>%s</strong>. All required fields must have a value. There must be no "
                                       "empty rows. Values of <strong>%s</strong> are allowed.",
    "validation_msg_missing_data": "Missing data detected in column <strong>%s</strong> at row <strong>%s</strong>. "
                                   "All required fields must have a value. There must be no empty rows. Values of "
                                   "<strong>%s</strong> are allowed, unless otherwise stated in the SOP.",
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
    "validation_msg_invalid_taxon": "TAXON_ID <strong>%s</strong> at row <strong>%s</strong> is invalid. "
                                    "Check SCIENTIFIC_NAME and TAXON_ID match at NCBI <a "
                                    "href='https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi'>here</a> or "
                                    "<a href='https://www.ncbi.nlm.nih.gov/Taxonomy/TaxIdentifier/tax_identifier.cgi'>"
                                    "here</a>. Please refer to the DTOL/ASG SOP. Contact ena-dtol@ebi.ac.uk or "
                                    "ena-asg@ebi.ac.uk for assistance.",
    "validation_msg_not_submittable_taxon": "TAXON_ID <strong>%s</strong> is not 'submittable' to ENA. Please see <a "
                                            "href="
                                            "'https://ena-docs.readthedocs.io/en/latest/faq/taxonomy_requests.html"
                                            "#creating-taxon-requests'>"
                                            "here</a> and contact ena-dtol@ebi.ac.uk or ena-asg@ebi.ac.uk to request "
                                            "an "
                                            "informal placeholder "
                                            "species name. Please also refer to the DTOL/ASG SOP.",
    "validation_msg_warning_racktube_format": "Warning: <strong>%s</strong> <strong>%s</strong> at row "
                                              "<strong>%s</strong> "
                                              "does not look like  FluidX format. Please check this is "
                                              "correct before clicking 'Finish'.",
    "validation_msg_warning_regex_gen": "Warning: <strong>%s</strong> <strong>%s</strong> at row <strong>%s</strong> "
                                        "is "
                                        "not in the expected format. Please check this is correct before clicking "
                                        "'Finish'.",
    "validation_msg_error_specimen_regex": "Invalid data: <strong>%s</strong> in column <strong>%s</strong> at row"
                                           " <strong>%s</strong>. Expected format for %s <strong>%s</strong> is "
                                           "<strong>"
                                           "%s</strong> followed by 7 digits.",
    "validation_msg_error_specimen_regex_dtol": "Invalid data: <strong>%s</strong> in column <strong>%s</strong> at row"
                                                " <strong>%s</strong>. Expected format for %s <strong>%s</strong> is "
                                                "<strong>"
                                                "%s</strong> followed by <strong>%s</strong>.",
    "validation_msg_warning_barcoding": "Warning: Overwriting PLATE_ID_FOR_BARCODING, "
                                        "TUBE_OR_WELL_ID_FOR_BARCODING, TISSUE_FOR_BARCODING and BARCODE_PLATE_PRESERVATIVE"
                                        "at row <strong>%s</strong> because TISSUE_REMOVED_FOR_BARCODING is <strong>%s</strong>",
    "validation_msg_original_field_missing": "Missing data: ORIGINAL_GEOGRAPHIC_LOCATION missing at row <strong>%s</strong>"
                                             ". If ORIGINAL_COLLECTION_DATE is provided, ORIGINAL_GEOGRAPHIC_LOCATION"
                                             " must also be provided.",
    "validation_msg_multiple_targets_with_same_id": "Multiple Targets found for RACK_OR_PLATE_ID/TUBE_OR_WELL_ID: "
                                                    "<strong>%s</strong>",
    "validation_msg_orphaned_symbiont": "Sybiont(s) found with TUBE_OR_WELL_ID: <strong>%s</strong> has no associated "
                                        "Target",
    "validation_message_wrong_specimen_taxon_pair" : "Invalid SPECIMEN_ID and TAXON pair: at row <strong>%s</strong>, "
                                                       "SPECIMEN_ID <strong>%s</strong> has already been used for "
                                                     "a specimen with TAXON_ID "
                                                       "<strong>%s</strong>"
}

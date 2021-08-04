from Bio import Entrez

from dal.copo_da import Profile
from submission.helpers.generic_helper import notify_frontend
from web.apps.web_copo.lookup import dtol_lookups as lookup
from web.apps.web_copo.utils.dtol.Dtol_Helpers import check_taxon_ena_submittable
from .tol_validator import TolValidtor
from .validation_messages import MESSAGES as msg

whole_used_specimens = set()
regex_human_readable = ""


class DtolEnumerationValidator(TolValidtor):

    def __init__(self, profile_id, fields, data, errors, warnings, flag, **kwargs):
        super().__init__(profile_id, fields, data, errors, warnings, flag, **kwargs)
        #self.warnings = list()
        self.taxonomy_dict = {}

    def validate(self):
        Entrez.api_key = lookup.NIH_API_KEY
        # build dictioanry of species in this manifest  max 200 IDs per query
        taxon_id_set = set([x for x in self.data['TAXON_ID'].tolist() if x])
        notify_frontend(data={"profile_id": self.profile_id},
                        msg="Querying NCBI for TAXON_IDs in manifest ",
                        action="info",
                        html_id="sample_info")
        taxon_id_list = list(taxon_id_set)
        if any(x for x in taxon_id_list):
            for taxon in taxon_id_list:
                # check if taxon is submittable
                ena_taxon_errors = check_taxon_ena_submittable(taxon)
                if ena_taxon_errors:
                    self.errors += ena_taxon_errors
                    self.flag = False

        if any(id for id in taxon_id_list):
            i = 0
            while i < len(taxon_id_list):
                window_list = taxon_id_list[i: i + 200]
                i += 200
                handle = Entrez.efetch(db="Taxonomy", id=window_list, retmode="xml")
                records = Entrez.read(handle)
                for element in records:
                    self.taxonomy_dict[element['TaxId']] = element
        for index, row in self.data[
            ['ORDER_OR_GROUP', 'FAMILY', 'GENUS', 'TAXON_ID', 'SCIENTIFIC_NAME']].iterrows():
            if all(row[header].strip() == "" for header in ['TAXON_ID', 'SCIENTIFIC_NAME']):
                self.errors.append(
                    "Missing data: both TAXON_ID and SCIENTIFIC_NAME missing from row <strong>%s</strong>. "
                    "Provide at least one" % (
                        str(index + 2)))
                self.flag = False
                continue
            notify_frontend(data={"profile_id": self.profile_id},
                            msg="Checking taxonomy information at row <strong>%s</strong> - "
                                "<strong>%s</strong>" % (
                                    str(index + 2), row['SCIENTIFIC_NAME']),
                            action="info",
                            html_id="sample_info")
            scientific_name = row['SCIENTIFIC_NAME'].strip()
            taxon_id = row['TAXON_ID'].strip()

            # suggest TAXON_ID if not provided
            if not taxon_id:
                handle = Entrez.esearch(db="Taxonomy", term=scientific_name)
                records = Entrez.read(handle)
                # errors.append(self.validation_msg_missing_taxon % (str(index+2), scientific_name,
                # records['IdList'][0]))
                if not records['IdList']:
                    self.errors.append(
                        "Invalid data: couldn't resolve SCIENTIFIC_NAME <strong>%s</strong> at row "
                        "<strong>%s</strong>" % (
                            scientific_name, str(index + 2)))
                    self.flag = False
                    continue
                self.warnings.append(msg["validation_warning_field"] % (
                    "TAXON_ID", str(index + 2), "TAXON_ID", scientific_name, records['IdList'][0]))
                self.data.at[index, "TAXON_ID"] = records['IdList'][0]
                taxon_id = records['IdList'][0]
                # check if taxon is submittable
                ena_taxon_errors = check_taxon_ena_submittable(taxon_id)
                if ena_taxon_errors:
                    self.errors += ena_taxon_errors
                    self.flag = False
                handle = Entrez.efetch(db="Taxonomy", id=taxon_id, retmode="xml")
                records = Entrez.read(handle)
                if records:
                    self.taxonomy_dict[records[0]['TaxId']] = records[0]

            if self.taxonomy_dict.get(taxon_id):
                if not scientific_name:
                    self.errors.append(msg["validation_msg_missing_scientific_name"] % ("SCIENTIFIC_NAME", str(index +
                                                                                                               2),))
                    self.flag = False
                    continue
                elif scientific_name.upper() != self.taxonomy_dict[taxon_id]['ScientificName'].upper():
                    handle = Entrez.esearch(db="Taxonomy", term=scientific_name)
                    records = Entrez.read(handle)
                    # check if the scientific name provided is a synonim
                    if taxon_id in records['IdList']:
                        self.warnings.append(msg["validation_warning_synonym"] % (scientific_name, str(index + 2),
                                                                                  self.taxonomy_dict[taxon_id][
                                                                                      'ScientificName']))
                        self.data.at[index, "SCIENTIFIC_NAME"] = self.taxonomy_dict[taxon_id][
                            'ScientificName'].upper()
                        other_info = ""
                        if self.data.at[index, "OTHER_INFORMATION"].strip():
                            other_info = self.data.at[index, "OTHER_INFORMATION"] + " | "
                        self.data.at[index, "OTHER_INFORMATION"] = other_info + \
                                                                   "COPO substituted the scientific name " \
                                                                   "synonym %s with %s" % (
                                                                       scientific_name,
                                                                       self.taxonomy_dict[taxon_id][
                                                                           'ScientificName'].upper())

                    elif not records['IdList']:
                        expected_name = self.taxonomy_dict[taxon_id].get('ScientificName', '[unknown]')
                        self.errors.append(msg["validation_msg_invalid_taxonomy"] % (
                            scientific_name, "SCIENTIFIC_NAME", str(index + 2), expected_name))
                        self.flag = False
                        continue
                    else:
                        self.errors.append(msg["validation_msg_invalid_taxonomy"] % (
                            taxon_id, "TAXON_ID", str(index + 2), str(records['IdList'])))
                        self.flag = False
                        continue

                if self.taxonomy_dict[taxon_id]['Rank'] != 'species':
                    # if not "ASG" in Profile().get_type(self.profile_id):  # ASG is allowed non species level ids
                    if not "SYMBIONT" in self.data.at[index, "SYMBIONT"]:
                        self.errors.append(msg["validation_msg_invalid_rank"] % (str(index + 2)))
                        self.flag = False
                        continue
                for element in self.taxonomy_dict[taxon_id]['LineageEx']:
                    rank = element.get('Rank')
                    if rank == 'genus':
                        if not row['GENUS'].strip():
                            self.warnings.append(msg["validation_warning_field"] % (
                                "GENUS", str(index + 2), "GENUS", scientific_name,
                                element.get('ScientificName').upper()))
                            self.data.at[index, "GENUS"] = element.get('ScientificName').upper()
                        elif row['GENUS'].strip().upper() != element.get('ScientificName').upper():
                            self.errors.append(msg["validation_msg_invalid_taxonomy"] % (
                                row['GENUS'], "GENUS", str(index + 2), element.get('ScientificName').upper()))
                            self.flag = False
                    elif rank == 'family':
                        if not row['FAMILY'].strip():
                            self.warnings.append(msg["validation_warning_field"] % (
                                "FAMILY", str(index + 2), "FAMILY", scientific_name,
                                element.get('ScientificName').upper()))
                            self.data.at[index, "FAMILY"] = element.get('ScientificName').upper()
                        elif row['FAMILY'].strip().upper() != element.get('ScientificName').upper():
                            self.errors.append(msg["validation_msg_invalid_taxonomy"] % (
                                row['FAMILY'], "FAMILY", str(index + 2), element.get('ScientificName').upper()))
                            self.flag = False
                    elif rank == 'order':
                        if not row['ORDER_OR_GROUP'].strip():
                            self.warnings.append(msg["validation_warning_field"] % (
                                "ORDER_OR_GROUP", str(index + 2), "ORDER_OR_GROUP", scientific_name,
                                element.get('ScientificName').upper()))
                            self.data.at[index, "ORDER_OR_GROUP"] = element.get('ScientificName').upper()
                        elif row['ORDER_OR_GROUP'].strip().upper() != element.get('ScientificName').upper():
                            self.errors.append(msg["validation_msg_invalid_taxonomy"] % (
                                row['ORDER_OR_GROUP'], "ORDER_OR_GROUP", str(index + 2),
                                element.get('ScientificName').upper()))
                            self.flag = False
            else:
                self.errors.append(
                    msg['validation_msg_invalid_taxon']
                    % (
                        row['TAXON_ID'], str(index + 2)))
                self.flag = False
        return self.errors, self.warnings, self.flag

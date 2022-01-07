from dal.copo_da import ValidationQueue
from web.apps.web_copo.validators.tol_validators import optional_field_dtol_validators as optional_validators, \
    taxon_validators
from web.apps.web_copo.validators.tol_validators import required_field_dtol_validators as required_validators
from web.apps.web_copo.validators.validator import Validator
import pandas
import inspect
import pickle
from web.apps.web_copo.lookup import dtol_lookups as lookup


class ProcessValidationQueue:

    def __init__(self):
        self.required_field_validators = list()
        self.optional_field_validators = list()
        self.optional_field_validators = list()
        self.taxon_field_validators = list()
        self.optional_validators = optional_validators
        self.required_validators = required_validators
        self.taxon_validators = taxon_validators
        self.symbiont_list = []
        self.validator_list = []
        self.sample_data = None

    def process_validation_queue(self):
        # get all manifests queued for validation
        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.required_field_validators.append(element)
        # create list of optional validators
        optional = dict(globals().items())["optional_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.optional_field_validators.append(element)
        # create list of taxon validators
        optional = dict(globals().items())["taxon_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, Validator) and not element.__name__ == "Validator":
                self.taxon_field_validators.append(element)

        queued_manifests = ValidationQueue().get_queued_manifests()

        for qm in queued_manifests:
            self.sample_data = pickle.loads(qm["manifest_data"])
            try:
                self.data = pandas.read_excel(self.sample_data, keep_default_na=False, na_values=lookup.NA_VALS)
            except:
                pass

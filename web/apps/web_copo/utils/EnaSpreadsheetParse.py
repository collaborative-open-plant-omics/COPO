from django.http import HttpResponse
from submission.helpers.generic_helper import notify_frontend
from django_tools.middlewares import ThreadLocal


# from .tol_validators import optional_field_dtol_validators as optional_validators

def parse_ena_spreadsheet(request):
    file = request.FILES["file"]
    name = file.name
    ena = ENASpreadsheet(file=file)
    if name.endswith("xlsx") or name.endswith("xls"):
        fmt = 'xls'
    elif name.endswith("csv"):
        fmt = 'csv'

    return HttpResponse()


class ENASpreadsheet:

    def __init__(self, file):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        sample_images = Path(settings.MEDIA_ROOT) / "sample_images"
        display_images = Path(settings.MEDIA_ROOT) / "img" / "sample_images"
        self.these_images = sample_images / self.profile_id
        self.display_images = display_images / self.profile_id
        self.data = None
        self.required_field_validators = list()
        self.optional_field_validators = list()
        self.taxon_field_validators = list()
        self.optional_validators = optional_validators
        self.required_validators = required_validators
        self.taxon_validators = taxon_validators
        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated
        if file:
            self.file = file
        else:
            self.sample_data = self.req.session.get("sample_data", "")
            self.isupdate = self.req.session.get("isupdate", False)

        # get type of manifest
        t = Profile().get_type(self.profile_id)
        if "ASG" in t:
            self.type = "ASG"
        elif "DTOL_EI" in t:
            self.type = "DTOL_EI"
        else:
            self.type = "DTOL"

        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, TolValidtor) and not element.__name__ == "Validator":
                self.required_field_validators.append(element)
        # create list of optional validators
        optional = dict(globals().items())["optional_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, TolValidtor) and not element.__name__ == "Validator":
                self.optional_field_validators.append(element)
        # create list of taxon validators
        optional = dict(globals().items())["taxon_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, TolValidtor) and not element.__name__ == "Validator":
                self.taxon_field_validators.append(element)

    def loadManifest(self, m_format):

        if self.profile_id is not None:
            notify_frontend(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                            html_id="sample_info")
            try:
                # read excel and convert all to string
                if m_format == "xls":
                    self.data = pandas.read_excel(self.file, keep_default_na=False,
                                                  na_values=lookup.NA_VALS)
                elif m_format == "csv":
                    self.data = pandas.read_csv(self.file, keep_default_na=False,
                                                na_values=lookup.NA_VALS)
                self.data = self.data.loc[:, ~self.data.columns.str.contains('^Unnamed')]
                '''
                for column in self.allowed_empty:
                    self.data[column] = self.data[column].fillna("")
                '''
                self.data = self.data.apply(lambda x: x.astype(str))
                self.data = self.data.apply(lambda x: x.str.strip())
                self.data.columns = self.data.columns.str.replace(" ", "")
            except Exception as e:
                # if error notify via web socket
                notify_frontend(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
                                action="info",
                                html_id="sample_info")
                return False
            return True

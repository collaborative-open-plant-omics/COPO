class TolValidtor:

    def __init__(self, profile_id, fields, data, errors, warnings, flag, **kwargs):
        self.profile_id = profile_id
        self.fields = fields
        self.data = data
        self.errors = errors
        self.warnings = warnings
        self.flag = flag
        self.kwargs = kwargs


    def validate(self):
        raise NotImplemented

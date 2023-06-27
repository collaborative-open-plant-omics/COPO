class Validator:
    # main header file for all manifest validator types
    def __init__(self, profile_id, checklist, fields, data, errors, warnings, flag, **kwargs):
        self.profile_id = profile_id
        self.checklist = checklist
        self.fields = fields
        self.data = data
        self.errors = errors
        self.warnings = warnings
        self.flag = flag
        self.kwargs = kwargs

    def validate(self):
        raise NotImplementedError

__author__ = 'etuka'

from exceptions_and_logging.logger import Logger
import web.apps.web_copo.lookup.lookup as lkup
import web.apps.web_copo.schemas.utils.data_utils as d_utils


class WizardSchemas:
    def __init__(self):
        self.wizard_paths = lkup.WIZARD_FILES

    def process_wizard_templates(self):
        """
        function reads schema files and presents in an easy to use manner
        :return:
        """

        template = dict()

        for k, v in self.wizard_paths.items():
            try:
                template[k] = d_utils.json_to_pytype(v)['properties']
            except Exception as e:
                Logger().exception(e)
                pass

        return template

    def get_wizard_template(self, identifier):
        template = self.process_wizard_templates()

        return template.get(identifier, list())

import traceback

from exceptions_and_logging.logger import Logger
from web.apps.web_copo.lookup.copo_enums import Loglvl

class LogUncaughtExceptions:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:

            return self.get_response(request)
        except Exception as e:
            Logger().log(e, level=Loglvl.ERROR)
            Logger().log(traceback.format_exc(), level=Loglvl.ERROR)


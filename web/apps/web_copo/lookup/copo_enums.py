__author__ = 'felix.shaw@tgac.ac.uk - 01/08/2016'

from enum import Enum


class Loglvl(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    DEBUG = 4


class Logtype(Enum):
    CONSOLE = 1
    FILE = 2


class bcolors(Enum):
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

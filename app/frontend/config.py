#
#
#######################################################################################

import logging

from . import defaults

from ..lib.config import Config

logger = logging.getLogger(__name__)
class FrontendConfig(Config):
    ''' create the configuration file for the backend '''

    def __init__(self):
        ''' init the config class with its default filename '''
        super().__init__(defaults.CONFIG_FILENAME)

    def _validate_and_correct(self):
        ''' check that the data is correct '''
        if not hasattr(self,"data"): self.data = {}
        if not isinstance(self.data,dict): self.data = {}
        if "version" not in self.data.keys(): self.data["version"] = VERSION
        if "sites"   not in self.data.keys(): self.data["sites"] = []
        for i in range(len(self.data["sites"])):
            if "token"   not in self.data["sites"][i].keys(): self.data["sites"][i]["token"]   = ""
            if "name"    not in self.data["sites"][i].keys(): self.data["sites"][i]["name"]    = ""
            if "address" not in self.data["sites"][i].keys(): self.data["sites"][i]["address"] = ""

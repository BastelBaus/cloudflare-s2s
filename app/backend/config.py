#
#
#######################################################################################

import logging
from . import defaults
from lib.config import Config


logger = logging.getLogger(__name__)

class BackendConfig(Config):
    ''' create the configuration file for the backend '''

    def __init__(self):
        ''' init the config class with its default filename '''
        super().__init__(defaults.CONFIG_FILENAME)

    def _validate_and_correct(self):
        ''' check that the data is correct '''
        if not hasattr(self,"data"): self.data = {}
        if not isinstance(self.data,dict): self.data = {}
        if "TUNNEL_TOKEN"   not in self.data.keys(): self.data["TUNNEL_TOKEN"]   = ""
        if "SERVER_NAME"   not in self.data.keys(): self.data["SERVER_NAME"]   = ""
        if "DNAT_TARGET"   not in self.data.keys(): self.data["DNAT_TARGET"]   = ""
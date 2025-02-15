
import os
import json

CONFIG_FILENAME = 'config.json'
VERSION = "0.1"

import logging
logger = logging.getLogger(__name__)

class config:
    
    def __init__(self):
        ''' '''
    
        self.data = config._default_config()
        if not os.path.exists(CONFIG_FILENAME):
            logger.warning(f"warning, could not find config file: {CONFIG_FILENAME}, create new one")
            self._validate_and_correct()
            self.store()
        if not os.path.exists(CONFIG_FILENAME):
            logger.warning(f"warning, could not create config file: {CONFIG_FILENAME}")
        else: self.load()


    def load(self):
        ''' load the current configuration from a file'''
        with open(CONFIG_FILENAME, 'r') as file:
            try:
                self.data = json.load(file)
            except: # in case of any error, start with a new file
                logger.warning("Could not read config file!")
                self.data = {}
        self._validate_and_correct()

    def store(self):
        ''' store the current configuration to a file '''
        with open(CONFIG_FILENAME, 'w') as file:
            json.dump(self.data, file, indent = " ")
        logger.warning(f"Wrote file:\n{self.data}")

    def _validate_and_correct(self):
        if not hasattr(self,"data"): self.data = {}
        if not isinstance(self.data,dict): self.data = {}
        if "version" not in self.data.keys(): self.data["version"] = VERSION
        if "sites"   not in self.data.keys(): self.data["sites"] = []
        for i in range(len(self.data["sites"])):
            if "token"   not in self.data["sites"][i].keys(): self.data["sites"][i]["token"]   = ""
            if "name"    not in self.data["sites"][i].keys(): self.data["sites"][i]["name"]    = ""
            if "address" not in self.data["sites"][i].keys(): self.data["sites"][i]["address"] = ""
            
        
    @staticmethod
    def _default_config():
        data = { "version":VERSION }
        return data

cfg = config()
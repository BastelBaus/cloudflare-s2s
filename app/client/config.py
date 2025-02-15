
import os
import json

CONFIG_FILENAME = 'config.json'
VERSION = "0.1"


class config:
    
    def __init__(self):
        ''' '''
    
        self.data = config._default_config()
        if not os.path.exists(CONFIG_FILENAME):
            self.store()
        if not os.path.exists(CONFIG_FILENAME):
            print("warning, could not find or create config file")
        else: self.load()


    def load(self):
        ''' load the current configuration from a file'''
        with open(CONFIG_FILENAME, 'r') as file:
            self.data = json.load(file)
        self._validate_and_correct()

    def store(self):
        ''' store the currenbt configuration to a file '''
        with open(CONFIG_FILENAME, 'w') as file:
            json.dump(self.data, file)

    def _validate_and_correct(self):
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
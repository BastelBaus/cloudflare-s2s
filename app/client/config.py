
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
        ''' load teh current configuration from a file'''
        with open(CONFIG_FILENAME, 'r') as file:
            self.data = json.load(file)

    def store(self):
        ''' store the currenbt configuration to a file '''
        with open(CONFIG_FILENAME, 'w') as file:
            json.dump(self.data, file)


    @staticmethod
    def _default_config():
        data = { 'version':VERSION }
        return data

cfg = config()
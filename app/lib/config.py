#
#
###########################################################################################
# pylint: disable=logging-fstring-interpolation

import os
import json

from . import defaults

import logging
logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod

class Config(ABC):
    ''' Generic conflig clas sto load and store as json file '''    

    def __init__(self,filename= defaults.CONFIG_FILENAME):
        ''' configure the config file '''
  
        self.filename = filename

        if not os.path.exists(self.filename):
            logger.warning(f"warning, could not find config file: {self.filename}, create new one")
            self._validate_and_correct()
            self.store()
        if not os.path.exists(self.filename):
            logger.warning(f"could not create config file: {self.filename}")
        else: self.load()


    def load(self):
        ''' load the current configuration from a file'''
        with open(self.filename, 'r', encoding="utf-8") as file:
            try:
                self.data = json.load(file)
            except: # pylint: disable=bare-except
                    # in case of any error, start with a new file
                    # TODO: what to catch ???
                logger.warning(f"Could not read config file ({self.filename})")
                self.data = {}
        self._validate_and_correct()

    def store(self):
        ''' store the current configuration to a file '''
        try:
            with open(self.filename, 'w', encoding="utf-8") as file:
                json.dump(self.data, file, indent = " ")
            logger.info(f"Wrote file: {self.filename}\n{self.data}")
        except: # pylint: disable=bare-except
                # in case of any error, start with a new file
                # TODO: what to catch ???
            logger.warning(f"Could not store file: {self.filename}\n{self.data}")
        
    @abstractmethod
    def _validate_and_correct(self):
        ''' must ensure that self.data is a correct structure ! '''
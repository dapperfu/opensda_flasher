# -*- coding: utf-8 -*-

import os

from configparser import ConfigParser, ExtendedInterpolation

from .utilities import path


class ExeClass(object):
    """Base class for Server and Client classes.
    
    Paramemters:
        config: ConfigParser configuration object.
        
    
    """
    def __init__(self, config=None):
        if config is None:
            self.config = ConfigParser(interpolation=ExtendedInterpolation())
            self.config.read(os.path.join(path, "opensda_flasher.ini"))
        else:
            self.config = config
        self.process = None
        
    def __del__(self):
        if self.process is not None:
            try:
                self.process.kill()
            except:
                pass

    @property
    def executable(self):
        raise(NotImplementedError("{} not implemented".format(self.__cls__.name)))
        
    @property
    def cmd(self):
        raise(NotImplementedError("{} not implemented".format(self.__cls__.name)))

    def launch(self):
        raise(NotImplementedError("{} not implemented".format(self.__cls__.name)))

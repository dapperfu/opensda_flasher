# -*- coding: utf-8 -*-
"""
@author: Jedediah Frey
"""

import os

from configparser import ConfigParser, ExtendedInterpolation


def read_config(local_config=None):
    if local_config is None:
        local_config = ""
    
    module_dir = os.path.dirname(__file__)
    home_dir = os.path.expanduser("~")
    
    default_config = os.path.join(module_dir, "opensda_flasher.ini")
    home_config = os.path.join(home_dir, ".opensda_flasher.ini")
    
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read([default_config, home_config, local_config])
    
    return config

if __name__ == "__main__":
    cfg = read_config()
    for k, v in cfg.items():
        print(k)
        for k2, v2 in v.items():
            print("\t{}: {}".format(k2,v2))

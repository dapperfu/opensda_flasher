# -*- coding: utf-8 -*-
"""Module config functions."""

from configparser import ConfigParser, ExtendedInterpolation
import os
import sys


def read_config(local_config=None):
    """Read Configuration File."""
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
    if len(sys.argv) > 1:
        cfg = read_config(sys.argv[1])
    else:
        cfg = read_config()

    for k, v in cfg.items():
        print(k)
        for k2, v2 in v.items():
            print("\t{}: {}".format(k2, v2))

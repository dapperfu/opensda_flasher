# -*- coding: utf-8 -*-
"""Base class for executables."""

from .config import read_config


class ExeClass(object):
    """Base class for Server and Client exe classes.

    Paramemters:
        config: ConfigParser configuration object.
    """

    def __init__(self, config=None):
        """Exe Class init."""
        if config is None:
            self.config = read_config()
        else:
            self.config = config
        self.process = None

    def __del__(self):
        """Exe Class destructor."""
        if self.process is not None:
            try:
                self.process.kill()
            except BaseException:
                pass

    @property
    def executable(self):
        """Not Implemented."""
        raise NotImplementedError

    @property
    def cmd(self):
        """Not Implemented."""
        raise NotImplementedError

    def launch(self):
        """Not Implemented."""
        raise NotImplementedError

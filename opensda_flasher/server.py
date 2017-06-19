# -*- coding: utf-8 -*-

import os

import delegator
from pexpect.exceptions import EOF

from .execlass import ExeClass

class Server(ExeClass):
    """ Debug server class
    """
    @property
    def executable(self):
        """ Executable
        """
        return os.path.join(self.config["S32"]["ROOT"],
                            "eclipse", 
                            "plugins",
                            self.config["SERVER"]["PLUGIN"],
                            self.config["SERVER"]["platform"],
                            self.config["SERVER"]["EXE"])
        
    @property
    def cmd(self):
        """ Command list to run
        """
        return [self.executable,
                "-startserver",
                "-singlesession",
                "-interface=OPENSDA",
                "-device={}".format(self.config["SERVER"]["DEVICE"]),
                "-serverport={}".format(self.config["SERVER"]["SERVERPORT"]),
                "-speed={}".format(self.config["SERVER"]["SPEED"]),
                "-port={}".format(self.config["SERVER"]["PORT"])]
    
    def kill(self):
        """ Kill the server.
        
        If a server is already running the task will fail. Use this to kill any
        existing processes.
        """
        self.process = delegator.run(["taskkill",
                                      "/f",
                                      "/im",
                                      os.path.basename(self.executable)],
                                      block=True)
        
    def launch(self):
        try:
            self.process = delegator.run(self.cmd, block=False)
            print("Waiting for GDB servers to complete startup ...", end="")
            # Look for the "All Serverns Running" message from stdout.
            self.process.expect("All Servers Running")
            print("... Done")
        except EOF:
            print("Server exited immediately. Is another {} instance running?".format(self.executable))

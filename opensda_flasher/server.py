# -*- coding: utf-8 -*-
"""Module server class."""
import os
import sys

import delegator
from pexpect.exceptions import EOF

from .execlass import ExeClass


class Server(ExeClass):
    """Debug server class."""

    @property
    def executable(self):
        """Path to server executable."""
        return os.path.join(self.config["S32"]["ROOT"],
                            "eclipse",
                            "plugins",
                            self.config["SERVER"]["PLUGIN"],
                            self.config["SERVER"]["platform"],
                            self.config["SERVER"]["EXE"])

    @property
    def cmd(self):
        """Command list to run."""
        return [self.executable,
                "-startserver",
                "-singlesession",
                "-interface=OPENSDA",
                "-device={}".format(self.config["SERVER"]["DEVICE"]),
                "-serverport={}".format(self.config["SERVER"]["SERVERPORT"]),
                "-speed={}".format(self.config["SERVER"]["SPEED"]),
                "-port={}".format(self.config["SERVER"]["PORT"])]

    def ports(self):
        """Print available ports."""
        self.process = delegator.run([self.executable,
                                      "-showhardware"],
                                     block=True)
        hardware = self.process.split("Done.")[-1]
        return hardware.strip()
        
    def kill(self):
        """Kill the server.

        If a server is already running the task will fail. Use this to kill any
        existing processes.
        """
        self.process = delegator.run(["taskkill",
                                      "/f",
                                      "/im",
                                      os.path.basename(self.executable)],
                                     block=True)

    def launch(self):
        """Launch debug server."""
        try:
            self.process = delegator.run(self.cmd, block=False)
            print("Waiting for GDB servers to complete startup ...", end="")
            sys.stdout.flush()
            # Look for the "All Serverns Running" message from stdout.
            self.process.expect("All Servers Running")
            print("... Done")
            sys.stdout.flush()
        except EOF:
            error="Server exited immediately. Is another {} instance running?".format(self.executable) # noqa
            raise(Exception(error))

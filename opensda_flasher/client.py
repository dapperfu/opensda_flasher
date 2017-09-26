# -*- coding: utf-8 -*-
"""OpenSDA GDB Client Class."""
import os
import sys
import tempfile
from time import sleep

import delegator
from jinja2 import Template

from .execlass import ExeClass


class Client(ExeClass):
    """Class for the GDB client that calls the flash functions."""

    def __init__(self, config=None):
        """Init Method."""
        # Call the super's init.
        super().__init__()
        # Generate a temporary file to feed to gdb.
        _, self.cmd_file = tempfile.mkstemp(suffix=".txt", prefix="gdb_")

        self.debug = False

    @property
    def executable(self):
        """Path to client executable."""
        return os.path.join(self.config["S32"]["ROOT"],
                            "Cross_Tools",
                            self.config["CLIENT"]["PLATFORM"],
                            "bin",
                            self.config["CLIENT"]["EXE"])

    @property
    def cmd(self):
        """List of commands for client to run."""
        return [self.executable,
                "--nx",
                "--command={}".format(self.cmd_file)]

    @property
    def template(self):
        """Jinja2 template class."""
        return Template(self.template_str)

    @property
    def template_str(self):
        """GDB command template."""
        return """target remote 127.0.0.1:{{ port }}

set mem inaccessible-by-default off
set tcp auto-retry on
set tcp connect-timeout 240
set remotetimeout 60

monitor preserve1 0

set architecture powerpc:vle

{%- for elf in elfs %}
load "{{ elf }}"
{%- endfor %}

{%-if debug %}
continue
{% else %}
monitor _reset
quit
{% endif %}
"""

    def render(self, elfs):
        """Render the Jinja2 template to the temp file."""
        # Escape filenames for windows.
        print("DEBUG: {}".format(self.cmd_file))
        if sys.platform == "win32":
            elfs = [elf.replace("\\", "\\\\") for elf in elfs]
        with open(self.cmd_file, "w") as fid:
            print(
                self.template.render(
                    port=self.config["SERVER"]["SERVERPORT"],
                    debug=self.debug,
                    elfs=elfs),
                file=fid)

    def flash(self, elfs):
        """Run the flash command."""
        self.render(elfs)
        print("Waiting for GDB client to flash ...", end="")
        sys.stdout.flush()
        self.process = delegator.run(self.cmd, block=False, timeout=120)
        if self.debug:
            print("... Give it a few moments.")
            print("There's currently no way to tell if this is working, so:")
            print("Press ^C to exit.")
            sys.stdout.flush()
            while 1:
                sleep(0.5)
            self.process.kill()
            self.process.terminate()
        else:
           self.process.block()
        print("... Done")
        sys.stdout.flush()
        print(self.process.err)

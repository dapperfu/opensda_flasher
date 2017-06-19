# -*- coding: utf-8 -*-

import os
import sys
import tempfile

import delegator
from jinja2 import Template

from .execlass import ExeClass


class Client(ExeClass):
    """ Class for the GDB client that calls the flash functions
    """
    
    def __init__(self, config=None):
        
        # Call the super's init.
        super().__init__()
        # Generate a temporary file to feed to gdb.
        _, self.cmd_file = tempfile.mkstemp(suffix=".txt", prefix="gdb_")
   
    @property
    def executable(self):
        """ Executable path
        """
        return os.path.join(self.config["S32"]["ROOT"],
                            "Cross_Tools", 
                            self.config["CLIENT"]["PLATFORM"],
                            "bin",
                            self.config["CLIENT"]["EXE"])
        
    @property
    def cmd(self):
        """ Command list to run
        """
        return [self.executable,
                "--nx",
                "--command={}".format(self.cmd_file)]
        
    @property
    def template(self):
        """ Jinja2 template class
        """
        return Template(self.template_str)
        
    @property
    def template_str(self):
        """ String of the gdb command template.
        """
        return """target remote 127.0.0.1:{{ port }}

monitor startmultiload

{%- for elf in elfs %}
load "{{ elf }}"
{%- endfor %}

monitor endmultiload
monitor _reset
quit"""

    def render(self, elfs):
        """ Render the Jinja2 template to the temp file
        """
        # Escape filenames for windows.
        if sys.platform == "win32":
            elfs = [elf.replace("\\", "\\\\") for elf in elfs]
        with open(self.cmd_file, "w") as fid:
            print(self.template.render(port=self.config["SERVER"]["SERVERPORT"], 
                                       elfs=elfs),
                                       file=fid)
        

    def flash(self, elfs):
        """ 
        """
        self.render(elfs)
        print("Waiting for GDB client to flash ...", end="")
        self.process = delegator.run(self.cmd, block=True)
        print("... Done")
        print(self.process.err)

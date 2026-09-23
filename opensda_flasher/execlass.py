"""Base class for executables."""

from __future__ import annotations

from abc import ABC, abstractmethod
from configparser import ConfigParser
from subprocess import Popen

from opensda_flasher.config import read_config
from opensda_flasher.processutil import terminate_popen


class ExeClass(ABC):
    """Base class for Server and Client exe classes."""

    def __init__(self, config: ConfigParser | None = None) -> None:
        self.config = read_config() if config is None else config
        self.process: Popen[str] | None = None

    def __del__(self) -> None:
        if self.process is not None:
            try:
                terminate_popen(self.process)
            except Exception:
                pass

    @property
    @abstractmethod
    def executable(self) -> str:
        """Resolved executable path."""

    @property
    @abstractmethod
    def cmd(self) -> list[str]:
        """Argv used to launch the executable."""

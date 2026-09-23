"""PEMicro pegdbserver process control."""

from __future__ import annotations

import queue
import threading
import time
from configparser import ConfigParser
from pathlib import Path
from subprocess import PIPE, Popen

from opensda_flasher.commands import (
    DEFAULT_CORENUM,
    DEFAULT_DEVICE,
    DEFAULT_INTERFACE,
    DEFAULT_PORT,
    DEFAULT_SERVERPORT,
    DEFAULT_SPEED,
    SERVER_BASENAME,
    SERVER_READY,
    server_devicelist_argv,
    server_showhardware_argv,
    server_start_argv,
)
from opensda_flasher.config import cfg_get, resolve_server
from opensda_flasher.execlass import ExeClass
from opensda_flasher.processutil import kill_by_basename, terminate_popen


class ServerLaunchError(Exception):
    """pegdbserver exited before it was ready."""


class Server(ExeClass):
    """Debug server class."""

    def __init__(self, config: ConfigParser | None = None, executable: str | Path | None = None) -> None:
        super().__init__(config)
        self._executable_override = executable
        self.lines: queue.Queue[str] = queue.Queue()

    @property
    def executable(self) -> str:
        """Path to server executable."""
        return resolve_server(self.config, self._executable_override)

    @property
    def cmd(self) -> list[str]:
        """Official flash/debug server argv."""
        return server_start_argv(
            self.executable,
            device=cfg_get(self.config, "SERVER", "device", DEFAULT_DEVICE),
            interface=cfg_get(self.config, "SERVER", "interface", DEFAULT_INTERFACE),
            port=cfg_get(self.config, "SERVER", "port", DEFAULT_PORT),
            speed=cfg_get(self.config, "SERVER", "speed", DEFAULT_SPEED),
            serverport=cfg_get(self.config, "SERVER", "serverport", DEFAULT_SERVERPORT),
            corenum=cfg_get(self.config, "SERVER", "corenum", DEFAULT_CORENUM),
        )

    def ports(self) -> str:
        """Print available ports via official -showhardware."""
        return self._run_query(server_showhardware_argv(self.executable)).split("Done.")[-1].strip()

    def devices(self) -> str:
        """Print valid device names via official -devicelist."""
        return self._run_query(server_devicelist_argv(self.executable)).strip()

    def _run_query(self, argv: list[str]) -> str:
        process = Popen(argv, stdout=PIPE, stderr=PIPE, text=True)
        self.process = process
        stdout, stderr = process.communicate()
        return stdout or stderr or ""

    def kill(self) -> None:
        """Kill the owned server and leftover pegdbserver processes."""
        terminate_popen(self.process)
        names = {SERVER_BASENAME, f"{SERVER_BASENAME}.exe"}
        try:
            names.add(self.executable)
        except Exception:
            pass
        kill_by_basename(names)
        self.process = None

    def launch(self) -> None:
        """Launch debug server and wait for the official ready message."""
        self.lines = queue.Queue()
        self.process = Popen(self.cmd, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)
        print("Starting server...", flush=True)
        try:
            self._wait_ready()
        except ServerLaunchError:
            terminate_popen(self.process)
            raise
        for stream in (self.process.stdout, self.process.stderr):
            if stream is not None:
                threading.Thread(target=self._pump, args=(stream,), daemon=True).start()
        print("Server ready.", flush=True)

    def _pump(self, stream) -> None:
        """Keep reading server output so the pipe cannot stall programming."""
        for line in stream:
            self.lines.put(line)

    def _wait_ready(self, timeout: float = 60) -> None:
        if self.process is None or self.process.stdout is None:
            raise ServerLaunchError("Server process has no stdout to monitor.")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                rest_out, rest_err = self.process.communicate()
                raise ServerLaunchError(
                    f"Server exited immediately. Is another {self.executable} instance running?"
                    + (f"\n{rest_out or rest_err}" if (rest_out or rest_err) else "")
                )
            line = self.process.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            if SERVER_READY in line:
                return
        raise ServerLaunchError(f"Timed out waiting for {SERVER_READY} from {self.executable}")

"""OpenSDA GDB client."""

from __future__ import annotations

import os
import queue
import sys
import tempfile
import threading
import time
from collections.abc import Sequence
from configparser import ConfigParser
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired

from opensda_flasher.commands import DEFAULT_CORENUM, DEFAULT_SERVERPORT, gdb_client_argv, render_gdb_script
from opensda_flasher.config import cfg_get, resolve_gdb
from opensda_flasher.execlass import ExeClass
from opensda_flasher.processutil import terminate_popen
from opensda_flasher.progress import FlashProgress


class FlashError(Exception):
    """GDB flash or verify failed."""


class Client(ExeClass):
    """GDB client that programs ELF images through pegdbserver."""

    def __init__(self, config: ConfigParser | None = None, executable: str | Path | None = None) -> None:
        super().__init__(config)
        _, cmd_file = tempfile.mkstemp(suffix=".txt", prefix="gdb_")
        self.cmd_file = Path(cmd_file)
        self.debug = False
        self._executable_override = executable

    @property
    def executable(self) -> str:
        """Path to client executable."""
        return resolve_gdb(self.config, self._executable_override)

    @property
    def cmd(self) -> list[str]:
        """Official GDB client argv plus the rendered command file."""
        return gdb_client_argv(self.executable, str(self.cmd_file))

    def render(self, elfs: Sequence[str]) -> None:
        """Render the official S32DS GDB sequence to the temp file."""
        rendered_elfs = [elf.replace("\\", "\\\\") for elf in elfs] if sys.platform == "win32" else list(elfs)
        script = render_gdb_script(
            rendered_elfs,
            port=cfg_get(self.config, "SERVER", "serverport", DEFAULT_SERVERPORT),
            corenum=cfg_get(self.config, "SERVER", "corenum", DEFAULT_CORENUM),
            debug=self.debug,
        )
        text = script if script.endswith(os.linesep) else f"{script}{os.linesep}"
        self.cmd_file.write_text(text, encoding="utf-8")

    def flash(self, elfs: Sequence[str], server_lines: queue.Queue[str] | None = None) -> None:
        """Run the flash or debug GDB session."""
        elf_list = list(elfs)
        self.render(elf_list)
        progress = FlashProgress(elf_list, debug=self.debug)
        self.process = Popen(self.cmd, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)
        transcript: list[str] = []
        finished = False
        try:
            if self.debug:
                print("Press ^C to exit.", flush=True)
                self._stream(progress, transcript, timeout=None, server_lines=server_lines)
            else:
                self._stream(progress, transcript, timeout=120, server_lines=server_lines)
                finished = True
        except KeyboardInterrupt:
            terminate_popen(self.process)
        finally:
            _drain_server(server_lines, progress)
            progress.finish(verdict=finished)
            terminate_popen(self.process)
        if self.debug or not finished:
            return
        problems = list(progress.errors)
        returncode = self.process.returncode if self.process is not None else None
        if returncode not in (0, None):
            problems.append(f"GDB exited with status {returncode}.")
        if not progress.saw_reset:
            problems.append("Target was not reset after flashing.")
        if problems:
            tail = "".join(transcript[-40:])
            detail = "\n".join(dict.fromkeys(problems))
            if tail.strip():
                detail = f"{detail}\n{tail.rstrip()}"
            raise FlashError(detail)
        print("Done.", flush=True)

    def _stream(
        self,
        progress: FlashProgress,
        transcript: list[str],
        timeout: float | None,
        server_lines: queue.Queue[str] | None = None,
    ) -> None:
        if self.process is None or self.process.stdout is None or self.process.stderr is None:
            raise FlashError("GDB process has no output pipes.")
        lines: queue.Queue[str | None] = queue.Queue()

        def _pump(stream) -> None:
            try:
                for line in stream:
                    lines.put(line)
            finally:
                lines.put(None)

        threading.Thread(target=_pump, args=(self.process.stdout,), daemon=True).start()
        threading.Thread(target=_pump, args=(self.process.stderr,), daemon=True).start()
        finished = 0
        deadline = None if timeout is None else time.monotonic() + timeout
        while finished < 2:
            remaining = None if deadline is None else deadline - time.monotonic()
            if remaining is not None and remaining <= 0:
                terminate_popen(self.process)
                raise TimeoutExpired(self.cmd, timeout or 0)
            try:
                item = lines.get(timeout=0.2 if remaining is None else min(0.2, remaining))
            except queue.Empty:
                _drain_server(server_lines, progress)
                continue
            if item is None:
                finished += 1
                continue
            _drain_server(server_lines, progress)
            transcript.append(item)
            progress.handle(item)


def _drain_server(server_lines: queue.Queue[str] | None, progress: FlashProgress) -> None:
    if server_lines is None:
        return
    while True:
        try:
            progress.handle_server(server_lines.get_nowait())
        except queue.Empty:
            return

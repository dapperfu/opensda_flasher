"""Cross-platform process helpers. Does not call taskkill."""

from __future__ import annotations

import os
import signal
import sys
import time
from collections.abc import Iterable
from pathlib import Path
from subprocess import Popen
from typing import Any


def terminate_popen(process: Popen[str] | None, timeout: float = 5) -> None:
    """Terminate a subprocess.Popen if it is still running."""
    if process is None or process.poll() is not None:
        return
    process.terminate()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return
        time.sleep(0.05)
    process.kill()


def kill_by_basename(basenames: Iterable[str]) -> None:
    """Terminate leftover processes whose comm/exe basename matches."""
    names = {Path(name).name for name in basenames if name}
    if not names:
        return
    if os.name == "nt":
        _kill_windows(names)
    else:
        _kill_posix(names)


def _kill_posix(names: set[str]) -> None:
    proc = Path("/proc")
    if not proc.is_dir():
        return
    my_pid = os.getpid()
    for _ in range(2):
        sig = signal.SIGTERM if _ == 0 else signal.SIGKILL
        for entry in proc.iterdir():
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid == my_pid:
                continue
            if _posix_basename(entry) in names:
                _signal_pid(pid, sig)
        if sig is signal.SIGTERM:
            time.sleep(0.15)


def _posix_basename(proc_dir: Path) -> str:
    try:
        comm = (proc_dir / "comm").read_text().strip()
        if comm:
            return comm
    except OSError:
        pass
    try:
        return Path(os.readlink(proc_dir / "exe")).name
    except OSError:
        return ""


def _signal_pid(pid: int, sig: signal.Signals) -> None:
    try:
        os.kill(pid, sig)
    except OSError:
        pass


def _kill_windows(names: set[str]) -> None:
    """Terminate matching processes via the Toolhelp snapshot API."""
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    th32cs_snapprocess = 0x00000002
    process_terminate = 0x0001
    invalid_handle = wintypes.HANDLE(-1).value

    class ProcessEntry32(ctypes.Structure):
        _fields_: list[tuple[str, Any]] = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.CHAR * 260),
        ]

    snapshot = kernel32.CreateToolhelp32Snapshot(th32cs_snapprocess, 0)
    if snapshot == invalid_handle:
        return
    try:
        entry = ProcessEntry32()
        entry.dwSize = ctypes.sizeof(ProcessEntry32)
        if not kernel32.Process32First(snapshot, ctypes.byref(entry)):
            return
        my_pid = os.getpid()
        while True:
            exe = entry.szExeFile.split(b"\x00", 1)[0].decode(sys.getfilesystemencoding(), "replace")
            if entry.th32ProcessID != my_pid and Path(exe).name in names:
                handle = kernel32.OpenProcess(process_terminate, False, entry.th32ProcessID)
                if handle:
                    kernel32.TerminateProcess(handle, 1)
                    kernel32.CloseHandle(handle)
            if not kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                break
    finally:
        kernel32.CloseHandle(snapshot)

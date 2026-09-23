"""Zip the PEMicro server, flash algorithms, and GDB for distribution."""

from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

from opensda_flasher import __version__

_SERVER_NAMES = ("pegdbserver_power_console", "pegdbserver_power_console.exe")
_HOSTS = (("linux", "lin"), ("windows", "win32"))


def build_tools_zip(output: Path, server_exe: str | Path, gdb_exe: str | Path) -> Path:
    """Write a zip containing the server tree and GDB client."""
    server = Path(server_exe).resolve()
    gdb = Path(gdb_exe).resolve()
    if not server.is_file():
        raise FileNotFoundError(server)
    if not gdb.is_file():
        raise FileNotFoundError(gdb)
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.parent / f".{output.stem}.staging"
    if staging.exists():
        shutil.rmtree(staging)
    try:
        hosts = _stage_hosts(staging, server, gdb)
        readme = staging / "README.txt"
        readme.write_text(_readme(hosts), encoding="utf-8")
        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(staging).as_posix())
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return output


def _stage_hosts(staging: Path, server: Path, gdb: Path) -> list[str]:
    hosts = _host_dirs(server)
    names: list[str] = []
    current = "windows" if os.name == "nt" else "linux"
    for label, directory in hosts:
        dest = staging / label
        _copy_server_tree(directory, dest)
        if label == current:
            _copy_gdb(gdb, dest)
        names.append(label)
    return names


def _host_dirs(server: Path) -> list[tuple[str, Path]]:
    plugin = server.parent.parent
    found: list[tuple[str, Path]] = []
    for label, folder in _HOSTS:
        host = plugin / folder
        if host.is_dir() and any((host / name).is_file() for name in _SERVER_NAMES):
            found.append((label, host))
    if found:
        return found
    label = "windows" if os.name == "nt" else "linux"
    return [(label, server.parent)]


def _copy_server_tree(source: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in _SERVER_NAMES:
        exe = source / name
        if exe.is_file():
            shutil.copy2(exe, dest / name)
    version = source / "build_version.txt"
    if version.is_file():
        shutil.copy2(version, dest / version.name)
    gdi = source / "gdi"
    if gdi.exists():
        shutil.copytree(gdi, dest / "gdi", symlinks=False)


def _copy_gdb(gdb: Path, dest: Path) -> None:
    """Copy GDB and the libraries named by its $ORIGIN/../linux_support rpath."""
    support = gdb.resolve().parent.parent / "linux_support"
    if not support.is_dir():
        shutil.copy2(gdb, dest / gdb.name)
        return
    bindir = dest / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(gdb, bindir / gdb.name)
    shutil.copytree(support, dest / "linux_support", symlinks=False, dirs_exist_ok=True)
    wrapper = dest / gdb.name
    wrapper.write_text(
        "#!/bin/sh\n"
        'root=$(CDPATH= cd -- "$(dirname "$0")" && pwd)\n'
        'exec "$root/bin/$(basename "$0")" "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)


def _readme(hosts: list[str]) -> str:
    lines = [
        "OpenSDA flasher tools",
        f"opensda_flasher {__version__}",
        "",
        "Binaries from S32 Design Studio for Power Architecture 2.1,",
        "PEMicro plugin com.pemicro.debug.gdbjtag.ppc_1.8.7.201906071634.",
        "pegdbserver_power_console and powerpc-eabivle-gdb are NXP / P&E",
        "programs. Redistribute this zip only if that license allows it.",
        "",
        "Install the Python tool, unzip this archive, then flash:",
        "",
    ]
    if "linux" in hosts:
        lines.extend(
            [
                "Linux:",
                "  osf --sd32 <unzipped>/linux --gdb <unzipped>/linux flash firmware.elf",
                "",
            ]
        )
    if "windows" in hosts:
        lines.extend(
            [
                "Windows:",
                "  The PEMicro server and gdi algorithms are in windows\\.",
                "  If powerpc-eabivle-gdb.exe is not in that directory, copy it",
                "  from an S32DS Windows install, then:",
                "  osf --sd32 <unzipped>\\windows --gdb <unzipped>\\windows flash firmware.elf",
                "",
            ]
        )
    return "\n".join(lines)

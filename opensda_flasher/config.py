"""Configuration loading and PEMicro / GDB executable discovery."""

from __future__ import annotations

import os
from configparser import ConfigParser, ExtendedInterpolation
from importlib.resources import files
from pathlib import Path
from shutil import which

from opensda_flasher.commands import GDB_BASENAME, SERVER_BASENAME


class ToolNotFound(Exception):
    """A required PEMicro or GDB executable could not be resolved."""


def read_config(local_config: str | Path | None = None) -> ConfigParser:
    """Read packaged, home, and local configuration files."""
    default_config = files("opensda_flasher").joinpath("opensda_flasher.ini")
    home_config = Path.home() / ".opensda_flasher.ini"
    paths: list[str] = [str(default_config), str(home_config)]
    if local_config:
        paths.append(str(local_config))
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(paths)
    return config


def cfg_get(config: ConfigParser | None, section: str, key: str, default: str = "") -> str:
    """Return a stripped config value or default if missing/empty."""
    if config is None or section not in config or key not in config[section]:
        return default
    value = config[section][key].strip()
    return value or default


def platform_basenames(name: str) -> list[str]:
    """Return basename candidates for the current host."""
    base = Path(name).name
    if not base:
        return []
    names = [base, base[:-4] if base.endswith(".exe") else f"{base}.exe"]
    if os.name == "nt":
        preferred = [n for n in names if n.endswith(".exe")]
        return preferred + [n for n in names if n not in preferred]
    preferred = [n for n in names if not n.endswith(".exe")]
    return preferred + [n for n in names if n not in preferred]


def resolve_explicit(path: str | Path, basenames: list[str], label: str, flag: str) -> str:
    """Resolve a CLI or INI path that is a file or a directory."""
    resolved = Path(path).expanduser().resolve()
    if resolved.is_file():
        return str(resolved)
    if resolved.is_dir():
        for name in basenames:
            candidate = resolved / name
            if candidate.is_file():
                return str(candidate)
    raise ToolNotFound(f"{label} not found at {resolved}. Pass {flag} or install it on PATH.")


def resolve_on_path(basenames: list[str], label: str, flag: str) -> str:
    """Resolve a tool via PATH."""
    for name in basenames:
        found = which(name)
        if found:
            return found
    shown = basenames[0] if basenames else label
    raise ToolNotFound(f"{label} ({shown}) is not on PATH. Pass {flag} or add it to PATH.")


def resolve_tool(
    cli_path: str | Path | None,
    configured_path: str,
    configured_exe: str,
    default_basename: str,
    label: str,
    flag: str,
) -> str:
    """Resolve an executable: CLI path, INI path, then PATH."""
    basenames = platform_basenames(configured_exe or default_basename)
    if cli_path:
        return resolve_explicit(cli_path, basenames, label, flag)
    if configured_path:
        return resolve_explicit(configured_path, basenames, label, flag)
    return resolve_on_path(basenames, label, flag)


def resolve_server(config: ConfigParser | None, cli_path: str | Path | None = None) -> str:
    """Resolve pegdbserver_power_console."""
    return resolve_tool(
        cli_path,
        cfg_get(config, "SERVER", "path"),
        cfg_get(config, "SERVER", "exe", SERVER_BASENAME),
        SERVER_BASENAME,
        "pegdbserver_power_console",
        "--sd32",
    )


def resolve_gdb(config: ConfigParser | None, cli_path: str | Path | None = None) -> str:
    """Resolve powerpc-eabivle-gdb."""
    return resolve_tool(
        cli_path,
        cfg_get(config, "CLIENT", "path"),
        cfg_get(config, "CLIENT", "exe", GDB_BASENAME),
        GDB_BASENAME,
        "powerpc-eabivle-gdb",
        "--gdb",
    )

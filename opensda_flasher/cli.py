"""Click command-line interface."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from subprocess import TimeoutExpired
from typing import TypeVar

import click

from opensda_flasher import __version__
from opensda_flasher.bundle import build_tools_zip
from opensda_flasher.client import Client, FlashError
from opensda_flasher.config import ToolNotFound, read_config, resolve_gdb, resolve_server
from opensda_flasher.progress import parse_boards
from opensda_flasher.server import Server, ServerLaunchError

T = TypeVar("T")


def _click_call(func: Callable[..., T], *args: object, **kwargs: object) -> T:
    try:
        return func(*args, **kwargs)
    except (ToolNotFound, ServerLaunchError, TimeoutExpired, FlashError) as exc:
        raise click.ClickException(str(exc)) from exc


def _resolve_elfs(ctx: click.Context, elfs: Sequence[str]) -> list[str]:
    config = ctx.obj["config_obj"]
    if elfs:
        return [str(Path(elf).resolve()) for elf in elfs]
    flash = config["FLASH"] if "FLASH" in config else {}
    values = [value for value in flash.values() if value]
    if not values:
        raise click.UsageError("No elf(s) specified in call or config file")
    config_dir = Path(ctx.obj["config"]).parent if ctx.obj["config"] else Path.cwd()
    resolved: list[str] = []
    for elf in values:
        path = Path(elf)
        resolved.append(str(path if path.is_absolute() else (config_dir / path).resolve()))
    return resolved


def _server(ctx: click.Context) -> Server:
    return Server(ctx.obj["config_obj"], executable=ctx.obj["sd32"])


def _client(ctx: click.Context) -> Client:
    return Client(ctx.obj["config_obj"], executable=ctx.obj["gdb"])


@click.group(invoke_without_command=False, no_args_is_help=True)
@click.pass_context
@click.option(
    "-c",
    "--config",
    type=click.Path(path_type=Path),
    default=Path("osf.ini"),
    show_default=True,
    help="Configuration file",
)
@click.option(
    "--sd32",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to pegdbserver_power_console, or a directory that contains it. If omitted, the tool is taken from PATH.",
)
@click.option(
    "--gdb",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to powerpc-eabivle-gdb, or a directory that contains it. If omitted, the tool is taken from PATH.",
)
def main(ctx: click.Context, config: Path, sd32: Path | None, gdb: Path | None) -> None:
    """opensda_flasher.
    A tool to programmatically flash NXP DEVKIT-MPC57xx boards.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config.resolve()
    ctx.obj["config_obj"] = read_config(config)
    ctx.obj["sd32"] = sd32
    ctx.obj["gdb"] = gdb
    if sd32:
        if "SERVER" not in ctx.obj["config_obj"]:
            ctx.obj["config_obj"]["SERVER"] = {}
        ctx.obj["config_obj"]["SERVER"]["path"] = str(sd32.resolve())
    if gdb:
        if "CLIENT" not in ctx.obj["config_obj"]:
            ctx.obj["config_obj"]["CLIENT"] = {}
        ctx.obj["config_obj"]["CLIENT"]["path"] = str(gdb.resolve())


@main.command("flash")
@click.pass_context
@click.argument("elfs", nargs=-1, type=click.Path(exists=True, path_type=Path))
def flash(ctx: click.Context, elfs: tuple[Path, ...]) -> None:
    """Flash specified ELF files."""
    resolved = _resolve_elfs(ctx, [str(elf) for elf in elfs])
    server = _server(ctx)
    boards = parse_boards(_click_call(server.ports))
    if not boards:
        raise click.ClickException("No OpenSDA board found. Check the USB connection.")
    for board in boards:
        click.echo(f"Found board: {board}")
    _click_call(server.launch)
    try:
        client = _client(ctx)
        client.debug = False
        _click_call(client.flash, resolved, server.lines)
    finally:
        server.kill()


@main.command("debug")
@click.pass_context
@click.argument("elfs", nargs=-1, type=click.Path(exists=True, path_type=Path))
def debug(ctx: click.Context, elfs: tuple[Path, ...]) -> None:
    """Debug specified ELF files in RAM."""
    resolved = _resolve_elfs(ctx, [str(elf) for elf in elfs])
    server = _server(ctx)
    _click_call(server.launch)
    try:
        client = _client(ctx)
        client.debug = True
        _click_call(client.flash, resolved)
    finally:
        server.kill()


@main.command("ports")
@click.pass_context
def ports(ctx: click.Context) -> None:
    """Show ports found by gdbserver."""
    click.echo(_click_call(_server(ctx).ports))


@main.command("devices")
@click.pass_context
def devices(ctx: click.Context) -> None:
    """Show devices reported by gdbserver."""
    click.echo(_click_call(_server(ctx).devices))


@main.command("kill")
@click.pass_context
def kill(ctx: click.Context) -> None:
    """Kill existing running servers."""
    click.echo("Killing ...", nl=False)
    _server(ctx).kill()
    click.echo("... Done")


@main.command("package")
@click.pass_context
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Zip file to write. Default: dist/opensda-flasher-tools-<version>.zip",
)
def package(ctx: click.Context, output: Path | None) -> None:
    """Zip pegdbserver, GDB, and flash algorithms for distribution."""
    config = ctx.obj["config_obj"]
    server_exe = _click_call(resolve_server, config, ctx.obj["sd32"])
    gdb_exe = _click_call(resolve_gdb, config, ctx.obj["gdb"])
    dest = output or Path("dist") / f"opensda-flasher-tools-{__version__}.zip"
    try:
        written = build_tools_zip(dest, server_exe, gdb_exe)
    except OSError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Wrote {written}")


@main.command("init")
@click.pass_context
@click.argument("elfs", nargs=-1, type=click.Path(exists=True, path_type=Path))
def init(ctx: click.Context, elfs: tuple[Path, ...]) -> None:
    """Initialize an empty config file."""
    config = ctx.obj["config_obj"]
    if elfs:
        config["FLASH"] = {}
        for idx, elf in enumerate(elfs):
            click.echo(f"Adding elf {elf} to ini.")
            config["FLASH"][f"elf{idx}"] = str(elf)
    if ctx.obj["sd32"]:
        if "SERVER" not in config:
            config["SERVER"] = {}
        config["SERVER"]["path"] = str(Path(ctx.obj["sd32"]).resolve())
    if ctx.obj["gdb"]:
        if "CLIENT" not in config:
            config["CLIENT"] = {}
        config["CLIENT"]["path"] = str(Path(ctx.obj["gdb"]).resolve())
    with Path(ctx.obj["config"]).open("w", encoding="utf-8") as fid:
        config.write(fid)

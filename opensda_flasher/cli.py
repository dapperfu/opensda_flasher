"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will
  cause problems: the code will get executed twice:

  - When you run `python -mnameless` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``nameless.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``nameless.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os

import click

from .client import Client
from .config import read_config
from .server import Server


@click.group(invoke_without_command=False, no_args_is_help=True)
@click.pass_context
@click.option(
    '-c',
    '--config',
    nargs=1,
    help="Configuration File",
    default="osf.ini")
def main(ctx, **kw_args): # noqa
    """opensda_flasher.
    A tool to programatically flash NXP DEVKIT-MPC57xx boards.
    """
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj["config"] = os.path.abspath(kw_args["config"])
    # Read the configuration file into a config object.
    ctx.obj["config_obj"] = read_config(kw_args["config"])


@main.command("flash")
@click.pass_context
@click.argument('elfs', nargs=-1, type=click.Path(exists=True))
def flash(ctx, **kw_args):
    """Flash specified ELF files."""
    # Get the config parser object.
    config = ctx.obj["config_obj"]

    if len(kw_args["elfs"]) == 0 and \
       ("FLASH" not in config or len(config["FLASH"].values()) == 0):
        raise(Exception("No elf(s) specified in call or config file"))

    if len(kw_args["elfs"]) > 0:
        elfs = kw_args["elfs"]
    elif len(config["FLASH"].values()) > 0:
        elfs = list(config["FLASH"].values())
    else:
        raise(Exception("No elf(s) specified in call or config file"))

    if ctx.obj["config"] is None:
        config_dir = os.path.abspath(os.curdir)
    else:
        config_dir = os.path.dirname(ctx.obj["config"])
    # Convert path to absolute relative to the config file.
    elfs = [os.path.join(config_dir, elf) for elf in elfs]

    s = Server(config)
    s.launch()

    c = Client(config)
    c.debug = False
    c.flash(elfs)

    s.kill()


@main.command("debug")
@click.pass_context
@click.argument('elfs', nargs=-1, type=click.Path(exists=True))
def debug(ctx, **kw_args):
    """Debug specified ELF files in RAM."""
    # Get the config parser object.
    config = ctx.obj["config_obj"]

    if len(kw_args["elfs"]) == 0 and \
       ("FLASH" not in config or len(config["FLASH"].values()) == 0):
        raise(Exception("No elf(s) specified in call or config file"))

    if len(kw_args["elfs"]) > 0:
        elfs = kw_args["elfs"]
    elif len(config["FLASH"].values()) > 0:
        elfs = list(config["FLASH"].values())
    else:
        raise(Exception("No elf(s) specified in call or config file"))

    if ctx.obj["config"] is None:
        config_dir = os.path.abspath(os.curdir)
    else:
        config_dir = os.path.dirname(ctx.obj["config"])
    # Convert path to absolute relative to the config file.
    elfs = [os.path.join(config_dir, elf) for elf in elfs]

    s = Server(config)
    s.launch()

    c = Client(config)
    c.debug = True
    c.flash(elfs)

    s.kill()

@main.command("ports")
@click.pass_context
def ports(ctx, *args, **kw_args):    
    """Kill existing running servers."""
    # Get the config parser object.
    config = ctx.obj["config_obj"]
    s = Server(config)
    print("Killing ...", end="")
    s.kill()
    print("... Done")

@main.command("kill")
@click.pass_context
def kill(ctx, *args, **kw_args):
    """Kill existing running servers."""
    # Get the config parser object.
    config = ctx.obj["config_obj"]
    s = Server(config)
    print("Killing ...", end="")
    s.kill()
    print("... Done")


@main.command('init')
@click.pass_context
@click.argument('elfs', nargs=-1, type=click.Path(exists=True))
def init(ctx, *args, **kw_args):
    """Initialize an empty config file."""
    # Get the config parser object.
    config = ctx.obj["config_obj"]

    # If elf(s) are passed in.
    if len(kw_args["elfs"]) > 0:
        # Add a flash section if it doesn't exist,
        # empty it if it does.
        config["FLASH"] = dict()
        # Loop through each of the given ELF files and add them to the flash
        # section.
        for idx, elf in enumerate(kw_args["elfs"]):
            print("Adding elf {} to ini.".format(elf))
            # The config key is unimportant, just the values.
            config["FLASH"]["elf{}".format(idx)] = elf
    # Write the config.
    with open(ctx.obj["config"], "w") as fid:
        config.write(fid)

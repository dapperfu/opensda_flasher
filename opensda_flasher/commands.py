"""Official PEMicro / S32DS 2.1 command construction.

Argument names and GDB monitor commands are taken from:

- pegdbserver_power_console -help (PEMicro GDB Server for Power 7.34.00.00)
- com.pemicro.debug.gdbjtag.ppc_1.8.7.201906071634 TabDebugger.class
  (getGdbServerCommandLineArray / getGdbClientCommandLineArray)
- ConfigurationAttributes.class and FinalLaunchSequence.class
- S32DS OpenSDA .launch files (gdbClientOtherCommands, otherRunCommands)

This module does not reconstruct argv from Windows Task Manager captures.
It does not invent -pcpfile; device-name selection is the official default.
"""

from __future__ import annotations

from collections.abc import Sequence

# Official PEMicro hardware interface token for OpenSDA (TabDebugger / HwInterface).
INTERFACE_OPENSDA = "OPENSDA"

# Ready string printed by pegdbserver after -startserver (Backend$GdbServerStep).
SERVER_READY = "All Servers Running"

# Official GDB client flags from TabDebugger.getGdbClientCommandLineArray
# and messages.properties ("mandatory '--interpreter=mi2 --nx'").
GDB_CLIENT_FLAGS = ("--interpreter=mi2", "--nx")

DEFAULT_DEVICE = "MPC5744P"
DEFAULT_INTERFACE = INTERFACE_OPENSDA
DEFAULT_PORT = "USB1"
DEFAULT_SPEED = "5000"
DEFAULT_SERVERPORT = "7224"
DEFAULT_CORENUM = "0"

SERVER_BASENAME = "pegdbserver_power_console"
GDB_BASENAME = "powerpc-eabivle-gdb"


def server_start_argv(
    executable: str,
    device: str = DEFAULT_DEVICE,
    interface: str = DEFAULT_INTERFACE,
    port: str = DEFAULT_PORT,
    speed: str = DEFAULT_SPEED,
    serverport: str = DEFAULT_SERVERPORT,
    corenum: str = DEFAULT_CORENUM,
) -> list[str]:
    """Argv to start pegdbserver for a GDB flash/debug session.

    Flag order follows TabDebugger.getGdbServerCommandLineArray, plus
    official -corenum from pegdbserver -help (default core 0).
    """
    return [
        executable,
        f"-device={device}",
        "-startserver",
        "-singlesession",
        f"-serverport={serverport}",
        f"-interface={interface}",
        f"-speed={speed}",
        f"-port={port}",
        f"-corenum={corenum}",
    ]


def server_showhardware_argv(executable: str) -> list[str]:
    """Argv for official -showhardware (ports command)."""
    return [executable, "-showhardware"]


def server_devicelist_argv(executable: str) -> list[str]:
    """Argv for official -devicelist (devices command)."""
    return [executable, "-devicelist"]


def gdb_client_argv(executable: str, command_file: str) -> list[str]:
    """Argv for official PEMicro GDB client launch plus a command file."""
    return [executable, *GDB_CLIENT_FLAGS, f"--command={command_file}"]


def render_gdb_script(
    elfs: Sequence[str],
    port: str = DEFAULT_SERVERPORT,
    corenum: str = DEFAULT_CORENUM,
    debug: bool = False,
) -> str:
    """Render the S32DS launch-file GDB command sequence."""
    loads = "\n".join(f'load "{elf}"' for elf in elfs)
    tail = "continue" if debug else "monitor _reset\nquit"
    return (
        "set mem inaccessible-by-default off\n"
        "set tcp auto-retry on\n"
        "set tcp connect-timeout 240\n"
        "set remotetimeout 60\n"
        f"target remote localhost:{port}\n"
        "monitor preserve1 0\n"
        f"monitor selectcore {corenum}\n"
        "set architecture powerpc:vle\n"
        f"{loads}\n"
        f"{tail}\n"
    )

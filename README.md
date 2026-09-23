# OpenSDA Flasher

## Summary

`osf` flashes NXP DEVKIT-MPC57xx boards over OpenSDA from the command line. It
drives PEMicro `pegdbserver_power_console` and `powerpc-eabivle-gdb` using the
S32 Design Studio 2.1 command set.

Put those two tools on `PATH`, or pass `--sd32` and `--gdb`. Python 3.10 or
newer is required.

## Usage

```text
osf --help
osf flash firmware.elf
osf debug firmware.elf
osf ports
osf devices
osf kill
```

If the PEMicro server and GDB are not on `PATH`:

```text
osf --sd32 /opt/S32PA/eclipse/plugins/com.pemicro.debug.gdbjtag.ppc_1.8.7.201906071634/lin \
    --gdb /opt/S32PA/S32DS/build_tools/powerpc-eabivle-4_9/bin \
    flash firmware.elf
```

`--sd32` and `--gdb` accept the executable or the directory that contains it.

Save those paths and an ELF into `osf.ini`, then flash without repeating them:

```text
osf --sd32 /opt/S32PA/eclipse/plugins/com.pemicro.debug.gdbjtag.ppc_1.8.7.201906071634/lin \
    --gdb /opt/S32PA/S32DS/build_tools/powerpc-eabivle-4_9/bin \
    --config osf.ini init firmware.elf
osf --config osf.ini flash
```

`package` zips the server, GDB, and flash algorithms for another machine:

```text
osf --sd32 /path/to/lin --gdb /path/to/bin package
```

If a leftover server is still running, stop it with `osf kill`.

## Installation

### pipx, from Git

```text
pipx install git+https://github.com/dapperfu/opensda_flasher.git
osf --help
```

Upgrade later with:

```text
pipx upgrade opensda-flasher
```

### pip, in a Python environment

```text
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/dapperfu/opensda_flasher.git
osf --help
```

From a local clone:

```text
git clone https://github.com/dapperfu/opensda_flasher.git
cd opensda_flasher
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

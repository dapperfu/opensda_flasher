
# OpenSDA Flasher

A short script to program NXP OpenSDA v1 PPC devices from the command line with Python.

Most of this was discovered through trial and error watching the S32 Design Studio debug messages fly by. If you have any problems [open an issue](https://github.com/jed-frey/opensda_flasher/issues).

Tested on:

- [DEVKIT-MPC5744P](https://www.nxp.com/products/microcontrollers-and-processors/power-architecture-processors/mpc5xxx-55xx-32-bit-mcus/ultra-reliable-mpc57xx-32-bit-automotive-industrial-microcontrollers-mcus/development-board-for-mpc5744p:DEVKIT-MPC5744P)
- com.pemicro.debug.gdbjtag.ppc_1.6.9.201706282002 Eclipse Plugin
- Python 3.6 (Should work on all versions).

## Use Cases:

- Continuous integration tests.
- Flashing development boards without having to launch Eclipse.
- Batch flash boards for Educational use without needing an expensive JTAG adapter. (Least expensive PPC JTAG board is \$399. These boards are ~\$35.)

## Installation

Install with pip directly from GitHub:

    pip install git+https://github.com/jed-frey/opensda_flasher.git#egg=opensda_flasher

Clone the repository and install locally:

    git clone https://github.com/jed-frey/opensda_flasher.git
    cd opensda_flasher
    python setup.py install

### Help:

    osf
    Usage: osf [OPTIONS] COMMAND [ARGS]...

      opensda flasher (osf) is a tool to programatically flash NXP DEVKIT-
      MPC57xx boards.

    Options:
      -c, --config TEXT  Configuration File
      --help             Show this message and exit.

    Commands:
      debug  Debug specified ELF files in RAM
      flash  Flash specified ELF files.
      init   Initialize an empty config file.
      kill   Kill existing running servers.

## Examples:

The default configuration assumes S32DS is installed at ```C:\NXP\S32DS_Power_v1.2``` and PEMicro Debug Plugin ```com.pemicro.debug.gdbjtag.ppc_1.6.9.201706282002```. The Eclipse workspace is ```C:\NXP\workspaceS32DS.Power12```

The examples are using the ADC_MPC5744P project which can be created as follows:

S32 Design Studio for Power Architecture > File > New > New S32DS Project From Example > S32DS Example Projects > MPC5744P > ADC_MPC5744P


1. Program an elf to the device flash:

  ```opensda_flasher flash C:\NXP\workspaceS32DS.Power12\ADC_MPC5744P\Debug\ADC_MPC5744P.elf```

2. Program an elf to the device RAM:

  ```opensda_flasher debug C:\NXP\workspaceS32DS.Power12\ADC_MPC5744P\Debug_RAM\ADC_MPC5744P.elf```
 
3. Create a local init. This can be used to customize the settings. By default this is saved to ```osf.ini```

  ```opensda_flasher init```
  
4. Program an elf to the device flash with local config settings. **osf** may be used interchangeably with **opensda_flasher**

  ```osf --config osf.ini flash C:\NXP\workspaceS32DS.Power12\ADC_MPC5744P\Debug\ADC_MPC5744P.elf```
  
5. Create a custom local init. The elf files can also be stored in the init.

  ```osf --config=adc.ini init C:\NXP\workspaceS32DS.Power12\ADC_MPC5744P\Debug\ADC_MPC5744P.elf```
  
  Then use the config to flash the elf.
  
  ```osf --config=adc.ini flash```

If you run osf and receive this error:

    Exception: Server exited immediately. Is another C:\NXP\S32DS_Power_v1.2\eclipse\plugins\com.pemicro.debug.gdbjtag.ppc_1.6.9.201706282002\win32\pegdbserver_power_console.exe instance running?
    
There is probably a gdbserver already running. You can kill existing servers with:

    osf kill

## Programmatic Use

The Python module can also be used programmatically in a Python script.


```python
from opensda_flasher.client import Client
from opensda_flasher.server import Server
from opensda_flasher.config import read_config
```


```python
config = read_config('adc.ini')
```


```python
s = Server(config)
s.launch()
```

    Waiting for GDB servers to complete startup ...... Done
    


```python
c = Client(config)
```


```python
elfs = [r"C:\NXP\workspaceS32DS.Power12\ADC_MPC5744P\Debug\ADC_MPC5744P.elf",]
c.flash(elfs)
```

    DEBUG: C:\Users\C3038028\AppData\Local\Temp\gdb_h0v0fvs5.txt
    Waiting for GDB client to flash ...... Done
    GNU gdb (GDB) 7.8.2
    Copyright (C) 2014 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
    and "show warranty" for details.
    This GDB was configured as "--host=i686-mingw32 --target=powerpc-eabivle".
    Type "show configuration" for configuration details.
    For bug reporting instructions, please see:
    <http://www.gnu.org/software/gdb/bugs/>.
    Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.
    For help, type "help".
    Type "apropos word" to search for commands related to "word".
    0x01000000 in ?? ()
    Command Executed successfully: preserve1 0
    Command Executed successfully: selectcore 0
    The target architecture is assumed to be powerpc:vle
    Loading section .rchw, size 0x4 lma 0xfa0000
    Loading section .cpu0_reset_vector, size 0x4 lma 0xfa0004
    Loading section .startup, size 0x1fe lma 0x1000000
    Loading section .core_exceptions_table, size 0xf4 lma 0x1001000
    Loading section .intc_vector_table, size 0xb78 lma 0x1002000
    Loading section .text, size 0x7d0 lma 0x1002b80
    Loading section .ctors, size 0x8 lma 0x1003350
    Loading section .dtors, size 0x8 lma 0x1003358
    Loading section .eh_frame, size 0x8 lma 0x1003360
    Loading section .data, size 0x4 lma 0x1003368
    Loading section .got2, size 0x1c lma 0x100336c
    Start address 0x1000000, load size 5754
    Transfer rate: 549 bytes/sec, 411 bytes/write.
    Command Executed successfully: _reset
    A debugging session is active.
    
    	Inferior 1 [Remote target] will be detached.
    
    Quit anyway? (y or n) [answered Y; input not from terminal]
    
    


```python
s.kill()
```

# Contributing

Contributions welcome.


```python
# Recursion
!jupyter nbconvert --to=markdown README.ipynb
```

    [NbConvertApp] Converting notebook README.ipynb to markdown
    [NbConvertApp] Writing 6232 bytes to README.md
    


```python

```

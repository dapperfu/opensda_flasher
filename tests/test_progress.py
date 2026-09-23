"""Progress parsing and GDB script checks."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from opensda_flasher.commands import render_gdb_script
from opensda_flasher.progress import FlashProgress, elf_load_size, parse_boards, parse_download

SAMPLE_PORTS = """
Command line arguments: -showhardware
-INTERFACE=OPENSDA        -PORT=51746E56                 ; USB1 : OpenSDA (51746E56)[PortNum=181]
-INTERFACE=OPENSDA        -PORT=USB1                     ; USB1 : OpenSDA (51746E56)[PortNum=181][DUPLICATE]
"""

ELF = Path("Golden_Binaries/ADC_MPC5744P/Debug/ADC_MPC5744P.elf")


def test_parse_boards_skips_duplicates():
    assert parse_boards(SAMPLE_PORTS) == ["USB1 : OpenSDA (51746E56)"]


def test_elf_load_size_matches_download_sections():
    assert elf_load_size(ELF) == 5754


def test_flash_script_is_load_then_reset():
    script = render_gdb_script(["/tmp/app.elf"])
    assert script.index('load "/tmp/app.elf"') < script.index("monitor _reset")
    assert "compare-sections" not in script


def test_debug_script_continues():
    script = render_gdb_script(["/tmp/app.elf"], debug=True)
    assert "compare-sections" not in script
    assert "continue" in script


def test_progress_bar_and_verify():
    progress = FlashProgress(["/tmp/app.elf"])
    progress.expected = 12
    buf = StringIO()
    lines = [
        '@"Command Executed successfully: preserve1 0\\r\\n"',
        '+download,{section=".text",section-size="8",total-size="12"}',
        '+download,{section=".data",section-size="4",total-size="12"}',
        '@"Command Executed successfully: _reset\\r\\n"',
    ]
    with redirect_stdout(buf):
        for line in lines:
            progress.handle(line)
        progress.handle_server("Verifying object file CRC-16 to device ranges ...\n")
        progress.handle_server("Checksum Verification Successful. (Cumulative CRC-16=$79E0)\n")
        progress.finish()
    text = buf.getvalue()
    assert "Connected." in text
    assert "Flashing ..." in text
    assert "Verify flash ... ok" in text
    assert "Resetting target... ok" in text
    assert progress.saw_reset
    assert progress.errors == []
    assert parse_download(lines[1]) == (".text", 8)

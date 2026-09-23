"""Board detection, ELF load size, and live flash progress."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from tqdm import tqdm

_SECTION = re.compile(
    r"^Section\s+(?P<name>\S+),\s+range\s+.+?:\s+(?P<result>matched|MIS-MATCHED)",
    re.IGNORECASE,
)
_MI_STRING = re.compile(r'^[&~@]"(?P<body>.*)"\s*$')
_DOWNLOAD = re.compile(r"\+download,\{(?P<body>[^}]*)\}")
_FIELD = re.compile(r'([\w-]+)="([^"]*)"')
_PORTNUM = re.compile(r"\s*\[PortNum=\d+\]")

_SHT_PROGBITS = 1
_SHF_ALLOC = 0x2


def parse_boards(text: str) -> list[str]:
    """Return hardware descriptions from pegdbserver -showhardware output."""
    boards: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if "[DUPLICATE]" in line or ";" not in line or not line.startswith("-INTERFACE="):
            continue
        desc = _PORTNUM.sub("", line.split(";", 1)[1]).strip()
        if desc and desc not in boards:
            boards.append(desc)
    return boards


def elf_load_size(path: str | Path) -> int:
    """Sum allocated PROGBITS section sizes, which GDB reports as downloads."""
    try:
        data = Path(path).read_bytes()
    except OSError:
        return 0
    if len(data) < 64 or data[:4] != b"\x7fELF":
        return 0
    elf_class = data[4]
    endian = "<" if data[5] == 1 else ">"
    if elf_class == 1:
        e_shoff = struct.unpack_from(endian + "I", data, 32)[0]
        e_shentsize = struct.unpack_from(endian + "H", data, 46)[0]
        e_shnum = struct.unpack_from(endian + "H", data, 48)[0]
    elif elf_class == 2:
        e_shoff = struct.unpack_from(endian + "Q", data, 40)[0]
        e_shentsize = struct.unpack_from(endian + "H", data, 58)[0]
        e_shnum = struct.unpack_from(endian + "H", data, 60)[0]
    else:
        return 0
    if e_shoff <= 0 or e_shnum == 0 or e_shentsize < 40:
        return 0
    total = 0
    for index in range(e_shnum):
        off = e_shoff + index * e_shentsize
        if off + e_shentsize > len(data):
            break
        sh_type = struct.unpack_from(endian + "I", data, off + 4)[0]
        if elf_class == 1:
            sh_flags = struct.unpack_from(endian + "I", data, off + 8)[0]
            sh_size = struct.unpack_from(endian + "I", data, off + 20)[0]
        else:
            sh_flags = struct.unpack_from(endian + "Q", data, off + 8)[0]
            sh_size = struct.unpack_from(endian + "Q", data, off + 32)[0]
        if sh_type == _SHT_PROGBITS and sh_flags & _SHF_ALLOC:
            total += sh_size
    return total


def parse_download(line: str) -> tuple[str, int] | None:
    """Return (section, section_size) from a GDB/MI +download record."""
    match = _DOWNLOAD.search(line.strip())
    if not match:
        return None
    fields = dict(_FIELD.findall(match.group("body")))
    if "section" not in fields or "section-size" not in fields:
        return None
    try:
        size = int(fields["section-size"])
    except ValueError:
        return None
    return fields["section"], size


def mi_text(line: str) -> str | None:
    """Unescape a GDB/MI console, target, or log string record."""
    match = _MI_STRING.match(line.strip())
    if not match:
        return None
    body = match.group("body")
    out: list[str] = []
    index = 0
    while index < len(body):
        if body[index] == "\\" and index + 1 < len(body):
            nxt = body[index + 1]
            out.append({"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"'}.get(nxt, nxt))
            index += 2
            continue
        out.append(body[index])
        index += 1
    return "".join(out)


class FlashProgress:
    """Print flash stages and drive a tqdm bar from GDB/MI output."""

    def __init__(self, elfs: list[str], debug: bool = False) -> None:
        self.elfs = elfs
        self.debug = debug
        self.expected = sum(elf_load_size(elf) for elf in elfs)
        self.errors: list[str] = []
        self.verified: list[tuple[str, bool]] = []
        self.saw_reset = False
        self.server_verified = False
        self._bar: tqdm | None = None
        self._flashing = False
        self._verify_open = False
        self._verdict_printed = False
        self._connected = False

    def handle(self, line: str) -> None:
        """Consume one GDB/MI line."""
        download = parse_download(line)
        if download is not None:
            self._on_download(download[1])
            return
        text = mi_text(line)
        if text:
            self._on_text(text)
            return
        if line.startswith("^error"):
            self.errors.append(line.strip())

    def handle_server(self, line: str) -> None:
        """Consume one pegdbserver stdout line. Verify is the server CRC check."""
        text = line.strip()
        if "Checksum Verification Successful" in text or "Application verified in memory" in text:
            self.server_verified = True
            self._start_verify()
            self._close_verify()
            return
        lowered = text.lower()
        if "verification failed" in lowered or "verify failed" in lowered:
            self._start_verify()
            self.errors.append(text)
            self._close_verify()

    def finish(self, verdict: bool = True) -> None:
        """Close the bar and, when the session finished, emit the verify verdict."""
        self._close_bar()
        if verdict and not self.debug:
            self._close_verify(final=True)
        if self.saw_reset:
            print("Resetting target... ok", flush=True)

    def _on_download(self, size: int) -> None:
        if not self._flashing:
            print("Flashing ...", flush=True)
            self._flashing = True
        if self._bar is None:
            desc = Path(self.elfs[0]).name if len(self.elfs) == 1 else "images"
            self._bar = tqdm(
                total=self.expected or None,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=desc,
                file=sys.stdout,
                leave=True,
                miniters=1,
            )
        self._bar.update(size)
        if self._bar.total is not None and self._bar.n > self._bar.total:
            self._bar.total = self._bar.n

    def _on_text(self, text: str) -> None:
        if "Command Executed successfully: preserve1" in text and not self._connected:
            print("Connected.", flush=True)
            self._connected = True
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            matched = _SECTION.match(line)
            if matched:
                self._start_verify()
                ok = matched.group("result").lower().startswith("matched")
                self.verified.append((matched.group("name"), ok))
                if not ok:
                    self.errors.append(f"{matched.group('name')} mismatched")
                continue
            if "Undefined command" in line and "compare-sections" in line:
                self.errors.append(line)
                self._start_verify()
            if "Error in sourced command file" in line or "cannot be used" in line:
                self.errors.append(line)
            if "Command Executed successfully: _reset" in line:
                self._close_bar()
                self.saw_reset = True

    def _start_verify(self) -> None:
        if self._verify_open or self.debug:
            return
        self._close_bar()
        print("Verify flash ...", end=" ", flush=True)
        self._verify_open = True

    def _close_verify(self, final: bool = False) -> None:
        if self.debug or self._verdict_printed:
            return
        if not self._verify_open:
            if not final:
                return
            print("Verify flash ... failed", flush=True)
            self.errors.append("Verify flash did not run.")
            self._verdict_printed = True
            return
        if self.server_verified and not self.errors:
            print("ok", flush=True)
            self._verdict_printed = True
            return
        print("failed", flush=True)
        if not self.server_verified and not self.errors:
            self.errors.append("Verify flash did not succeed.")
        self._verdict_printed = True

    def _close_bar(self) -> None:
        if self._bar is None:
            return
        self._bar.close()
        self._bar = None

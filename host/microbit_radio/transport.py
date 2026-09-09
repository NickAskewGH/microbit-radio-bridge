"""Transport helpers for command-driven radio firmware over serial."""

from __future__ import annotations

from collections.abc import Iterator
import re
from typing import Any, Protocol


HEX_RUN = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]+(?![0-9a-fA-F])")


class SerialPort(Protocol):
    def write(self, data: Any, /) -> int | None: ...

    def flush(self) -> None: ...

    def readline(self) -> bytes: ...


def extract_hex_record(text: str, *, min_bytes: int, max_bytes: int) -> bytes | None:
    """Extract a packet record while ignoring prompts and other shell output."""
    for match in HEX_RUN.finditer(text):
        encoded = match.group()
        if len(encoded) % 2 == 0 and min_bytes * 2 <= len(encoded) <= max_bytes * 2:
            return bytes.fromhex(encoded)
    return None


class SerialShellTransport:
    def __init__(self, port: SerialPort) -> None:
        self.port = port

    def send_command(self, command: str) -> None:
        self.port.write(f"{command}\n".encode("ascii"))
        self.port.flush()

    def wait_for_text(self, expected: str, *, max_lines: int = 20) -> None:
        for _ in range(max_lines):
            line = self.port.readline()
            if not line:
                break
            if expected in line.decode("ascii", errors="ignore"):
                return
        raise TimeoutError(f"firmware did not acknowledge: {expected}")

    def records(self, *, min_bytes: int, max_bytes: int) -> Iterator[bytes]:
        while True:
            line = self.port.readline()
            if not line:
                continue
            try:
                text = line.decode("ascii").strip()
            except UnicodeDecodeError:
                continue
            payload = extract_hex_record(text, min_bytes=min_bytes, max_bytes=max_bytes)
            if payload is not None:
                yield payload

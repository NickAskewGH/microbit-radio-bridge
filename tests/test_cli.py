import argparse
import sys
from types import SimpleNamespace

import pytest

from microbit_radio import cli


class StopSniff(Exception):
    pass


class FakeSerialPort:
    def __init__(self, lines: list[bytes] | None = None) -> None:
        self.writes: list[bytes] = []
        self.flushed = False
        self.lines = iter(lines or [])

    def __enter__(self) -> "FakeSerialPort":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def write(self, data: bytes) -> None:
        self.writes.append(data)

    def flush(self) -> None:
        self.flushed = True

    def readline(self) -> bytes:
        try:
            return next(self.lines)
        except StopIteration:
            raise StopSniff from None


def test_sniff_configures_makecode_receiver(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakeSerialPort()
    serial_module = SimpleNamespace(Serial=lambda *args, **kwargs: port)
    monkeypatch.setitem(sys.modules, "serial", serial_module)
    args = argparse.Namespace(port="/dev/ttyACM0", baud=115200, group=20, frequency=7)

    with pytest.raises(StopSniff):
        cli._sniff(args)

    assert port.writes == [b"makecode_rx 20 7\n"]
    assert port.flushed


def test_sniff_ignores_shell_output_and_decodes_prefixed_packet(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = bytes.fromhex("01000101d20400000000000038fdffff0178").ljust(32, b"\x00")
    port = FakeSerialPort(
        [
            b"Clock has started\r\n",
            b"\x1b[m\r\n",
            b"\x1b[1;32muart:~$ \x1b[mmakecode_rx 20 7\r\n",
            b"MakeCode RX started: group 20, band 7\r\n",
            b"\x1b[1;32muart:~$ \x1b[m" + payload.hex().encode("ascii") + b"\r\n",
        ]
    )
    serial_module = SimpleNamespace(Serial=lambda *args, **kwargs: port)
    monkeypatch.setitem(sys.modules, "serial", serial_module)
    args = argparse.Namespace(port="/dev/ttyACM0", baud=115200, group=20, frequency=7)

    with pytest.raises(StopSniff):
        cli._sniff(args)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == (
        '{"group":20,"name":"x","packet_type":1,"serial":0,"timestamp_ms":1234,"value":-712}\n'
    )

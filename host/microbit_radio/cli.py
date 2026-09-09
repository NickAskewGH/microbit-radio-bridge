"""Command-line entry point for the USB stream."""

from __future__ import annotations

import argparse
import sys

from .protocols.base import ProtocolDecodeError, RadioProtocol
from .protocols.makecode import MakeCodeProtocol
from .transport import SerialShellTransport


def _stream(transport: SerialShellTransport, protocol: RadioProtocol) -> None:
    transport.send_command(protocol.receiver_command)

    for payload in transport.records(
        min_bytes=protocol.min_payload_bytes,
        max_bytes=protocol.max_payload_bytes,
    ):
        try:
            packet = protocol.decode(payload)
        except ProtocolDecodeError as exc:
            print(f"decode error: {exc}", file=sys.stderr)
            continue

        print(packet.to_json(), flush=True)


def _sniff(args: argparse.Namespace) -> int:
    try:
        import serial
    except ImportError:
        print(
            "Install the optional serial dependency with: uv sync --extra serial", file=sys.stderr
        )
        return 2

    with serial.Serial(args.port, args.baud, timeout=None) as port:
        protocol = MakeCodeProtocol(group=args.group, frequency=args.frequency)
        transport = SerialShellTransport(port)
        _stream(transport, protocol)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    sniff = subparsers.add_parser("sniff", help="decode hex packet lines from the dongle")
    sniff.add_argument("--port", required=True)
    sniff.add_argument("--baud", type=int, default=115200)
    sniff.add_argument("--group", type=int, default=None)
    sniff.add_argument("--frequency", type=int, default=7)
    sniff.set_defaults(func=_sniff)
    args = parser.parse_args(argv)
    return args.func(args)

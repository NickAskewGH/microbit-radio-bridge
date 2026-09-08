"""Command-line entry point for the USB stream."""

from __future__ import annotations

import argparse
import sys

from .protocol import PacketDecodeError, decode_packet


def _sniff(args: argparse.Namespace) -> int:
    try:
        import serial
    except ImportError:
        print("Install the optional serial dependency: python -m pip install -e '.[serial]'", file=sys.stderr)
        return 2

    with serial.Serial(args.port, args.baud, timeout=1) as port:
        for line in port:
            payload = bytes.fromhex(line.decode("ascii").strip())
            try:
                print(decode_packet(payload, expected_group=args.group).to_json(), flush=True)
            except PacketDecodeError as exc:
                print(f"decode error: {exc}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    sniff = subparsers.add_parser("sniff", help="decode hex packet lines from the dongle")
    sniff.add_argument("--port", required=True)
    sniff.add_argument("--baud", type=int, default=115200)
    sniff.add_argument("--group", type=int, default=None)
    sniff.set_defaults(func=_sniff)
    args = parser.parse_args(argv)
    return args.func(args)

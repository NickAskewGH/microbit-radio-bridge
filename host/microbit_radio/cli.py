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


def _serve(args: argparse.Namespace) -> int:
    try:
        import serial
    except ImportError:
        print("Install API dependencies with: uv sync --extra api", file=sys.stderr)
        return 2

    try:
        from .api import create_app
        from .controller import ControlValues, MakeCodeCarController
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    with serial.Serial(args.port, args.baud, timeout=0.2) as port:
        transport = SerialShellTransport(port)
        controller = MakeCodeCarController(
            transport,
            group=args.group,
            frequency=args.frequency,
            neutral=ControlValues(args.neutral_x, args.neutral_y),
            default_duration_ms=args.default_duration,
            max_duration_ms=args.max_duration,
            control_limit=args.limit,
        )
        app = create_app(controller)
        try:
            app.run(host=args.host, port=args.http_port, debug=False, use_reloader=False)
        finally:
            controller.close()
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
    serve = subparsers.add_parser("serve", help="serve the mini-car control API")
    serve.add_argument("--port", required=True, help="serial port")
    serve.add_argument("--baud", type=int, default=115200)
    serve.add_argument("--group", type=int, default=20)
    serve.add_argument("--frequency", type=int, default=7)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--http-port", type=int, default=5000)
    serve.add_argument("--default-duration", type=int, default=500)
    serve.add_argument("--max-duration", type=int, default=60_000)
    serve.add_argument("--neutral-x", type=int, default=0)
    serve.add_argument("--neutral-y", type=int, default=0)
    serve.add_argument("--limit", type=int, default=1023)
    serve.set_defaults(func=_serve)
    args = parser.parse_args(argv)
    return args.func(args)

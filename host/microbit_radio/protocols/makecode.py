"""Decode and configure BBC micro:bit MakeCode radio packets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import struct
from typing import ClassVar

from .base import ProtocolDecodeError


DAL_HEADER_VERSION = 1
DAL_PROTOCOL_RADIO = 1
PACKET_TYPE_NUMBER = 0
PACKET_TYPE_VALUE = 1
PACKET_TYPE_STRING = 2


class PacketDecodeError(ProtocolDecodeError):
    """Raised when a radio payload is not a supported MakeCode packet."""


@dataclass(frozen=True)
class MakeCodePacket:
    group: int
    packet_type: int
    timestamp_ms: int
    serial: int
    value: int | None = None
    name: str | None = None
    text: str | None = None

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        return {key: value for key, value in result.items() if value is not None}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PacketDecodeError(message)


def decode_packet(raw: bytes, *, expected_group: int | None = None) -> MakeCodePacket:
    """Decode a MakeCode packet, ignoring zero padding after its logical payload."""
    _require(len(raw) >= 12, "packet is shorter than the DAL/PXT header")
    version, group, protocol = raw[:3]
    _require(version == DAL_HEADER_VERSION, f"unsupported DAL version: {version}")
    _require(protocol == DAL_PROTOCOL_RADIO, f"unsupported DAL protocol: {protocol}")
    _require(expected_group is None or group == expected_group, f"unexpected group: {group}")

    packet_type = raw[3]
    timestamp_ms = int.from_bytes(raw[4:8], "little")
    serial = int.from_bytes(raw[8:12], "little")

    if packet_type == PACKET_TYPE_NUMBER:
        _require(len(raw) >= 16, "number packet is truncated")
        value = struct.unpack_from("<i", raw, 12)[0]
        return MakeCodePacket(group, packet_type, timestamp_ms, serial, value=value)

    if packet_type == PACKET_TYPE_VALUE:
        _require(len(raw) >= 17, "value packet is missing its name length")
        value = struct.unpack_from("<i", raw, 12)[0]
        name_length = raw[16]
        _require(name_length <= 8, "MakeCode value name exceeds eight bytes")
        end = 17 + name_length
        _require(len(raw) >= end, "value packet name is truncated")
        try:
            name = raw[17:end].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PacketDecodeError("value packet name is not UTF-8") from exc
        return MakeCodePacket(group, packet_type, timestamp_ms, serial, value=value, name=name)

    if packet_type == PACKET_TYPE_STRING:
        _require(len(raw) >= 13, "string packet is missing its length")
        text_length = raw[12]
        end = 13 + text_length
        _require(text_length <= 19, "MakeCode string exceeds nineteen bytes")
        _require(len(raw) >= end, "string packet is truncated")
        try:
            text = raw[13:end].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PacketDecodeError("string packet is not UTF-8") from exc
        return MakeCodePacket(group, packet_type, timestamp_ms, serial, text=text)

    raise PacketDecodeError(f"unsupported MakeCode packet type: {packet_type}")


@dataclass(frozen=True)
class MakeCodeProtocol:
    min_payload_bytes: ClassVar[int] = 12
    max_payload_bytes: ClassVar[int] = 32

    group: int
    frequency: int = 7

    @property
    def receiver_command(self) -> str:
        return f"makecode_rx {self.group} {self.frequency}"

    def decode(self, payload: bytes) -> MakeCodePacket:
        packet = decode_packet(payload)
        if packet.group not in (0, self.group):
            raise PacketDecodeError(f"unexpected group: {packet.group}")
        return replace(packet, group=self.group)

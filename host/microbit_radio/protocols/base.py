"""Interfaces implemented by supported radio protocols."""

from __future__ import annotations

from typing import ClassVar, Protocol


class DecodedPacket(Protocol):
    def to_json(self) -> str: ...


class ProtocolDecodeError(ValueError):
    """Raised when a captured payload does not match a protocol."""


class RadioProtocol(Protocol):
    min_payload_bytes: ClassVar[int]
    max_payload_bytes: ClassVar[int]

    @property
    def receiver_command(self) -> str: ...

    def decode(self, payload: bytes) -> DecodedPacket: ...

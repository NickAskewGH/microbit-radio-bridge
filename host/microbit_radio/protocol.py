"""Compatibility exports for the original MakeCode decoder module."""

from .protocols.makecode import MakeCodePacket, PacketDecodeError, decode_packet

__all__ = ["MakeCodePacket", "PacketDecodeError", "decode_packet"]

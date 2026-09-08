from microbit_radio.protocol import PacketDecodeError, decode_packet
from pathlib import Path


FIXTURES = Path(__file__).parents[1] / "protocol" / "fixtures"


def packet(packet_type: int, timestamp: int, serial: int, body: bytes, group: int = 20) -> bytes:
    return bytes((1, group, 1, packet_type)) + timestamp.to_bytes(4, "little") + serial.to_bytes(4, "little") + body


def test_decodes_send_value_x_with_padding() -> None:
    raw = packet(1, 1234, 0, (-712).to_bytes(4, "little", signed=True) + bytes((1,)) + b"x")
    result = decode_packet(raw + bytes(32 - len(raw)), expected_group=20)
    assert result.to_dict() == {"group": 20, "packet_type": 1, "timestamp_ms": 1234, "serial": 0, "value": -712, "name": "x"}


def test_decodes_checked_in_x_fixture() -> None:
    raw = bytes.fromhex((FIXTURES / "send-value-x-group20.hex").read_text())
    result = decode_packet(raw, expected_group=20)
    assert result.name == "x"
    assert result.value == -712


def test_decodes_send_value_y_and_serial() -> None:
    raw = packet(1, 99, 0x12345678, (250).to_bytes(4, "little", signed=True) + bytes((1,)) + b"y")
    result = decode_packet(raw)
    assert result.name == "y"
    assert result.value == 250
    assert result.serial == 0x12345678


def test_decodes_checked_in_y_fixture() -> None:
    raw = bytes.fromhex((FIXTURES / "send-value-y-group20.hex").read_text())
    result = decode_packet(raw, expected_group=20)
    assert result.name == "y"
    assert result.value == 250


def test_rejects_wrong_group() -> None:
    raw = packet(1, 1, 0, (1).to_bytes(4, "little", signed=True) + bytes((1,)) + b"x", group=7)
    try:
        decode_packet(raw, expected_group=20)
    except PacketDecodeError as exc:
        assert "unexpected group" in str(exc)
    else:
        raise AssertionError("expected group mismatch")


def test_rejects_truncated_value_name() -> None:
    raw = packet(1, 1, 0, (1).to_bytes(4, "little", signed=True) + bytes((2,)) + b"x")
    try:
        decode_packet(raw)
    except PacketDecodeError as exc:
        assert "truncated" in str(exc)
    else:
        raise AssertionError("expected truncation")

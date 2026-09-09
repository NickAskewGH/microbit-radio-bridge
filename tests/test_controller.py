from microbit_radio.controller import ControlValues, MakeCodeCarController
from microbit_radio.protocols.makecode import decode_packet


class FakeTransport:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def send_command(self, command: str) -> None:
        self.commands.append(command)

    def wait_for_text(self, expected: str, *, max_lines: int = 20) -> None:
        assert expected == "MakeCode TX sent"


def command_packet(command: str) -> bytes:
    name, group, frequency, payload = command.split()
    assert name == "makecode_tx"
    assert (group, frequency) == ("20", "7")
    return bytes.fromhex(payload)


def test_sends_x_y_and_duration_as_one_logical_directive() -> None:
    transport = FakeTransport()
    controller = MakeCodeCarController(transport)
    try:
        duration_ms = controller.send(ControlValues(x=-300, y=700))

        x_packet, y_packet, t_packet = map(decode_packet, map(command_packet, transport.commands))
        assert duration_ms == 500
        assert (x_packet.name, x_packet.value) == ("x", -300)
        assert (y_packet.name, y_packet.value) == ("y", 700)
        assert (t_packet.name, t_packet.value) == ("t", 500)
        assert x_packet.timestamp_ms == y_packet.timestamp_ms == t_packet.timestamp_ms
        assert x_packet.group == y_packet.group == t_packet.group == 0
    finally:
        controller.close()


def test_explicit_duration_is_sent_to_car() -> None:
    transport = FakeTransport()
    controller = MakeCodeCarController(transport)
    try:
        controller.send(ControlValues(-775, 775), duration_ms=2000)

        packets = [decode_packet(command_packet(command)) for command in transport.commands]
        assert [(packet.name, packet.value) for packet in packets] == [
            ("x", -775),
            ("y", 775),
            ("t", 2000),
        ]
    finally:
        controller.close()


def test_rejects_values_outside_control_limit() -> None:
    transport = FakeTransport()
    controller = MakeCodeCarController(transport)
    try:
        try:
            controller.send(ControlValues(1024, 0))
        except ValueError as exc:
            assert "between -1023 and 1023" in str(exc)
        else:
            raise AssertionError("expected control limit error")
        assert transport.commands == []
    finally:
        controller.close()


def test_stop_sends_neutral_directive() -> None:
    transport = FakeTransport()
    controller = MakeCodeCarController(transport, neutral=ControlValues(11, 22))
    try:
        controller.stop()

        packets = [decode_packet(command_packet(command)) for command in transport.commands]
        assert [(packet.name, packet.value) for packet in packets] == [
            ("x", 11),
            ("y", 22),
            ("t", 1),
        ]
    finally:
        pass


def test_rejects_invalid_duration() -> None:
    transport = FakeTransport()
    controller = MakeCodeCarController(transport)
    try:
        for duration_ms in (0, 60_001):
            try:
                controller.send(ControlValues(0, 0), duration_ms)
            except ValueError as exc:
                assert "t must be between" in str(exc)
            else:
                raise AssertionError("expected duration error")
    finally:
        controller.close()

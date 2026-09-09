from microbit_radio.transport import extract_hex_record


def test_extracts_packet_after_ansi_shell_prompt() -> None:
    packet = bytes(range(32))
    text = f"\x1b[1;32muart:~$ \x1b[m{packet.hex()}"

    assert extract_hex_record(text, min_bytes=12, max_bytes=32) == packet


def test_ignores_shell_text_and_out_of_range_hex() -> None:
    assert (
        extract_hex_record("MakeCode RX started: group 20, band 7", min_bytes=12, max_bytes=32)
        is None
    )
    assert extract_hex_record("001122", min_bytes=4, max_bytes=32) is None

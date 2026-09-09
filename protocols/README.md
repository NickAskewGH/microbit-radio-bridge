# Protocol workspaces

Each supported remote-control family has its own directory containing verified
radio parameters, packet notes, and replay fixtures. Shared serial transport and
capture mechanics belong in `host/microbit_radio/transport.py`; protocol-specific
decoding and command encoding belong in `host/microbit_radio/protocols/`.

Do not fill unknown radio parameters with plausible defaults. Record captures
and establish modulation, frequency behavior, addressing, whitening, CRC,
pairing, and failsafe behavior before implementing transmission.
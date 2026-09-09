# Polar Mouse Droid (MSE-6) remote

Status: capture and protocol identification required.

The two incoming large vehicles use the same remote family and will share this
protocol workspace. Before implementing an adapter or transmitter, capture and
verify:

- modulation and data rate
- fixed, selectable, or hopping frequencies
- address and pairing behavior
- packet length, whitening, and CRC
- control fields, sequence counters, and checksums
- neutral, timeout, loss-of-link, and emergency-stop behavior
- whether both vehicles use distinct identities or pairing state

Store annotated recordings under `captures/polar_mouse/`. Once those facts are
known, add `host/microbit_radio/protocols/polar_mouse.py` and a matching firmware
PHY profile. Transmission must remain disabled until neutral and loss-of-link
behavior have repeatable tests.
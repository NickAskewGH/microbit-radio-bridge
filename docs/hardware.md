# Hardware bring-up

The target is the GeeekPi nRF52840 Micro Dev Kit USB Dongle, expected to behave like the Nordic PCA10059 nRF52840 USB dongle.

Before flashing a production image:

1. Confirm the board exposes a UF2/DFU bootloader and identify its USB serial device.
2. Confirm the crystal, antenna, and USB power are stable.
3. Match the radio data rate, channel, base address, and group settings to the existing remote/car pair.
4. Capture raw packets with the firmware's USB output enabled.
5. Replay those captures through `pytest` and compare decoded `x`/`y` values with the remote display or car behavior.

No transmit path is enabled in this milestone. That is intentional while the protocol and radio settings are being validated.

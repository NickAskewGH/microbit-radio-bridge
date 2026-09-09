# Hardware bring-up

The target is the GeeekPi nRF52840 Micro Dev Kit USB Dongle, expected to behave like the Nordic PCA10059 nRF52840 USB dongle.

Before flashing a production image:

1. Confirm the board exposes a UF2/DFU bootloader and identify its USB serial device.
2. Confirm the crystal, antenna, and USB power are stable.
3. Match the radio data rate, channel, base address, and group settings to the existing remote/car pair.
4. Capture raw packets with the firmware's USB output enabled.
5. Replay those captures through `pytest` and compare decoded `x`/`y` values with the remote display or car behavior.

No transmit path is enabled in this milestone. That is intentional while the protocol and radio settings are being validated.

## MakeCode receiver firmware

`nordic_firmware/radio_test` is based on Nordic's Zephyr radio-test sample. It
adds this serial shell command:

```text
makecode_rx <group 0-255> [frequency band 0-100]
```

The command configures the radio to match the micro:bit DAL:

- Nordic proprietary 1 Mbit/s mode
- base address `0x75626974` (`uBit`) with the group as the address prefix
- 8-bit length field and a 32-byte maximum radio payload
- little-endian packet format with whitening IV `0x18`
- two-byte CRC, initial value `0xffff`, polynomial `0x11021`

The default MakeCode frequency band is `7` (2407 MHz). Each received packet is
written to the serial console as one lowercase hex payload line without the
radio length byte. MakeCode can advertise a 35-byte frame length while the
radio transfers at most 32 payload bytes; the firmware safely caps the serial
record at those 32 bytes. Frames can also carry zero in their legacy group
byte; the host reports the group selected by the radio address filter instead.

Build the UF2 firmware with nRF Connect SDK 3.4.0:

```shell
west build -p always -b nrf52840_mdk_usb_dongle nordic_firmware/radio_test \
	-d build/radio_test_makecode -- -DCONFIG_BUILD_OUTPUT_UF2=y
```

The resulting images are under
`build/radio_test_makecode/radio_test/zephyr/`. The connected
`/dev/ttyACM0` device identifies as a Zephyr CDC ACM application interface, so
flashing must use the dongle's UF2/DFU bootloader or an SWD probe rather than
the serial device.

After flashing, this command opens CDC ACM and automatically sends
`makecode_rx 20 7` before listening:

```shell
just sniff /dev/ttyACM0 20
```

Pass a non-default frequency as the fourth recipe argument, for example
`just sniff /dev/ttyACM0 20 115200 50`.

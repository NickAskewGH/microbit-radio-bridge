# nRF52840 RX firmware scaffold

This directory targets the GeeekPi nRF52840 USB dongle (PCA10059-compatible form factor).

The firmware must configure the nRF52840 RADIO peripheral for the micro:bit's Nordic proprietary 2.4 GHz packet mode, receive 1 Mbit/s packets, and expose each raw payload over USB CDC ACM as one lowercase hex line. The host decoder intentionally receives raw payloads rather than partially decoded fields.

The current `src/main.c` is a hardware boundary scaffold: it documents the required RADIO register setup and the USB record format without pretending that an unverified SDK configuration is a flashable image. The next hardware task is to pin an nRF Connect SDK/Zephyr version and implement the board-specific USB and RADIO drivers behind this interface.

Expected record format:

```text
01140101d20400000000000038fdffff0178
```

The example is a group-20 `sendValue("x", -712)` payload.

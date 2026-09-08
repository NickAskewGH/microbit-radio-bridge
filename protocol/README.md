# MakeCode radio packet notes

The supported packet starts with the three-byte DAL header:

```text
01             DAL radio header version
GROUP          8-bit radio group, normally 20 for the car project
01             DAL datagram protocol
```

For `radio.sendValue(name, integer)` the remaining bytes are:

```text
01             packet type: value
TIME[4]        little-endian running time in milliseconds
SERIAL[4]      little-endian serial number; zero when disabled
VALUE[4]       little-endian signed 32-bit integer
NAME_LEN[1]    UTF-8 name length, maximum 8
NAME           UTF-8 name bytes
```

The nRF radio may expose a fixed-width payload with zero padding after the logical packet. The decoder accepts that padding but never treats it as part of the name.

This layout is based on the MakeCode packet documentation and the reference implementation used by micro:bit MicroPython/MakeCode radio bridges. Capture fixtures should be added from the real `mini-car-remote` before transmit support is implemented.

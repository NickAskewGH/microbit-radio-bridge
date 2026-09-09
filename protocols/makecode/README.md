# MakeCode radio packet notes

The supported packet starts with the three-byte DAL header:

```text
01             DAL radio header version
GROUP          legacy group field; observed as zero on the car remote
01             DAL datagram protocol
```

The radio address prefix, rather than the legacy payload field, selects group
20. For `radio.sendValue(name, integer)` the remaining bytes are:

```text
01             packet type: value
TIME[4]        little-endian running time in milliseconds
SERIAL[4]      little-endian serial number; zero when disabled
VALUE[4]       little-endian signed 32-bit integer
NAME_LEN[1]    UTF-8 name length, maximum 8
NAME           UTF-8 name bytes
```

The nRF radio exposes a fixed-width payload with zero padding after the logical
packet. The decoder accepts that padding but never treats it as part of the name.
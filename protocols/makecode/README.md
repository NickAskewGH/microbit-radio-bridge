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

## Legacy mini-car control calibration

The API forwards the remote's raw `x` and `y` values; they are joystick axes,
not independent left/right wheel speeds. Hardware observations show strict
receiver thresholds around `-500` and `500`:

| Values | Observed result |
| --- | --- |
| `x=0, y=-550` | Both wheels forward at medium speed |
| `x=-50, y=-550` | Both wheels forward at medium speed |
| `x=-250, y=-550` | Both wheels forward at medium speed |
| `x=500, y=0` | No movement |
| `x=575, y=-200` | Left forward slowly; right briefly twitches in reverse |
| `x=575, y=-250` | Left forward slowly; right reverses slowly |
| `x=-500, y=-250` | No movement |
| `x=-501, y=-250` | Left reverses quickly; right does not move |

The original car source processed each received axis independently and directly
overwrote both motors:

- `x < -500`: M1 backward and M2 forward.
- `x > 500`: M1 forward and M2 backward.
- `-500 <= x <= 500`: both motors are explicitly stopped.
- `y < -250`: both motors forward.
- `y > 250`: both motors backward.
- `-250 <= y <= 250`: motor state is unchanged because the `y` handler has no
	neutral `else` branch.

With that legacy receiver, the API sends `x` first and `y` second. A `y` value
outside ±250 therefore overwrites the turn established by `x`; a `y` value
inside that range preserves the `x` result. The legacy receiver cannot produce
a stable curved drive.

The abrupt negative-`x` behavior is caused by an apparent endpoint error in the
car source. M1 uses `Math.map(value, 500, -1023, 0, 255)` while M2 uses
`Math.map(value, -500, -1023, 0, 255)`. At `x=-501`, M1 is therefore commanded
to roughly 168 while M2 is commanded near zero. Changing M1's first endpoint
from `500` to `-500` would make the negative turn symmetric with the positive
turn.

The updated `mini-car` TypeScript receiver uses group 20 and interprets `x` and
`y` as direct signed M1/M2 wheel demands. A third `t` value carries duration in
milliseconds. The car applies only complete fresh triplets and enforces duration
with its local clock, avoiding intermediate packet and host scheduling jitter.
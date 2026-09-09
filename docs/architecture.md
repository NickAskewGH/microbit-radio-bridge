# Architecture

```text
remote or host command
      │
      ▼
protocol adapter (MakeCode, Polar Mouse, ...)
      │  decoded events / encoded packets
      ▼
shared serial transport
      │  firmware commands / packet hex records
      ▼
nRF52840 PHY profile
      │  protocol-specific 2.4 GHz radio configuration
      ▼
vehicle receiver
```

The nRF52840 firmware owns time-critical radio operation: modulation, channels,
addresses, whitening, CRC, packet capture, and transmission timing. Each PHY
profile is selected through an explicit serial command such as `makecode_rx`.

The host transport owns only CDC shell framing and extraction of packet records.
Protocol adapters own setup commands, packet semantics, decoding, encoding,
pairing state, and protocol-level safety rules. Raw captures and fixtures remain
outside the Python package so they can be inspected and replayed independently.

MakeCode is the first implemented adapter. Polar Mouse Droid remains a protocol
workspace until captures establish its PHY and packet format; no values are
assumed merely because it also operates in the 2.4 GHz ISM band.

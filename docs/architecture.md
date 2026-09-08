# Architecture

```text
micro:bit remote
      │  Nordic proprietary 2.4 GHz, 1 Mbit/s
      ▼
nRF52840 dongle firmware
      │  USB CDC ACM; one captured packet per hex line
      ▼
Ubuntu host CLI
      │
      └── MakeCode packet decoder → JSON lines
```

The firmware owns radio timing, channel/address configuration, packet capture, and USB framing. The host owns protocol interpretation, filtering, logging, and later integration with the car controller. Keeping those responsibilities separate makes raw captures available when the project-specific radio settings need correction.

The first hardware milestone is to receive traffic from `mini-car-remote` without changing `mini-car`. The capture tool should record raw hex lines before decoding so fixtures can be replayed in tests.

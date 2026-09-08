# microbit-radio-bridge

Ubuntu tooling and nRF52840 firmware for receiving BBC micro:bit MakeCode radio packets over USB.

The first milestone is deliberately receive-only: sniff packets from the existing `mini-car-remote`, decode `radio.sendValue("x", value)` and `radio.sendValue("y", value)` messages, and stream decoded events to a host computer. The `mini-car` project is not modified by this repository.

## Status

- Host-side MakeCode packet decoder: implemented and tested.
- JSON-lines serial protocol and CLI: implemented.
- nRF52840 proprietary-radio receive firmware: scaffolded for the GeeekPi/PCA10059-style dongle; hardware validation and SDK pinning remain before producing a flashable image.
- Transmit support: intentionally out of scope for this first milestone.

## Quick start

```shell
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
microbit-radio --help
```

Once the firmware is connected, stream decoded packets with:

```shell
microbit-radio sniff --port /dev/ttyACM0 --group 20
```

The CLI emits one JSON object per line, for example:

```json
{"group":20,"name":"x","value":-712,"timestamp_ms":1234,"serial":0}
```

## Repository layout

```text
firmware/   nRF52840 radio/USB firmware scaffold
host/       Python package and CLI
protocol/   packet format notes and captured fixtures
tests/      decoder and serial protocol tests
docs/       architecture, hardware, and capture workflow
```

## Safety and scope

This project only observes radio traffic. It does not change the car firmware, send control packets, or provide a motor-control failsafe yet. Do not connect an unvalidated transmitter to a powered vehicle until the later transmit milestone has been tested safely.

## References

- [MakeCode radio packet reference](https://makecode.microbit.org/v9/reference/radio/packet)
- [MakeCode `sendValue`](https://makecode.microbit.org/reference/radio/send-value)
- [micro:bit DAL radio header](https://github.com/lancaster-university/microbit-dal/blob/master/inc/drivers/MicroBitRadio.h)
- `NickAskewGH/mini-car-remote` and `NickAskewGH/mini-car` are the project-specific references to validate over-the-air settings and names.

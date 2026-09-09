# 2.4 GHz radio bridge toolkit

Ubuntu tooling and nRF52840 firmware for learning and implementing explicitly
supported 2.4 GHz remote-control protocols.

The first milestone is deliberately receive-only: sniff packets from the existing `mini-car-remote`, decode `radio.sendValue("x", value)` and `radio.sendValue("y", value)` messages, and stream decoded events to a host computer. The `mini-car` project is not modified by this repository.

## Status

- Shared serial transport and protocol adapter boundary: implemented and tested.
- MakeCode packet decoder and receive profile: implemented and hardware tested.
- Polar Mouse Droid (MSE-6) protocol: workspace created; capture required.
- JSON-lines serial protocol and CLI: implemented.
- nRF52840 proprietary-radio receive firmware: MakeCode RX is implemented and hardware tested on the Makerdiary-compatible dongle.
- MakeCode one-shot transmit firmware and local Flask control API: implemented;
	vehicle-side validation remains.

Planned sequence:

1. Implement and safely validate the mini-car MakeCode sender.
2. Implement the receive-only Polar Mouse learning milestone in
	[`docs/milestone-polar-mouse-learning.md`](docs/milestone-polar-mouse-learning.md).
3. Design Polar Mouse decoding and transmission only from verified captures.

## Quick start

```shell
uv sync --all-groups
just check
radio-bridge --help
```

The project uses `uv` for environment and dependency management, Ruff for
formatting and linting, and `just` for repeatable development commands. Run
`just` to see the available recipes.

Once the firmware is connected, stream decoded packets with:

```shell
just sniff /dev/ttyACM0 20
```

The sniffer configures group 20 on the default 2407 MHz band, then waits
indefinitely for newline-delimited hex packets; press `Ctrl-C` to stop it.

The CLI emits one JSON object per line, for example:

```json
{"group":20,"name":"x","value":-712,"timestamp_ms":1234,"serial":0}
```

After flashing firmware with MakeCode TX support, start the localhost control API:

```shell
just serve /dev/ttyACM0 20
```

See [`docs/hardware.md`](docs/hardware.md) for locally timed `x/y/t` directives
and the required raised-wheel test procedure.

## Repository layout

```text
firmware/          original nRF52840 radio/USB boundary scaffold
nordic_firmware/   buildable Zephyr firmware and PHY profiles
host/              shared transport, protocol adapters, and CLI
protocols/         per-remote packet notes and replay fixtures
captures/          immutable learning-session recordings and metadata
tests/             transport, adapter, decoder, and CLI tests
docs/              architecture and hardware workflows
```

## Safety and scope

Transmission is limited to explicitly supported protocol profiles. The MakeCode
The vehicle enforces each directive's duration locally and stops when it expires.
Test with driven wheels raised and a physical power cutoff before operating a
vehicle on the ground.

## References

- [MakeCode radio packet reference](https://makecode.microbit.org/v9/reference/radio/packet)
- [MakeCode `sendValue`](https://makecode.microbit.org/reference/radio/send-value)
- [micro:bit DAL radio header](https://github.com/lancaster-university/microbit-dal/blob/master/inc/drivers/MicroBitRadio.h)
- `NickAskewGH/mini-car-remote` and `NickAskewGH/mini-car` are the project-specific references to validate over-the-air settings and names.

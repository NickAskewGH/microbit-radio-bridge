# Milestone: Polar Mouse receive-only learning

Status: **TODO after the mini-car MakeCode sender milestone**

## Goal

Add a receive-only nRF52840 learning profile and host capture/analysis commands
that can discover and characterize the Polar Mouse Droid (MSE-6) remote used by
both incoming vehicles. This milestone gathers reproducible evidence for a later
protocol adapter; it does not transmit or control either vehicle.

## Entry criteria

Start this milestone only after the mini-car sender can safely reproduce the
existing MakeCode remote commands and has tested neutral/stop behavior. Preserve
the working MakeCode RX and sender profiles as regression-tested adapters.

Before capture work begins:

- Record remote, vehicle, and regulatory identifiers and photograph the labels.
- Identify the remote's radio IC from documentation or a non-destructive inspection when possible.
- Establish a safe test setup with driven wheels raised or the vehicle unpowered.
- Assign stable identifiers to both vehicles and both remotes.

## Firmware deliverable

Implement a separate receive-only `learn` profile rather than weakening the
validated MakeCode profile. It should provide:

- Energy/RSSI scanning across configurable 2.4 GHz frequency ranges.
- Configurable candidate PHY profiles supported by the nRF52840.
- Channel lists, dwell time, packet length, address, whitening, and CRC options.
- Capture with CRC disabled for discovery and enabled once a candidate CRC is known.
- Raw records containing timestamp, frequency, PHY profile, RSSI, payload, and reception status.
- Bounded buffering with explicit dropped-record counters.
- Start, stop, status, and configuration commands over CDC ACM.
- No radio transmit path reachable from learning mode.

The scanner must document that the nRF52840 is not a wideband receiver: it can
observe only the currently configured frequency and PHY. Channel hopping and
unknown modulation may therefore require repeated experiments or additional
hardware such as an SDR or logic analyzer.

## Host deliverable

Add protocol-neutral commands under `radio-bridge`:

```text
radio-bridge capture --profile ... --output captures/polar_mouse/<session>/
radio-bridge analyze captures/polar_mouse/<session>/
```

`capture` should:

- Save raw records without rewriting or interpreting payload bytes.
- Write session metadata including firmware revision, settings, hardware IDs,
  operator annotations, timestamps, and controlled remote action.
- Support clean interruption and retain partial captures.
- Report packet, CRC, malformed-record, and dropped-record counts.

`analyze` should:

- Group records by frequency, length, address candidate, and repeated prefix.
- Compare named action sessions such as neutral, forward, reverse, left, and right.
- Identify constant, changing, counter-like, and checksum-like fields.
- Report timing, repetition rate, hopping sequences, and correlations between remotes.
- Export selected records as reviewed fixtures under `protocols/polar_mouse/fixtures/`.
- Keep hypotheses visibly distinct from verified protocol facts.

PCAP export and a Wireshark dissector are optional follow-ups after framing is
understood; they are not prerequisites for initial analysis.

## Capture plan

Collect separate sessions for:

1. Remote powered on without input.
2. Neutral/idle traffic.
3. Each control at minimum, midpoint, and maximum where applicable.
4. One control transition at a time.
5. Combined controls such as forward-left and reverse-right.
6. Pairing, startup, shutdown, and loss-of-link behavior.
7. Both remote/vehicle pairs under identical actions.
8. One remote near both vehicles to determine identity and pairing behavior.

Repeat captures to distinguish control values from counters, timing fields, and
random session state.

## Acceptance criteria

- MakeCode receive and sender regression tests still pass.
- Learning mode cannot transmit, including malformed serial commands.
- A capture session can run long enough to observe every tested control without
  silently losing records; any loss is counted.
- Raw captures and complete metadata are replayable without connected hardware.
- Analysis identifies active frequencies and candidate packet framing for both remotes.
- Repeated actions produce stable, testable field-difference reports.
- At least one neutral and one movement fixture from each remote are reviewed and checked in.
- Unknown or unsupported PHY behavior is documented with evidence and a recommended next tool.

## Explicitly deferred

- Polar Mouse packet transmission or vehicle control.
- Pairing emulation.
- Production command APIs.
- Autonomous control and multi-vehicle arbitration.
- Wireshark dissector work before packet framing is verified.

The next milestone may implement a Polar Mouse decoder only after these capture
and analysis acceptance criteria are met. Transmission requires a later safety
review covering neutral commands, dead-man timeout, rate limits, and a physical
emergency stop.
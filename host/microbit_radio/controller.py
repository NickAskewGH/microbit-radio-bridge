"""MakeCode mini-car control over the nRF52840 serial shell."""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Protocol

from .protocols.makecode import encode_value


class CommandTransport(Protocol):
    def send_command(self, command: str) -> None: ...

    def wait_for_text(self, expected: str, *, max_lines: int = 20) -> None: ...


@dataclass(frozen=True)
class ControlValues:
    x: int
    y: int


class MakeCodeCarController:
    def __init__(
        self,
        transport: CommandTransport,
        *,
        group: int = 20,
        frequency: int = 7,
        neutral: ControlValues = ControlValues(0, 0),
        default_duration_ms: int = 500,
        max_duration_ms: int = 60_000,
        control_limit: int = 1023,
    ) -> None:
        if not 0 <= group <= 255:
            raise ValueError("group must be between 0 and 255")
        if not 0 <= frequency <= 100:
            raise ValueError("frequency must be between 0 and 100")
        if default_duration_ms <= 0:
            raise ValueError("default duration must be positive")
        if max_duration_ms < default_duration_ms:
            raise ValueError("maximum duration must not be below the default")
        if control_limit <= 0:
            raise ValueError("control limit must be positive")

        self._transport = transport
        self._group = group
        self._frequency = frequency
        self._neutral = neutral
        self._default_duration_ms = default_duration_ms
        self._max_duration_ms = max_duration_ms
        self._control_limit = control_limit
        self._lock = threading.Lock()

    def send(self, values: ControlValues, duration_ms: int | None = None) -> int:
        if abs(values.x) > self._control_limit or abs(values.y) > self._control_limit:
            raise ValueError(
                f"x and y must be between {-self._control_limit} and {self._control_limit}"
            )
        duration_ms = self._default_duration_ms if duration_ms is None else duration_ms
        if not 0 < duration_ms <= self._max_duration_ms:
            raise ValueError(f"t must be between 1 and {self._max_duration_ms} ms")
        with self._lock:
            self._send_directive(values, duration_ms)
        return duration_ms

    def stop(self) -> None:
        with self._lock:
            self._send_directive(self._neutral, 1)

    def close(self) -> None:
        self.stop()

    def _send_directive(self, values: ControlValues, duration_ms: int) -> None:
        timestamp_ms = time.monotonic_ns() // 1_000_000 & 0xFFFFFFFF
        for name, value in (("x", values.x), ("y", values.y), ("t", duration_ms)):
            payload = encode_value(name, value, timestamp_ms=timestamp_ms)
            self._transport.send_command(
                f"makecode_tx {self._group} {self._frequency} {payload.hex()}"
            )
            self._transport.wait_for_text("MakeCode TX sent")

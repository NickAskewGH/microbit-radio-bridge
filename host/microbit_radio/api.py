"""Flask application for controlling the MakeCode mini-car."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .controller import ControlValues, MakeCodeCarController


def _control_values(data: Mapping[str, Any] | None) -> tuple[ControlValues, int | None]:
    if data is None or type(data.get("x")) is not int or type(data.get("y")) is not int:
        raise ValueError("JSON body must contain integer x and y values")
    duration_ms = data.get("t")
    if duration_ms is not None and type(duration_ms) is not int:
        raise ValueError("t must be an integer number of milliseconds")
    return ControlValues(x=data["x"], y=data["y"]), duration_ms


def create_app(controller: MakeCodeCarController):
    try:
        from flask import Flask, jsonify, request
    except ImportError as exc:
        raise RuntimeError("Install API dependencies with: uv sync --extra api") from exc

    app = Flask(__name__)

    @app.post("/api/control")
    def control():
        try:
            values, requested_duration = _control_values(request.get_json(silent=True))
            duration_ms = controller.send(values, requested_duration)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        except (OSError, TimeoutError) as exc:
            return jsonify(error=str(exc)), 503
        return jsonify(status="sent", x=values.x, y=values.y, t=duration_ms)

    @app.post("/api/stop")
    def stop():
        controller.stop()
        return jsonify(status="stopped")

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    return app

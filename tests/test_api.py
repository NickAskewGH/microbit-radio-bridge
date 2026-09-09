from microbit_radio.api import create_app
from microbit_radio.controller import ControlValues


class FakeController:
    def __init__(self) -> None:
        self.values: list[tuple[ControlValues, int | None]] = []
        self.stops = 0

    def send(self, values: ControlValues, duration_ms: int | None = None) -> int:
        self.values.append((values, duration_ms))
        return 500 if duration_ms is None else duration_ms

    def stop(self) -> None:
        self.stops += 1


def test_control_endpoint_accepts_integer_x_and_y() -> None:
    controller = FakeController()
    client = create_app(controller).test_client()

    response = client.post("/api/control", json={"x": -300, "y": 700})

    assert response.status_code == 200
    assert response.get_json() == {"status": "sent", "x": -300, "y": 700, "t": 500}
    assert controller.values == [(ControlValues(-300, 700), None)]


def test_control_endpoint_accepts_duration_ms() -> None:
    controller = FakeController()
    client = create_app(controller).test_client()

    response = client.post("/api/control", json={"x": -775, "y": 775, "t": 2000})

    assert response.status_code == 200
    assert response.get_json() == {"status": "sent", "x": -775, "y": 775, "t": 2000}
    assert controller.values == [(ControlValues(-775, 775), 2000)]


def test_control_endpoint_rejects_missing_or_non_integer_values() -> None:
    controller = FakeController()
    client = create_app(controller).test_client()

    assert client.post("/api/control", json={"x": 1}).status_code == 400
    assert client.post("/api/control", json={"x": True, "y": 0}).status_code == 400
    assert client.post("/api/control", json={"x": 0, "y": 0, "t": 1.5}).status_code == 400
    assert controller.values == []


def test_stop_endpoint_sends_neutral() -> None:
    controller = FakeController()
    client = create_app(controller).test_client()

    response = client.post("/api/stop")

    assert response.status_code == 200
    assert controller.stops == 1

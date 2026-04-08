"""Tests for learning record push client and push tracking."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import httpx
import pytest

from raise_cli.memory.learning import LearningRecord
from raise_cli.memory.push import LearningPushClient, is_pushed, write_push_marker

_SERVER_URL = "http://localhost:8000"
_API_KEY = "rsk_test_key_123"


def _make_record(**overrides: object) -> LearningRecord:
    defaults: dict[str, object] = {
        "skill": "rai-story-design",
        "work_id": "S100.1",
        "version": "2.4.0",
        "timestamp": "2026-04-03T10:00:00",
    }
    defaults.update(overrides)
    return LearningRecord.model_validate(defaults)


def _make_client(
    status_code: int,
    json_body: dict[str, object] | None = None,
    *,
    capture: list[httpx.Request] | None = None,
) -> LearningPushClient:
    """Create a LearningPushClient with a mock transport."""

    def handler(request: httpx.Request) -> httpx.Response:
        if capture is not None:
            capture.append(request)
        return httpx.Response(status_code=status_code, json=json_body or {})

    transport = httpx.MockTransport(handler)
    mock_http = httpx.Client(base_url=_SERVER_URL, transport=transport)
    return LearningPushClient(_SERVER_URL, _API_KEY, _client=mock_http)


class TestLearningPushClient:
    def test_push_returns_uuid_on_success(self) -> None:
        server_id = uuid.uuid4()
        client = _make_client(200, {"id": str(server_id), "status": "ok"})

        result = client.push(_make_record())

        assert result == server_id

    def test_push_sends_correct_payload(self) -> None:
        server_id = uuid.uuid4()
        captured: list[httpx.Request] = []
        client = _make_client(200, {"id": str(server_id), "status": "ok"}, capture=captured)

        client.push(_make_record(skill="rai-epic-design", work_id="S200.1"))

        assert len(captured) == 1
        body = json.loads(captured[0].content)
        assert body["event_type"] == "learning_record"
        assert body["payload"]["skill"] == "rai-epic-design"
        assert body["payload"]["work_id"] == "S200.1"

    def test_push_sends_to_correct_endpoint(self) -> None:
        captured: list[httpx.Request] = []
        client = _make_client(
            200, {"id": str(uuid.uuid4()), "status": "ok"}, capture=captured
        )

        client.push(_make_record())

        assert captured[0].url.path == "/api/v1/agent/events"

    def test_push_raises_on_server_error(self) -> None:
        client = _make_client(500, {"detail": "Internal server error"})

        with pytest.raises(httpx.HTTPStatusError):
            client.push(_make_record())

    def test_push_raises_on_auth_error(self) -> None:
        client = _make_client(401, {"detail": "Invalid API key"})

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            client.push(_make_record())

        assert exc_info.value.response.status_code == 401

    def test_push_raises_on_403_plan_required(self) -> None:
        client = _make_client(403, {"detail": "Requires team plan"})

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            client.push(_make_record())

        assert exc_info.value.response.status_code == 403

    def test_close_closes_underlying_client(self) -> None:
        client = _make_client(200)
        client.close()

        assert client._client.is_closed


class TestPushTracking:
    def test_write_marker_creates_file(self, tmp_path: Path) -> None:
        server_id = uuid.uuid4()
        marker = write_push_marker(tmp_path, server_id)

        assert marker.exists()
        assert marker.name == ".pushed"
        content = marker.read_text()
        assert str(server_id) in content

    def test_is_pushed_returns_true_when_marker_exists(self, tmp_path: Path) -> None:
        write_push_marker(tmp_path, uuid.uuid4())

        assert is_pushed(tmp_path) is True

    def test_is_pushed_returns_false_when_no_marker(self, tmp_path: Path) -> None:
        assert is_pushed(tmp_path) is False

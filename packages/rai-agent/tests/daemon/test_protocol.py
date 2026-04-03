"""Tests for WebSocket protocol frame types."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from rai_agent.daemon.protocol import (
    AuthChallengePayload,
    AuthRequestPayload,
    EventFrame,
    ReqFrame,
    ResFrame,
)


class TestReqFrame:
    def test_valid_req_frame(self) -> None:
        frame = ReqFrame(type="req", id="abc-123", method="auth")
        assert frame.type == "req"
        assert frame.id == "abc-123"
        assert frame.method == "auth"
        assert frame.params == {}

    def test_req_frame_with_params(self) -> None:
        frame = ReqFrame(type="req", id="x", method="run", params={"prompt": "hello"})
        assert frame.params == {"prompt": "hello"}

    def test_wrong_type_literal_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ReqFrame(type="res", id="x", method="auth")  # type: ignore[arg-type]

    def test_missing_id_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ReqFrame(type="req", method="auth")  # type: ignore[call-arg]

    def test_missing_method_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ReqFrame(type="req", id="x")  # type: ignore[call-arg]

    def test_roundtrip_json(self) -> None:
        frame = ReqFrame(type="req", id="x", method="run", params={"k": "v"})
        restored = ReqFrame.model_validate_json(frame.model_dump_json())
        assert restored == frame


class TestResFrame:
    def test_valid_success_response(self) -> None:
        frame = ResFrame(type="res", id="abc-123", ok=True)
        assert frame.ok is True
        assert frame.error is None
        assert frame.payload == {}

    def test_valid_error_response(self) -> None:
        frame = ResFrame(type="res", id="abc-123", ok=False, error="auth failed")
        assert frame.ok is False
        assert frame.error == "auth failed"

    def test_wrong_type_literal_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ResFrame(type="req", id="x", ok=True)  # type: ignore[arg-type]

    def test_roundtrip_json(self) -> None:
        frame = ResFrame(type="res", id="x", ok=False, error="oops")
        restored = ResFrame.model_validate_json(frame.model_dump_json())
        assert restored == frame


class TestEventFrame:
    def test_valid_event_frame(self) -> None:
        frame = EventFrame(type="event", event="auth_challenge", seq=0)
        assert frame.event == "auth_challenge"
        assert frame.seq == 0
        assert frame.state_version == 0
        assert frame.payload == {}

    def test_event_with_payload(self) -> None:
        frame = EventFrame(
            type="event",
            event="agent_message",
            payload={"content": "hello"},
            seq=42,
            state_version=3,
        )
        assert frame.payload == {"content": "hello"}
        assert frame.seq == 42
        assert frame.state_version == 3

    def test_wrong_type_literal_rejected(self) -> None:
        with pytest.raises(ValidationError):
            EventFrame(type="req", event="x", seq=0)  # type: ignore[arg-type]

    def test_seq_required(self) -> None:
        with pytest.raises(ValidationError):
            EventFrame(type="event", event="x")  # type: ignore[call-arg]

    def test_roundtrip_json(self) -> None:
        frame = EventFrame(type="event", event="x", seq=7, payload={"a": 1})
        restored = EventFrame.model_validate_json(frame.model_dump_json())
        assert restored == frame


class TestAuthPayloads:
    def test_auth_challenge_payload(self) -> None:
        payload = AuthChallengePayload(nonce="550e8400-e29b-41d4-a716-446655440000")
        assert len(payload.nonce) > 0

    def test_auth_request_payload(self) -> None:
        payload = AuthRequestPayload(token="base64sighere")
        assert payload.token == "base64sighere"

    def test_auth_challenge_missing_nonce(self) -> None:
        with pytest.raises(ValidationError):
            AuthChallengePayload()  # type: ignore[call-arg]

    def test_auth_request_missing_token(self) -> None:
        with pytest.raises(ValidationError):
            AuthRequestPayload()  # type: ignore[call-arg]

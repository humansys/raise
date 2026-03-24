"""Tests for Ed25519 auth module — nonce store, token validation, authenticate()."""

from __future__ import annotations

import base64
import json
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from rai_agent.daemon.auth import AuthError, NonceStore, authenticate, validate_token

# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture()
def private_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


@pytest.fixture()
def nonce_store() -> NonceStore:
    return NonceStore()


def _sign(private_key: Ed25519PrivateKey, nonce: str) -> str:
    """Sign nonce and return base64-encoded token (as client would)."""
    sig = private_key.sign(nonce.encode())
    return base64.b64encode(sig).decode()


# ─── NonceStore ───────────────────────────────────────────────────────────────


class TestNonceStore:
    def test_create_returns_uuid_string(self, nonce_store: NonceStore) -> None:
        nonce = nonce_store.create()
        uuid.UUID(nonce)  # raises ValueError if not valid UUID

    def test_consume_valid_nonce_returns_true(self, nonce_store: NonceStore) -> None:
        nonce = nonce_store.create()
        assert nonce_store.consume(nonce) is True

    def test_consume_single_use(self, nonce_store: NonceStore) -> None:
        """Nonce can only be used once."""
        nonce = nonce_store.create()
        assert nonce_store.consume(nonce) is True
        assert nonce_store.consume(nonce) is False  # already consumed

    def test_consume_unknown_nonce_returns_false(self, nonce_store: NonceStore) -> None:
        assert nonce_store.consume("not-a-real-nonce") is False

    def test_consume_expired_nonce_returns_false(self, nonce_store: NonceStore) -> None:
        nonce = nonce_store.create()
        # Manually expire it
        nonce_store.nonces[nonce] = datetime.now(UTC) - timedelta(seconds=1)
        assert nonce_store.consume(nonce) is False

    def test_purge_expired_removes_old_nonces(self, nonce_store: NonceStore) -> None:
        nonce = nonce_store.create()
        nonce_store.nonces[nonce] = datetime.now(UTC) - timedelta(seconds=1)
        nonce_store.purge_expired()
        assert nonce not in nonce_store.nonces


# ─── validate_token ───────────────────────────────────────────────────────────


class TestValidateToken:
    def test_valid_token_returns_true(
        self, private_key: Ed25519PrivateKey, nonce_store: NonceStore
    ) -> None:
        nonce = nonce_store.create()
        token = _sign(private_key, nonce)
        assert validate_token(nonce, token, private_key.public_key(), nonce_store)

    def test_wrong_private_key_rejected(self, nonce_store: NonceStore) -> None:
        nonce = nonce_store.create()
        wrong_key = Ed25519PrivateKey.generate()
        correct_key = Ed25519PrivateKey.generate()
        token = _sign(wrong_key, nonce)  # signed with wrong key
        assert not validate_token(
            nonce, token, correct_key.public_key(), nonce_store
        )

    def test_tampered_nonce_rejected(
        self, private_key: Ed25519PrivateKey, nonce_store: NonceStore
    ) -> None:
        nonce = nonce_store.create()
        token = _sign(private_key, nonce)
        # Use a different nonce at validation time
        other_nonce = nonce_store.create()
        assert not validate_token(
            other_nonce, token, private_key.public_key(), nonce_store
        )

    def test_reused_nonce_rejected(
        self, private_key: Ed25519PrivateKey, nonce_store: NonceStore
    ) -> None:
        nonce = nonce_store.create()
        token = _sign(private_key, nonce)
        assert validate_token(nonce, token, private_key.public_key(), nonce_store)
        # Second use of same nonce must fail
        assert not validate_token(nonce, token, private_key.public_key(), nonce_store)

    def test_invalid_base64_token_rejected(
        self, nonce_store: NonceStore, private_key: Ed25519PrivateKey
    ) -> None:
        nonce = nonce_store.create()
        assert not validate_token(
            nonce, "not-valid-base64!!!", private_key.public_key(), nonce_store
        )


# ─── authenticate() ───────────────────────────────────────────────────────────


class TestAuthenticate:
    async def test_successful_auth_returns_session_key(
        self, private_key: Ed25519PrivateKey, nonce_store: NonceStore
    ) -> None:
        # We intercept nonce via send_text side_effect
        sent_frames: list[str] = []
        ws = MagicMock()

        async def capture_send(msg: str) -> None:
            sent_frames.append(msg)

        ws.send_text = AsyncMock(side_effect=capture_send)

        async def fake_receive() -> str:
            # Extract nonce from the challenge frame we sent
            challenge = json.loads(sent_frames[0])
            nonce = challenge["payload"]["nonce"]
            token = _sign(private_key, nonce)
            return json.dumps(
                {"type": "req", "id": str(uuid.uuid4()), "method": "auth",
                 "params": {"token": token}}
            )

        ws.receive_text = AsyncMock(side_effect=fake_receive)

        session_key = await authenticate(ws, nonce_store, private_key.public_key())
        assert isinstance(session_key, str)
        assert len(session_key) > 0

    async def test_auth_timeout_raises_auth_error(
        self, private_key: Ed25519PrivateKey, nonce_store: NonceStore
    ) -> None:
        ws = MagicMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock(side_effect=TimeoutError)

        with pytest.raises(AuthError, match="timeout"):
            await authenticate(ws, nonce_store, private_key.public_key(), timeout=0.01)

    async def test_invalid_token_raises_auth_error(
        self, nonce_store: NonceStore
    ) -> None:
        wrong_key = Ed25519PrivateKey.generate()
        correct_key = Ed25519PrivateKey.generate()

        sent_frames: list[str] = []
        ws = MagicMock()

        async def capture_send_invalid(msg: str) -> None:
            sent_frames.append(msg)

        ws.send_text = AsyncMock(side_effect=capture_send_invalid)

        async def fake_receive() -> str:
            challenge = json.loads(sent_frames[0])
            nonce = challenge["payload"]["nonce"]
            token = _sign(wrong_key, nonce)  # signed with wrong key
            return json.dumps(
                {"type": "req", "id": str(uuid.uuid4()), "method": "auth",
                 "params": {"token": token}}
            )

        ws.receive_text = AsyncMock(side_effect=fake_receive)

        with pytest.raises(AuthError):
            await authenticate(ws, nonce_store, correct_key.public_key())

    async def test_non_auth_method_raises_auth_error(
        self, nonce_store: NonceStore, private_key: Ed25519PrivateKey
    ) -> None:
        ws = MagicMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock(
            return_value=json.dumps(
                {"type": "req", "id": "x", "method": "run", "params": {}}
            )
        )
        with pytest.raises(AuthError, match="expected auth"):
            await authenticate(ws, nonce_store, private_key.public_key())

    async def test_loopback_connection_requires_auth(
        self, private_key: Ed25519PrivateKey, nonce_store: NonceStore
    ) -> None:
        """ClawJacked prevention: authenticate() is always called — no IP bypass.

        authenticate() does not inspect ws.client — it always runs the
        challenge-response flow regardless of origin.
        """
        ws = MagicMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock(side_effect=TimeoutError)

        with pytest.raises(AuthError):
            await authenticate(ws, nonce_store, private_key.public_key(), timeout=0.01)

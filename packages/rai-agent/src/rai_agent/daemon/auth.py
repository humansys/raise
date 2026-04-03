"""Ed25519 challenge-response authentication for the Rai daemon.

Flow:
  1. Daemon sends EventFrame(auth_challenge, {nonce: uuid})
  2. Client signs nonce with its Ed25519 private key
  3. Client sends ReqFrame(auth, {token: base64(signature)})
  4. Daemon validates signature against configured public key

Security invariant (ClawJacked prevention):
  authenticate() is ALWAYS called — loopback origin is NOT exempt.
"""

from __future__ import annotations

import asyncio
import base64
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from cryptography.exceptions import InvalidSignature
from pydantic import ValidationError

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from rai_agent.daemon.protocol import (
    AuthChallengePayload,
    AuthRequestPayload,
    EventFrame,
    ReqFrame,
    ResFrame,
)

_NONCE_TTL = timedelta(seconds=30)
_AUTH_TIMEOUT = 10.0


class AuthError(Exception):
    """Raised when authentication fails for any reason."""


class NonceStore:
    """Single-use nonce registry with TTL expiry."""

    def __init__(self) -> None:
        self._nonces: dict[str, datetime] = {}  # nonce → expiry

    def create(self) -> str:
        """Generate a new single-use nonce and register it."""
        nonce = str(uuid.uuid4())
        self._nonces[nonce] = datetime.now(UTC) + _NONCE_TTL
        return nonce

    def consume(self, nonce: str) -> bool:
        """Return True and remove nonce if valid and unexpired. False otherwise."""
        expiry = self._nonces.pop(nonce, None)
        if expiry is None:
            return False
        return datetime.now(UTC) < expiry

    def purge_expired(self) -> None:
        """Remove all expired nonces. Call periodically to prevent memory growth."""
        now = datetime.now(UTC)
        self._nonces = {k: v for k, v in self._nonces.items() if v > now}

    @property
    def nonces(self) -> dict[str, datetime]:
        """Read/write access to the nonce registry. Exposed for testing."""
        return self._nonces


def validate_token(
    nonce: str,
    token: str,
    public_key: Ed25519PublicKey,
    nonce_store: NonceStore,
) -> bool:
    """Validate an Ed25519 token against a nonce.

    Consumes the nonce (single-use) before validating the signature.
    Returns False on any error — never raises.
    """
    if not nonce_store.consume(nonce):
        return False
    try:
        signature = base64.b64decode(token)
        public_key.verify(signature, nonce.encode())
        return True
    except (InvalidSignature, ValueError):
        return False


async def authenticate(
    websocket: Any,
    nonce_store: NonceStore,
    public_key: Ed25519PublicKey,
    timeout: float = _AUTH_TIMEOUT,
) -> str:
    """Perform challenge-response auth handshake.

    Sends auth_challenge event, waits for auth ReqFrame, validates token.
    Returns session_key string on success. Raises AuthError on any failure.

    SECURITY: Called for ALL connections regardless of origin (loopback included).
    """
    nonce = nonce_store.create()

    challenge = EventFrame(
        type="event",
        event="auth_challenge",
        payload=AuthChallengePayload(nonce=nonce).model_dump(),
        seq=0,
    )
    await websocket.send_text(challenge.model_dump_json())

    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=timeout)
    except TimeoutError:
        raise AuthError(f"auth timeout — no response within {timeout}s") from None

    try:
        req = ReqFrame.model_validate_json(raw)
    except ValidationError as exc:
        raise AuthError(f"invalid frame: {exc}") from exc

    if req.method != "auth":
        raise AuthError(f"expected auth method, got {req.method!r}")

    try:
        auth_payload = AuthRequestPayload.model_validate(req.params)
    except ValidationError as exc:
        raise AuthError(f"invalid auth params: {exc}") from exc

    if not validate_token(nonce, auth_payload.token, public_key, nonce_store):
        raise AuthError("invalid token — signature verification failed")

    # Send auth success — auth flow fully owned by authenticate()
    success = ResFrame(type="res", id=req.id, ok=True)
    await websocket.send_text(success.model_dump_json())

    return req.id  # session_key: refined in S2.3 with full session scheme

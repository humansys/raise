# E616: raise-server License MVP — Design

## Gemba (Current State)

raise-server is a FastAPI application with:
- **DB**: PostgreSQL 16 via SQLAlchemy 2.0 async + Alembic (2 migrations)
- **Auth**: API key (SHA-256 hash, per-org, `Bearer rsk_...`)
- **Tables**: organizations, api_keys, graph_nodes, graph_edges, agent_events, memory_patterns
- **Endpoints**: health, graph (sync/query), memory (patterns), agent (events)
- **Deploy**: Docker multi-stage + docker-compose (postgres + server)
- **Pattern**: thin routers → services → queries. Stateless services, session_factory injected.
- **Config**: pydantic-settings, `RAI_*` env vars

No license infrastructure exists. All endpoints require only API key auth (org-scoped).

## Target Components

### New: `raise_server.db.models.LicenseRow`

```
licenses table:
  id          UUID PK
  org_id      FK → organizations
  key_hash    String(128)    -- SHA-256 of raw license key
  prefix      String(12)     -- first 12 chars for identification
  plan        String(20)     -- "pro", "team", "enterprise"
  features    JSONB          -- ["jira", "confluence", "odoo", "gitlab"]
  seats       Integer        -- max concurrent activations
  status      String(20)     -- "active", "expired", "revoked"
  expires_at  DateTime(tz)
  created_at  DateTime(tz)
  updated_at  DateTime(tz)
```

### New: `raise_server.db.models.ActivationRow`

```
activations table:
  id          UUID PK
  license_id  FK → licenses
  org_id      FK → organizations
  machine_id  String(255)    -- optional, for future fingerprinting
  activated_at DateTime(tz)
  last_seen_at DateTime(tz)  -- for seat counting
```

### New: `raise_server.services.license`

Service layer:
- `activate_license(session_factory, key, machine_id?) → LicenseActivation`
- `generate_license(session_factory, org_id, plan, features, seats, expires_at) → LicenseKey`
- `validate_license(session_factory, key) → LicenseStatus`

### New: `raise_server.api.v1.license`

Router `/api/v1/license`:
- `POST /activate` — public (no API key needed, license key IS the auth)
- `POST /generate` — admin only (requires API key)
- `GET /validate` — public (verify a key is still valid)

### New: `raise_server.crypto`

JWT signing/verification:
- Ed25519 key pair (private key in env var, public key embedded in raise-cli)
- `sign_license_jwt(claims) → str`
- `verify_license_jwt(token) → dict | None`

### Modified: `raise_server.config.ServerConfig`

New fields:
- `license_private_key: str` — Ed25519 private key (PEM, base64, or file path)
- `license_public_key: str` — Ed25519 public key (for self-verification)

### Modified: `raise_server.app.create_app`

Register new router: `license_router`.

## Key Contracts

### POST /api/v1/license/activate

```
Request:
  { "key": "rai_pro_xxxxxxxx" }

Response 200:
  {
    "token": "<signed JWT>",
    "plan": "pro",
    "features": ["jira", "confluence", "odoo", "gitlab"],
    "org": "humansys",
    "expires_at": "2027-03-25T00:00:00Z"
  }

Response 401:
  { "detail": "Invalid or expired license key" }

Response 409:
  { "detail": "Seat limit reached (5/5 active)" }
```

### POST /api/v1/license/generate (admin)

```
Request (requires Bearer rsk_... API key):
  {
    "plan": "pro",
    "features": ["jira", "confluence"],
    "seats": 5,
    "expires_at": "2027-03-25T00:00:00Z"
  }

Response 201:
  {
    "key": "rai_pro_a8f3c9...",
    "prefix": "rai_pro_a8f3",
    "plan": "pro",
    "seats": 5,
    "expires_at": "2027-03-25T00:00:00Z"
  }
```

### JWT Claims (signed EdDSA)

```json
{
  "sub": "org:humansys",
  "plan": "pro",
  "features": ["jira", "confluence", "odoo", "gitlab"],
  "seats": 5,
  "iat": 1711900000,
  "exp": 1743436000,
  "iss": "raise-server"
}
```

## Architectural Decisions

### D1: License activation is public (no API key)

The license key itself is the credential. Requiring an API key too would mean
clients need two secrets. The activation endpoint validates the license key
hash against the DB — same pattern as JetBrains activation codes.

### D2: Ed25519 for JWT signing (not RS256)

Ed25519 keys are 32 bytes (vs 2048+ bit RSA). Faster signing, smaller keys.
PyJWT supports EdDSA via `cryptography` (already a raise-pro dependency).
The public key can be embedded directly in the raise-cli package.

### D3: Separate `activations` table for seat tracking

Instead of a simple counter on `licenses`, track individual activations with
`machine_id` and `last_seen_at`. This enables:
- Accurate seat counting (deactivation, stale seat cleanup)
- Future machine fingerprinting (V2)
- Audit trail of who activated when

### D4: License keys use typed prefix `rai_{plan}_`

Format: `rai_pro_<32 hex chars>` (total ~42 chars).
Benefits: human-readable plan, easy to identify in logs, prefix stored for DB lookup.

### D5: No phone-home in MVP

JWT is self-contained and offline-verifiable. The server only participates
at activation time. Renewal = admin generates new key, client re-activates.
Phone-home adds complexity without blocking client onboarding.

## Story Breakdown (Revised)

### S616.1: Alembic migration + license model (S)

Migration 003: `licenses` and `activations` tables. SQLAlchemy models.
Pydantic schemas for API request/response. No endpoints yet — just DB layer.

**Size:** S (migration + models + schemas + tests)
**Dependencies:** None

### S616.2: Crypto module + license service (M)

Ed25519 key pair management. JWT signing/verification. License service:
activate, generate, validate. Unit tests with in-memory DB.

**Size:** M (crypto + service logic + tests)
**Dependencies:** S616.1

### S616.3: License API endpoints (S)

Router with POST /activate, POST /generate, GET /validate.
Thin handlers delegating to service. Integration tests.

**Size:** S (thin handlers + integration tests)
**Dependencies:** S616.2

### S616.4: Deployment and seed (S)

Docker config updated. Env vars for Ed25519 keys. Seed script for first
org + license. Alembic migration in Docker entrypoint. Deployment docs.

**Size:** S (DevOps + docs)
**Dependencies:** S616.3

## Dependency Graph

```
S616.1 (migration/models)
    ↓
S616.2 (crypto + service)
    ↓
S616.3 (API endpoints)
    ↓
S616.4 (deploy + seed)
```

Linear chain — no parallelism, but each story is independently testable.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Ed25519 key management complexity | Medium | High | Use env var for private key, embed public key as constant. No file-based key management in MVP. |
| Seat counting race conditions | Low | Medium | Use DB-level unique constraint on (license_id, machine_id). Count at activation time, not validation. |
| Migration conflicts with other epics | Low | Low | Linear Alembic chain, migration 003 is next in sequence. |

## Deferred (Parking Lot)

- Phone-home renewal with JWT refresh (promote when clients report expiry friction)
- License revocation list / CRL (promote when client count > 20)
- Usage telemetry per license (promote when billing needs usage data)
- Admin web console (promote when manual SQL/API becomes burden)

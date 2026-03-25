# E616: raise-server License MVP — Scope

**Jira:** RAISE-616
**Labels:** pro-launch, v2.4
**Branch:** dev (stories branch from dev)
**Depends on:** None (E621 depends on this)
**Design:** [design.md](design.md)

## Objective

Add server-side license management to raise-server: key generation, activation
with signed JWT issuance, and seat tracking. This is the backend counterpart
to RAISE-621 (CLI-side licensing).

## In Scope

- Alembic migration 003: `licenses` + `activations` tables
- Ed25519 crypto module for JWT signing/verification
- License service: generate, activate, validate
- `POST /api/v1/license/activate` — public, key → signed JWT
- `POST /api/v1/license/generate` — admin (API key required)
- `GET /api/v1/license/validate` — public, verify key status
- License key format: `rai_{plan}_{32 hex}` (typed prefix)
- Seat tracking via activations table
- Docker deployment with Ed25519 key config
- Seed script for first client org + license

## Out of Scope

- CLI commands (`rai activate`, etc.) — that's E621
- Entry point gating / graceful degradation — that's E621
- Web admin console (seed via API/SQL for now)
- Phone-home renewal / automatic JWT refresh
- Machine fingerprinting
- Payment/billing integration
- License revocation CRL (manual DB update if needed)

## Stories (Revised from Design)

### S616.1: Alembic migration + license models (S)

Migration 003: `licenses` and `activations` tables. SQLAlchemy models
(`LicenseRow`, `ActivationRow`). Pydantic schemas for API request/response.
No endpoints yet — DB layer only.

**Dependencies:** None

### S616.2: Crypto module + license service (M)

Ed25519 key pair management (env var config). JWT signing/verification
module. License service: `activate_license`, `generate_license`,
`validate_license`. Unit tests with in-memory DB.

**Dependencies:** S616.1

### S616.3: License API endpoints (S)

Router `/api/v1/license` with three endpoints: activate (public),
generate (admin), validate (public). Thin handlers delegating to service.
Integration tests.

**Dependencies:** S616.2

### S616.4: Deployment and seed (S)

Docker config updated for Ed25519 key env vars. Seed script for first
org + license key. Alembic migration in entrypoint. Deployment docs.

**Dependencies:** S616.3

## Done Criteria

- [ ] `licenses` and `activations` tables exist via migration 003
- [ ] `POST /license/activate` returns valid signed JWT (EdDSA)
- [ ] `POST /license/generate` creates new license key (admin only)
- [ ] `GET /license/validate` reports license status
- [ ] Seat tracking limits concurrent activations
- [ ] Ed25519 private key configurable via env var
- [ ] Public key extractable for embedding in raise-cli (E621)
- [ ] raise-server deployed and accessible for first clients
- [ ] First client org + license seeded

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

## Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S616.1 Migration + models | pending | |
| S616.2 Crypto + service | pending | |
| S616.3 API endpoints | pending | |
| S616.4 Deploy + seed | pending | |

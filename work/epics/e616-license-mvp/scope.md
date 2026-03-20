# E616: raise-server License MVP — Scope

**Jira:** RAISE-616
**Label:** pro-launch
**Branch:** dev (stories branch from dev)

## Objective

Add license management to raise-server: issuance, activation, and validation.
Enable raise-pro to check licenses at runtime with graceful degradation.

## In Scope

- Alembic migration: `licenses` table (org_id, tier, seats, expires_at, key_hash)
- `POST /api/v1/license/activate` endpoint (key → signed JWT)
- `GET /api/v1/license/validate` endpoint (JWT → validity + entitlements)
- `rai license activate <KEY>` CLI command in raise-cli
- License check decorator for raise-pro entry points
- Graceful degradation (no license → stub commands with upgrade message)
- JWT signing with Ed25519 (offline validation with public key)
- Deploy raise-server (Docker) for first clients

## Out of Scope

- Web admin console (seed via API/SQL)
- Phone-home renewal / automatic refresh
- Machine fingerprinting
- Payment/billing integration (Stripe, Paddle)
- Per-feature entitlements (tier-based only for MVP)
- License revocation (manual DB update if needed)

## Stories (Planned)

### S616.1: License migration and activation endpoint (M)

Alembic migration 003 for licenses table. `POST /api/v1/license/activate`
receives key, validates, registers seat, returns signed JWT (Ed25519).
`GET /api/v1/license/validate` for health checks.

**Dependencies:** None

### S616.2: `rai license activate` CLI command (S)

New CLI command group `rai license`. `activate <KEY>` calls server endpoint,
stores JWT to `~/.raise/license.key`. `status` shows current license info.

**Dependencies:** S616.1

### S616.3: License check on raise-pro entry points (S)

License loader in raise-cli (reads `~/.raise/license.key`, verifies JWT signature
with embedded public key). Decorator `@requires_license(tier)` for raise-pro
commands. Stub commands when license missing/expired/insufficient tier.

**Dependencies:** S616.2

### S616.4: raise-server Docker deployment (S)

Production-ready Docker Compose for raise-server. Environment config,
TLS, seed script for first org + license. Deployment documentation.

**Dependencies:** S616.1

## Done Criteria

- [ ] `licenses` table exists with migration
- [ ] Activation endpoint issues valid signed JWT
- [ ] `rai license activate` stores JWT locally
- [ ] `rai license status` shows tier, org, expiry
- [ ] raise-pro commands check license at invocation time
- [ ] Missing license shows "upgrade to Pro" message (not crash)
- [ ] JWT validates offline with public key
- [ ] raise-server deployed and accessible
- [ ] First client org + license seeded

## Architecture Notes

### License JWT Claims

```json
{
  "sub": "org:humansys",
  "tier": "pro",
  "seats": 10,
  "iat": 1711000000,
  "exp": 1742536000
}
```

### Validation Flow

```
rai license activate <KEY>
    → POST /api/v1/license/activate {key, machine_id?}
    ← JWT signed with Ed25519 private key
    → stored at ~/.raise/license.key

rai backlog search "..."
    → raise-pro entry point loads
    → license_loader reads ~/.raise/license.key
    → verifies signature with public key (offline)
    → checks tier >= required
    → proceeds or shows upgrade message
```

### Tier Model (MVP)

| Tier | Entitlements |
| ---- | ------------ |
| community | raise-cli (no license needed) |
| pro | + raise-pro adapters (Jira, Confluence, Odoo, GitLab) |
| team | + raise-server (governance, metrics, cross-repo graphs) |
| enterprise | + raise-agent, SSO, audit |

## Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S616.1 License migration + endpoint | pending | |
| S616.2 CLI command | pending | |
| S616.3 Entry point check | pending | |
| S616.4 Server deployment | pending | |

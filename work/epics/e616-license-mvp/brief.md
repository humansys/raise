# E616: raise-server License MVP — Brief

## Hypothesis

Adding a minimal license management layer to raise-server (licenses table, activation
endpoint, CLI command, entry point check) will enable per-client, per-tier licensing
of raise-pro features with offline-capable JWT tokens, providing the foundation for
the raise commercial model.

## Problem

raise-pro has zero runtime access control. Once installed, all features are available
to anyone. For a commercial product, we need:
- Per-org licensing with tier-based entitlements
- Offline-capable validation (devs work air-gapped, CI has no internet)
- Minimal DX friction (one activation, then forget about it)
- Foundation for raise-server, raise-agent licensing later

raise-server exists as a PoC with FastAPI, PostgreSQL, API key auth, and graph/memory
endpoints. It needs a license management layer.

## Appetite

Small — 3-4 stories. The server infrastructure exists; this adds a domain (licenses)
with one migration, one endpoint, one CLI command, and one decorator.

## Success Metrics

1. `rai license activate <KEY>` stores a signed JWT in `~/.raise/license.key`
2. raise-pro entry points check license at command invocation (not import)
3. Missing/expired license → graceful "upgrade to Pro" message, not crash
4. License works fully offline after activation (JWT verified with public key)
5. raise-server deployed and accessible for first clients

## Rabbit Holes

- Don't build a web console — seed licenses via SQL/API for now
- Don't build phone-home renewal yet — static JWT with expiry is enough
- Don't build machine fingerprinting — org+tier+expiry is the MVP
- Don't build payment integration — manual license issuance

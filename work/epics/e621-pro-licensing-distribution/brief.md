# E621: raise-pro CLI — Licensing & Distribution MVP — Brief

## Hypothesis

Implementing Nx Powerpack-style license activation in raise-pro (offline JWT validation
with embedded public key) combined with GitLab Package Registry distribution will enable
controlled onboarding of paying clients without building complex SaaS infrastructure.

## Problem

raise-pro is a functional CLI plugin with no access control or distribution mechanism.
It publishes to public PyPI alongside raise-cli. First Pro clients need:
- A way to install raise-pro that is access-controlled and revocable
- License activation that works offline after initial setup
- Graceful degradation when license is missing/expired (not crashes)
- Legal clarity on the source-available license

## Appetite

Medium — 4-6 stories. Spans CLI activation, JWT validation, entry point gating,
private distribution, FSL headers, and documentation. Target: 2 weeks (Mar 28 - Apr 10).

## Success Metrics

1. `rai activate LICENSE_KEY` stores signed JWT locally
2. raise-pro commands check license at invocation time (not import)
3. Missing/expired license shows upgrade message, never crashes
4. raise-pro installable only via authenticated GitLab Package Registry
5. FSL 1.1-ALv2 headers on all raise-pro source files
6. Client onboarding documentation complete

## Rabbit Holes

- Don't build phone-home renewal — static JWT with expiry is enough for MVP
- Don't integrate Keygen.sh — custom JWT is simpler and zero-cost
- Don't build machine fingerprinting — org+plan+expiry is sufficient
- Don't build self-service key generation — admin seeds via RAISE-616 server API
- Don't build a trial flow yet — manual key issuance for first clients

## Dependencies

- **RAISE-616** (raise-server license MVP): server must emit signed JWTs before
  CLI can activate against it. E616 provides `POST /license/activate` endpoint.

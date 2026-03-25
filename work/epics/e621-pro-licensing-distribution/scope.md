# E621: raise-pro CLI — Licensing & Distribution MVP — Scope

**Jira:** RAISE-621
**Labels:** pro-launch, licensing, raise-pro, mvp-apr16
**Branch:** dev (stories branch from dev)
**Depends on:** RAISE-616 (raise-server license MVP)

## Objective

Implement license activation, offline JWT validation, entry point gating, and private
distribution for raise-pro CLI. Inspired by Nx Powerpack model.

## In Scope

- `rai activate LICENSE_KEY` CLI command — calls E616 server, stores JWT
- `rai doctor --check license` — license status diagnostic
- License loader in raise-cli (reads `~/.raise/license.key`, verifies EdDSA signature)
- `@requires_license(plan)` decorator for raise-pro entry points
- Graceful degradation: valid → warning (30d) → expired → upgrade prompt
- JWT claims: sub, plan, features, exp, iat, iss
- Public key embedded in raise-cli for offline validation
- GitLab Package Registry: publish raise-pro with deploy tokens
- FSL 1.1-ALv2 license headers on raise-pro source files
- Entry point stub commands when raise-pro not installed
- Client installation and activation documentation

## Out of Scope (V2)

- License server with phone-home renewal (E616 covers static issuance only)
- Keygen.sh integration
- Machine fingerprinting
- Automatic key rotation
- Self-service key generation portal
- Trial activation flow

## Relationship with RAISE-616

```
RAISE-616 (server)                    RAISE-621 (CLI)
─────────────────                     ───────────────
licenses table                        rai activate KEY
POST /license/activate ──JWT──→       store ~/.raise/license.key
POST /license/generate                license_loader (verify EdDSA)
Docker deploy                         @requires_license decorator
                                      GitLab Package Registry
                                      FSL headers + docs
```

## Stories (Planned)

### S621.1: License loader and JWT validation in raise-cli (M)

License loader module in raise-cli: reads `~/.raise/license.key`, verifies
EdDSA signature with embedded public key, parses claims (sub, plan, features,
exp). Returns LicenseInfo or None. Zero external dependencies beyond PyJWT.

**Dependencies:** None (can develop against test JWTs)

### S621.2: `rai activate` CLI command (S)

New CLI command: `rai activate LICENSE_KEY`. Calls E616 server endpoint
`POST /api/v1/license/activate`, receives signed JWT, stores to
`~/.raise/license.key`. Shows license info on success. `rai license status`
subcommand for current license info.

**Dependencies:** S621.1, RAISE-616 S616.1

### S621.3: Entry point gating and graceful degradation (S)

`@requires_license(plan)` decorator for raise-pro commands. Stub commands
in raise-cli for known pro features when raise-pro not installed. Degradation
levels: valid → warning (expires <30d) → grace (expired <7d) → block.

**Dependencies:** S621.1

### S621.4: GitLab Package Registry and private distribution (S)

Modify release workflow to exclude raise-pro from public PyPI. Configure
GitLab Package Registry publish. Create deploy tokens per client. Verify
uv/pip install with authenticated index URL.

**Dependencies:** None (DevOps/config)

### S621.5: FSL license headers and client documentation (XS)

Add FSL 1.1-ALv2 license headers to all raise-pro source files. Create
client onboarding guide: installation, activation, verification, troubleshooting.

**Dependencies:** S621.4

## Done Criteria

- [ ] `rai activate KEY` stores valid JWT locally
- [ ] License validates offline with embedded public key
- [ ] raise-pro commands check license at invocation (not import)
- [ ] Missing/expired license shows upgrade message (not crash)
- [ ] Graceful degradation with warning → grace → block levels
- [ ] raise-pro NOT published to public PyPI
- [ ] raise-pro installable via authenticated GitLab Package Registry
- [ ] FSL 1.1-ALv2 headers on raise-pro source files
- [ ] Client onboarding documentation complete
- [ ] `rai doctor --check license` reports license status

## Architecture Notes

### JWT Claims

```json
{
  "sub": "org:humansys",
  "plan": "pro",
  "features": ["jira", "confluence", "odoo", "gitlab"],
  "iat": 1711900000,
  "exp": 1743436000,
  "iss": "raise-server"
}
```

### Tier Model (MVP)

| Plan | Entitlements |
| ---- | ------------ |
| community | raise-cli (no license needed) |
| pro | + raise-pro adapters (Jira, Confluence, Odoo, GitLab) |
| team | + raise-server (governance, metrics, cross-repo graphs) |
| enterprise | + raise-agent, SSO, audit |

## Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S621.1 License loader + JWT | pending | |
| S621.2 rai activate CLI | pending | |
| S621.3 Entry point gating | pending | |
| S621.4 GitLab Registry | pending | |
| S621.5 FSL headers + docs | pending | |

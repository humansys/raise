# E621: raise-pro CLI — Licensing & Distribution MVP — Scope

**Jira:** RAISE-621
**Labels:** pro-launch, licensing, raise-pro, mvp-apr16
**Branch:** dev (stories branch from dev)
**Depends on:** RAISE-616 (raise-server license MVP)
**Design:** [design.md](design.md) (pending — E616 design drives architecture)

## Objective

Configure raise-pro for client distribution via private GitLab Package Registry,
implement `rai configure` for server connection setup, and add CLI-side plan
enforcement that delegates to raise-server. Add FSL legal headers and client docs.

## Key Insight: Always-Connected

raise-pro requires raise-server for its features. License validation is server-side
(E616). The CLI does NOT validate licenses locally — it just needs to be configured
to talk to the server, and the server handles auth + plan checks.

## In Scope

- `rai configure --server URL --key KEY` — stores server URL + API key in `~/.raise/config.yaml`
- `rai license status` — queries server for current member's plan + features
- `rai doctor --check license` — license status diagnostic
- CLI-side plan error handling (403 from server → clear upgrade message)
- GitLab Package Registry: publish raise-pro with deploy tokens
- FSL 1.1-ALv2 license headers on raise-pro source files
- Entry point stub commands when raise-pro not installed
- Client onboarding documentation (install + configure + verify)

## Out of Scope

- License validation logic (server-side, E616)
- JWT / offline crypto (eliminated by always-connected model)
- Admin member management (server-side, E616)
- Keygen.sh, machine fingerprinting, payment integration

## Relationship with RAISE-616 (Revised)

```
RAISE-616 (server)                    RAISE-621 (CLI)
─────────────────                     ───────────────
members table + auth                  rai configure --server --key
licenses table + plan check           rai license status (queries server)
requires_plan() middleware            403 → "Requires Pro plan" message
POST /admin/members                   rai doctor --check license
POST /admin/license/generate          GitLab Package Registry
                                      FSL headers + client docs
```

## Stories (Revised)

### S621.1: `rai configure` and server connection (S)

`rai configure --server URL --key KEY` stores connection info in
`~/.raise/config.yaml`. raise-pro HTTP client reads config to connect
to raise-server. `rai configure status` shows connection info.

**Dependencies:** RAISE-616 S616.2 (server must accept member API keys)

### S621.2: CLI plan error handling and `rai license status` (S)

Handle 403 responses from server with clear plan upgrade messages.
`rai license status` queries server for member info (plan, features,
org, expiry). `rai doctor --check license` diagnostic.

**Dependencies:** S621.1, RAISE-616 S616.2

### S621.3: GitLab Package Registry and private distribution (S)

Modify release workflow to exclude raise-pro from public PyPI. Configure
GitLab Package Registry publish. Create deploy tokens per client. Verify
uv/pip install with authenticated index URL.

**Dependencies:** None (DevOps/config, can run in parallel)

### S621.4: FSL license headers and client documentation (XS)

Add FSL 1.1-ALv2 license headers to all raise-pro source files. Create
client onboarding guide: install, configure, verify, troubleshoot.

**Dependencies:** S621.3

## Done Criteria

- [ ] `rai configure --server --key` stores connection config
- [ ] raise-pro talks to raise-server using stored config
- [ ] 403 from server → clear "Requires X plan" CLI message
- [ ] `rai license status` shows plan, features, org, expiry
- [ ] `rai doctor --check license` reports license health
- [ ] raise-pro NOT published to public PyPI
- [ ] raise-pro installable via authenticated GitLab Package Registry
- [ ] FSL 1.1-ALv2 headers on raise-pro source files
- [ ] Client onboarding documentation complete

## Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S621.1 rai configure | pending | |
| S621.2 Plan error handling + status | pending | |
| S621.3 GitLab Registry | pending | can run parallel |
| S621.4 FSL headers + docs | pending | |

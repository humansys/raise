# Epic E352: rai doctor — Scope

> **Status:** IN PROGRESS
> **Release:** 2.2.0a1
> **Created:** 2026-03-05

## Objective

Give every RaiSE user a single command (`rai doctor`) that diagnoses their setup, reports actionable problems, and lets them send a bug report — so they never need to ask an expert why something isn't working.

**Value:** Unblocks self-service onboarding, reduces support load, makes the upgrade path (2.1 -> 2.2) seamless via built-in config migration. Prerequisite for open source release.

## Stories (5 stories)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S352.1 | Check infrastructure | S | Pending | DoctorCheck protocol, CheckRegistry, CLI surface (`rai doctor`) |
| S352.2 | Environment checks | S | Pending | Python version, rai-cli version, OS, installed extras, optional deps |
| S352.3 | Project checks | M | Pending | .raise/ structure, manifest coherence, graph staleness, adapter config, MCP health, skill sync |
| S352.4 | Auto-fix | S | Pending | `rai doctor --fix` with backup — stale graph rebuild, missing config scaffold |
| S352.5 | Bug report via email | S | Pending | `rai doctor report` generates local .md, `--send` opens mailto: link to JSM |

**Total:** 5 stories

## Scope

**In scope (MUST):**
- `rai doctor` — run all checks, show only problems (silent when healthy)
- `rai doctor -v` — verbose, show all checks including passing
- `rai doctor --json` — JSON output for CI (exit code 0/1)
- `rai doctor report` — generate diagnostic report to local file
- `rai doctor report --send` — open mailto: link with pre-filled report
- 3-level severity: pass / warning / error
- Check registry via `rai.doctor.checks` entry points

**In scope (SHOULD):**
- `rai doctor --fix` — auto-remediate common issues (stale graph, missing config)
- `rai doctor <category>` — run single category by name
- Config migration detection (older version -> current)

**Out of scope:**
- Interactive repair wizard -> deferred to post-2.2
- Dimensional scoring (score per area) -> deferred, P9 in research
- Online checks (Jira connectivity, MCP server health) as default -> behind `--online` flag
- Sentry-style telemetry -> not appropriate for CLI tool, privacy

## Done Criteria

**Per story:**
- [ ] Code with type annotations
- [ ] Tests passing (RED-GREEN)
- [ ] Quality checks pass (ruff, pyright)

**Epic complete:**
- [ ] All stories complete (S352.1-S352.5)
- [ ] `rai doctor` runs clean on raise-commons
- [ ] `rai doctor` runs clean on la-aldea-erp (portability)
- [ ] `rai doctor report --send` opens email client with correct content
- [ ] Epic retrospective done
- [ ] Merged to `dev`

## Dependencies

```
S352.1 (check infra + CLI)
  |
  +---> S352.2 (environment checks)
  |       |
  +---> S352.3 (project checks)
  |       |
  +-------+---> S352.4 (auto-fix, needs checks to exist)
  |
  +---> S352.5 (report, only needs S352.1 CLI surface)
```

S352.2 and S352.3 are parallel after S352.1.
S352.4 depends on S352.2 + S352.3 (needs checks to fix).
S352.5 only depends on S352.1 (CLI surface + check results).

**External:** None

## Architecture

| Decision | ADR | Summary |
|----------|-----|---------|
| Check protocol (not gate reuse) | ADR-052 | Separate domain: gates validate user products, doctor validates RaiSE itself. Same pattern, own entry points. |
| Email for bug reports (not API) | D-RPT-1 | mailto: link, no embedded credentials. User sees what they send. JSM email channel as backend. |
| Never touch secrets | D-RPT-2 | Report collects only non-sensitive data. Lesson from OpenClaw redaction bugs. |

> Research: `dev/research/e352-doctor-research.md`
> Problem Brief: RAISE-312

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| mailto: body too long for some email clients | M/M | Truncate to essentials, full report in local .md file |
| Check execution too slow (MCP health, adapter checks) | M/L | Online checks behind `--online` flag, default is local-only |
| Config migration breaks existing setups | L/H | `--fix` creates `.bak` backup before any mutation |

## Parking Lot

- Dimensional scoring (score per area) -> E352 v2 or separate epic
- Interactive repair wizard -> post open-source feedback
- Plugin checks (third-party extensions) -> after plugin ecosystem exists

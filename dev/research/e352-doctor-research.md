# Research: E352 rai doctor — Competitive Analysis

> Evidence catalog for epic design. 2026-03-05.
> Triangulated across 8 tools, 3 categories.

## 1. AI Coding Agents

### Claude Code `/doctor` (builtin)

- **Checks**: 5-8 in <15s — install state, auth, network, env compatibility
- **Output**: Green/red per check, actionable suggestions ("run `/login` to fix")
- **Pattern**: Linear checks, pass/fail, no categories
- **Source**: [Troubleshooting docs](https://code.claude.com/docs/en/troubleshooting)

### cc-health-check (community, by Yurukusa)

- **Checks**: 20 questions, scores across 6 dimensions (safety, automation, monitoring, recovery)
- **Implementation**: ~300 lines Node.js, zero deps, scans settings.json + CLAUDE.md
- **Pattern**: Multi-dimensional scoring, not just pass/fail
- **Source**: [cc-health-check](https://yurukusa.github.io/cc-health-check/)

### OpenClaw `openclaw doctor` (gold standard)

- **Architecture**: Multi-phase pipeline with dependency ordering:
  ```
  config migration -> auth health -> state integrity -> sandbox/service -> workspace -> gateway -> final config write
  ```
- **3 primary functions**:
  1. Config Migration — migrates legacy keys, normalizes schema to current version
  2. State Repair — detects/repairs on-disk inconsistencies (sessions, creds, permisos)
  3. System Audit — validates gateway, sandbox images, auth profiles, supervisor configs
- **Check categories**: source install, OAuth/auth, Docker/sandbox, supervisor, workspace
- **Flags**: `--fix` (auto-remediation with `.bak` backup), TTY-aware (skip interactive in headless)
- **Source structure**:
  ```
  src/commands/doctor-config-flow.ts
  src/commands/doctor-state-integrity.ts
  src/commands/doctor-state-migrations.ts
  ```
- **Source**: [OpenClaw Doctor docs](https://docs.openclaw.ai/gateway/doctor), [DeepWiki](https://deepwiki.com/openclaw/openclaw/14.2-doctor-command-guide)

### Cursor

- **Tool**: `cursor --diag` — dumps diagnostic info to file
- **Pattern**: Log dump for support, not interactive checks
- **Source**: [Troubleshooting](https://cursor.com/docs/troubleshooting/troubleshooting-guide)

### Aider, Cline, OpenHands

- **No doctor command**. Manual troubleshooting via docs only.

## 2. Package Manager Gold Standards

### Homebrew `brew doctor`

- **Architecture**: Registry of `check_*` methods in `diagnostic.rb`, auto-discovered
- **Pattern**: Silent by default (only warns). `--list-checks` to enumerate. Individual checks as args.
- **Exit codes**: 0 = healthy, 1 = issues (CI-friendly)
- **Extensibility**: OS-specific modules (`extend/os/mac/diagnostic.rb`)
- **Source**: [diagnostic.rb](https://github.com/Homebrew/brew/blob/master/Library/Homebrew/diagnostic.rb), [doctor.rb](https://github.com/Homebrew/brew/blob/master/Library/Homebrew/cmd/doctor.rb)

### Flutter `flutter doctor`

- **Severity levels**: pass / warning / error (3-level, not boolean)
- **Categories**: SDK, IDE, plugins, devices, dependencies — each a "validator"
- **Verbose mode**: `flutter doctor -v` shows all checks, default shows only problems
- **Third-party validators**: Plugin authors can register custom validators
- **Source**: [Flutter doctor guide](https://flutterfever.com/flutter-doctor-command/)

## 3. Extracted Patterns

| # | Pattern | Origin | Confidence |
|---|---------|--------|------------|
| P1 | **Check registry** — convention-named methods, auto-discovered | brew | Very High |
| P2 | **3-level severity** — pass/warning/error, not boolean | flutter | Very High |
| P3 | **Pipeline with deps** — config valid before state checks, state before gateway | OpenClaw | High |
| P4 | **Migration = Doctor** — doctor should migrate config between versions | OpenClaw | High |
| P5 | **`--fix` with backup** — auto-remediation creates `.bak` first | OpenClaw | High |
| P6 | **Silent default** — only show problems, `-v` for everything | brew | High |
| P7 | **Actionable output** — each failure suggests a fix command | Claude Code | High |
| P8 | **Exit codes** — 0/1 for CI integration | brew | High |
| P9 | **Dimensional scoring** — score per area, not just pass/fail | cc-health-check | Medium |
| P10 | **TTY-aware** — skip interactive prompts in headless/CI | OpenClaw | Medium |
| P11 | **Individual checks** — run single check by name | brew | Medium |

## 4. Recommendation for `rai doctor`

### Must-have (P1-P8)

```
$ rai doctor
Environment    Python 3.12.3, rai-cli 2.2.0a1, OS linux
Project        .raise/ valid, manifest.yaml coherent
[!] Adapters   Jira configured but JIRA_API_TOKEN not set
[x] Graph      Stale -- last built 3 days ago, 2 files changed
Skills         12/12 synced, no stale deployments
[!] MCP        context7 healthy, jira unhealthy (timeout)

2 warnings, 1 error. Run 'rai doctor --fix' for auto-remediation.
```

### Architecture

```
src/rai_cli/doctor/
    __init__.py
    registry.py        # Check registry (P1) -- auto-discover check_* functions
    models.py          # CheckResult(status, message, fix_hint) (P2, P7)
    pipeline.py        # Ordered phases with deps (P3)
    checks/
        environment.py # S352.1 -- Python, OS, versions, extras
        project.py     # S352.2 -- .raise/ structure, config coherence
        adapters.py    # Adapter health, env vars
        graph.py       # Graph staleness, build status
        skills.py      # Skill sync, deployment status
        mcp.py         # MCP server health
    fix.py             # --fix auto-remediation with backup (P5)
```

### Pipeline order (P3)

```
environment -> project -> adapters -> graph -> skills -> mcp
```

Each phase can declare `depends_on` — if environment fails critically, skip downstream.

### CLI surface

```
rai doctor              # Run all checks, show only problems (P6)
rai doctor -v           # Verbose -- show all checks including passing
rai doctor --fix        # Auto-remediate with backup (P5)
rai doctor --json       # JSON output for CI (P8)
rai doctor environment  # Run single category (P11)
```

### Key insight from OpenClaw

Doctor and migration are the same tool. When `rai doctor` detects config from
an older version, it should offer to migrate — not just warn. This covers the
upgrade path (2.1 -> 2.2) seamlessly.

## 5. What NOT to do

- Don't score dimensions (P9) in v1 — adds complexity, defer to v2
- Don't build interactive repair wizard — `--fix` is non-interactive with backup
- Don't check external services (Jira connectivity) by default — too slow, add `--online` flag

## 6. Contrary Evidence

- **Aider succeeds without doctor** — their docs + error messages are good enough for a technical audience. But Rai targets teams with mixed skill levels (Aquiles, Fernando) where self-service diagnostics matter more.
- **Cursor's log dump approach** is simpler but unhelpful for end users — only useful for support teams reading logs.

## References

- [Claude Code troubleshooting](https://code.claude.com/docs/en/troubleshooting)
- [cc-health-check](https://yurukusa.github.io/cc-health-check/)
- [OpenClaw Doctor](https://docs.openclaw.ai/gateway/doctor)
- [OpenClaw Doctor architecture](https://deepwiki.com/openclaw/openclaw/14.2-doctor-command-guide)
- [brew diagnostic.rb](https://github.com/Homebrew/brew/blob/master/Library/Homebrew/diagnostic.rb)
- [flutter doctor](https://flutterfever.com/flutter-doctor-command/)
- [Cursor troubleshooting](https://cursor.com/docs/troubleshooting/troubleshooting-guide)

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Worktree lifecycle** (`rai worktree register/list/close`) — multi-worktree development with session isolation and propagation. New in 3.1 (E14697).
- **Full cross-harness parity** — Codex CLI and Kimi now expose the same 36 MCP tools as Claude Code. Codex gains PostToolUse staleness detection (RAISE-14908).
- **Mechanical scope guard** (RAISE-15618) — `rai discover scan` output is now scoped to the current checkout; cross-worktree symbol leakage is closed.

### Changed

- **Session continuity is now scoped to worktree + agent** (E15456, ADR-2026-07-27) — a session only inherits continuity from the last session closed in the *same worktree* (main checkout donates only to main), with the agent session id as a tie-breaker within the worktree. The previous project-wide "last closed session" fallback was **removed** from the donor chain, `rai session context`, and `rai session measure`; history, ledger auto-surface, and recent-sessions reads default to the caller's scope.
- **Behavior change for main-checkout users:** session history written before schema V67 carries no worktree/agent attribution and is now excluded from continuity. Worst case is a clean start (no inherited context) instead of inheriting the last project-wide session.
- Session ids gain an entropy suffix to prevent minute-collision between concurrent sessions (RAISE-15482).

### Fixed

- **SQLite WAL write-lock** (RAISE-15605) — orphaned `BEGIN` transactions from failed schema migrations blocked all writers for the life of the process. Fixed with `with conn:` in `create_all()` and 8 write paths hardened.
- **Graph scoped by checkout** (RAISE-15607) — KG queries no longer return symbols from other worktrees. `checkout_root` + `validate_asserted_root()` enforce per-checkout isolation.
- **Tier display false evidence** (RAISE-15610) — `rai` no longer prints a tier that contradicts ADR-082.
- **3 CI drift guards** (RAISE-15608) — architectural drift now fails CI instead of warning-and-continue.
- **Windows: bare `rai` no longer crashes** (RAISE-15650) — the cockpit imported the Unix-only `termios`/`tty` at module scope; it now detects the missing raw-input support and prints the available commands instead.
- **Windows: `rai gate check` no longer crashes on startup** (RAISE-15653) — the worker-budget ledger imported the Unix-only `fcntl` at module scope; it now selects a locking backend at runtime (`msvcrt` on Windows).
- **Install scripts can actually install the beta** (RAISE-15651, RAISE-15670) — the published installers default to the GitLab pre-release registry, keep a project's existing `.venv` untouched, and document how flags survive `curl | bash`.
- **`rai cartridge` reports live node counts** (RAISE-15615) — honours checkout-wins visibility instead of counting only one provenance.
- **`rai init --force` no longer wipes cartridge content** (RAISE-15655) — it overwrites only what the bundle owns and leaves hand-curated corpus/eval/extractor content in place.
- **deploy:docs actually deploys** (RAISE-15654) — the CI job now runs the deploy with Node 22 and a pinned wrangler.
- 390 additional bugs resolved across 13 subsystems since 3.1.0a1 (S1-High: 31, S2-Medium: 290, S3-Low: 69).

## [3.1.0a1] - 2026-05-28

### Added

- Multi-dev foundation: team model, `rai connect` device auth, governance sync, pattern promotion lifecycle, activity feed (E5477, E5593, E5596, E5604, E5708)
- Zero-friction onboarding: `rai init --server`, `rai repo register`, `rai connect <org>`, journey-aligned checklist with auto-detection (E6030, E6097, E6098)
- Knowledge Graph auto-update on story/epic close with staleness detection in `rai doctor` (E6173, ADR-085/086)
- KG server sync: `DualWriteBackend`, federated cross-repo queries via `rai graph query --cross-repo` (E6174)
- Domain Cartridges: `rai cartridge init/validate/pack/install/uninstall` with JSON Schema spec (E5875, ADR-083)
- Console HUD (`rai hud`): TUI with Missions/Sessions/Pipeline/Events/Insights tabs (E2724, E3128)
- Rai for Rovo: 5 Forge Actions connecting Rovo to raise-server (E5399)
- MCP-primary: 100% skill migration to MCP-first, 3 new tools (E6003, ADR-084)
- Drift prevention system: 8 CI guards, mandatory architecture-review gate (E2100, E2313)
- Auto-upgrade on session start: syncs skills, patterns (55→60 BASE), methodology (v1→v2) on version mismatch (E6100/S6100.5)
- Backlog attachments: `rai backlog attach` and `rai backlog get-attachments` (S2503.7)
- `rai project create/link-repo/list` CLI commands (RAISE-6178, RAISE-6179)
- `/rai-onboard-repo` skill for guided repository onboarding (RAISE-6219)

### Changed

- SQLite is canonical graph backend; Kuzu optional at runtime (E5664)
- Graph session context: 3.8s → ~200ms via recursive CTEs and lazy loading (E4513)
- Environment variable prefix: `RAI_*` → `RAISE_*` (**breaking**)
- `atlassian-python-api` and `kuzu` promoted to default dependencies
- Jira REST API upgraded to v3 Cloud standard (E2503)
- Branch model: development branch → `release/3.1.0` (E6100/S6100.1)
- Product line canonicalized: one product, OSS/Community/Pro tiers (ADR-082)
- Schema: CLI SQLite V1→V31, Server Alembic 011→027

### Fixed

- 86 bugs resolved across 13 subsystems (10 S1-High, 67 S2-Medium, 10 S3-Low)
- See `work/release/3.1.0a1-alpha-notes.md` for complete bug list

## [3.0.0] - 2026-05-04

### Changed

- Pre-release 3.0.0a3: git-first config cascade (RAISE-2025), MCP bridge foundation (E1962)

## [2.3.0] - 2026-03-30

### Added

- Session identity model — deterministic session IDs per developer+repo using timestamp-based format `S-{prefix}-{YYMMDD}-{HHMM}`, Pydantic prefix registry with collision detection, per-project active pointer (E654, RAISE-654)
- CLI extension mechanism via entry points — `ExtensionInfo` discovery, collision and duplicate protection, wired into main CLI (RAISE-594)
- `rai doctor` adapter availability diagnostics (RAISE-614, S613.1)

### Changed

- Session data moved from global `~/.rai/` tracking to per-project `.raise/rai/personal/` directory (E654) — **breaking** for tools that read `developer.yaml` active session fields
- Pattern add default scope changed from `personal` to `project` (RAISE-608)

### Fixed

- CLAUDE.local.md references removed from skills_base close skills (RAISE-635)
- Session-start context loss — load session state before migration so previous state is preserved (RAISE-566)
- `promote_unreleased` fails when Unreleased is last section in changelog — add `\Z` to regex (RAISE-547)
- Unicode symbols crash on Windows CP1252 terminals — add symbols module with fallbacks (RAISE-554)
- C# scanner not extracting constructor dependencies — pass `depends_on` through `build_hierarchy` (RAISE-227)
- `rai init` ide.type not syncing with `agents.types[0]` (RAISE-218)
- CI container missing git — add to `apt-get install` (RAISE-570)
- Regex precedence/grouping fixes in ADR and changelog parsers (RAISE-589)
- Story-plan skill enforces project-wide verification scope (RAISE-572)
- Doctor callback cognitive complexity reduced from 47 to ~7 via extract refactoring (RAISE-598)
- SonarQube code smells resolved: S1192, S6019, S1172, S7503, S5713, S7632, S125, S5754 (RAISE-541)

### Security

- authlib 1.6.8 → 1.6.9 — 3 CVEs patched (RAISE-574)
- PyJWT ≥ 2.12.0 — critical `crit` header bypass, CVE-2026-32597 (RAISE-575)
- astro/cloudflare/undici dependencies upgraded — 9 Snyk CVEs in docs site (RAISE-576)

## [2.2.3] - 2026-03-11

Initial open-source release. RaiSE Framework v2 — a lean methodology and deterministic
toolkit for reliable AI-assisted software engineering.

### Highlights

- **37 skills** covering the full SDLC: epic, story, discovery, implementation, review, debug, research
- **Knowledge graph** for project context, patterns, and cross-session memory
- **Multi-language discovery**: Python, TypeScript, JavaScript, C#, PHP, Dart, Svelte
- **Governance as code**: constitution, guardrails, ADRs, gates — all versioned in Git
- **Adapter plugin system**: extensible via entry points (filesystem built-in, Jira/Confluence via raise-pro)
- **Doctor diagnostics**: `rai doctor` with `--fix` auto-remediation
- **Documentation site**: docs.raiseframework.ai (EN + ES)

### CLI Commands

72 subcommands across 17 groups: `init`, `session`, `graph`, `pattern`, `signal`,
`backlog`, `skill`, `discover`, `adapter`, `mcp`, `gate`, `doctor`, `docs`,
`artifact`, `release`, `info`, `profile`.

### Framework

- 5 work cycles: solution, project, feature, setup, improve
- 3-layer architecture: Context (wisdom), Kata (practice), Skill (action)
- Jidoka (stop-and-fix) verification at every step
- Skill sets: distributable, customizable skill collections per team

### Pro/Community Boundary (E478)

- **Separated pro adapters** into `packages/raise-pro/` workspace package
- **Removed 6 pro-only dependencies** from community install (atlassian-python-api, authlib, cryptography, requests, urllib3, certifi)
- **Clean entry points**: Jira/Confluence adapters register only when raise-pro is installed
- **Removed hardcoded Jira CLI logic** from community package (-207 lines)
- **Gitignored adapter configs** (.raise/jira.yaml, .raise/confluence.yaml) to prevent PII leaks

[Unreleased]: https://github.com/humansys/raise/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/humansys/raise/compare/v2.2.3...v2.3.0
[2.2.3]: https://github.com/humansys/raise/releases/tag/v2.2.3

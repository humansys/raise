# Epic Scope: E493 — Developer Setup Experience

**Objective:** A developer can go from zero to productive in under 15 minutes on any supported OS, with guided tooling for both new and returning developer scenarios.

## In Scope

- OS-specific installation guide (macOS, Linux, Windows/WSL)
- `rai profile export` / `rai profile import` for portable identity
- ~~`/rai-welcome` returning-developer detection~~ → moved to RAISE-501 (Universal Entry Point epic)
- `rai doctor --new-machine` environment portability checks
- CLI `.env` loading for Jira/Confluence credentials
- Fix `raise-cli` pipx install without `--include-deps`

## Out of Scope

- Unifying identity layers into a single mechanism
- Full installer/bootstrapper binary
- Windows native (non-WSL) support
- GUI or web-based setup wizard

## Planned Stories

| # | Story | Size | Depends On |
|---|-------|------|------------|
| S1 | OS-specific installation guide | S | — |
| S2 | `rai profile export/import` | M | — |
| ~~S3~~ | ~~`/rai-welcome` returning developer detection~~ | ~~M~~ | Moved to RAISE-501 |
| S4 | `rai doctor --new-machine` | M | S1 |
| S5 | CLI loads `.env` for adapter credentials | S | — |
| S6 | Fix `raise-cli` pipx install | S | — |

**Note:** RAISE-492 (installation docs) already exists and maps to S1.

## Done Criteria

- 5 stories closed with passing gates (S3 moved to RAISE-501)
- New-user walkthrough validated on macOS and Linux
- `rai doctor` covers all 8 friction points

---

## Implementation Plan

### Sequencing Strategy: Quick Wins + Critical Path

Rationale: S5/S6 are small independents that deliver immediate terminal DX value.
Then S1+S2 in parallel (docs + profile portability). S3/S4 build on those.

### Story Sequence

| Pos | Story | Rationale | Hard Deps | Enables | Parallel With |
|-----|-------|-----------|-----------|---------|---------------|
| 1 | S5 — CLI `.env` loading | Quick win — fixes daily friction (rai backlog from terminal) | — | — | S6 |
| 2 | S6 — Pipx install fix | Quick win — investigate first, may close as N/A | — | — | S5 |
| 3 | S1 — Installation guide | Docs-only, unblocks S4 (doctor references install steps) | — | S4 | S2 |
| 4 | S2 — Profile export/import | Critical path starter — new CLI commands + portability logic | — | S3 | S1 |
| 5 | S3 — Welcome returning dev | Skill-only — uses profile detection concepts from S2 | S2 | — | S4 |
| 6 | S4 — Doctor new machine | Capstone — references install docs (S1), benefits from all other stories | S1 | — | S3 |

### Critical Path

```
S5+S6 (parallel) → S1+S2 (parallel) → S3+S4 (parallel)
                                         ↑        ↑
                                         S2       S1
```

### Milestones

#### M1: Terminal DX (S5 + S6)
- **Stories:** S5, S6
- **Success:** `rai backlog list` works from terminal with `.env` credentials. `pipx install rai-cli` works without `--include-deps` (or S6 closed as N/A).
- **Demo:** Run `rai backlog list` from a fresh terminal without manual `export`.

#### M2: Identity Portability (S1 + S2)
- **Stories:** S1, S2
- **Success:** `docs/installation.md` covers macOS+Linux+WSL. `rai profile export` produces bundle, `rai profile import` restores on new machine.
- **Demo:** Export profile on Linux, import on macOS, verify `rai profile show` matches.

#### M3: Feature Complete (S4)
- **Stories:** S4 (S3 moved to RAISE-501)
- **Success:** `rai doctor --new-machine` reports all 8 friction points with fix hints.
- **Demo:** Run `rai doctor --new-machine` — all checks pass or show actionable hints.

#### M4: Epic Complete
- **Criteria:** All done criteria met. New-user walkthrough validated. Returning-developer flow validated E2E.

### Progress Tracking

| Story | Size | Status | Notes |
|-------|------|--------|-------|
| S5 — CLI `.env` loading | S | done | 1.67x velocity, 12 min |
| S6 — Pipx install fix | S | done | Verified working, no changes needed |
| S1 — Installation guide | S | done | 2.33x velocity, 15 min |
| S2 — Profile export/import | M | done | 2.0x velocity, 45 min |
| ~~S3 — Welcome returning dev~~ | ~~M~~ | moved to RAISE-501 | Scope expanded to full situational router |
| S4 — Doctor new machine | S (redefined) | done | 4 developer checks added to existing doctor |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| S6 investigation blocks Wave 1 | Timebox to 1 hour — if unclear, close as N/A and revisit |
| S2 takes longer than M (profile edge cases) | Strict scope: YAML bundle only, no Claude memory or MCP portability |
| S4 doctor scope creep | Cap at 8 checks, one per documented friction point |

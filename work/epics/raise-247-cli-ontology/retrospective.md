# Epic Retrospective: E247 CLI Ontology Restructuring

**Completed:** 2026-02-23
**Duration:** 1 day active work (epic branch created 2026-02-23, design done in prior session)
**Features:** 6 stories delivered
**Jira:** RAISE-247

---

## Summary

Decomposed the `rai memory` God Object (7 commands, 3 concerns) into a clean CLI taxonomy: `rai graph` (7 commands), `rai pattern` (2), `rai signal` (3). Also merged `publish`+`release`, flattened `base`→`info`/`profile` singletons, killed 3 redundant commands, and swept all 22 skills + CLAUDE.md to use new names. Backward-compat deprecation shims preserve existing workflows.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 6 | S1-S6 |
| Total Actual Time | 300 min | ~5 hours |
| Tests | 2522 pass | 0 regressions |
| Average Velocity | 1.94x | range: 0.8x–3.0x |
| Patterns Captured | 14 | PAT-E-434 through PAT-E-451 |
| Commands Restructured | 12 | 7 graph + 2 pattern + 3 signal |
| Commands Removed | 3 | generate, add-session, add-calibration |
| Skills Updated | 19 | + CLAUDE.md |

### Story Breakdown

| Story | Size | Actual | Velocity | Key Learning |
|-------|:----:|:------:|:--------:|--------------|
| S1: graph group | M | 150 min | 1.6x | God Object decomposition needs thorough test migration |
| S2: pattern group | S | 45 min | 1.33x | Extract-and-delegate pattern works cleanly |
| S3: signal group | S | 21 min | 2.86x | Third extraction benefits from S1/S2 muscle memory |
| S4: kill redundancies | XS | 25 min | 0.8x | Coverage gate enforcement adds overhead but catches gaps |
| S5: merge+flatten | S | 29 min | 2.07x | Singleton flattening simpler than expected |
| S6: skill sweep | M | 30 min | 3.0x | Parallel subagents ideal for mechanical sweeps |

---

## What Went Well

- **Acceleration curve:** Velocity climbed from 1.6x → 3.0x as the pattern became familiar. S3 and S6 were notably fast because the approach was proven by S1/S2.
- **Arch review integration:** Architecture review after S4 descoped 2 stories (Skill Registry → RAISE-242, backward-compat removal → future release), keeping the epic focused.
- **Quality reviews caught real issues:** Pre-existing `--input` flag bug (S6), test muda cleanup (S5), redundant `invoke_without_command` (S5).
- **Independence of S1-S5:** Design decision to make stories independent (no artificial chain) enabled working any order. Saved coordination overhead.
- **Backward-compat shims:** Deprecation warnings + delegation pattern means nothing breaks for existing users.

## What Could Be Improved

- **`rai init` skill sync bug:** Content changes in SKILL.md aren't propagated when YAML frontmatter format drifts. Had to use direct `cp` as workaround. Needs a fix in the sync comparison logic.
- **S4 velocity drag (0.8x):** Coverage gate enforcement added unexpected overhead. Worth it for quality, but estimate should account for gate time.
- **Scope doc had stale S6 status:** Two places tracked story status (features table + progress table), leading to inconsistency. Single source of truth would be better.

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-E-434 | Extract-and-delegate for backward compat | CLI restructuring |
| PAT-E-435 | Test organization mirrors command hierarchy | CLI testing |
| PAT-E-436 | Deprecation shim pattern (warn + delegate) | API evolution |
| PAT-E-440 | Small group extraction benefits from prior large extraction | Sequential refactoring |
| PAT-E-441 | Pattern group needs 2 commands minimum to justify existence | CLI design |
| PAT-E-442 | Three subcommands over unified emit | CLI ontology |
| PAT-E-444 | Coverage gate during refactoring catches gaps but adds overhead | Quality gates |
| PAT-E-446 | Singleton flatten: callback + invoke_without_command | Typer CLI |
| PAT-E-447 | Deprecation shim for whole group (import + delegate) | CLI evolution |
| PAT-E-450 | Parallel subagents for mechanical sweeps | Automation |
| PAT-E-451 | rai init sync sensitive to YAML frontmatter format | Framework bug |

## Process Insights

- **God Object decomposition** is best done as multiple independent stories, not one big refactor. Each extraction is self-contained and can be verified independently.
- **Arch review as story gate** (not just epic gate) caught over-engineering early in S4/S5.
- **Skill cycle even for XS stories** adds ~5 min overhead but catches scope creep and documents decisions.
- **Parallel subagents** scale linearly for mechanical work — 3 agents = ~3x throughput on independent file edits.

---

## Artifacts

- **Scope:** `work/epics/raise-247-cli-ontology/scope.md`
- **Design:** `work/epics/raise-247-cli-ontology/design.md`
- **Stories:** `work/epics/raise-247-cli-ontology/stories/s247.{1-6}/`
- **ADR:** `dev/decisions/adr-038-cli-ontology-restructuring.md`

---

## Next Steps

- Merge to `main` (this epic close)
- `rai init` sync bug → add to RAISE-144 backlog
- RAISE-242 (Skill Ecosystem) unblocked by skill registry deferral
- Backward-compat aliases remain until next major version

---

*Epic retrospective — E247 CLI Ontology Restructuring complete*

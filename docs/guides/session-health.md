---
title: Session Health
description: Session Doctor diagnostics and Workstream Monitor insights — automated health checks and productivity feedback.
---

RaiSE v2.4 adds two features that maintain session hygiene automatically: **Session Doctor** detects and cleans stale session state, and **Workstream Monitor** provides productivity insights at session close.

## Session Doctor

### What It Does

The Session Doctor runs automatically on `rai session start`. It checks for stale or orphaned session state in `.raise/rai/personal/` and cleans up what's safe to remove.

### What It Detects

| Finding | Severity | What It Means | Auto-Clean? |
|---------|----------|--------------|-------------|
| **Zombie session** | warning | Active session pointer >48h old, no content to preserve | Yes |
| **Zombie with content** | warning | Active session pointer >48h old, has narrative/state | No — needs your review |
| **Stale output** | info | `session-output.yaml` >24h old | Yes |
| **Retention exceeded** | info | >20 session directories accumulated | No — batch decision |

### How It Works

The doctor follows a 3-phase pattern:

1. **Diagnose** — scan for issues, no side effects
2. **Classify** — separate auto-safe from needs-consent items
3. **Execute** — clean only authorized items

Items classified as "auto-safe" (empty zombies, stale output files) are cleaned without prompting. Items that might contain work you haven't saved require explicit consent.

### Example Output

```
Session Doctor — 2 finding(s):

  [!] Zombie session: S-E-260401-0900 (72h old)
      No content to preserve
      Action: Clear stale pointer

  [i] Stale session-output.yaml (26h old)
      26.1 KB — safe to remove
      Action: Remove stale output file

Auto-cleaned:
  - Cleared zombie pointer: S-E-260401-0900
  - Removed stale output: session-output.yaml
```

### Running Manually

To inspect without modifying anything:

```bash
rai session doctor
```

### Skipping (CI/Automation)

For CI pipelines or scripts that don't need health checks:

```bash
rai session start --no-doctor
```

### Configuration

Default thresholds (not yet user-configurable):

| Threshold | Default | Purpose |
|-----------|---------|---------|
| Zombie age | 48 hours | When an active session pointer is considered stale |
| Stale output age | 24 hours | When output files are considered safe to remove |
| Directory retention | 20 | Maximum session directories before suggesting cleanup |

---

## Workstream Monitor

### What It Does

The Workstream Monitor analyzes your git history at `rai session close` and provides brief productivity insights. It's purely advisory — it suggests improvements but never blocks your work.

### What It Measures

| Metric | Source | What It Tells You |
|--------|--------|-------------------|
| **Commit count** | `git log` | Session productivity |
| **Test commit ratio** | Commit subjects starting with `test` | TDD compliance |
| **Revert count** | Commit subjects starting with `Revert` | Stability of approach |
| **Duration** | First to last commit timestamps | Session time span |

### Insights

The monitor suggests improvements when patterns indicate room for growth:

**Low TDD compliance** (test ratio <30%):

> Test commit ratio is 2/14 (14%). Consider writing test commits before implementation (RED-GREEN-REFACTOR).

**High revert frequency** (>2 reverts):

> 3 reverts detected. Consider smaller, more focused commits to reduce revert frequency.

### Example Output

```
Session S-E-260403-1000 closed.
  Patterns added: 2
  Corrections recorded: 1

  Session insights: 14 commits | Test ratio: 28% | Reverts: 1 | Duration: 95m
```

### Future (v3.0)

The current monitor uses simple git heuristics. In v3.0, it will support:

- Cross-session trend detection
- Team-level pattern recognition
- Deeper analysis via async agents

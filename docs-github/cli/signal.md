---
title: rai signal
description: Emit lifecycle and telemetry signals for flow analysis.
---

Emit lifecycle and telemetry signals. Signals feed local analytics for lead time, velocity, and bottleneck detection.

## `rai signal emit-work`

Emit a work lifecycle event for Lean flow analysis. Tracks work items (epics, stories) through normalized phases.

| Argument | Description |
|----------|-------------|
| `WORK_TYPE` | Work type: `epic`, `story` (**required**) |
| `WORK_ID` | Work ID, e.g. `E9`, `S9.4` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--event` | `-e` | Event: `start`, `complete`, `blocked`, `unblocked`, `abandoned`. Default: `start` |
| `--phase` | `-p` | Phase: `design`, `plan`, `implement`, `review`. Default: `design` |
| `--blocker` | `-b` | Blocker description (for `blocked` events) |
| `--session` | | Session ID (falls back to `RAI_SESSION_ID` env var) |

```bash
# Epic lifecycle
rai signal emit-work epic E9 --event start --phase design
rai signal emit-work epic E9 -e complete -p design

# Story lifecycle
rai signal emit-work story S9.4 --event start --phase implement
rai signal emit-work story S9.4 -e complete -p implement

# Work blocked
rai signal emit-work story S9.4 -e blocked -p plan -b "unclear requirements"
```

---

## `rai signal emit-session`

Emit a session event to telemetry. Records session completion for local learning and insights.

| Flag | Short | Description |
|------|-------|-------------|
| `--type` | `-t` | Session type: `story`, `research`, `maintenance`, etc. Default: `story` |
| `--outcome` | `-o` | Outcome: `success`, `partial`, `abandoned`. Default: `success` |
| `--duration` | `-d` | Session duration in minutes. Default: `0` |
| `--stories` | `-f` | Stories worked on (comma-separated) |
| `--session` | | Session ID (falls back to `RAI_SESSION_ID` env var) |

```bash
# Basic session complete
rai signal emit-session --type story --outcome success

# With duration and stories
rai signal emit-session -t story -o success -d 45 -f S9.1,S9.2,S9.3
```

---

## `rai signal emit-calibration`

Emit a calibration event to telemetry. Records estimate vs. actual for velocity tracking. Velocity is calculated automatically: `estimated / actual` (>1.0 = faster than estimated).

| Argument | Description |
|----------|-------------|
| `STORY` | Story ID, e.g. `S9.4` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--size` | `-s` | T-shirt size: `XS`, `S`, `M`, `L`. Default: `S` |
| `--estimated` | `-e` | Estimated duration in minutes. Default: `0` |
| `--actual` | `-a` | Actual duration in minutes. Default: `0` |
| `--session` | | Session ID (falls back to `RAI_SESSION_ID` env var) |

```bash
# Story completed faster than estimated
rai signal emit-calibration S9.4 --size S --estimated 30 --actual 15

# Story took longer
rai signal emit-calibration S9.4 -s M -e 60 -a 90
```

**See also:** [`rai session close`](cli/session.md), [`rai pattern reinforce`](cli/pattern.md)

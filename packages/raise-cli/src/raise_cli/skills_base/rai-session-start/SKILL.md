---
name: rai-session-start
description: Load context and propose session focus. Use at the start of every working session.
model: haiku

allowed-tools:
  - Read
  - Grep
  - Glob

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "start"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "7.0.0"
  raise.visibility: public
  raise.inputs: |
    - project_path: string, required, argument
    - developer_profile: file_path, required, config
  raise.outputs: |
    - session_id: string, next_skill
    - context_bundle: string, cli
---

# Session Start

## Purpose

Open a working session in ONE composite call. The deterministic sequence
(working-tree hygiene, base-branch drift, DB health, mission resolution,
context bundle, MCP health) runs in `raise-cli` — this skill only presents
the result and interprets signals (ADR-093 / ADR-024).

## Mastery Levels (ShuHaRi)

- **Shu**: Explain context, checks, and concepts in the presentation
- **Ha**: Explain only new or non-obvious signals
- **Ri**: Minimal output — context line, focus, signals, "Go."

## Context

**When to use:** At the start of every working session.

**When to skip:** Continuation of an active session (context already loaded).

**Inputs:** Project/worktree path. Developer profile (`~/.rai/developer.yaml`).

## Steps

### Step 1: Open (one call)

Use the `raise_session_open` MCP tool with cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:

```bash
rai session open --project . -f json
```

Telemetry is emitted server-side — do NOT call signal/topic tools here.

### Step 2: Handle the report

Every check returns `status: ok|warn|blocked` with structured data.

| Condition | Action |
|-----------|--------|
| `status: ok` | Present (Step 3) |
| `hygiene: blocked` (orphan staged changes) | **STOP** — present the staged list and the options `discard / stash / keep`; wait for the developer's choice. Never auto-resolve |
| `drift: warn` con `data.in_worktree: true` | Advisorio únicamente, en **todos** los niveles ShuHaRi — nunca auto-mergear. Mencionar `data.suggestion` (`git rebase {target}`) y continuar. Regla 2 (RAISE-15825): dentro de CUALQUIER worktree, ningún paso automático toca `HEAD`, nunca — el developer decide cuándo actualizar, deliberadamente. |
| `drift: warn` con `data.in_worktree: false` | **Ri**: ejecutar automáticamente `git fetch origin {dev_branch} && git merge origin/{dev_branch} --ff-only`; reportar N commits incorporados en una línea. Si `--ff-only` falla (divergencia), escalar al developer. **Shu/Ha**: mencionar y pedir confirmación antes de ejecutar. Este caso es el checkout principal (no un worktree) — sesión Ri larga y autónoma (afb15fd8a); sigue siendo seguro auto-sincronizar porque no hay contexto de branch que colapsar. |
| `db: warn` | Suggest running rai db migrate; continue |
| `mcp` has `down` servers | Report as "not connected" — never alarming, never tracebacks |
| `graph: warn` | Advisory at **every** ShuHaRi level — never blocks (RAISE-16049, ADR-085). Mention `data.message`; suggest running rai graph build. If `data.tier: critical`, recommend rebuilding before relying on graph-backed reviews/patterns this session. If `data.tier: never_built`, the graph has simply never been built — same suggestion, no alarm. |
| `update: warn` (newer `rai` release published) | Ask the developer in chat: "Nueva versión disponible: {latest} (tienes: {current}). ¿Instalar con `rai self-update`?" — **ask at every ShuHaRi level, no exception** (unlike `drift`, this replaces the running binary — bigger blast radius even though checksum-verified). If yes, run the following via Bash:

```bash
rai self-update
```

**Baseline disposition (non-blocking).** When `hygiene` is `warn`/`blocked`
(uncommitted changes) OR the report carries pre-existing gate failures, surface
the baseline gate state before story work begins — never proceed silently into
a red state. Present the count and three explicit options:

```
Baseline gate state: {N} failures ({breakdown, e.g. pytest: 2, pyright: 1})
Options:
  (a) Fix failures before starting story work [recommended]
  (b) Document as known failures in scope.md (baseline-excluded)
  (c) Proceed — treat failures as baseline-excluded
```

This check is **non-blocking**: the agent may choose (c) and continue. When the
worktree is clean (no uncommitted changes, no pre-existing failures), omit the
block entirely — no baseline disposition on a clean state (no noise).

If the bundle identifies a current story with a Jira key, bind it:
use the `raise_session_bind` MCP tool with key="RAISE_SESSION_JIRA_KEY",
value="{jira_key}", cwd="{project_or_worktree_path}" (fallback: `rai session bind RAISE_SESSION_JIRA_KEY "{key}"`).
Skip silently when there is no key.

### Step 3: Present (adapt to ShuHaRi level)

Interpret the bundle: next-session prompt > deadlines > narrative >
pending decisions. Propose focus from pending items > current story > deadlines.

```
## Session: YYYY-MM-DD
**Context:** [Release →] [Epic] → [Story], [phase]
**Worktree:** {worktree_id} — {workitem_id} (or "None")
**Focus:** [proposed goal]
**MCP:** [{healthy}/{total} healthy]  (omit line if total = 0)
**Signals:** [warnings from checks, or "None"]
```

Shu: explain context and concepts · Ha: only new/non-obvious signals ·
Ri: context line, focus, signals, "Go."

## Output

| Item | Destination |
|------|-------------|
| Session opened + checks | Via `raise_session_open` (CLI fallback: `rai session open`) |
| Focus proposed | Presented to developer |

## Quality Checklist

- [ ] ONE composite call (plus optional Jira bind) — no manual check sequence
- [ ] `blocked` always escalates to the human with the options verbatim
- [ ] No telemetry calls from the skill — the handler emits server-side

## References

- Service: `raise_cli/session/open_service.py` · Complement: `/rai-session-close`

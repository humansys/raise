# Design: E325 Agent-Orchestrated Workflow

**Epic:** [RAISE-325](https://humansys.atlassian.net/browse/RAISE-325)
**Date:** 2026-03-01
**Research:** `research-synthesis.md`

---

## Architecture: Layered Orchestration

```
┌─────────────────────────────────────────┐
│  Agent Runtime                          │  Claude Code, Roo, Cursor, etc.
│  (permissions, hooks, subagents)        │  Runtime-specific mechanics
├─────────────────────────────────────────┤
│  Orchestrator Skills                    │  /rai-story-run, /rai-epic-run
│  (read DAG, respect delegation profile) │  Portable SKILL.md
├─────────────────────────────────────────┤
│  Lifecycle Skills                       │  Existing 12 skills + I/O contracts
│  (typed inputs → work → typed outputs)  │  + backlog integration
├─────────────────────────────────────────┤
│  rai CLI (ACI layer)                    │  rai backlog, rai graph, rai docs*
│  (agent-optimized output)               │  Shell commands, any agent can call
├─────────────────────────────────────────┤
│  Backends (adapters)                    │  Jira, Confluence, PostgreSQL, FS
└─────────────────────────────────────────┘
```

*rai docs: future, out of scope for this epic.

## Key Contracts

### 1. Skill I/O Contract (SKILL.md frontmatter)

```yaml
metadata:
  raise.inputs:
    - name: story_id
      type: string
      source: argument | previous_skill | cli
      required: true
    - name: epic_scope
      type: file_path
      source: previous_skill
      required: false
  raise.outputs:
    - name: story_branch
      type: string
      destination: next_skill | state_file
    - name: scope_commit
      type: string
      destination: state_file
```

Inputs/outputs are typed metadata, not enforced by code. The agent reads them to understand what to pass between skills. State persists via files (YAML/JSON in work/), not conversation memory.

### 2. Delegation Profile (developer.yaml)

```yaml
delegation:
  default_level: ha  # shu | ha | ri
  overrides:
    rai-story-design: review    # always pause for human review
    rai-story-start: auto       # mechanical, proceed silently
    rai-story-implement: notify  # show output, continue unless human interrupts
    rai-story-review: review     # always pause — retrospective needs human input
```

Three HITL levels:
- **review**: Pause, present output, wait for explicit approval
- **notify**: Present output, continue after brief pause (human can interrupt)
- **auto**: Proceed silently, log output to state file

ShuHaRi defaults:
- **Shu**: All skills = review (current behavior)
- **Ha**: Design + review = review, start + plan + close = notify, implement = notify
- **Ri**: Only gates (design decisions, retrospective) = review, everything else = auto

### 3. CLI as ACI (output format)

```bash
# Current (verbose, raw)
rai backlog search 'project = "RAISE"' --limit 5
# → Full JSON with all fields, 200+ tokens per issue

# Optimized (agent-friendly)
rai backlog search 'project = "RAISE"' --limit 5 --format agent
# → RAISE-325 | In Progress | Agent-Orchestrated Workflow | M | epic
#   RAISE-301 | In Progress | Agent Tool Abstraction | L | epic
```

ACI principles (from SWE-agent research):
1. Simple — one command, one purpose
2. Compact — minimal tokens per operation
3. Informative — even empty results get explicit acknowledgment
4. Guardrailed — invalid operations fail fast with clear feedback

### 4. Orchestrator Flow (story-level)

```
/rai-story-run S325.1

Agent reads:
  1. Delegation profile from developer.yaml
  2. Skill DAG from metadata (raise.next chain)
  3. Current state from work/stories/s325.1/state.yaml

Agent executes:
  story-start [auto]  → state.yaml updated
  story-design [review] → PAUSE → human reviews → approved
  story-plan [notify]  → shown briefly → continues
  story-implement [notify] → TDD cycle, commits per task
  story-review [review] → PAUSE → human reviews retro
  story-close [auto]   → merge, cleanup, transition Jira
```

State file (`work/stories/s{N}.{M}/state.yaml`) is the handoff mechanism:
```yaml
story_id: S325.1
phase: implement  # current phase
branch: story/s325.1/skill-io-contracts
jira_key: RAISE-326
started_at: 2026-03-02T10:00:00
phases_completed:
  start: { commit: abc123, at: "2026-03-02T10:01:00" }
  design: { artifact: design.md, approved_by: emilio, at: "2026-03-02T10:15:00" }
  plan: { tasks: 5, at: "2026-03-02T10:20:00" }
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State handoff | File-based (YAML), not conversation memory | Survives context compaction. Portable. Inspectable. |
| I/O contracts | Metadata in SKILL.md, not code-enforced | Agent reads and interprets. No runtime dependency. Portable across agents. |
| Delegation config | In developer.yaml, not per-project | Developer trust is personal, not project-specific. |
| Orchestrator | SKILL.md (meta-skill), not code | Portable. Editable. Follows ADR-040. No new runtime. |
| CLI output format | `--format agent` flag on existing commands | Non-breaking. Opt-in. Agent uses it, humans don't. |
| Backlog integration | In individual skills, not as hook | Skills know WHEN to call backlog (semantic). Hooks only know WHAT tool was called (mechanical). |

## Target Components

| Component | Location | Change |
|-----------|----------|--------|
| 12 lifecycle SKILL.md files | `src/rai_cli/skills_base/rai-*/SKILL.md` | Add raise.inputs/outputs to frontmatter |
| developer.yaml schema | `src/rai_cli/onboarding/profile.py` | Add delegation section |
| rai backlog CLI | `src/rai_cli/cli/commands/backlog.py` | Add `--format agent` output mode |
| rai graph CLI | `src/rai_cli/cli/commands/graph.py` | Add `--format agent` output mode |
| 5 discover/onboard skills | `src/rai_cli/skills_base/rai-discover-*/SKILL.md` | Compaction + auto-wiring |
| 2 new orchestrator skills | `src/rai_cli/skills_base/rai-story-run/SKILL.md` | New meta-skills |
| session-start skill | `src/rai_cli/skills_base/rai-session-start/SKILL.md` | Load delegation profile |
| skill validator | `src/rai_cli/skills/validator.py` | Validate I/O contract metadata |

---

*Designed: 2026-03-01, SES-304*

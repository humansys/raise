---
name: rai-pipeline-setup
description: Define your team's own pipeline in one conversation — start from your flow, map it to your repo, write .raise/pipelines/{name}.yaml and verify it loads.
model: sonnet

allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - "Bash(rai:*)"
  - "mcp__rai-workspace__pipeline_list"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: "rai-pipeline-run"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
---

# Pipeline Setup

## Purpose

Turn your team's process into a runnable pipeline: start from the flow you follow, map each step to what your repo already has, fill the gaps, write `.raise/pipelines/{name}.yaml`, and prove it loads. One real question; everything else is proposed as a default and confirmed.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all 7 steps; show each proposal before writing
- **Ha**: Accept the canonical flow, confirm the mapping once, write and verify
- **Ri**: Give the flow as a list; the skill writes and verifies in one pass

## Context

**When to use:** After the project is initialized with RaiSE, when your team wants its own flow with its own skills and scripts.

**When to skip:** The built-in pipelines already fit. Missing skills are not a reason to skip: Step 3 resolves them.

**Inputs:** Your team's flow. Optional: existing `.raise/pipelines/*.yaml` (offered for extension).

**Prerequisites:** a git repository. Skills are dispatched by the exact name in `skill:` (`kg-design` runs `/kg-design`).

## Steps

### Step 1: Flow

If `.raise/pipelines/*.yaml` exists, offer to extend it. Otherwise show the default flow and ask the one real question:

> `design → implement → verify → review → close` — which steps does *your* process have? Rename, drop, add.

The answer is the ordered list of phase ids.

### Step 2: Map

For each step find what covers it, then show a table (step · covered by · phase type):

- Scripts in `package.json` (lockfile picks `pnpm`, `yarn` or `npm`), `pyproject.toml` or `Makefile` → `deterministic` phase, command verbatim.
- Team skills in `.claude/skills/*/SKILL.md` → `llm` phase; read their `## Output` table for the evidence glob.

### Step 3: Gaps

For each uncovered step, one proposal, default first: (1) an installed RaiSE skill from `references/reusable-skills.md`; (2) create `{team}-{step}` with `/rai-skill-create`; (3) a `deterministic` command when the step is mechanical.

### Step 4: Gates, evidence and tracker

Propose, then confirm: one `hitl` `REVIEW` gate where a human decides (default: after the first `llm` phase), and one evidence glob per `llm` phase.

Then the tracker. If `.raise/backlog.yaml` exists, propose `target_status` per phase (default yes: the issue moves on its own and every item is traceable). If not, say in one line that a connected tracker (`/rai-backlog-setup`) is the ideal end state, and continue without it: run state stays local in `.raise/`, and phases and gates are enforced regardless. Never a prerequisite.

### Step 5: Write

Write `.raise/pipelines/{name}.yaml` with the Write tool (it creates the directory). Name default: `{team}-story`, where `team` is the common prefix of the team's skills (`kg-design`, `kg-review` → `kg`), else the repository name. Keep `worktree_isolation: false` so the engine does not create worktrees in your repo.

```yaml
name: kg-story
description: "Kurigage story flow — design → lint → test → review"
issue_types: [story, task]
execution:
  worktree_isolation: false
phases:
  - id: design
    type: llm
    skill: kg-design
    gate:
      type: hitl
      level: REVIEW
    validates:
      - pattern: "docs/design/*.md"
        description: "Design note produced by /kg-design"
  - id: lint
    type: deterministic
    commands:
      - "pnpm run lint"
  - id: test
    type: deterministic
    commands:
      - "pnpm test"
  - id: review
    type: llm
    skill: kg-review
    validates:
      - patterns: ["docs/reviews/*.md", "REVIEW.md"]
        description: "Review record"
```

If the tracker was accepted in Step 4, add `target_status` to each phase.

### Step 6: Verify

Call `pipeline_list(cwd="{project_path}")`: expect `{name}` with its phases. Without MCP:

```bash
rai mcp call rai-workspace pipeline_list --args '{"cwd":"{project_path}"}'
```

If `rai-workspace` is not registered yet: `rai mcp scaffold rai-workspace --command rai-mcp-pipeline --args "--project ."`. A `PipelineError` names the offending field; fix and re-run.

<verification>`pipeline_list` shows `{name}` with the phase ids from Step 1.</verification>

### Step 7: Hand off

Tell the user: start it with `/rai-pipeline-run {name} {ISSUE}` (CLI: `rai pipeline start {name} {ISSUE}`), and commit `.raise/pipelines/{name}.yaml`.

## Output

| Item | Destination |
|------|-------------|
| Pipeline definition | `.raise/pipelines/{name}.yaml` |
| Verification | `pipeline_list` output listing `{name}` |

## Quality Checklist

- [ ] Flow asked first; phase ids are the team's steps
- [ ] Every step mapped or given a gap proposal
- [ ] Gates and evidence confirmed, tracker decided in Step 4
- [ ] No `store:` validates; `target_status` only if accepted
- [ ] `pipeline_list` lists the pipeline

## References

- Reusable RaiSE skills: `references/reusable-skills.md`
- Create a missing skill: `/rai-skill-create`
- Run it: `/rai-pipeline-run`
- Connect a tracker: `/rai-backlog-setup`

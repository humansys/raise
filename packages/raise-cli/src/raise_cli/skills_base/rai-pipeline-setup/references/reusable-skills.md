# Reusable RaiSE skills for a team pipeline

Skills that `rai init` already installs and that can fill an uncovered flow step. Verified by reading each skill's Context, Inputs and Output (RAISE-19068, D10), not by name. Dispatch is verbatim: `skill: rai-debug` runs `/rai-debug`.

Never propose skills that belong to RaiSE's own story, epic, bugfix or session lifecycles: they require our scope and plan files and an issue tracker.

## Suggest these

| Skill | Flow step it covers | Needs on disk | Phase snippet |
|-------|---------------------|---------------|---------------|
| `rai-debug` | investigate / diagnose a defect (5 Whys, Ishikawa) | Nothing. Input is the problem statement. Medium/large bugs write `work/debug/{name}/analysis.md` (optional). Its closing hand-off to RaiSE's own planning step does not apply in a team flow; ignore it. | `- {id: debug, type: llm, skill: rai-debug}` |
| `rai-adversarial-review` | challenge a design or analysis before acting on it | Path to the artifact under review. Its model is `fable`: override per project in `.raise/skill_models.yaml` if the runtime has no such model. Returns JSON to the caller; it writes no file. | `- {id: challenge, type: llm, skill: rai-adversarial-review}` (no `validates`) |

## Suggest with a stated caveat

These two work, but they follow RaiSE's own layout. Tell the team before proposing them; if they would rather not adopt it, propose `{team}-review` via `/rai-skill-create`.

| Skill | Flow step it covers | Needs on disk | Phase snippet |
|-------|---------------------|---------------|---------------|
| `rai-quality-review` | code review after the checks pass (semantic bugs, type honesty, test waste) | A git branch with a merge base, `branches.development` in `.raise/manifest.yaml` (the vocabulary check fails loudly without it), optional `project.test_command` / `lint_command` / `type_check_command` overrides. Report path depends on the scope it infers: `work/bugs/{issue_key}/qr.md` (bugfix) or `work/epics/*/stories/*-qr.md` (story) — use both globs. | `- {id: review, type: llm, skill: rai-quality-review, validates: [{patterns: ["work/bugs/*/qr.md", "work/epics/*/stories/*-qr.md"], description: "Review report"}]}` |
| `rai-architecture-review` | proportionality review (YAGNI/KISS, duplication) | Same git and manifest needs, plus a design doc (`design.md` or `scope.md`) stating the intent. Report path is scope-dependent like `rai-quality-review`: `work/bugs/{issue_key}/ar.md` or `work/epics/*/stories/*-ar.md`. | `- {id: simplify, type: llm, skill: rai-architecture-review, validates: [{patterns: ["work/bugs/*/ar.md", "work/epics/*/stories/*-ar.md"], description: "Architecture review"}]}` |

## Checked and not suggested

| Skill | Why |
|-------|-----|
| `rai-research` | Entry point that hands off to a nested multi-phase research orchestrator, web-search API keys and its own pipeline definition. Not a single phase. |
| `rai-bug-file` | Files a bug in Jira; requires a connected tracker. |
| `rai-discover` | One-time repository scan that builds the knowledge graph; project setup, not a flow step. |
| `rai-docs-update` | Syncs RaiSE module docs against the knowledge graph and RaiSE's fidelity scripts. |

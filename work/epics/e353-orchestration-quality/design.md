---
epic_id: "E353"
grounded_in: "Gemba of src/rai_cli/skills_base/rai-story-run/SKILL.md, src/rai_cli/skills_base/rai-epic-run/SKILL.md"
---

# Epic Design: Orchestration Quality — Checkpoint & Fork

## Affected Surface (Gemba)

| Module/File | Current State | Changes |
|-------------|---------------|---------|
| `src/rai_cli/skills_base/rai-story-run/SKILL.md` | 234 lines. Invokes phases inline via `/rai-story-{phase}` directives. Phase detection via artifact reverse-scan. 4 delegation gates. | Fork heavy phases (design, plan, implement, AR, QR, review) via Agent tool. Keep start/close inline. Add summary protocol. |
| `.claude/skills/rai-story-run/SKILL.md` | Deployment copy of above | Mirror changes from builtin |
| `src/rai_cli/skills_base/rai-epic-run/SKILL.md` | 181 lines. Invokes `/rai-story-run` per story inline. Phase detection via scope.md artifacts. 3 delegation gates. | Fork each story-run as Agent tool subagent. Keep epic-level phases (start, design, AR, plan, close) inline. |
| `.claude/skills/rai-epic-run/SKILL.md` | Deployment copy of above | Mirror changes from builtin |

## Target Components

| Component | Responsibility | Key Interface |
|-----------|---------------|---------------|
| story-run orchestrator | Coordinate story lifecycle phases | Agent tool spawn per heavy phase; artifact read/write |
| epic-run orchestrator | Coordinate epic lifecycle across stories | Agent tool spawn per story-run invocation |
| Phase skills (unchanged) | Execute individual phases | Read artifacts from disk, write artifacts to disk, return summary |

## Key Contracts

### Artifact I/O per phase (story-run)

| Phase | Reads from disk | Writes to disk |
|-------|----------------|----------------|
| start (inline) | — | `s{N}.{M}-story.md`, `s{N}.{M}-scope.md`, branch |
| design (fork) | `s{N}.{M}-story.md`, `s{N}.{M}-scope.md` | `s{N}.{M}-design.md` |
| plan (fork) | `s{N}.{M}-design.md` | `s{N}.{M}-plan.md` |
| implement (fork) | `s{N}.{M}-plan.md`, source code | source code, tests, commits |
| AR (fork) | `s{N}.{M}-design.md`, source code | AR verdict + findings (in review artifacts or inline) |
| QR (fork) | source code, tests | QR verdict + findings |
| review (fork) | all story artifacts | `s{N}.{M}-retrospective.md` |
| close (inline) | `s{N}.{M}-retrospective.md` | merge, branch cleanup |

### Agent tool spawn pattern (story-run)

```
For each heavy phase:
1. Read target skill's SKILL.md from src/rai_cli/skills_base/rai-story-{phase}/SKILL.md
2. Spawn Agent tool with:
   - prompt: skill content + story context (story_id, paths to prior artifacts)
   - subagent_type: "general-purpose"
3. Agent executes skill in fresh context:
   - Reads prior artifacts from disk
   - Executes all skill steps
   - Writes output artifacts to disk
4. Orchestrator reads summary from agent result
5. Apply delegation gate (main thread)
6. Proceed or pause
```

### Agent tool spawn pattern (epic-run, story iteration)

```
For each story in progress tracking:
1. Spawn Agent tool with:
   - prompt: "Run /rai-story-run for {story_id}. Story scope: {path}. Epic: {epic_id}."
   - subagent_type: "general-purpose"
2. Agent runs full story lifecycle inline (can't fork further — F5 constraint)
3. Orchestrator reads story completion status
4. Update progress tracking in scope.md
5. Proceed to next story
```

### Nesting depth constraint (F5)

```
Main thread (epic-run)
  └── Subagent (story-run) — depth 1
       └── Cannot fork further — phases run inline

Main thread (story-run standalone)
  └── Subagent (heavy phase) — depth 1
       └── Cannot fork further — skill runs inline
```

Max depth is always 1. This is enforced by Claude Code, not by our code.

## Migration Path

No backward compatibility concern. The orchestrator SKILL.md changes are purely additive — they change HOW phases are invoked (fork vs inline) but not WHAT phases do. Individual phase skills are unchanged.

Phase detection (artifact reverse-scan) is unaffected — it checks files on disk regardless of how they were created.

Delegation gates are unaffected — they happen in the main thread between fork invocations.

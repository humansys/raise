---
epic_id: "E353"
grounded_in: "Gemba of all 8 phase skills + rai-story-run + rai-epic-run in src/rai_cli/skills_base/"
---

# Epic Design: Orchestration Quality — Checkpoint & Fork

## Affected Surface (Gemba)

| Module/File | Current State | Changes |
|-------------|---------------|---------|
| `src/rai_cli/skills_base/rai-story-run/SKILL.md` | 234 lines. Invokes phases inline via `/rai-story-{phase}` directives. Phase detection via artifact reverse-scan. 4 delegation gates. | Fork heavy phases (design, plan, implement, AR, QR, review) via Agent tool. Keep start/close inline. Add summary protocol. |
| `.claude/skills/rai-story-run/SKILL.md` | Deployment copy of above | Mirror changes from builtin |
| `src/rai_cli/skills_base/rai-epic-run/SKILL.md` | 181 lines. Invokes `/rai-story-run` per story inline. Phase detection via scope.md artifacts. 3 delegation gates. | Keep story-run invocation inline (main thread) so story-run can fork its phases. Epic-level phases (start, design, AR, plan, close) stay inline. Add thin checkpoint between stories (summary + progress update). |
| `.claude/skills/rai-epic-run/SKILL.md` | Deployment copy of above | Mirror changes from builtin |

## Target Components

| Component | Responsibility | Key Interface |
|-----------|---------------|---------------|
| story-run orchestrator | Coordinate story lifecycle phases | Agent tool spawn per heavy phase; artifact read/write |
| epic-run orchestrator | Coordinate epic lifecycle across stories | Skill tool invocation of story-run (inline, main thread); thin checkpoint between stories |
| Phase skills (unchanged) | Execute individual phases | Read artifacts from disk, write artifacts to disk, return summary |

## Key Contracts

### Artifact I/O per phase (story-run) — Gemba-verified

| Phase | Classification | Reads from disk | Writes to disk | Returns inline |
|-------|:-------------:|----------------|----------------|----------------|
| start | Light (inline) | `.raise/manifest.yaml`, epic `scope.md` | `s{N}.{M}-story.md`, `s{N}.{M}-scope.md` | branch name |
| design | Heavy (fork) | `s{N}.{M}-story.md`, epic `scope.md` (optional) | `s{N}.{M}-design.md` | — |
| plan | Heavy (fork) | `s{N}.{M}-design.md` (optional), `s{N}.{M}-story.md` | `s{N}.{M}-plan.md` | — |
| implement | Heavy (fork) | `s{N}.{M}-plan.md`, `s{N}.{M}-design.md`, `.raise/manifest.yaml` | source code, tests, commits, `progress.md` | task completion summary |
| AR | Heavy (fork) | `s{N}.{M}-design.md`, `.raise/manifest.yaml`, git diff | **nothing** | verdict (PASS/PASS WITH QUESTIONS/SIMPLIFY) + findings |
| QR | Heavy (fork) | `.raise/manifest.yaml`, git diff | **nothing** | verdict (PASS/PASS WITH RECOMMENDATIONS/FAIL) + findings |
| review | Heavy (fork) | story artifacts, `.raise/manifest.yaml`, behavioral patterns | `s{N}.{M}-retrospective.md` | patterns emitted via CLI |
| close | Light (inline) | `s{N}.{M}-retrospective.md`, `.raise/manifest.yaml`, epic `scope.md` | epic scope update | merge commit |

### Subagent return contract

For phases that write artifacts, the orchestrator confirms success by checking the file exists on disk.
For AR/QR (inline-only, no persistent output), the orchestrator reads the verdict from the Agent tool return value.

| Phase type | Success signal | Orchestrator reads |
|-----------|---------------|-------------------|
| Artifact-producing (design, plan, implement, review) | File exists on disk | File path confirmation from agent return |
| Inline-only (AR, QR) | Agent return contains verdict | Verdict + findings from return value |

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

### Epic-run story iteration (inline, NOT forked)

```
For each story in progress tracking:
1. Invoke /rai-story-run {story_id} via Skill tool (inline, main thread)
2. story-run executes in main thread → CAN fork its heavy phases via Agent tool
3. Each heavy phase gets fresh context (depth 1)
4. After story completes, epic-run reads summary + updates progress tracking
5. Proceed to next story
```

**Critical rule:** epic-run MUST NOT fork story-run as a subagent. Forking
would make story-run a subagent (depth 1), preventing it from forking its
own phases (would need depth 2, blocked by F5). We never operate at known
lower quality levels.

**Context management:** The main thread accumulates context across stories,
but epic-run is thin — it only sees summaries between stories, not the full
tool call history of each phase (those live in forked subagent contexts that
are discarded). This keeps the main thread lightweight enough for multi-story
epics.

### Execution depth model

```
Main thread (story-run standalone OR story-run inside epic-run)
  └── Subagent (heavy phase) — depth 1
       └── Skill runs in fresh context, writes artifacts to disk

Main thread (epic-run)
  ├── story-run A (inline, main thread)
  │   └── Subagent (heavy phase) — depth 1
  ├── story-run B (inline, main thread)
  │   └── Subagent (heavy phase) — depth 1
  └── ...
```

Max depth is always 1. story-run always runs in main thread so it can fork.

## Migration Path

No backward compatibility concern. The orchestrator SKILL.md changes are purely additive — they change HOW phases are invoked (fork vs inline) but not WHAT phases do. Individual phase skills are unchanged.

Phase detection (artifact reverse-scan) is unaffected — it checks files on disk regardless of how they were created.

Delegation gates are unaffected — they happen in the main thread between fork invocations.

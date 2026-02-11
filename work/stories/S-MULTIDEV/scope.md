# Spike: Multi-Developer Collaboration Safety

## Story ID: S-MULTIDEV
## Type: Spike (research + design, no implementation)

## Problem

Fer is about to `git pull origin v2` and start working with Rai on the same repo. We haven't formally designed the multi-developer scenario. Several `.raise/` files are tracked in git and could cause:

1. **Merge conflicts** on generated files (index.json, patterns.jsonl)
2. **Overwrites** of per-developer state (session-state.yaml)
3. **Pattern collision** (both devs adding patterns with auto-incremented IDs)
4. **Graph thrash** (each `rai memory build` regenerates index.json differently)

## Known Risk Areas

| File | Tracked? | Risk | Notes |
|------|----------|------|-------|
| `.raise/rai/memory/index.json` | Yes | HIGH — merge conflicts guaranteed | 35K-line generated JSON, changes on every build |
| `.raise/rai/memory/patterns.jsonl` | Yes | HIGH — append conflicts, ID collisions | PAT-NNN auto-increments; two devs = duplicate IDs |
| `.raise/rai/session-state.yaml` | Yes | HIGH — per-developer state in shared file | Current story, phase, branch — different per dev |
| `.raise/rai/framework/methodology.yaml` | Yes | LOW | Rarely changes, shared definition |
| `.raise/rai/personal/` | .gitignored | SAFE | Telemetry, sessions — already personal |
| `~/.rai/developer.yaml` | Per-machine | SAFE | Profile, coaching — already personal |
| `CLAUDE.local.md` | .gitignored | SAFE | Already personal |
| `work/stories/*/` | Yes | MEDIUM | Different devs working different stories — usually OK |
| `governance/` | Yes | LOW | Shared governance, intentional collaboration |

## Questions to Answer

### Q1: What should be gitignored vs tracked?
- Should `index.json` be generated-on-demand (gitignored) instead of committed?
- Should `session-state.yaml` move to `.raise/rai/personal/`?
- Should `patterns.jsonl` be shared or per-developer?

### Q2: How do shared patterns work?
- If both devs add patterns, how do IDs stay unique?
- Should patterns be namespaced by developer? (`PAT-E-NNN` vs `PAT-F-NNN`?)
- Or should patterns.jsonl use UUIDs instead of sequential IDs?
- What's the merge strategy for JSONL? (append-only is JSONL's strength, but git doesn't know that)

### Q3: What's the "pull and start" experience?
- What does Fer need to do after `git pull origin v2`?
- Does he need `rai init`? Or just `rai session start`?
- What if his `~/.rai/developer.yaml` doesn't exist yet?

### Q4: Graph rebuild ownership
- Who rebuilds the graph? Both devs? Only on merge?
- Should `rai memory build` be a pre-commit hook?
- Or should index.json be gitignored and rebuilt on `rai session start`?

### Q5: Concurrent story work
- Two devs on different stories — branches are fine (git handles this)
- But what about shared work artifacts? (backlog.md, epic scope, etc.)
- What if both devs modify the same epic scope?

## In Scope
- Identify all files at risk
- Design gitignore/personal split
- Design pattern ID strategy for multi-dev
- Design "new developer onboard" flow
- Produce concrete recommendations (may become ADR)

## Out of Scope
- Implementation (this is a spike)
- CI/CD pipelines
- More than 2 developers (solve for 2 first)

## Done Criteria
- [ ] Risk matrix complete (all .raise/ files classified)
- [ ] Recommendation for gitignore changes
- [ ] Pattern ID collision strategy defined
- [ ] "Fer's first pull" checklist documented
- [ ] Decision on whether index.json should be tracked

## Priority
P1 — Fer is pulling v2 NOW. This needs answering before he makes his first commit.

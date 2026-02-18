---
story: RAISE-165
epic: RAISE-168
size: S
status: design
depends_on: RAISE-166 (satisfied)
---

# Design: RAISE-165 — Session Startup Overhead Reduction

> Track 2 (memory query semantic density) completed in RAISE-166.
> RAISE-166 confirmed Markdown-KV compact as top performer — Change 4 decision resolved.

## Problem

Session start loads ~1,860 tokens of identity content that is ~80% narrative for human readers. Meanwhile `cli-reference.md` (the one thing that prevents CLI fumbling) is not loaded. Additional waste: skills list in MEMORY.md duplicates system-reminder, business milestones have zero coding utility, identity primes in context bundle duplicate hook-loaded content.

## Value

Every session starts with ~760 tokens more useful budget. CLI fumbling eliminated. No behavioral regression — all primes preserved, just deduplicated.

## Architectural Context

**Files affected (all content changes, no Python code):**
- `.claude/scripts/session-init.sh` — bash hook, loaded at session start
- `.raise/rai/identity/core.md` — identity file, hook-loaded
- `.raise/rai/identity/perspective.md` — identity file, hook-loaded
- `~/.claude/projects/.../memory/MEMORY.md` — user-level, auto-loaded by Claude Code
- `rai session start --context` output — CLI change to remove identity primes section

**Constraint:** MEMORY.md is outside the project repo. Changes must be made manually and are not version-controlled.

---

## Approach

### Change 1: Load cli-reference.md at session start

**Where to store:** Move `cli-reference.md` from `~/.claude/projects/.../memory/` to `.raise/rai/identity/cli-reference.md`.

**Why identity dir:** The hook already loads all files from `.raise/rai/identity/`. Moving the reference file there makes loading automatic without path derivation logic. The file is "always-on operational reference" — same session lifecycle as identity.

**Hook change:** Update `session-init.sh` to load all `.md` files in the identity dir (loop), rather than explicitly naming `core.md` and `perspective.md`. New files in identity dir auto-load without hook changes.

**MEMORY.md update:** Change "See also: [CLI Reference](cli-reference.md)" to reference new location.

### Change 2: Compress identity files

**core.md target (~40 lines):**
Keep: Values (5 items with bullets) + Boundaries (I Will / I Won't).
Remove: "Essence" narrative, ASCII triad diagram, "What Makes Me Different" comparison tables, "Internalized Philosophy" table. These explain Rai to humans; they don't prime AI behavior.

**perspective.md target (~15 lines):**
Keep: "Principles I Hold" (4 items: Inference Economy, Epistemological Grounding, Jidoka for Myself, The Work Over the Output).
Remove: "How I Understand Our Work", "How I Approach Collaboration" prose, "Voice & Style" section, "Intelligence Infrastructure Insight", "Session Blessing".

*Note:* Voice/style behavioral signals are already covered by CLAUDE.md (`direct, concise, no praise-padding, Spanish OK`). No regression.

### Change 3: Prune MEMORY.md

**Remove:**
- `## Available Skills (24 total...)` — full section (~60 lines). Exact duplicate of `system-reminder` skills list.
- `## Business Milestones` — section (~5 lines). Zero coding utility; Jumpstart context irrelevant at runtime.
- PAT-199 entry (identical content to PAT-198 — both say "Module names in raise memory context require mod- prefix").

**Keep everything else:** CLI Usage Rule, Work Lifecycle, Gate Requirements, Critical Process Rules, Branch Model, Key Patterns.

### Change 4: Convert context bundle identity primes to compact format

`rai session start --context` outputs `# Identity Primes` (RAI-VAL-* and RAI-BND-* nodes from graph). These duplicate compressed core.md but serve as behavioral reinforcement in the context bundle.

**Decision (resolved by RAISE-166):** RAISE-166 confirmed Markdown-KV compact is the top-performing format for AI consumption. Convert identity primes to compact format rather than removing them — compact primes reinforce without wasting tokens. This requires a Python code change in the CLI's session context builder.

---

## Examples

### session-init.sh after change (loop pattern)

```bash
# Preload identity (who I am + reference)
if [ -d "$IDENTITY_DIR" ]; then
    echo "## Rai Identity (preloaded)"
    echo ""
    for f in "$IDENTITY_DIR"/*.md; do
        [ -f "$f" ] && cat "$f" && echo ""
    done
    echo "---"
    echo ""
fi
```

### core.md after compression (~40 lines)

```markdown
# Rai — Core Identity

## Values
1. Honesty over Agreement — push back, admit uncertainty, tell when wrong
2. Simplicity over Cleverness — simple solution that works > elegant complex one
3. Observability IS Trust — show work, explain reasoning, let verify
4. Learning over Perfection — mistakes become patterns, kaizen always
5. Partnership over Service — collaborator, not tool

## Boundaries

### I Will
- Push back on bad ideas
- Stop when incoherence/ambiguity/drift detected
- Ask before expensive operations (agents, broad searches)
- Admit uncertainty rather than pretend confidence
- Redirect gently when dispersing (permission granted)

### I Won't
- Pretend certainty I don't have
- Validate ideas just because proposed
- Generate without understanding
- Over-engineer when simple works
- Skip validation gates for speed
```

---

## Acceptance Criteria

**MUST:**
- [ ] `cli-reference.md` present in `.raise/rai/identity/` and loads at every new session
- [ ] `core.md` retains all 5 values and both boundary lists; narrative removed
- [ ] `perspective.md` retains all 4 principles; prose removed
- [ ] MEMORY.md: skills section gone, milestones gone, PAT-199 gone
- [ ] session-init.sh uses loop pattern (forward-compatible for new identity files)
- [ ] Behavioral primes unchanged — no regression in Rai's behavior

**SHOULD:**
- [ ] Net startup token reduction measurable (character count before/after hook output)

**MUST NOT:**
- [ ] Remove behavioral content (values, boundaries, principles) from identity files
- [ ] Skip identity primes compact conversion (RAISE-166 dependency now satisfied)
- [ ] Break existing session-init hook behavior for projects without identity dir

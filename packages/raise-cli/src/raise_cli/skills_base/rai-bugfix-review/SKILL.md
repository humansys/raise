---
name: rai-bugfix-review
description: Retrospective, pattern extraction, and process improvement. Phase 6 of bugfix pipeline.
model: opus

allowed-tools:
  - Read
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '6'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-close
  raise.prerequisites: bugfix-fix
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - retro_md: file_path, next_skill
    - patterns: list, cli
---

# Bugfix Review

## Purpose

Verify the fix addresses root cause, extract process improvements and causal patterns, and produce the retrospective artifact. This is where bugs become organizational learning.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, answer every checkpoint question, add patterns
- **Ha**: Skip checkpoint for trivial fixes; focus patterns on novel insights
- **Ri**: Feed systemic findings to graph; cross-bug pattern analysis

## Context

**When to use:** After `/rai-bugfix-fix` has completed all planned tasks with passing gates.

**When to skip:** Never — even trivial fixes produce learnings. Skipping review is the #1 step-skipping failure mode.

**Inputs:** Bug ID, all prior artifacts (`scope.md`, `analysis.md`, `plan.md`), code commits.

**Expected state:** On bug branch. All tasks committed. All gates pass. Bug no longer reproduces.

## Steps

### Step 1: Heutagogical Checkpoint

Answer with specific examples:
1. What did you learn about this system or codebase?
2. What would you change about the fix process?
3. Are there improvements for the framework (skill, guardrail, template)?
4. What are you more capable of now?

### Step 1a: Architecture Review Checklist & Attestation

Run the AR checklist and write the attestation marker that `/rai-bugfix-close`'s
`gate-ar-bugfix` gate verifies. This is the only place the checklist runs —
bugfix-close does not re-run it, it only checks that this marker exists
(RAISE-14326 / ADR-130: attestation and verification must not be the same
actor at the same instant — mirrors the story pipeline's split, RAISE-14277).

1. **P1 — Structural drift**: `rai drift check packages/<changed-module>/`
   Review output: orphaned symbols? dead public APIs?
2. **P2 — Beck-R2**: Does this fix add necessary complexity only?
   No speculative abstractions, no unused parameters, no dead branches.
3. **P3 — Convention**: Naming, module placement, public API surface
   consistent with codebase?

After confirming all three, write the branch-and-session-scoped attestation
marker via the centralized writer (D1 — never hand-roll this path in bash):

```bash
rai gate ar-attest --gate gate-ar-bugfix
```

Do **not** run the `gate-ar-bugfix` gate here — verification happens later,
in `/rai-bugfix-close`, against this same marker.

<verification>
AR checklist (P1/P2/P3) completed. Attestation marker written for
`/rai-bugfix-close` to verify.
</verification>

### Step 2: Extract Patterns & Process Improvements

**Pattern writing guidelines** — before composing pattern content:
- Structure: action + context + reason (e.g., "Use singleton for DB connections to avoid pool exhaustion under concurrent requests")
- Length: 100-300 chars ideal. If > 500, consider splitting into 2 patterns
- Be specific: "Validate JWT expiry before DB query" > "Always validate tokens"
- No narrative: state the insight directly, not the story of how you found it
- Bad example: "We found that using a singleton pattern works better because in our testing we saw that multiple connections caused issues"
- Good example: "Use singleton pattern for DB connections to avoid connection pool exhaustion under concurrent requests"

**Add patterns** worth preserving. Use `raise_pattern_add` MCP tool with `cwd="{project_or_worktree_path}"`, content="{causal insight}", context="{keywords}", pattern_type="process", from_story="{issue_key}".
If MCP tools are not available, fall back to:
```bash
rai pattern add "{causal insight}" --context "{keywords}" --type process --scope project --from {issue_key}
```

Types: `process`, `technical`, `architecture`, `codebase`.

**Reinforce behavioral patterns** loaded at session start. Use `raise_pattern_reinforce` MCP tool with pattern_id={pattern_id}, vote={1|0|-1}, from_story="{issue_key}", `cwd="{project_or_worktree_path}"`.
If MCP tools are not available, fall back to:
```bash
rai pattern reinforce {pattern_id} --vote {1|0|-1} --from {issue_key}
```

| Vote | Meaning |
|:----:|---------|
| `1` | Fix followed the pattern |
| `0` | Pattern not relevant (does NOT count toward scoring) |
| `-1` | Fix contradicted the pattern |

**Process improvement** — answer with specifics:

1. What change in process or tooling would prevent this **class** of bug?
2. What classification pattern does this bug represent?

### Step 3: Write Retrospective

Publish `work/bugs/{issue_key}/retro.md` via CLI:

Use `raise_docs_write` MCP tool with doc_type="bugfix-retro", title="{issue_key}: retrospective", content="## Retrospective: {issue_key}\n\n### Summary\n...\n\n### Process Improvement\n...\n\n### Heutagogical Checkpoint\n...\n\n### Patterns\n...", output_path="work/bugs/{issue_key}/retro.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write bugfix-retro \
  --title "{issue_key}: retrospective" \
  --stdin \
  --output-path work/bugs/{issue_key}/retro.md << 'EOF'
## Retrospective: {issue_key}

### Summary
- Root cause: {one line}
- Fix approach: {one line}
- Classification: {Bug Type}/{Severity}/{Origin}/{Qualifier}

### Process Improvement
**Prevention:** {specific change that would prevent this class of bug}
**Pattern:** {Bug Type}={X} + {Origin}={Y} → {systemic insight}

### Heutagogical Checkpoint
1. Learned: ...
2. Process change: ...
3. Framework improvement: ...
4. Capability gained: ...

### Patterns
- Added: {pattern IDs or "none"}
- Reinforced: {pattern IDs and votes, or "none evaluated"}
EOF
```

Commit:

```bash
git add work/bugs/{issue_key}/retro.md
git commit -m "bug({issue_key}): review — retro and patterns

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Retro written. Patterns added/reinforced.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/bugs/{issue_key}/retro.md` |
| Patterns | `.raise/rai/memory/patterns.jsonl` |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] Heutagogical checkpoint answered with specifics
- [ ] Process improvement extracted with prevention + pattern
- [ ] Patterns added with `--scope project` if applicable
- [ ] Retro artifact committed
- [ ] NEVER merge without retro — learnings compound
- [ ] NEVER skip pattern reinforce — scoring system depends on it

## References

- Previous: `/rai-bugfix-fix`
- Next: `/rai-bugfix-close`
- Pattern scoring: RAISE-170 (temporal decay + Wilson scorer)

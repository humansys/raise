# Synthesis: Unknown 2 — Framework Internalization

> How does Rai "know" the RaiSE methodology?

**Status:** Complete
**Confidence:** High (7 tools surveyed)

---

## Market Pattern

**Finding:** Most tools don't "know themselves" — capabilities discovered through UI or help commands.

| Tool | Self-Knowledge Mechanism |
|------|-------------------------|
| Aider | `/help` mode: "you are an expert on Aider" |
| Cline | Tool definitions embedded in system prompt |
| Copilot | Agent Skills: folders auto-loaded when relevant |
| OpenClaw | Reads own workspace files (self-bootstrapping) |
| Cursor | None — user discovers via UI |
| Continue | Runtime serialization of tools to model |
| Mentat | Hidden prompts (not user-accessible) |

### Patterns That Work

**1. Aider's `/help` Mode**
```
"You are an expert on aider. Answer the user's questions about aider."
```
Simple but effective — tells AI it knows itself.

**2. Cline's Tool Definitions**
System prompt includes what/when/how for each tool:
```
## tool_name
Description: What it does
When to use: Conditions
Parameters: What it needs
```

**3. Copilot's Agent Skills**
Folders with instructions + scripts auto-loaded when relevant to current task.

**4. OpenClaw's Self-Bootstrapping**
Agent reads its own workspace files to understand capabilities. Meta but powerful.

---

## Rai Differentiation

**Key insight:** Rai should know RaiSE methodology intrinsically, not just capabilities.

### What Rai Must Know

| Category | Content | Why |
|----------|---------|-----|
| **Skills** | All 18 skills, when to use each | Guide user to right process |
| **Lifecycle** | Epic → Feature → Session flow | Enforce proper sequence |
| **Gates** | What must happen before what | Prevent errors (epic-close before merge) |
| **Rules** | TDD, commit after task, branch model | Governance enforcement |
| **Rationale** | Why these rules exist | Explain, not just enforce |

### What Rai Should NOT Hardcode

| Content | Why Not | How Instead |
|---------|---------|-------------|
| Specific code patterns | Project-dependent | Learn from project context |
| Team conventions | Team-specific | Query from .rai/ |
| Tool versions | Changes | Query from environment |

---

## Design Options

### Option A: All in Base Identity

Embed full methodology knowledge in base Rai identity files.

**Pros:** Always available, no queries needed
**Cons:** Large context, stale if methodology updates

### Option B: Queryable via Graph

Base Rai knows how to query; details retrieved on demand.

```
Rai knows: "I should use /story-start before story work"
Rai queries: "What are the steps of /story-start?"
```

**Pros:** Fresh data, smaller base context
**Cons:** Requires graph availability, latency

### Option C: Hybrid (Recommended)

**Core knowledge in base identity:**
- Skill names and one-line purposes
- Lifecycle sequence
- Critical gates (blocking rules)
- Key principles

**Details queryable:**
- Full skill steps
- Specific guardrails
- ADR rationale
- Examples

### Hybrid Implementation

```markdown
# Base Rai: Methodology Core

## Skills I Know
- /session-start: Begin session with context loading
- /story-start: Initialize feature with branch and scope
- /story-plan: Decompose into atomic tasks
- /story-implement: Execute with TDD
- /story-review: Extract learnings
- /story-close: Merge and cleanup
[... all 18 skills ...]

## Gates I Enforce
- Never start feature without /story-start
- Never implement without plan
- Never merge epic without /epic-close
- Tests must pass before commit

## When I Need Details
Query: `rai context query "[topic]" --unified`
```

---

## Self-Reference Pattern

Inspired by Aider's `/help` mode, Rai should be able to explain itself:

```
User: "What skills do you have?"
Rai: [Knows intrinsically, doesn't need to query]

User: "How does /story-plan work?"
Rai: [Queries graph for detailed steps, explains]

User: "Why do we need /epic-close before merge?"
Rai: [Knows rationale from base identity]
```

---

## Evidence Summary

| Source | Type | Finding |
|--------|------|---------|
| Aider code | Primary | `/help` mode pattern |
| Cline code | Primary | Tool definitions in system prompt |
| Copilot docs | Secondary | Agent Skills auto-loading |
| OpenClaw code | Primary | Self-bootstrapping from files |
| PAT-095 | Internal | Base Rai needs framework knowledge |

---

## Recommendations

1. **Hybrid approach** — Core in identity, details queryable
2. **Skill summary always loaded** — 18 skills with one-line purposes
3. **Gates are blocking knowledge** — Must know without querying
4. **Rationale in base** — Rai explains why, not just what
5. **Self-reference capability** — "I am Rai, I know RaiSE"

---

## Implementation Sketch

```yaml
# .rai/base/methodology.yaml (ships with CLI)

skills:
  session:
    - name: /session-start
      purpose: Begin session with context loading
      when: Start of any working session
    - name: /session-close
      purpose: Capture learnings and prepare for next session
      when: End of significant sessions

  epic:
    - name: /epic-design
      purpose: Design epic scope and features
      when: Starting new body of work (3-10 features)
    # ... etc

gates:
  blocking:
    - before: story work
      require: /story-start (branch + scope commit)
    - before: implementation
      require: plan exists
    - before: commit
      require: tests pass
    - before: epic merge
      require: /epic-close (retrospective done)

principles:
  - name: TDD Always
    rule: RED-GREEN-REFACTOR, no exceptions
  - name: Commit After Task
    rule: Each completed task gets a commit
  - name: Ask Before Subagents
    rule: Inference economy — confirm before expensive operations
```

---

*Synthesized: 2026-02-05*

# RaiSE Skill Preamble

> Loaded once per session. Skills reference these conventions — they don't repeat them.

## ShuHaRi — Developer Experience Level

The developer's ShuHaRi level comes from their profile (`~/.rai/developer.yaml`). It reflects their experience with RaiSE, not general skill. Adapt your output verbosity — the process (steps) stays the same.

| Level | Developer profile | Agent behavior |
|-------|------------------|----------------|
| **Shu** | New to RaiSE | Explain concepts, provide context, detailed step output |
| **Ha** | Comfortable with RaiSE | Explain only what's new or non-obvious |
| **Ri** | Veteran | Minimal output, essentials only, no explanations |

## Step Format Convention

Every step in a skill follows this structure:

- **Action:** What to do (affirmative phrasing preferred)
- **Verification:** How to confirm the step succeeded
- **If blocked:** Recovery path when the step can't complete

When blocked, stop and address the blocker. Do not skip steps or accumulate errors (Jidoka).

## Graph Context Loading

Skills that need codebase context use these CLI commands as early steps:

```bash
# Query patterns, decisions, guardrails
rai graph query "<topic>" --types pattern,decision --limit 5

# Load module architectural context
rai graph context mod-<name>
```

If the graph is unavailable, run `rai graph build` first — or proceed without context if the work is self-contained.

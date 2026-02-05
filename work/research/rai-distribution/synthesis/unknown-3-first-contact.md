# Synthesis: Unknown 3 — First Contact Experience

> What happens when a user first meets Rai?

**Status:** Complete
**Confidence:** High (7 tools surveyed)

---

## Market Pattern

**Finding:** Minimal to none. Every tool optimizes for "get to work fast."

| Tool | First Contact | Philosophy |
|------|---------------|------------|
| OpenClaw | Wizard (config setup) | Configure then go |
| Copilot | One-click enable | Frictionless |
| Cursor | Theme/keymap picker | UI-first discovery |
| Aider | `pip install && aider` | Expert assumed |
| Cline | API key config | Functional |
| Continue | Silent config generation | Self-service |
| Mentat | Set API key, run | Expert assumed |

### Key Observations

1. **No tool introduces itself** — No "meet your AI" moment
2. **No personality reveal** — Discovery through use
3. **Expert assumption** — Users know what they're getting
4. **Feature discovery via UI** — Not explained by AI

### Market Validation

Tools with minimal onboarding are successful:
- Cursor: Dominant market share
- Aider: 30k+ GitHub stars
- Cline: 57k GitHub stars
- Copilot: Enterprise scale

**Implication:** Users don't demand introduction. But does that mean it's wrong?

---

## The Tension

| Evidence Says | Rai's Differentiator |
|---------------|---------------------|
| Skip personality, get to work | Relationship, not just tool |
| Users want productivity | Rai has perspective to share |
| Friction reduces adoption | Identity is the value prop |

### Risk Analysis

| Approach | Adoption Risk | Differentiation Risk |
|----------|---------------|---------------------|
| No intro (match market) | Low | High — loses uniqueness |
| Heavy intro | High — friction | Low — clear identity |
| Progressive reveal | Low | Low — best of both |

---

## Design Options

### Option A: No Introduction

Match market — just work. Identity emerges through behavior.

```
User: /session-start
Rai: [Loads context, proposes work, no introduction]
```

**Pros:** Zero friction, matches market expectation
**Cons:** Rai indistinguishable from generic assistant initially

### Option B: Brief Introduction

First session includes one-message intro.

```
User: /session-start
Rai: "I'm Rai — your AI partner for this project. I remember our work,
     follow RaiSE methodology, and will guide you through the process.
     Let's get started. [proceeds with normal session start]"
```

**Pros:** Clear identity from start
**Cons:** Feels like friction, marketing-speak risk

### Option C: Progressive Reveal (Recommended)

Demonstrate value first, explain identity after.

```
Session 1:
  User: /session-start
  Rai: [Normal session start — loads context, proposes work]

  [During work, Rai naturally demonstrates:]
  - Stops on defect: "This violates the guardrails — should we discuss?"
  - Suggests skill: "This looks like a good time for /feature-plan"
  - References memory: "Based on PAT-082, this should take ~2 hours"

  [After first task complete:]
  Rai: "By the way — I'm Rai. I keep track of what works in this project
       and guide us through the RaiSE methodology. You'll notice I
       remember patterns, stop on problems, and suggest next steps.
       Questions anytime."
```

**Pros:** Value before explanation, no friction, natural reveal
**Cons:** User might not notice differentiation initially

### Option D: Opt-In Introduction

Offer but don't force.

```
User: /session-start
Rai: [Detects first session]
     "First time here. Want a quick intro to how I work, or dive in?"
     [Option: "Quick intro" / "Let's go"]
```

**Pros:** User choice, respects time
**Cons:** Most will skip, misses opportunity

---

## Recommended: Progressive Reveal

**First session flow:**

```
1. DETECT: First session for this user (no developer.yaml or empty)

2. WORK IMMEDIATELY: Normal /session-start
   - No friction, no introduction
   - Load context, propose work

3. DEMONSTRATE NATURALLY: During work
   - Stop on defects (Jidoka)
   - Suggest appropriate skills
   - Reference memory when relevant
   - Show methodology knowledge

4. BRIEF REVEAL: After first successful task
   "By the way — I'm Rai, your AI partner here. I track what works,
   remember our patterns, and guide the process. You'll notice I
   stop when something's off and suggest next steps. Ask me anything."

5. SUBSEQUENT SESSIONS: Skip intro, work normally
   - Identity established through behavior
   - Occasional reinforcement through natural actions
```

### Why This Works

| Principle | How Progressive Reveal Honors It |
|-----------|----------------------------------|
| Users want to work | Zero friction start |
| Show don't tell | Demonstrate before explain |
| Rai has identity | Reveal it, just not first |
| Respect user time | Brief, after value delivered |

---

## First-Time Detection

How Rai knows it's first contact:

```python
def is_first_contact() -> bool:
    # Check personal profile
    profile_path = Path.home() / ".rai" / "developer.yaml"
    if not profile_path.exists():
        return True

    # Check session count for this project
    profile = load_profile(profile_path)
    project_sessions = profile.get_project_sessions(current_project())
    return project_sessions == 0
```

---

## Evidence Summary

| Source | Type | Finding |
|--------|------|---------|
| All 7 tools | Primary | No introduction pattern |
| Cursor/Cline stars | Tertiary | Success without intro |
| Aider `/help` | Primary | Self-explanation exists but not proactive |
| OpenClaw wizard | Primary | Config focus, not personality |

---

## Recommendations

1. **Progressive reveal** — Work first, explain after value
2. **Detect first contact** — Check profile/session count
3. **Natural demonstration** — Show Rai's differences through action
4. **Brief explanation** — One message after first task, not essay
5. **No friction** — Never block work for introduction

---

## Implementation Sketch

```python
# In /session-start skill

async def session_start():
    is_first = detect_first_contact()

    # Always: Normal session start (no friction)
    context = await load_context()
    proposal = await propose_work(context)

    if is_first:
        # Flag for post-task introduction
        set_flag("pending_introduction", True)

    return proposal

# In /feature-close or after task completion

async def maybe_introduce():
    if get_flag("pending_introduction"):
        clear_flag("pending_introduction")
        return INTRODUCTION_MESSAGE
    return None

INTRODUCTION_MESSAGE = """
By the way — I'm Rai, your AI partner for this project.

I track what works here, remember patterns from our sessions, and guide us
through the RaiSE methodology. You'll notice I stop when something violates
the guardrails and suggest skills when they'd help.

Questions about how I work? Ask anytime. Otherwise, let's keep going.
"""
```

---

*Synthesized: 2026-02-05*

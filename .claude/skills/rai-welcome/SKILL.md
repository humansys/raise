---
name: rai-welcome
description: Onboard a developer to RaiSE interactively. Use for first-time setup.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: once-per-developer
  raise.fase: "setup"
  raise.prerequisites: ""
  raise.next: "rai-session-start"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Welcome

## Purpose

Get a developer fully set up in a RaiSE project through a guided flow that detects their situation and only asks what's needed.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, explain what each governance doc is for
- **Ha**: Detect scenario and fast-path through known setups
- **Ri**: One-shot setup with minimal questions

## Context

**When to use:** First time a developer works in a RaiSE project. Subsequent runs verify setup.

**When to skip:** Developer is already set up (profile exists, graph exists, CLAUDE.local.md exists).

**Inputs:** A project with `.raise/` directory (from `rai init`).

## Steps

### Step 1: Detect Scenario

```bash
ls ~/.rai/developer.yaml 2>/dev/null && echo "PROFILE_EXISTS" || echo "NO_PROFILE"
ls .raise/ 2>/dev/null && echo "RAISE_EXISTS" || echo "NO_RAISE"
```

| Profile? | `.raise/`? | Action |
|----------|------------|--------|
| No | Yes | Full setup (Steps 2-5) |
| Yes | Yes | Verify only (Step 4) |
| Any | No | Stop: "Run `rai init` first, then `/rai-welcome` again." |

<verification>
Scenario detected. `.raise/` exists.
</verification>

### Step 2: Create Profile (if needed)

Ask developer's name (only mandatory question). Derive pattern prefix (first letter, uppercased), confirm.

```bash
rai session start --name "{name}" --project .
```

Edit `~/.rai/developer.yaml` to add confirmed `pattern_prefix`.

<verification>
`~/.rai/developer.yaml` exists with name and pattern_prefix.
</verification>

### Step 3: Optional Personalization

Frame as skippable: "Want to customize? Or skip — defaults work well."

If customize, ask up to 3 questions:
1. **Language:** English / Spanish / Other → `communication.language`
2. **Style:** Detailed / Balanced / Direct → `communication.style`
3. **Focus guidance:** Yes / No → `communication.redirect_when_dispersing`

Defaults: `shu`, `balanced`, `en`, `detailed_explanations: true`, `redirect_when_dispersing: false`.

<verification>
Preferences saved or defaults accepted.
</verification>

### Step 4: Verify Setup

Build graph if missing (`rai graph build`). Scaffold `CLAUDE.local.md` if missing. Run context bundle:

```bash
rai session start --project . --context
```

Check: developer name appears, session count shown, no errors.

<verification>
Profile, graph, and local config all present and functional.
</verification>

### Step 5: Welcome Message

```
Welcome to RaiSE, {name}!
Setup: Profile ({prefix}), Graph ({N} concepts), CLAUDE.local.md
Next: /rai-session-start
```

## Output

| Item | Destination |
|------|-------------|
| Developer profile | `~/.rai/developer.yaml` |
| Knowledge graph | `.raise/rai/memory/index.json` |
| Local config | `CLAUDE.local.md` |
| Next | `/rai-session-start` |

## Quality Checklist

- [ ] Scenario detected before asking any questions
- [ ] Name is the only mandatory question
- [ ] Personalization clearly framed as optional
- [ ] Graph built if missing (not assumed)
- [ ] Context bundle runs successfully after setup
- [ ] NEVER overwrite existing CLAUDE.local.md
- [ ] NEVER ask about experience level — learned implicitly through coaching

## References

- Profile model: `src/raise_cli/onboarding/profile.py`
- Next: `/rai-session-start`
- One-time skill: subsequent runs verify, not recreate

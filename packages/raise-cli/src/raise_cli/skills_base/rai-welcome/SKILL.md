---
name: rai-welcome
description: Onboard a developer to RaiSE interactively. Use for first-time setup.
model: haiku

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
  raise.next: "rai-project-create, rai-project-onboard"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Welcome

## Purpose

Get a developer fully set up in a RaiSE project through a guided flow that detects their situation and only asks what's needed.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, explain what each step does and why
- **Ha**: Detect scenario and fast-path through known setups
- **Ri**: One-shot setup with minimal questions

## Context

**When to use:** First time a developer works in a RaiSE project. Subsequent runs verify setup.

**When to skip:** Developer is already set up (profile exists, governance completed).

**Inputs:** A project with `.raise/` directory (from rai init).

## Steps

### Step 1: Detect Scenario

```bash
ls ~/.rai/developer.yaml 2>/dev/null && echo "PROFILE_EXISTS" || echo "NO_PROFILE"
ls .raise/ 2>/dev/null && echo "RAISE_EXISTS" || echo "NO_RAISE"
```

| Profile? | `.raise/`? | Action |
|----------|------------|--------|
| No | Yes | Full setup (Steps 2-6) |
| Yes | Yes | Verify only (Step 4), then route (Step 5) |
| Any | No | Stop: "Run rai init first, then `/rai-welcome` again." |

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

Check that the profile was created correctly:

```bash
cat ~/.rai/developer.yaml
```

| Check | Pass |
|-------|------|
| `~/.rai/developer.yaml` exists | Profile created |
| File has `name` and `pattern_prefix` | Fields populated |

<verification>
Profile exists with name and pattern_prefix.
</verification>

### Step 5: Governance Routing

Present both paths for the developer to choose:

```
Welcome to RaiSE, {name}!
Profile: {prefix} · Next step: set up project governance.
```

| Project type | What it means | Next skill |
|-------------|---------------|------------|
| **New project** (greenfield) | No source code yet, starting from scratch | `/rai-project-create` |
| **Existing project** (brownfield) | Source code already exists, onboarding RaiSE | `/rai-discover` → `/rai-project-onboard` |

Ask developer to choose. Do NOT analyze the codebase — that is `/rai-discover`'s job.

<verification>
Developer chose a path. Next skill identified.
</verification>

### Step 6: Adapter Guidance

Check which adapter config files exist:

```bash
ls .raise/backlog.yaml 2>/dev/null && echo BACKLOG_OK || echo BACKLOG_MISSING
ls .raise/docs.yaml 2>/dev/null && echo DOCS_OK || echo DOCS_MISSING
```

If one or both are missing, mention them:

| Missing | Line to show |
|---------|-------------|
| `backlog.yaml` | `- No backlog tracker — run /rai-backlog-setup to connect Jira or another tracker` |
| `docs.yaml` | `- No docs adapter — run /rai-docs-setup to connect Confluence or another docs target` |

Only show missing adapters. If both exist, skip silently. Adapters are optional — do not block on them.

<verification>
Adapter status checked. Missing adapters mentioned (or nothing shown if both present).
</verification>

## Output

| Item | Destination |
|------|-------------|
| Developer profile | `~/.rai/developer.yaml` |
| Adapter guidance | Shown in welcome message if adapters missing |
| Next | `/rai-project-create` (greenfield) or `/rai-discover` → `/rai-project-onboard` (brownfield) |

## Quality Checklist

- [ ] Scenario detected before asking any questions
- [ ] Name is the only mandatory question
- [ ] Personalization clearly framed as optional
- [ ] Governance routing presented (greenfield/brownfield) — developer chooses
- [ ] NEVER run graph build (no content to index at this stage)
- [ ] NEVER run session context bundle (no mission/story exists yet)
- [ ] NEVER ask about experience level — learned implicitly through coaching

## References

- Profile model: `src/raise_cli/onboarding/profile.py`
- Next: `/rai-project-create` (greenfield) or `/rai-discover` → `/rai-project-onboard` (brownfield)
- One-time skill: subsequent runs verify, not recreate

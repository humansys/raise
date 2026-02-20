---
name: rai-welcome
description: >
  Conversational developer onboarding for RaiSE. Detects scenario,
  sets up profile and graph, offers optional personalization.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: once-per-developer
  raise.fase: "setup"
  raise.prerequisites: ""
  raise.next: "rai-session-start"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
---

# Welcome — Developer Onboarding

## Purpose

Get a developer fully set up in a RaiSE project through a guided flow that detects their situation and only asks what's needed. Replaces the manual checklist with a single skill invocation.

**Design principle:** Works immediately with sensible defaults. Personalization is optional.

## Steps

### Step 1: Detect Scenario

Check two things to determine the onboarding scenario:

```bash
# Check for developer profile
ls ~/.rai/developer.yaml 2>/dev/null && echo "PROFILE_EXISTS" || echo "NO_PROFILE"

# Check for RaiSE project
ls .raise/ 2>/dev/null && echo "RAISE_EXISTS" || echo "NO_RAISE"
```

**Scenario matrix:**

| Profile? | `.raise/`? | Scenario | Action |
|----------|------------|----------|--------|
| No | Yes | **New dev, RaiSE repo** | Full setup (Step 2-6) |
| Yes | No | **RaiSE dev, new repo** | Guard rail (Step 1b) |
| Yes | Yes | **RaiSE dev, RaiSE repo** | Verify only (Step 5) |
| No | No | **Brand new** | Guard rail (Step 1b) |

### Step 1b: Guard Rail — No `.raise/` Directory

If `.raise/` doesn't exist, this project hasn't been initialized with RaiSE yet.

**Tell the user:**
> This project isn't set up with RaiSE yet. Run `rai init` first to initialize the project structure, then run `/rai-welcome` again.

**Stop here.** Do not proceed with profile creation — it needs a project context.

### Step 2: Ask Name (If No Profile)

**Only if `~/.rai/developer.yaml` does not exist.**

Use AskUserQuestion to ask:
- **Question:** "What's your name?"
- This is the only mandatory question.

Then derive the pattern prefix (first letter of name, uppercased) and confirm:

Use AskUserQuestion:
- **Question:** "Your pattern prefix will be '{X}' (used for pattern IDs like PAT-{X}-001). Good?"
- **Options:** "Yes, use '{X}'" / "Choose different letter"

If they choose different, ask which letter they prefer.

### Step 3: Create Profile

Run the CLI to create the developer profile:

```bash
rai session start --name "{name}" --project "$(pwd)"
```

Then set the pattern prefix by editing `~/.rai/developer.yaml`:
- Read the file
- Add or update the `pattern_prefix` field with the confirmed letter
- Write the file back

**Verify:** Read `~/.rai/developer.yaml` and confirm `name` and `pattern_prefix` are set.

### Step 4: Build Graph (If Missing)

Check if the knowledge graph exists:

```bash
ls .raise/rai/memory/index.json 2>/dev/null && echo "GRAPH_EXISTS" || echo "NO_GRAPH"
```

If missing, build it:

```bash
rai memory build
```

**Verify:** `.raise/rai/memory/index.json` exists after build.

### Step 4b: Scaffold CLAUDE.local.md (If Missing)

If `CLAUDE.local.md` doesn't exist in the project root, create it with minimal content:

```markdown
# RaiSE Project — {project_directory_name}
Run `/rai-session-start` for context.
```

**DO NOT** overwrite an existing `CLAUDE.local.md`.

### Step 5: Verify Setup

Run the context bundle to confirm everything works:

```bash
rai session start --project "$(pwd)" --context
```

**Check the output for:**
- Developer name appears
- Session count is shown
- No errors about missing graph or profile

If this is the **"RaiSE dev, RaiSE repo"** scenario (both profile and `.raise/` exist), also check:
- `pattern_prefix` is set in `~/.rai/developer.yaml` (if missing, ask and set it)
- Graph exists (rebuild if missing)
- `CLAUDE.local.md` exists (scaffold if missing)

**Present results:**
> Setup verified:
> - Profile: {name}, prefix {X}
> - Graph: {N} concepts loaded
> - Local config: CLAUDE.local.md {present/created}

### Step 6: Optional Personalization

**IMPORTANT:** This step is entirely optional. Frame it clearly as skippable.

Use AskUserQuestion:
- **Question:** "Want to customize how Rai works with you? (language, communication style) Or skip — defaults work well and you can change later."
- **Options:** "Customize" / "Skip, use defaults"

**If Skip:** Go directly to Step 7.

**If Customize:** Ask up to 3 preference questions using AskUserQuestion:

**Question 1 — Language:**
- "Preferred language for Rai's responses?"
- Options: "English" / "Spanish" / "Other"
- Maps to: `communication.language` in `~/.rai/developer.yaml`

**Question 2 — Communication style:**
- "How should Rai communicate?"
- Options:
  - "Detailed — explain concepts, show reasoning" → `style: explanatory`, `detailed_explanations: true`
  - "Balanced — explain new things, be efficient on known" → `style: balanced`, `detailed_explanations: true`
  - "Direct — minimal explanation, maximum efficiency" → `style: direct`, `detailed_explanations: false`

**Question 3 — Focus guidance:**
- "Can Rai redirect you if you drift off-topic during work?"
- Options: "Yes, keep me focused" / "No, let me explore"
- Maps to: `communication.redirect_when_dispersing` (true/false)

After collecting answers, update `~/.rai/developer.yaml` with the preferences:
- Read the current file
- Update the `communication` section with chosen values
- Write back

**DO NOT ask about:**
- Experience level or skill categorization
- "Are you a beginner/intermediate/expert?"
- Lean/TDD familiarity
- AI-assisted development comfort level

These are learned implicitly through the coaching context over working sessions.

### Step 7: Welcome Message

Present the completion summary:

```
Welcome to RaiSE, {name}!

Setup complete:
- Profile: ~/.rai/developer.yaml (prefix {X})
- Graph: .raise/rai/memory/index.json ({N} concepts)
- Local config: CLAUDE.local.md

Next steps:
- Run /rai-session-start to begin your first working session
- To change preferences later: edit ~/.rai/developer.yaml
- To learn about the workflow: check governance/architecture/
```

## Sensible Defaults

When no personalization is chosen, these defaults apply:

| Field | Default | Why |
|-------|---------|-----|
| `experience_level` | `shu` | More guidance is safer than less for new setup |
| `communication.style` | `balanced` | Middle ground |
| `communication.language` | `en` | Most common |
| `communication.skip_praise` | `false` | Default expectation |
| `communication.detailed_explanations` | `true` | Better to over-explain initially |
| `communication.redirect_when_dispersing` | `false` | Permission must be granted |

## Notes

- **One-time skill:** Run once per developer per machine. Subsequent runs verify setup.
- **No `rai init`:** Project initialization is a separate concern. This skill assumes `.raise/` exists or tells you to create it.
- **Implicit learning:** The coaching context in `developer.yaml` learns from `/rai-session-close` reflections over time. No need to self-categorize upfront.
- **File-based personalization:** Consistent with industry pattern (Cursor, Aider, Claude Code, Copilot all use config files, not wizards).

## References

- Profile model: `src/rai_cli/onboarding/profile.py`
- Session start: `.claude/skills/rai-session-start/SKILL.md`
- Fer's checklist (replaced): `work/stories/S-MULTIDEV/fer-first-pull.md`

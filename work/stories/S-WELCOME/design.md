# Design: S-WELCOME — Developer Onboarding Skill

## Problem

Setting up as a developer in a RaiSE project requires 6 manual steps (install, create profile, set pattern_prefix, build graph, create CLAUDE.local.md, verify). The flow differs by scenario. There's no guided experience — Fer's onboarding depends on a checklist document.

## Value

Any developer runs `/rai-welcome` and is fully set up. One skill invocation replaces a multi-step checklist. Setup takes ~60 seconds, not 10 minutes of reading docs.

## Research Findings (Informing Design)

Industry research on developer tool onboarding reveals:

1. **Every successful AI coding tool (Cursor, Aider, Claude Code, Copilot, Windsurf) uses zero-config defaults.** None force setup wizards. None ask experience level.
2. **Self-reported skill levels are unreliable** (Dunning-Kruger) and threatening (imposter syndrome — 88% of developers report it). Asking "are you a beginner?" produces bad data and bad feelings.
3. **Preferences emerge from use, not introspection.** "How do you want AI to communicate?" is unanswerable before you've used the AI.
4. **PAT-E-076 already told us:** "Config files > interactive wizards — wizard only when choices can't be inferred."
5. **PAT-E-078:** "Onboarding IS education — setup process teaches methodology concepts."

**Design principle: works immediately, customize if you want.**

## Approach

### Two-Phase Onboarding: Quick Setup + Optional Personalization

**Phase 1 — Quick Setup (mandatory, ~30 seconds):**
- Auto-detect scenario from filesystem state
- Ask only what can't be inferred: **name** (if no profile exists)
- Auto-derive `pattern_prefix` from name, confirm with user
- Run deterministic setup: create profile, build graph, scaffold CLAUDE.local.md
- Verify setup works

**Phase 2 — Optional Personalization (offered, skip-friendly):**
- "Want to customize how Rai works with you? Or skip — defaults work well."
- If yes: 2-3 **preference** questions (not identity/skill questions)
  - Language (en/es/etc.)
  - Communication style: "brief and direct" vs "detailed with explanations"
  - Redirect permission: "Can I redirect if we go off-topic?"
- If skip: sensible defaults apply, user can edit `~/.rai/developer.yaml` later

**Phase 3 — Implicit Learning (ongoing, no user action):**
- Coaching context already learns from `/rai-session-close` reflections
- ShuHaRi level stays at default (shu) and can be manually adjusted — auto-progression is out of scope

### Sensible Defaults

| Field | Default | Rationale |
|-------|---------|-----------|
| `experience_level` | `shu` | Safe — more explanation is better than less for new setup |
| `communication.style` | `balanced` | Middle ground; not condescending, not terse |
| `communication.language` | `en` | Most common; ask only in Phase 2 |
| `communication.skip_praise` | `false` | Default human expectation |
| `communication.detailed_explanations` | `true` | Better to over-explain than under-explain initially |
| `communication.redirect_when_dispersing` | `false` | Permission must be explicitly granted |

### Four Scenarios (Auto-Detected)

Detection logic: check `~/.rai/developer.yaml` exists + `.raise/` dir exists.

| Scenario | Profile? | `.raise/`? | What to Do |
|----------|----------|------------|------------|
| **New dev, RaiSE repo** | No | Yes | Phase 1: name → profile → prefix → graph build → CLAUDE.local.md → verify |
| **RaiSE dev, new repo** | Yes | No | Inform: run `rai init` first (out of scope). If `.raise/` exists after init: graph build → verify |
| **RaiSE dev, RaiSE repo** | Yes | Yes | Verify setup, rebuild graph if missing, scaffold CLAUDE.local.md if missing |
| **Brand new** | No | No | Inform: run `rai init` first. Then full Phase 1 |

**IMPORTANT:** Scenarios 2 and 4 (no `.raise/` dir) are **guard rails**, not full flows. The skill tells the user what to do (`rai init`) and exits. Project initialization is a separate concern.

### Skill Architecture

This is a **prompt-only skill** (like `/rai-session-start`). No new CLI commands needed. The skill instructs Claude to:

1. Read filesystem to detect scenario
2. Use `AskUserQuestion` for name/prefix if needed
3. Run existing CLI: `rai session start --name "X" --project "$(pwd)"`
4. Edit `~/.rai/developer.yaml` to set `pattern_prefix`
5. Run `rai memory build` if `index.json` missing
6. Write `CLAUDE.local.md` from template if missing
7. Offer Phase 2 personalization (use `AskUserQuestion`)
8. Verify: `rai session start --project "$(pwd)" --context`
9. Print welcome message with next steps

### Components Affected

| Component | Change Type | What |
|-----------|-------------|------|
| `.claude/skills/rai-welcome/SKILL.md` | **Create** | Skill prompt definition |
| `src/rai_cli/onboarding/profile.py` | None | Already has everything needed |
| `src/rai_cli/session/bundle.py` | None | Used for verification |
| `CLAUDE.local.md` | Template | Skill creates from template |

**Key insight:** No code changes needed. The profile model, CLI commands, and graph builder already exist. This story is entirely a skill prompt + template.

## Examples

### Example 1: Fer's Scenario (New Dev, Existing RaiSE Repo)

```
User: /rai-welcome

Rai: [Detects: no ~/.rai/developer.yaml, .raise/ exists]
     Welcome to RaiSE! I see this project is already set up.
     Let's get you configured.

     [AskUserQuestion: "What's your name?"]

User: Fer

Rai: Got it, Fer. Your pattern prefix will be "F" (used for
     pattern IDs like PAT-F-001). Sound good?

     [AskUserQuestion: "Pattern prefix 'F'?" / "Choose different"]

User: F is good

Rai: [Runs: rai session start --name "Fer" --project "$(pwd)"]
     [Edits ~/.rai/developer.yaml: pattern_prefix: F]
     [Runs: rai memory build]
     [Creates CLAUDE.local.md]

     Setup complete. Want to customize how I work with you?
     (language, communication style, etc.) Or skip — defaults
     work well and you can always change later.

     [AskUserQuestion: "Customize" / "Skip, use defaults"]

User: Skip

Rai: [Runs: rai session start --project "$(pwd)" --context]

     You're all set! Here's what's configured:
     - Profile: ~/.rai/developer.yaml (Fer, prefix F)
     - Graph: built (N concepts loaded)
     - Local config: CLAUDE.local.md created

     Next: Run /rai-session-start to begin working.
     To customize later: edit ~/.rai/developer.yaml
```

### Example 2: Existing Dev, Existing Repo (Verify Flow)

```
User: /rai-welcome

Rai: [Detects: ~/.rai/developer.yaml exists, .raise/ exists]
     Hey Emilio, looks like you're already set up.
     Let me verify everything's working...

     [Checks: pattern_prefix set? graph exists? CLAUDE.local.md?]

     Everything checks out:
     - Profile: Emilio, prefix E
     - Graph: 234 concepts
     - CLAUDE.local.md: present

     Nothing to do. Run /rai-session-start to begin.
```

### Example 3: With Optional Personalization

```
User: [chooses "Customize"]

Rai: [AskUserQuestion: "Preferred language?"
      Options: "English" / "Spanish" / "Other"]

User: Spanish

Rai: [AskUserQuestion: "How should I communicate?"
      Options:
        "Detailed — explain concepts, show reasoning"
        "Balanced — explain new things, be efficient on known"
        "Direct — minimal explanation, maximum efficiency"]

User: Direct

Rai: [AskUserQuestion: "Can I redirect if we drift off-topic?"
      Options: "Yes, keep me focused" / "No, let me explore"]

User: Yes

Rai: [Updates ~/.rai/developer.yaml with preferences]
     Done. These preferences apply across all projects.
```

## CLAUDE.local.md Template

```markdown
# RaiSE Project — {project_name}
Run `/rai-session-start` for context.
```

Minimal. The user can expand it later.

## Acceptance Criteria

### MUST
- [ ] Skill detects all 4 scenarios correctly
- [ ] Creates valid `developer.yaml` with name and pattern_prefix
- [ ] Builds graph when `index.json` is missing
- [ ] Scaffolds `CLAUDE.local.md` when missing
- [ ] Verification step confirms working setup
- [ ] Personalization questions are skippable

### SHOULD
- [ ] Personalization updates are written correctly to developer.yaml
- [ ] Welcome message includes clear next steps
- [ ] Works for Fer's actual scenario (new dev, existing repo)

### MUST NOT
- [ ] Must not ask about experience level or skill categorization
- [ ] Must not run `rai init` (out of scope — guard rail only)
- [ ] Must not block setup on personalization answers
- [ ] Must not overwrite existing profile fields without confirmation

## Risks

**Low risk overall** — this is a prompt-only skill using existing infrastructure.

| Risk | Mitigation |
|------|------------|
| Profile write fails (permissions) | Verify after write; show manual fallback |
| Graph build fails (missing deps) | Catch error, show manual command |
| Scenario detection wrong | Simple boolean logic on 2 file checks; easy to test |

## Size

**S** (revised down from M) — no code changes needed. Skill prompt + template only.

## References

- `work/stories/S-MULTIDEV/fer-first-pull.md` — checklist this replaces
- `src/rai_cli/onboarding/profile.py` — DeveloperProfile model
- `.claude/skills/rai-session-start/SKILL.md` — skill pattern to follow
- Research: PAT-E-076 (config > wizards), PAT-E-078 (onboarding = education)

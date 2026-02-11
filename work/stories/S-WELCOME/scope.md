# Feature Scope: S-WELCOME

> `/rai-welcome` skill — conversational developer onboarding for RaiSE

## Problem

Setting up as a developer in a RaiSE project requires multiple manual steps (create profile, set pattern_prefix, build graph, create CLAUDE.local.md). The flow differs based on whether the developer and/or repo are new to RaiSE. There's no guided experience — Fer's onboarding depends on a checklist document.

## Value

Any developer can run `/rai-welcome` and be fully set up through a conversational flow that detects their situation and only asks what's needed. Reduces onboarding from a multi-step checklist to a single skill invocation.

## Four Scenarios (Auto-Detected)

| Scenario | `~/.rai/developer.yaml` | `.raise/` dir | Flow |
|----------|------------------------|---------------|------|
| **New dev, existing RaiSE repo** | Missing | Exists | Full profile creation + graph build |
| **RaiSE dev, new repo** | Exists | Missing | `rai init` + link profile + conventions |
| **RaiSE dev, RaiSE repo** | Exists | Exists | Verify setup, update if needed |
| **Brand new to everything** | Missing | Missing | Full profile + `rai init` |

## Conversational Intake

Questions adapt based on scenario. Only ask what's missing.

1. **Name** → `developer.yaml:name` + auto-derive `pattern_prefix` (first letter, confirm with user)
2. **Lean/TDD familiarity** → Maps to `experience_level` (shu/ha/ri). Examples:
   - "Never heard of TDD" → shu
   - "I do TDD sometimes" → ha
   - "TDD is second nature, I know lean well" → ri
3. **AI-assisted dev comfort** → Maps to `communication.style` + `detailed_explanations`:
   - "First time with AI coding" → explanatory, detailed=true
   - "Used Copilot/ChatGPT" → balanced
   - "Power user" → direct, detailed=false
4. **Guidance preference** → `communication.redirect_when_dispersing`, skip_praise
5. **Language** → `communication.language` (en, es, etc.)

## What the Skill Does After Intake

1. Creates/updates `~/.rai/developer.yaml` with answers
2. Sets `pattern_prefix` automatically (confirm with user)
3. Runs `rai memory build` if graph missing
4. Creates `CLAUDE.local.md` if missing
5. Verifies setup with a test `rai session start --context`
6. Prints a welcome message with next steps

## Permanent Context Influence

The answers should shape how Rai interacts going forward:
- **shu** devs get more explanation, step-by-step guidance, concept definitions
- **ha** devs get balanced output, only new concepts explained
- **ri** devs get minimal ceremony, maximum efficiency
- Communication style persists across all sessions via `developer.yaml`

## In Scope

- Skill definition (`.claude/skills/rai-welcome/`)
- Auto-detection of the 4 scenarios
- Conversational intake mapped to developer.yaml fields
- Pattern prefix auto-assignment
- Graph build if needed
- CLAUDE.local.md scaffolding
- Verification step

## Out of Scope

- Project initialization (`rai init` — already exists as separate command)
- Team management / admin features
- CI/CD integration
- Modifying existing `/rai-session-start` (it should just work after welcome)

## Done Criteria

- [ ] `/rai-welcome` skill exists and is loadable
- [ ] Detects all 4 scenarios correctly
- [ ] Creates valid `developer.yaml` from conversation
- [ ] Sets `pattern_prefix` automatically
- [ ] Builds graph when missing
- [ ] Scaffolds `CLAUDE.local.md` when missing
- [ ] Verification step confirms working setup
- [ ] Works for Fer's actual onboarding scenario

## Size Estimate

M — conversational skill with 4 scenario branches, profile creation, verification.

## References

- `work/stories/S-MULTIDEV/fer-first-pull.md` — current manual checklist this replaces
- `src/rai_cli/onboarding/profile.py` — DeveloperProfile model
- `.claude/skills/rai-session-start/` — skill pattern to follow
- S-MULTIDEV action item: "Auto-set pattern_prefix in rai session start --name"

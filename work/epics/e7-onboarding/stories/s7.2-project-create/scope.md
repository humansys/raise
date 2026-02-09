## Feature Scope: S7.2

**Story:** `/project-create` skill — greenfield onboarding
**Epic:** E7 (Onboarding)
**Size:** M
**Depends on:** S7.1 (governance scaffolding CLI) — done

**In Scope:**
- `/project-create` skill that guides greenfield project setup through conversation
- Conversational flow: project name, description, tech stack, guardrails preferences
- Fill governance doc content (PRD, vision, guardrails, architecture) from conversation
- Run `raise memory build` as final gate — 30+ governance nodes
- Skill distributed via `DISTRIBUTABLE_SKILLS`
- Experience-level adaptive verbosity (Shu/Ha/Ri)

**Out of Scope:**
- Brownfield/discovery support (S7.3)
- Multi-language convention detection (Python first)
- `raise status` or `raise doctor` commands
- Router skill (`/onboard`)
- Auto Shu→Ha→Ri progression

**Done Criteria:**
- [ ] Skill file exists in skills directory with proper framework structure
- [ ] Conversational flow collects project info and generates governance content
- [ ] Generated docs have correct YAML frontmatter for graph parsers
- [ ] `raise memory build` produces 30+ governance nodes from generated content
- [ ] `/session-start` works after `/project-create` completes
- [ ] Skill in DISTRIBUTABLE_SKILLS
- [ ] Quality gates pass (ruff, pyright for any CLI code)
- [ ] M2 milestone demo: full greenfield walkthrough

# S7.3: `/project-onboard` Skill

## Feature Scope

**In Scope:**
- `/project-onboard` skill for brownfield projects (existing codebases)
- Discovery pipeline integration: detect project type, languages, conventions
- Conversation-driven governance content generation (reuse S7.2 patterns)
- Architecture doc generation from discovered codebase structure
- Graph build gate: `raise memory build` produces architecture + governance nodes
- Skill file in `.claude/skills/project-onboard/`

**Out of Scope:**
- Changes to discovery CLI commands (already exist)
- Changes to `raise init` or governance templates (S7.1 done)
- Changes to graph parser or memory build
- Automatic migration from other frameworks

**Done Criteria:**
- [ ] `/project-onboard` skill exists and is loadable
- [ ] Brownfield walkthrough: existing Python project → discovery + conventions + governance → graph built
- [ ] Graph contains architecture nodes from discovery
- [ ] `raise memory build` succeeds after onboarding
- [ ] `/session-start` works after onboarding
- [ ] Tests pass
- [ ] Retrospective complete

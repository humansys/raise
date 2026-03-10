---
id: S7.1
title: "Governance Scaffolding CLI"
epic: E7
size: S
status: in-progress
branch: epic/e7/onboarding
---

# S7.1: Governance Scaffolding CLI

## In Scope

- Extend `rai init` to scaffold `governance/` directory with parser-compatible templates
- Templates: PRD, vision, guardrails, architecture (system-context, system-design, domain-model)
- YAML frontmatter matching graph parser expectations (correct `type`, `id`, `title` fields)
- `rai init` output recommends next skill based on detected project type (greenfield vs brownfield)
- Integration test: scaffold → `rai memory build` → governance nodes in graph

## Out of Scope

- Filling governance content (that's S7.2/S7.3 skill work)
- Multi-language template variants (Python-only for now)
- `rai status` / `rai doctor` health checks (post-F&F)
- Router skill for onboarding (YAGNI)

## Done Criteria

- [ ] `rai init` scaffolds `governance/` with all required templates
- [ ] Templates have correct YAML frontmatter for graph parsers
- [ ] `rai memory build` produces governance nodes from scaffolded templates
- [ ] `rai init` output recommends `/project-create` or `/project-onboard`
- [ ] Tests pass with >90% coverage
- [ ] Quality gates pass (ruff, pyright, bandit)

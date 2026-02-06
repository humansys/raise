# Research Prompt: Multi-Developer Configuration in AI Coding Tools

## Role

You are a software architecture researcher specializing in developer tooling and AI-assisted development. Your task is to investigate how leading AI coding assistants handle the separation of personal vs shared configuration data in multi-developer repositories.

## Research Question

**Primary:** How do AI coding assistants (Cursor, Aider, Continue, Cody, Copilot, Claude Code) handle personal vs shared configuration in multi-developer repos?

**Secondary:**
1. What data is considered "personal" vs "project-shared"?
2. Where is personal data stored (project dir, home dir, XDG)?
3. What patterns exist for migration/initialization?
4. How do they handle telemetry in multi-dev scenarios?

## Decision Context

This research informs F14.15 of RaiSE — separating personal data (sessions, telemetry, calibration) from shared project data (identity, patterns) to prevent merge conflicts and privacy leaks in multi-developer repos.

## Search Strategy

**Keywords:**
- "{tool} .gitignore configuration"
- "{tool} multi-user team settings"
- "{tool} personal vs project config"
- "{tool} XDG directory structure"
- "{tool} ~/.{tool} vs .{tool}/"

**Tools to investigate:**
1. Cursor (.cursor/, .cursorignore)
2. Aider (.aider*, aider.conf.yml)
3. Continue (.continue/, config.json)
4. Cody (.cody/, sourcegraph)
5. GitHub Copilot (.github/copilot)
6. Claude Code (.claude/)

**Sources to check:**
- Official documentation
- GitHub repos (dotfiles, config schemas)
- GitHub issues about multi-user/team scenarios
- Community discussions (Reddit, HN)

## Evidence Evaluation

| Level | Criteria |
|-------|----------|
| Very High | Official docs, source code |
| High | GitHub issues with maintainer response |
| Medium | Community consensus, blog posts |
| Low | Single user reports |

## Output Format

For each tool, document:
1. **Personal data location** (where stored)
2. **Project data location** (where stored)
3. **Gitignore patterns** (what's ignored by default)
4. **Team/multi-user patterns** (how they handle it)

Then synthesize:
- Common patterns across tools
- Best practices emerging
- Gaps/opportunities for RaiSE

## Quality Checklist

- [ ] 5+ tools investigated
- [ ] Official docs consulted for each
- [ ] GitHub config schemas checked
- [ ] Gitignore patterns documented
- [ ] Multi-user scenarios explicitly addressed

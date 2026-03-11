# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Initial open-source release. RaiSE Framework v2 — a lean methodology and deterministic
toolkit for reliable AI-assisted software engineering.

### Highlights

- **37 skills** covering the full SDLC: epic, story, discovery, implementation, review, debug, research
- **Knowledge graph** for project context, patterns, and cross-session memory
- **Multi-language discovery**: Python, TypeScript, JavaScript, C#, PHP, Dart, Svelte
- **Governance as code**: constitution, guardrails, ADRs, gates — all versioned in Git
- **Adapter plugin system**: extensible via entry points (filesystem built-in, Jira/Confluence via raise-pro)
- **Doctor diagnostics**: `rai doctor` with `--fix` auto-remediation
- **Documentation site**: docs.raiseframework.ai (EN + ES)

### CLI Commands

72 subcommands across 17 groups: `init`, `session`, `graph`, `pattern`, `signal`,
`backlog`, `skill`, `discover`, `adapter`, `mcp`, `gate`, `doctor`, `docs`,
`artifact`, `release`, `info`, `profile`.

### Framework

- 5 work cycles: solution, project, feature, setup, improve
- 3-layer architecture: Context (wisdom), Kata (practice), Skill (action)
- Jidoka (stop-and-fix) verification at every step
- Skill sets: distributable, customizable skill collections per team

### Pro/Community Boundary (E478)

- **Separated pro adapters** into `packages/raise-pro/` workspace package
- **Removed 6 pro-only dependencies** from community install (atlassian-python-api, authlib, cryptography, requests, urllib3, certifi)
- **Clean entry points**: Jira/Confluence adapters register only when raise-pro is installed
- **Removed hardcoded Jira CLI logic** from community package (-207 lines)
- **Gitignored adapter configs** (.raise/jira.yaml, .raise/confluence.yaml) to prevent PII leaks

[Unreleased]: https://github.com/humansys/raise/compare/v2.2.3...HEAD

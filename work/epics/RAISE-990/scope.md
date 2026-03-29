# RAISE-990: E-WINDOWS-DX — Scope

**Jira:** RAISE-990
**Labels:** windows, dx, onboarding, v3.1
**Branch:** release/2.4.0 (scope artifacts) → release/3.1.0 (implementation)
**Target release:** v3.1

## Objective

Reduce the Windows installation experience from ~2.5 hours / 5 engineers to
<15 minutes self-service for non-dev users. Produce an automated script,
visual guide, and Claude Desktop configuration so that sales, CS, and
management team members can use rai independently.

## Problem Statement

On 2026-03-27, installing rai on Gerardo's Windows PC required:

| Step | Friction | Time |
|------|----------|------|
| 1. Python from Microsoft Store | PATH not auto-configured | ~10 min |
| 2. Verify Python in PowerShell | `python --version` confusion | ~5 min |
| 3. Install raise-cli via pip | Wrong tool (should be pipx) | ~10 min |
| 4. Claude Code install | PATH not auto-configured | ~10 min |
| 5. Add PATH entries manually | Environment variables UI is buried | ~10 min |
| 6. PowerShell ExecutionPolicy | Restricted by default, needs admin | ~5 min |
| 7. Git install + SSH keygen | Full manual process | ~20 min |
| 8. GitLab SSH key registration | Manual web UI flow | ~10 min |
| 9. Claude auth (org account) | Account confusion, no password set | ~15 min |
| 10. rai init + MCP adapters | atlassian-python-api deps on Windows | ~15 min |
| **Total** | | **~110 min active + overhead** |

**Root causes:**
1. No installation documentation for Windows
2. No automation — every step is manual
3. pip vs pipx confusion
4. Windows PATH management requires manual intervention
5. PowerShell defaults block script execution
6. No guidance on Claude account setup for org users

## Stories

### S990.1: Installation Audit & Gap Documentation (S) — RAISE-991

Document every step, dependency, and environment variable required. Produce a
gap analysis: what works automatically on Linux/Mac but fails on Windows.

**Deliverable:** Audit document with dependency list, gap analysis, friction ranking

### S990.2: PowerShell Installation Script (M) — RAISE-992

Create `install-rai.ps1` that automates all 9+ steps:

```powershell
# Target UX:
irm https://install.raise.dev/windows | iex
# Or local:
.\install-rai.ps1
```

Handles: Python, pipx, rai, Claude Code, git, PATH, ExecutionPolicy, verification.
Idempotent, bilingual (ES/EN), generates install log.

**Deliverable:** Working PowerShell script in `tools/install/`

### S990.3: Windows Installation Guide (M) — RAISE-993

Step-by-step visual guide for non-devs:
1. Prerequisites
2. Quick Install (script)
3. Manual Install (with screenshots)
4. First Run + authentication
5. Connecting to Jira, Gmail, Calendar
6. Troubleshooting (all 9 known issues)

Primary language: Spanish. Published to Confluence.

**Deliverable:** Confluence page under Operations, PDF export

### S990.4: Claude Desktop/Work Configuration (M) — RAISE-994

Research spike: Can Claude Desktop replace VS Code for non-dev users?

Questions:
1. Claude Desktop + rai MCP servers on Windows — feasible?
2. Claude Work (web) + local tools — feasible?
3. Minimal MCP config for non-dev (Jira + Gmail + Calendar)?
4. Comparison matrix: Desktop vs VS Code vs Terminal
5. Recommendation for v3.1

**Deliverable:** Feasibility report + configuration guide (if feasible)

### S990.5: Installation Smoke Test (S) — RAISE-995

Validate script + guide on clean Windows 10/11. Non-dev user follows guide
independently, measures time, documents failures.

**Dependencies:** S990.2, S990.3
**Deliverable:** Test results, remaining issues backlogged

## Story Dependencies

```
S990.1 (audit) ──→ S990.2 (script) ──→ S990.5 (smoke test)
                ──→ S990.3 (guide)  ──→ S990.5 (smoke test)
S990.4 (Claude Desktop research) — independent, can run in parallel
```

## In Scope (MUST)

- Installation audit with all dependencies documented
- PowerShell script automating full installation
- Visual installation guide for non-devs (Spanish)
- Smoke test on clean Windows environment

## In Scope (SHOULD)

- Claude Desktop feasibility research
- Bilingual script output (ES/EN)
- PDF export of guide

## Out of Scope

- GUI installer (MSI/EXE) — too much effort for v3.1
- Dropping Python dependency — architecture change, v4.0
- Linux/Mac installation improvements — already works
- rai code changes for Windows compatibility — separate epic
- Docker-based installation — different approach, evaluate later
- Mobile/tablet installation

## Done Criteria

- [ ] All dependencies documented in audit (S990.1)
- [ ] install-rai.ps1 works on clean Windows 10 and 11
- [ ] Guide published to Confluence with screenshots
- [ ] Non-dev user (Gerardo) installs independently in < 30 min
- [ ] Claude Desktop recommendation documented
- [ ] All stories closed in Jira

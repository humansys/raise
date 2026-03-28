# RAISE-990: E-WINDOWS-DX — Windows Installation Experience

**Date:** 2026-03-28
**Author:** Emilio Osorio + Rai

---

## Hypothesis

The current rai installation process on Windows is prohibitively complex for non-dev
users (2.5 hours, 5 engineers required). An automated installation script + visual
guide can reduce this to <15 minutes self-service, enabling non-technical team members
(sales, CS, management) to use rai independently.

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Installation time | ~156 min | < 15 min (script) / < 30 min (manual) |
| Engineers required | 5 | 0 (self-service) |
| Manual steps | 9 | 1 (run script) |
| Non-dev success rate | 0% (failed without help) | 100% |
| Platforms validated | 0 | Windows 10 + Windows 11 |

## Appetite

- **Size:** M (5 stories, ~15-20h total)
- **Timebox:** 2 sessions
- **Target release:** v3.1

## Rabbit Holes (avoid)

- Do NOT redesign rai's dependency model — just automate what exists
- Do NOT build a GUI installer (MSI/EXE) — PowerShell script is sufficient for v3.1
- Do NOT drop Python dependency — that's a v4.0 conversation
- Do NOT build Claude Desktop integration if it requires rai code changes — document
  what works today, backlog what doesn't
- Do NOT solve Linux/Mac installation — that already works

## Context

- **Trigger:** Live installation session on 2026-03-27 (transcript: dev/transcripts/Tableros Jira.txt)
- **Participants:** Emilio, Fernando, Daniel, Gerardo Davila, Gerardo Osorio
- **User profile:** Gerardo Osorio — non-dev, sales/CS role, Windows PC
- **Desired UX:** Open app, talk to Rai, get things done with Jira/Gmail/Calendar
- **Current blocker:** Installation complexity prevents non-dev adoption

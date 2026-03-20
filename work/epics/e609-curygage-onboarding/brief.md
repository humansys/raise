---
epic_id: "RAISE-609"
title: "CuryGage RaiSE Onboarding — lean delivery from requirement to production"
status: "active"
created: "2026-03-20"
---

# Epic Brief: CuryGage RaiSE Onboarding

## Hypothesis
For CuryGage technical leaders who need to deliver software predictably and transparently,
a guided RaiSE onboarding is a structured enablement program
that takes them from business requirement to production using lean methodology.
Unlike generic AI-assisted development, our solution gives them a custom skillset tuned
to their tools (Jira, Confluence, Bitbucket) and their own process conventions.

## Success Metrics
- **Leading:** One team runs a complete user story end-to-end (requirement → production) using RaiSE within session 5
- **Lagging:** Team can autonomously run `/rai-story-run` with their custom skillset without facilitation after the program

## Appetite
M — 5 sessions + prep work. Target: 1 week with one pilot team.

## Scope Boundaries
### In (MUST)
- RaiSE onboarding plan: 5 structured sessions with objectives, agenda, and expected outputs
- Jira adapter working in their environment (ACLI-based, just completed by Emilio)
- Confluence adapter working for their documentation
- Custom skillset scaffold tuned to CuryGage conventions
- `rai init --detect` on their repo + governance bootstrap
- One complete story run as live demo in sessions

### In (SHOULD)
- Bitbucket integration awareness (delivery pipeline)
- Session facilitation guide for Fer to run the onboarding solo
- Handoff docs so team can continue autonomously post-program

### No-Gos
- Building new CLI features during onboarding — use what exists
- Onboarding all teams simultaneously — pilot one team first
- Custom adapters beyond Jira/Confluence — out of scope for v1

### Rabbit Holes
- Perfecting Bitbucket integration before validating Jira/Confluence basics
- Over-customizing skillset before team has used the generic ones
- Spending time on Telegram/ontology extractor work (Emilio's lane, not this epic)

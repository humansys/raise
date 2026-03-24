# Personal Agent Hosting — Research

> **Research ID:** RES-PERSONAL-HOSTING-001
> **Date:** 2026-03-22
> **Researcher:** Rai + Emilio
> **Jira:** RAISE-658 (under RAISE-657)
> **Confidence:** HIGH
> **Prior Research:** RES-OPENCLAW-001

## Purpose

Map the competitive landscape of low-cost personal agent hosting and assess technical viability for mass hosting environments (WHM/cPanel/VPS). Identify reusable patterns from NanoClaw and the broader *Claw ecosystem.

## Contents

- `evidence-catalog.md` — 15 sources with confidence ratings
- `findings.md` — Full spike findings (landscape, NanoClaw patterns, viability)

## Key Findings

1. **Market validated** — 6+ managed hosting providers ($2-40/mo), self-host from $4/mo
2. **NanoClaw is reference architecture** — 700 lines, Anthropic SDK, container isolation
3. **cPanel shared NOT viable** — needs persistent processes, Docker, WebSocket
4. **VPS reselling VIABLE** — Docker template on any VPS
5. **Recommendation: GO** — Docker Compose template as Priority 1

## Confluence

- [Epic page](https://humansys.atlassian.net/wiki/spaces/rAIse/pages/3128393729)
- [Spike findings](https://humansys.atlassian.net/wiki/spaces/rAIse/pages/3128492033)

# RAISE-863: Confluence IA Grooming — Brief

**Date:** 2026-03-27
**Author:** Emilio Osorio + Rai

---

## Hypothesis

The RaiSE1 Confluence space currently has ~40+ pages in a flat structure with no
hierarchy, inconsistent naming, and no index pages. Applying the Information
Architecture designed in S760.4 will make the space navigable, searchable
(CQL-friendly), and ready for Rovo agent consumption.

## Success Metrics

| Metric | Target |
|--------|--------|
| Pages organized into sections | 100% of existing pages |
| Index pages created | 1 per top-level section |
| Naming convention compliance | 100% of moved pages |
| Orphan pages (no parent section) | 0 |
| Labels applied per taxonomy | All pages labeled |

## Appetite

- **Size:** S-M (design epic, no code)
- **Timebox:** 1 session (~3-4 hours)
- **Stories:** 4-5

## Rabbit Holes (avoid)

- Do NOT redesign the IA — S760.4 is the accepted design, just apply it
- Do NOT create templates yet — that's a separate epic (RAISE-830)
- Do NOT build `rai docs publish` alignment — that's adapter work
- Do NOT move pages between spaces (Ventas content stays in RaiSE1 for now, under a clear section)

## Context

- **Design source:** S760.4 Confluence IA Design (work/epics/RAISE-760/confluence-ia-design.md)
- **Current state:** ~40 pages, flat, no hierarchy
- **Target state:** 12 top-level sections with proper page tree, naming, labels
- **Feeds into:** RAISE-830 (Confluence adapter), Rovo agent setup

# Epic Brief: Session Identity Fix

> **Epic:** E654
> **Jira:** RAISE-654
> **Date:** 2026-03-22
> **Problem Brief:** `work/problem-briefs/session-identity-fix-2026-03-22.md`

---

## Hypothesis

**Si** movemos la data de sesión a git (aislada por dev+repo, independiente del environment/channel), **entonces** desaparecerá la queja de "contexto equivocado / sesión perdida / numeración rota" **para** el equipo de desarrollo, **medido por** cero incidentes de leakage cross-repo y continuidad de sesión entre environments en 4 semanas.

## Success Metrics

| Metric | Target | How to measure |
|--------|--------|----------------|
| Cross-repo leakage incidents | 0 | Manual tracking over 4 weeks |
| Session continuity across environments | 100% | Same session ID resolves from any channel |
| Session numbering consistency | Monotonic per dev+repo | `rai session list` output |

## Appetite

**Timeframe:** v2.2.4 bugfix release
**Size:** Small (3-5 stories estimated)
**Complexity:** Medium — touches session lifecycle, storage layer, and CLI commands

## Rabbit Holes

- **Over-engineering merge semantics** — session data in git doesn't need complex merge strategies yet. Simple per-developer directories with append-only logs are sufficient.
- **Backward compatibility obsession** — existing session state files outside git can be migrated once, not maintained in parallel forever.
- **Multi-developer conflict scenarios** — each developer's session data is isolated by identity; git merge conflicts between developers are structurally impossible if namespaced correctly.

## Constraints

- Must not break `rai session start/close` CLI contract
- Must work without requiring git hooks or special merge drivers
- Session data must be `.gitignore`-safe for sensitive fields (if any)
- Migration path from current `~/.rai/` storage to in-repo storage

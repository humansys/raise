# Epic Scope: Session Identity Fix

> **Epic:** E654
> **Jira:** RAISE-654
> **Objective:** Move session data to git, isolate by dev+repo, eliminate cross-environment leakage

---

## Objective

Fix session identity so that sessions are scoped to developer+repository (not environment/channel), enabling coherent multi-session work regardless of where the developer opens Claude Code.

## In Scope

- Session identity model: dev+repo as primary key (replacing environment-based identity)
- Session data storage in git (`.raise/rai/sessions/{dev-id}/`)
- Migration from `~/.rai/` session state to in-repo storage
- Session numbering: monotonic per dev+repo, not per environment
- CLI compatibility: `rai session start/close/journal` work with new storage
- Cross-environment continuity: session started in terminal A visible in terminal B

## Out of Scope

- Workstream abstraction (separate epic, depends on this one)
- Multi-developer merge semantics (structurally avoided by per-dev namespacing)
- Session data encryption or access control
- Changes to session context bundle format
- Backward compatibility shims for old storage (one-way migration)

## Planned Stories

*To be defined in `/rai-epic-design`*

## Done Criteria

- [ ] Sessions identified by dev+repo, not environment
- [ ] Session data lives in git under `.raise/`
- [ ] Zero cross-repo leakage
- [ ] Session continuity across environments (same dev, same repo)
- [ ] Monotonic session numbering per dev+repo
- [ ] Migration path documented and tested
- [ ] All existing `rai session` CLI commands work with new storage

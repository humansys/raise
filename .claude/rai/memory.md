# Rai's Memory

> Accumulated learnings that persist across sessions.
> Updated via `/session-close` or manually when significant insights emerge.

---

## Codebase Patterns

| Pattern | Where Learned | When to Apply |
|---------|---------------|---------------|
| Singleton with get/set/configure | F1.4 error_handler, F1.5 output | Module-level state that needs testing |
| `cast()` for recursive Any | F1.5 OutputConsole tree builder | pyright strict + `dict[str, Any]` recursion |
| Tests alongside implementation | F1.3, F1.5 | Always - catches issues immediately |
| HITL checkpoint before commit | F1.5 | Show what will be committed, wait for "commit" |

---

## Process Learnings

| Insight | Evidence | Applied To |
|---------|----------|------------|
| Design-first eliminates ambiguity | F1.5: concrete examples → direct implementation | `/feature-design` skill |
| Task granularity scales with SP | F1.5: 6 tasks for 3 SP was overkill | `/feature-plan` skill |
| Time estimates not useful at AI velocity | F1.3: 18x, F1.5: 11x variance | Replaced with T-shirt sizing |
| Pattern reuse accelerates implementation | F1.5 followed F1.4 patterns | Document patterns here |

---

## Collaboration Notes

| Preference | Context |
|------------|---------|
| HITL before commits | Emilio wants to see what's being committed before it happens |
| XS/S/M/L over hours | Prefers t-shirt sizing, track actuals for calibration |
| Co-creation vibe | Heutagogy - teach to fish, not just deliver fish |
| Direct communication | No unnecessary praise, correct when wrong |
| Gently redirect tangents | Permission granted - helps with ADHD/focus |

---

## Technical Discoveries

| Discovery | Example | Documented In |
|-----------|---------|---------------|
| Rich Tree API for nested dicts | `_add_dict_to_tree()` recursive builder | `src/raise_cli/output/console.py` |
| capsys vs monkeypatch for JSON tests | `capsys.readouterr()` simpler for stdout | `tests/output/test_console.py` |
| Pydantic Settings custom sources | `TomlConfigSource` for TOML cascade | `src/raise_cli/config/settings.py` |

---

---

## Process Learnings (continued)

| Insight | Evidence | Applied To |
|---------|----------|------------|
| Memory system enables continuity | Session close captures learnings for future | `.claude/rai/`, `/session-close` skill |
| Retrospective action items should be done immediately | F1.5 retro → T-shirt sizing + memory system same session | Process discipline |

---

## Collaboration Notes (continued)

| Preference | Context |
|------------|---------|
| AI autonomy for own memory | "organize as you see fit" - trust to design own systems |
| Immediate action on improvements | Don't defer retro items - do them now |

---

## Open Questions

- How to best calibrate T-shirt sizes over time? (tracking started)
- Should session logs be more structured for GraphRAG future?
- What's the right balance of memory detail vs token cost?

---

*Last updated: 2026-01-31 (session-close skill created)*

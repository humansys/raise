# RAISE-541: Fix Plan

## Verification Commands (from manifest)

- test:       `uv run pytest --tb=short`
- lint:       `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`
- type-check: `uv run pyright`
- sonar:      `sonar list issues -p humansys-demos_raise-commons --format table`

## Tasks (TDD order, ascending risk)

### T1 — S125: Remove commented-out code
- File: `src/raise_cli/adapters/filesystem.py:125`
- Action: Delete the commented block
- Test: no regression test needed (dead code removal)
- Verify: lint + type-check
- Commit: `chore(RAISE-541): S125 — remove commented-out code in filesystem.py`

### T2 — S7632: Fix malformed type: ignore comment
- File: `src/raise_cli/memory/writer.py:439`
- Action: Fix syntax of `# type: ignore` (add rule code or remove if not needed)
- Test: pyright must pass without error on that line
- Verify: type-check
- Commit: `chore(RAISE-541): S7632 — fix malformed type ignore comment in writer.py`

### T3 — S5713: Remove redundant exception classes in except tuples
- Files: adapter.py:189, mcp_confluence.py:183, mcp_jira.py:181/266,
         artifact.py:73, discover.py:236, pending.py:65, loader.py:209, writer.py:356
- Action: Remove the subclass from `except (Parent, Child)` → `except Parent`
- Test: no regression needed (same catch semantics)
- Verify: lint + type-check
- Commit: `chore(RAISE-541): S5713 — remove redundant exception subclass in except tuples`

### T4 — S7503: Remove unnecessary async keyword
- File: `src/raise_cli/adapters/mcp_confluence.py:115`
- Action: Change `async def` → `def`, remove any `await` if present, verify callers
- Test: grep callers, run tests
- Verify: lint + type-check + tests
- Commit: `chore(RAISE-541): S7503 — remove unnecessary async in mcp_confluence`

### T5 — S1172: Prefix unused parameters with _
- Files: filesystem.py:205, mcp_confluence.py:115, agents/copilot_plugin.py:31/36,
         config/agent_plugin.py:93/98/103, context/builder.py:884/1029/1294,
         memory/writer.py:439, onboarding/instructions.py:45/70
- Action: Rename param `foo` → `_foo` (preserves interface, silences sonar)
- Note: check if any are Protocol/ABC implementations — signature must be kept
- Verify: lint + type-check + tests
- Commit: `chore(RAISE-541): S1172 — prefix unused parameters with _ across codebase`

### T6 — S6019: Fix reluctant quantifiers in regex
- Files: adr.py:81, epic.py:142, glossary.py:216, guardrails.py:169,
         instructions.py:242, changelog.py:18/47
- Action: Remove `?` from quantifiers that can only match 0 or 1 repetitions
  (e.g., `.*?` at end of pattern → `.*`, or `+?` → `+`)
- Test: write/run regex unit test to confirm match behavior unchanged
- Verify: lint + type-check + tests
- Commit: `chore(RAISE-541): S6019 — fix reluctant quantifiers in regex patterns`

### T7 — S1192: Extract duplicate string literals to constants
- Files: ~28 instances across 15+ files
- Action: Extract each repeated literal to a module-level constant
- Strategy: group by file, extract at top of each file
- Verify: lint + type-check + tests
- Commit: `chore(RAISE-541): S1192 — extract duplicate string literals to constants`

### T8 — S5754: Reraise silenced exception
- File: `src/raise_cli/session/bundle.py:102`
- Action: Read context, decide: reraise or log+suppress with intent comment
- Test: write test that exercises the exception path
- Verify: lint + type-check + tests
- Commit: `chore(RAISE-541): S5754 — reraise silenced exception in session/bundle.py`

### T9 — Final Sonar Verification
- Run sonar scan + list issues
- Confirm 0 violations for S1192/S1172/S5713/S6019/S125/S7503/S5754/S7632

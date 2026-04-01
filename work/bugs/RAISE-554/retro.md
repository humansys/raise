## Retrospective: RAISE-554

### Summary
- Root cause: 68 hardcoded Unicode symbols (✓, ✗, ⚠) across 16 files — no terminal encoding check. CP1252 on Windows cannot render them.
- Fix approach: symbols.py module with get_symbols() + ASCII fallbacks, replace all 68 call sites (commits e207647f, 3e96f69d)
- Classification: Interface/S2-Medium/Code/Missing

### Verification
- src/raise_cli/output/symbols.py created — detects encoding, returns ASCII fallbacks for CP1252
- 68 literal occurrences replaced with module imports across 16 files
- Fix is correct: encoding detection at module load, fallback transparent to callers

### Process Improvement
**Prevention:** Terminal output should never assume Unicode support. A central symbols/formatting module should exist from the start for any CLI tool. "Works on my machine" (UTF-8 Linux/Mac) is not sufficient testing.
**Pattern:** Interface + Code + Missing → missing encoding boundary check. The fix is a central abstraction (symbols module) not 68 individual fixes. When you have N call sites with the same assumption, the fix is to remove the assumption from all N, not patch each.

### Heutagogical Checkpoint
1. Learned: 68 call sites means the hardcoded symbols were copied 67 times without anyone questioning encoding support. The first occurrence set the pattern; every subsequent copy reinforced it.
2. Process change: For CLI tools, create output/symbols or output/format as one of the first modules — before any UI rendering.
3. Framework improvement: None — this is a CLI engineering practice, not framework-specific.
4. Capability gained: Pattern for encoding-safe CLI output in Python: detect at module load, expose constants, import everywhere.

### Patterns
- Added: PAT-F-049 (see below)
- Reinforced: none evaluated

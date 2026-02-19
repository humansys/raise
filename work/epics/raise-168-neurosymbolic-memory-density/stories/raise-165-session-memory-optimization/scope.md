## Story Scope: RAISE-165

**Epic:** RAISE-168 (Neurosymbolic Memory Density)
**Size:** S
**Depends on:** RAISE-166 ✅ (Markdown-KV compact confirmed as top performer)

### Problem

Session context fragmented across 5 proprietary mechanisms (hook, memory dir, identity files via hook, CLI primes, MEMORY.md). Creates brittleness, duplication, and platform lock-in.

### In Scope

- Consolidate CLAUDE.md as single always-on file (identity + process + CLI ref in MK-KV compact)
- Delete session-init.sh hook
- Clean up ~/.claude/.../memory/ (vacate MEMORY.md, delete cli-reference.md)
- Remove identity primes from CLI context bundle (Python code change)
- Preserve .raise/rai/identity/ as canonical source (unchanged)

### Out of Scope

- `rai init --ide X` command (future — this design enables it)
- `rai cli reference --compact` auto-generation (parking lot)
- Modifying identity source files (core.md, perspective.md)
- Changes to CLAUDE.local.md

### Done Criteria

- [ ] CLAUDE.md consolidated (~95 lines: identity, process, branch, CLI ref compact, file ops)
- [ ] session-init.sh deleted
- [ ] Memory dir cleaned (MEMORY.md redirected, cli-reference.md deleted)
- [ ] CLI identity primes section removed (Python change)
- [ ] Identity source files unchanged in .raise/rai/identity/
- [ ] No behavioral regression
- [ ] Retrospective complete

## Story Scope: RAISE-161 — Windows Compatibility Verification

**Epic:** RAISE-144 (Engineering Health)
**Size:** XS
**Driver:** Sofi (Kurigage, .NET/Windows)

**In Scope:**
- Audit codebase for Windows path compatibility issues (os.sep, Path handling)
- Audit for Unix-only shell assumptions in CLI commands
- Fix any issues found
- Add cross-platform tests where needed

**Out of Scope:**
- Actually running on a Windows machine (no Windows CI available)
- PowerShell skill compatibility (skills are Claude Code markdown, not shell scripts)
- WSL-specific behavior

**Done Criteria:**
- [ ] All `Path` usage audited — no hardcoded `/` separators in path construction
- [ ] No `os.system()` or subprocess calls with Unix-only commands
- [ ] Cross-platform path tests added for critical paths
- [ ] Any issues documented with workarounds
- [ ] Tests pass
- [ ] Retrospective complete

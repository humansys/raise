## Story Scope: hooks-cleanup

**Title:** Remove duplicate bash hook telemetry — use CLI telemetry only

**Context:** Two parallel systems write to `signals.jsonl`: bash Stop hooks (`.raise/scripts/log-*.sh`) from E9 Phase 1 and CLI telemetry (`raise memory emit-work` / `telemetry/writer.py`). CLI version is strictly better (Pydantic schemas, file locking, proper error handling). Bash hooks are vestigial.

**In Scope:**
- Strip `hooks:` sections from all distributable skills (SKILL.md files)
- Remove bash scripts from `rai_base/scripts/`
- Remove `_copy_scripts` from bootstrap.py
- Update `raise init` if it scaffolds hook scripts
- Verify CLI `emit-work` calls in skill steps still work

**Out of Scope:**
- Changing CLI telemetry behavior or schemas
- Adding new telemetry features
- Modifying non-distributable skills (source skills in `.claude/skills/`)

**Done Criteria:**
- [ ] No `hooks:` sections in any distributable skill SKILL.md
- [ ] No bash scripts in `rai_base/scripts/`
- [ ] Bootstrap no longer copies scripts
- [ ] `raise init` no longer scaffolds hook scripts
- [ ] CLI telemetry still emits correctly
- [ ] Tests pass
- [ ] Retrospective complete

# Story S2: CLI Reference Update — Scope

**Epic:** RAISE-153 (Developer Enablement)
**Size:** M
**Branch:** `story/s153.2/cli-reference-update`

---

## In Scope

- Document all `rai` CLI commands against actual v2.0.0a9 output
- Verify every command, subcommand, flag matches `rai <cmd> --help`
- Update existing CLI reference page in Starlight docs
- Add new commands: session --agent/--session, backlog, publish
- Examples for key commands

## Out of Scope

- API/SDK docs (no public API)
- Tutorials or guides (S3 scope)
- New Starlight pages beyond CLI reference
- CLI code changes

## Done Criteria

- [ ] Every `rai` command documented with flags and description
- [ ] All docs match actual `--help` output
- [ ] Builds without errors (`npm run build` in docs/)
- [ ] Renders correctly in local preview
- [ ] Retrospective complete

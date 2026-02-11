# Story Scope: S-RELEASE — TestPyPI Hardening

**Type:** Standalone pre-release story (branchless epic pattern)
**Branch:** `story/s-release/testpypi-hardening` off `v2`

## In Scope

- Add `--exclude` flag to `raise discover scan` (PAT-247) — prevent noise from `vendor/`, `node_modules/`, etc.
- Fix README.md `uv run raise` → `raise` for end-user docs (done)
- Rebuild wheel from current source
- Publish to TestPyPI
- Verify install works via `pip install --index-url https://test.pypi.org/simple/ raise-cli`

## Out of Scope

- Absorb `/discover-complete` into `/discover-validate` (behavior change, risky pre-release)
- Rename `discover-describe` → `discover-document` (cosmetic, post-F&F)
- Drift detector calibration (post-F&F)
- Any new features or refactoring

## Done Criteria

- [ ] `raise discover scan --exclude vendor/ --exclude node_modules/` works
- [ ] Wheel builds cleanly
- [ ] Package published to TestPyPI
- [ ] `pip install` from TestPyPI succeeds on clean venv
- [ ] `raise --version` works after install
- [ ] Tests pass, types check, lint clean

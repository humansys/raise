# Release Engineering

> **Status:** Active
> **Version:** 1.0.0
> **Last Updated:** 2026-02-14
> **Owner:** Emilio + Rai

---

## Purpose

Standard Operating Procedure for releasing `rai-cli` to PyPI with quality gates, security scanning, and automated delivery via GitHub Actions.

## Scope

This SOP covers the complete release pipeline from quality validation to PyPI publication:
- Pre-release quality gates
- Version management (PEP 440)
- Changelog discipline
- Git workflow (commit, tag, push)
- Trusted Publishers automation
- Dual remote handling (GitLab + GitHub)

---

## Prerequisites

**Required:**
- Clean working tree (no uncommitted changes)
- All tests passing (`pytest`)
- Type checks clean (`pyright`)
- Linting passes (`ruff check`)
- Security scan passes (`bandit`)
- CHANGELOG.md has unreleased entries

**Access:**
- PyPI maintainer access to `rai-cli` project
- GitHub write access to `humansys/raise` repository
- GitLab write access to `humansys-demos/product/raise1/raise-commons`

---

## Process

### 1. Run Quality Gates

```bash
rai publish check
```

**Quality gates (10 total):**
1. Tests pass (>90% coverage required)
2. Type checks clean (pyright --strict)
3. Lint clean (ruff)
4. Security scan (bandit)
5. Build succeeds
6. Package validates (twine check)
7. CHANGELOG has unreleased entries
8. Version is PEP 440 compliant
9. Version sync (pyproject.toml ↔ __init__.py)
10. Git working tree clean

**If gates fail:**
- **Blocking issues** (new regressions): Fix before release
- **Pre-existing issues**: Document as hotfix (HF-N) in `governance/backlog.md`, proceed with `--skip-check`

### 2. Determine Version Bump

**Bump types:**
- `major` — Breaking changes (2.0.0 → 3.0.0)
- `minor` — New features, backward compatible (2.0.0 → 2.1.0)
- `patch` — Bug fixes only (2.0.0 → 2.0.1)
- `alpha` — Pre-release iteration (2.0.0a7 → 2.0.0a8)
- `beta` — Beta iteration (2.0.0b1 → 2.0.0b2)
- `rc` — Release candidate iteration (2.0.0rc1 → 2.0.0rc2)
- `release` — Promote pre-release to stable (2.0.0a8 → 2.0.0)

**Decision criteria:**
- Review commits since last release: `git log v{LAST_TAG}..HEAD --oneline`
- Check for breaking changes, new features, or bug fixes only
- For alpha releases (current), use `alpha` bump

### 3. Sync Public Skills (if applicable)

```bash
python scripts/sync-skills.py
```

This filters skills by visibility metadata:
- **Public skills** → copied to `src/rai_cli/skills_base/`
- **Internal skills** → excluded (e.g., `rai-publish`, `rai-framework-sync`)

Commit changes if any:
```bash
git add src/rai_cli/skills_base/
git commit -m "chore: sync public skills for distribution"
```

### 4. Execute Release (Dry Run First)

```bash
# Dry run to preview
rai publish release --bump {type} --dry-run

# Execute (will prompt for confirmation)
rai publish release --bump {type}

# Or skip quality gates if pre-existing issues documented
rai publish release --bump {type} --skip-check
```

**What happens:**
1. Version bumped in `pyproject.toml` and `src/rai_cli/__init__.py`
2. CHANGELOG.md updated ([Unreleased] → [version] - date)
3. Git commit created: `release: v{version}`
4. Git tag created: `v{version}`
5. Push to origin (GitLab)

### 5. Push to GitHub (Triggers Automation)

```bash
git push github v2 --tags
```

**Why this step exists:**
- `origin` = GitLab (primary development)
- `github` = GitHub (automation, public mirror)
- `git push` only pushes to `origin` by default
- GitHub Actions requires the tag on GitHub to trigger

**Automation triggered:**
1. **Build job** — `uv build` creates wheel + sdist
2. **Publish job** — Uploads to PyPI via Trusted Publishers (OIDC)
3. **GitHub Release** — Creates release notes from commits

### 6. Verify Publication

**PyPI:**
```bash
pip install --upgrade --pre rai-cli
rai --version  # Should show new version
```

**GitHub Actions:**
- Check: https://github.com/humansys/raise/actions
- Verify all jobs passed (build → publish → github-release)

**GitHub Release:**
- Verify release created: https://github.com/humansys/raise/releases

---

## Trusted Publishers Setup

**If first-time setup or "invalid-publisher" error:**

1. Go to: https://pypi.org/manage/project/rai-cli/settings/publishing/
2. Add trusted publisher:
   - **PyPI Project:** `rai-cli`
   - **Owner:** `humansys`
   - **Repository:** `raise`
   - **Workflow:** `release.yml`
   - **Environment:** `pypi`
3. Save configuration
4. Re-run failed GitHub Action if needed

---

## Troubleshooting

### Quality Gates Fail

**Pre-existing issues (not your changes):**
1. Document as hotfix in `governance/backlog.md`:
   ```markdown
   | HF-N | Title | Description | Status | Priority | Found In | Target |
   | HF-5 | Type annotations... | ... | 🔴 Open | P2 | v2.0.0a8 | v2.0.0a9 |
   ```
2. Release with `--skip-check`
3. Fix in separate hotfix story

**New regressions (your changes):**
1. Fix before releasing
2. Re-run `rai publish check`

### Trusted Publisher Fails

**Error:** `invalid-publisher: valid token, but no corresponding publisher`

**Fix:** Update PyPI configuration (see "Trusted Publishers Setup" above)

### GitHub Actions Not Triggering

**Check:**
1. Tag exists on GitHub: `git ls-remote --tags github`
2. Workflow file exists: `.github/workflows/release.yml`
3. Tag matches pattern: `v*` (e.g., `v2.0.0a8`)

**Fix:**
```bash
# Ensure tag pushed to GitHub
git push github v2 --tags

# Or re-run workflow manually from GitHub UI
```

---

## Post-Release

### Announce to Team

**Slack message template:**
```markdown
🚀 rai-cli v{VERSION} — Disponible en PyPI

**Qué hay de nuevo:**
- [Feature 1]
- [Feature 2]

**Para actualizar:**
pip install --upgrade --pre rai-cli

**Estado:**
- PyPI: ✅ Publicado
- GitHub Actions: ✅ Automatizado
```

### Update Documentation

If major changes:
- Update README.md
- Update architecture docs if needed
- Update CLAUDE.md if workflow changes

---

## References

- **Skill:** `.claude/skills/rai-publish/SKILL.md`
- **Workflow:** `.github/workflows/release.yml`
- **Research:** `work/research/RES-PUBLISH-001/`
- **Backlog:** `governance/backlog.md` (§4: Hotfixes)

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-02-14 | Rai + Emilio | Initial SOP from v2.0.0a8 release experience |

---

**Note:** This SOP is not yet ingested into the knowledge graph. Governance extractor needs extension to parse SOPs. See HF-5 in backlog.

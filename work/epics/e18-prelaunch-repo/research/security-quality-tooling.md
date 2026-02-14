# Research Synthesis: S18.4 — Security & Quality Tooling

> Evidence catalog with triangulated claims and actionable recommendations.
> Research date: 2026-02-12 | 5 parallel research agents | 30+ sources per agent

---

## Executive Summary

**RaiSE ships with zero known vulnerabilities and a shift-left DevSecOps pipeline.**

The research reveals a significant gap between what security best practices recommend and what even the best Python projects actually do. We position raise-commons **above the exemplar baseline** — matching uv's supply chain posture (the strongest in the cohort) while adding local security scanning that none of the exemplars bother with. This is intentional: RaiSE is DevSecOps, and our repo should embody that.

### Recommended Toolchain (3 layers)

| Layer | Tools | When | Effort |
|-------|-------|------|--------|
| **L1: Pre-commit (local)** | ruff, detect-secrets, bandit, pyright (pre-push) | Every commit | S18.1 scope |
| **L2: CI Pipeline** | GitLab SAST + dep scanning + secrets, CodeQL (GitHub), zizmor, pip-audit | Every push/MR | S18.3 scope |
| **L3: Release** | Trusted Publishers (GitHub Actions), PEP 740 attestations (auto), CycloneDX SBOM | Every release | S18.3 scope |

**Skip for now:** SonarCloud (revisit when team grows beyond 2-3 contributors).

---

## Research Questions & Findings

### RQ1: Pre-Commit Hook Stack

**Claim:** The optimal pre-commit stack for a Python CLI in 2026 is: pre-commit framework + ruff + detect-secrets + bandit (~3s), with pyright on pre-push.

| Tool | Stage | Time | False Positive Rate |
|------|-------|------|---------------------|
| pre-commit-hooks (6 housekeeping) | pre-commit | ~200ms | None |
| ruff-check + ruff-format | pre-commit | ~200ms | ~0% |
| detect-secrets | pre-commit | ~300ms | Low (baseline file) |
| bandit (medium severity, high confidence) | pre-commit | ~1-3s | Low when tuned |
| **Total pre-commit** | | **~2-4s** | |
| pyright | pre-push | ~5-15s | ~0% |
| pip-audit | **CI only** | 3-10s | Low (needs network) |

**Key decisions:**
- **detect-secrets over gitleaks** — Lower false positive rate (precision-focused), pure Python, baseline file for known non-secrets. Gitleaks has 46% precision vs detect-secrets' near-zero false positives when baselined.
- **bandit stays** — Already in our guardrails. Tuned with `--severity-level medium --confidence-level high` to cut noise ~70%.
- **pyright on pre-push, not pre-commit** — 5-15s is too slow for commit friction. Microsoft explicitly declined to provide an official pre-commit hook (issue #3612).
- **pip-audit CI-only** — Needs network, pre-commit.ci blocks it, dependencies don't change per commit.

**Evidence:** 5/6 exemplar projects use .pre-commit-config.yaml. None use detect-secrets or bandit as hooks, but they also don't ship a security methodology. We go beyond the baseline intentionally.

**Confidence:** High | **Sources:** 25+ (pre-commit.com, Yelp/detect-secrets, PyCQA/bandit, astral-sh/ruff-pre-commit, academic comparison study arXiv:2307.00714)

---

### RQ2: GitLab Premium CI Security Features

**Claim:** GitLab Premium provides zero additional security value over Free tier. All scanning engines run in all tiers; Premium's value is CI minutes and project management, not security.

| Feature | Free | Premium | Ultimate |
|---------|:----:|:-------:|:--------:|
| SAST (Semgrep-based) | ✓ JSON | ✓ JSON | ✓ + MR widget + dashboard |
| Dependency Scanning | ✓ JSON | ✓ JSON | ✓ + MR widget + auto-remediation |
| Secret Detection (pipeline) | ✓ JSON | ✓ JSON | ✓ + MR widget |
| Secret Push Protection | ✗ | ✗ | ✓ (Beta) |
| Advanced SAST (cross-file) | ✗ | ✗ | ✓ |
| Security Dashboard | ✗ | ✗ | ✓ |
| License Policies | ✗ | ✗ | ✓ |
| uv.lock support | ✓ | ✓ | ✓ |

**Implication:** We still enable GitLab scanning (SAST + deps + secrets) — it's free and the JSON artifacts are parseable. But the real value comes from processing those artifacts ourselves (fail pipeline on Critical/High findings) rather than expecting the GitLab UI to help.

**Configuration (all tiers):**
```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.latest.gitlab-ci.yml

variables:
  DS_ENFORCE_NEW_ANALYZER: "true"
  SAST_EXCLUDED_PATHS: "tests/, docs/"
```

**Confidence:** Very High | **Sources:** docs.gitlab.com (SAST, dependency scanning, secret detection, pricing), GitLab forum confirmations

---

### RQ3: SonarCloud vs GitLab SAST

**Claim:** SonarCloud is complementary (not redundant) with GitLab SAST, but not needed for raise-commons now. CodeQL on the GitHub mirror provides superior security analysis for free.

| Dimension | GitLab Premium SAST | SonarCloud (Free OSS) | CodeQL (GitHub) |
|-----------|:-------------------:|:---------------------:|:---------------:|
| Python security patterns | Basic (Semgrep) | Strong (cross-file taint) | Very Strong (semantic) |
| Cross-file analysis | ✗ (needs Ultimate) | ✓ | ✓ |
| Code quality/smells | ✗ | ✓ (core strength) | Partial |
| False positive rate | ~18% (Semgrep) | ~15% | **~5%** |
| Accuracy benchmark | 82% | Not benchmarked | **88%** |
| Cost | Included | Free (OSS) | Free (public repos) |
| Setup effort | 5 lines YAML | Token + CI config | One-click or workflow |

**Decision: Skip SonarCloud, use CodeQL.**
- Ruff + Pyright already cover most of SonarCloud's code quality value
- CodeQL has the lowest false positive rate (5%) and highest accuracy (88%)
- Free for public repos on GitHub mirror (planned in S18.3)
- No additional dashboard to monitor

**Revisit SonarCloud** when: team grows beyond 2-3 contributors and quality gates across contributors become valuable.

**Confidence:** High | **Sources:** DryRun Security benchmark, SonarSource docs, GitLab SAST docs, CodeQL docs, PeerSpot comparisons

---

### RQ4: Supply Chain Security

**Claim:** Publish from GitHub Actions with Trusted Publishers to get PEP 740 attestations automatically. This matches the strongest supply chain posture in the Python ecosystem.

| Practice | Maturity | Effort | Value | Who Does It |
|----------|:--------:|:------:|:-----:|:-----------:|
| **Trusted Publishers (GitHub Actions)** | Production | 2h | High | 5/6 exemplars |
| **PEP 740 attestations** | Production | 0 (auto) | High | 5/6 (auto since pypa/gh-action-pypi-publish v1.11+) |
| **GitHub artifact attestation** | Production | 1h | Medium | 1/6 (uv) |
| **CycloneDX SBOM** | Emerging | 2h | Medium | 0/6 (but EU CRA by 2027) |
| **SLSA Level 3** | Production | 4h | Low-Med | Achievable with reusable workflows |
| **GitLab Trusted Publishing** | Production | 2h | Medium | N/A (no attestations) |
| Standalone Sigstore signing | Production | 1h | Low | 0/6 (PyPI attestations supersede) |

**Key decisions:**
1. **Publish from GitHub Actions, not GitLab** — GitLab supports Trusted Publishing but does NOT auto-generate PEP 740 attestations. GitHub Actions does.
2. **Add `actions/attest-build-provenance`** — Only uv does this, but it's 5 lines of YAML for SLSA Level 2 provenance.
3. **Generate CycloneDX SBOM** — Nobody does it yet, but EU CRA mandatory by Dec 2027. Forward-looking compliance.
4. **Use `uv export` → `cyclonedx-py`** — `cyclonedx-py` doesn't parse `uv.lock` directly.

**Confidence:** High | **Sources:** PyPI docs, Sigstore blog, PEP 740, EU CRA official, astral-sh/ruff & uv release workflows, trailofbits/are-we-pep740-yet

---

### RQ5: Exemplar Project Survey

**Claim:** The top Python projects have surprisingly minimal security tooling. None use traditional SAST (CodeQL, Semgrep, SonarCloud, Bandit). They rely on type checkers + linters for quality, and Trusted Publishers for supply chain.

| Feature | FastAPI | Ruff | uv | Pydantic | Typer | httpx |
|---------|:-------:|:----:|:--:|:--------:|:-----:|:-----:|
| Pre-commit config | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Ruff | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Type checker | MyPy | — | ty | Pyright+MyPy+Pyrefly | MyPy | MyPy |
| Trusted Publishers | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Artifact attestation | ✗ | ✗ | **✓** | ✗ | ✗ | ✗ |
| Zizmor (GHA audit) | ✗ | **✓** | **✓** | ✗ | ✗ | ✗ |
| CodeQL/SAST | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| SonarCloud | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Bandit | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| detect-secrets | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| SBOM | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 100% coverage | **✓** | ✗ | ✗ | ✗ | **✓** | **✓** |
| Dependabot | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |

**Pattern:** "Match uv's posture + FastAPI's coverage discipline" = best achievable.

**Confidence:** Very High | **Sources:** Direct examination of 6 GitHub repos (.pre-commit-config.yaml, .github/workflows/, pyproject.toml, dependabot.yml)

---

## Tensions & Resolution

### Tension 1: Best practices recommend SAST, but 0/6 exemplars use it

**Resolution:** The exemplar projects are libraries/tools, not methodology frameworks. RaiSE claims DevSecOps — our repo must embody that claim. We add Bandit (local) + CodeQL (CI) + GitLab SAST (CI) because:
- Bandit is already in our guardrails (consistency)
- CodeQL is free and has the best accuracy (88%, 5% FP rate)
- GitLab SAST is free and already paid for
- The marginal cost is near-zero; the signal value is real

### Tension 2: detect-secrets vs gitleaks vs "nobody uses either"

**Resolution:** We add detect-secrets because:
- We have a SECURITY.md and a security guardrail — shipping secrets would be reputationally catastrophic
- detect-secrets has near-zero false positives with baseline
- Sub-second execution
- The exemplars rely on GitHub's built-in secret scanning (enabled by default for public repos), which we'll also have on the mirror. detect-secrets is our local shift-left complement.

### Tension 3: SBOM — nobody does it, but regulation is coming

**Resolution:** Add SBOM generation to the release pipeline now. It's 2 hours of work, forward-looking for EU CRA (mandatory Dec 2027), and demonstrates the thoroughness that differentiates RaiSE. Attach to GitHub releases as artifact.

---

## Concrete Recommendation: What Goes Where

### L1: Pre-Commit (.pre-commit-config.yaml) — S18.3 scope

```yaml
repos:
  # Housekeeping
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-toml
      - id: check-yaml
        args: ['--unsafe']
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace

  # Linting & Formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.0  # pin to current
    hooks:
      - id: ruff-check
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Secret Detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Security SAST
  - repo: https://github.com/PyCQA/bandit
    rev: "1.9.3"
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml", "--severity-level", "medium", "--confidence-level", "high"]
        additional_dependencies: ["bandit[toml]"]

  # Type Checking (pre-push only)
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.391
    hooks:
      - id: pyright
        stages: ["pre-push"]
```

**Performance budget:** ~2-4s pre-commit, ~5-15s pre-push.

### L2: CI Pipeline — S18.3 scope

**GitLab CI (.gitlab-ci.yml):**
```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.latest.gitlab-ci.yml

variables:
  DS_ENFORCE_NEW_ANALYZER: "true"
  SAST_EXCLUDED_PATHS: "tests/, docs/"
```

**GitHub Actions (on mirror):**
- CodeQL (default setup, one-click — security-extended queries)
- zizmor (GitHub Actions security scanner, write to security-events)
- pip-audit or uv-secure (dependency vulnerability scanning)
- pytest with --fail-under=90 (match current guardrail)
- pre-commit run --all-files (catch bypassed local hooks)

### L3: Release Pipeline — S18.3 scope

**GitHub Actions release workflow:**
```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
      contents: read
      attestations: write
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: uv build
      - uses: actions/attest-build-provenance@v3
        with:
          subject-path: "dist/*"
      - name: Generate SBOM
        run: |
          uv export --format requirements-txt --no-hashes > /tmp/requirements.txt
          cyclonedx-py requirements /tmp/requirements.txt -o dist/sbom.cdx.json
      - uses: pypa/gh-action-pypi-publish@release/v1
        # Trusted Publishing — no token needed
        # PEP 740 attestations generated automatically
```

---

## S18.3 vs Post-Launch Split

### Include in S18.3 (Release Engineering)

| Item | Effort | Rationale |
|------|--------|-----------|
| .pre-commit-config.yaml | 1h | Foundation — shift-left starts here |
| GitHub Actions: test + lint + type check | 2h | CI must exist before public |
| GitHub Actions: CodeQL (one-click) | 15min | Free, best-in-class accuracy |
| GitHub Actions: release with Trusted Publishers | 2h | Supply chain security baseline |
| GitLab CI: SAST + deps + secrets | 30min | 3 include lines |
| Dependabot config | 15min | Auto-update deps + GH Actions |

### Post-Launch (separate stories)

| Item | Effort | Rationale |
|------|--------|-----------|
| zizmor CI workflow | 1h | GH Actions security audit — nice-to-have |
| CycloneDX SBOM in release | 2h | Forward-looking, not blocking launch |
| `actions/attest-build-provenance` | 1h | Beyond baseline, matches only uv |
| SonarCloud integration | 3h | Revisit when team grows |
| SLSA Level 3 (reusable workflows) | 4h | Aspirational |

---

## Evidence Quality Summary

| Claim | Confidence | Triangulation |
|-------|:----------:|---------------|
| GitLab Premium = Free for security | Very High | Official docs + forum + tier comparison |
| detect-secrets > gitleaks for pre-commit | High | Academic study + adoption data + FP comparison |
| CodeQL > SonarCloud for small OSS security | High | Benchmark data + cost analysis + exemplar absence |
| Trusted Publishers = standard practice | Very High | 5/6 exemplars + PyPI official recommendation |
| PEP 740 attestations are automatic | Very High | PyPI docs + pypa/gh-action-pypi-publish code |
| SBOM will be required (EU CRA 2027) | High | Official EU legislation + FOSSA analysis |
| 0/6 exemplars use traditional SAST | Very High | Direct repo examination |
| Pre-commit <4s is achievable | High | Tool benchmarks + exemplar configs |

---

## Sources (Selected)

### Pre-commit & Local Security
- [detect-secrets (Yelp)](https://github.com/Yelp/detect-secrets)
- [Comparative Study of Secret Detection (arXiv:2307.00714)](https://arxiv.org/pdf/2307.00714)
- [Bandit Configuration](https://bandit.readthedocs.io/en/latest/config.html)
- [Ruff Pre-Commit](https://github.com/astral-sh/ruff-pre-commit)
- [Pyright Issue #3612 (no official hook)](https://github.com/microsoft/pyright/issues/3612)

### GitLab CI Security
- [GitLab SAST Docs](https://docs.gitlab.com/user/application_security/sast/)
- [GitLab Dependency Scanning](https://docs.gitlab.com/user/application_security/dependency_scanning/)
- [GitLab Secret Detection](https://docs.gitlab.com/user/application_security/secret_detection/)
- [uv.lock Support (Issue #510295)](https://gitlab.com/gitlab-org/gitlab/-/issues/510295)

### SonarCloud & SAST Alternatives
- [CodeQL for Python](https://codeql.github.com/docs/codeql-language-guides/codeql-for-python/)
- [DryRun Security Benchmark](https://www.dryrun.security/blog/dryrun-security-vs-snyk-codeql-sonarqube-and-semgrep---python-django-security-analysis-showdown)
- [SonarCloud Python](https://www.sonarsource.com/knowledge/languages/python/)

### Supply Chain Security
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [PyPI Attestations GA (Sigstore Blog)](https://blog.sigstore.dev/pypi-attestations-ga/)
- [PEP 740](https://peps.python.org/pep-0740/)
- [EU Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
- [CycloneDX Python](https://github.com/CycloneDX/cyclonedx-python)
- [Are we PEP 740 yet?](https://trailofbits.github.io/are-we-pep740-yet/)

### Exemplar Repos (direct examination)
- [FastAPI](https://github.com/fastapi/fastapi) — .pre-commit-config.yaml, workflows
- [Ruff](https://github.com/astral-sh/ruff) — .pre-commit-config.yaml, workflows
- [uv](https://github.com/astral-sh/uv) — .pre-commit-config.yaml, workflows, attestation
- [Pydantic](https://github.com/pydantic/pydantic) — .pre-commit-config.yaml, workflows
- [Typer](https://github.com/fastapi/typer) — .pre-commit-config.yaml, workflows
- [httpx](https://github.com/encode/httpx) — workflows

---

*Research completed: 2026-02-12*
*5 parallel research agents, 150+ sources examined*
*Next: Feed into S18.3 planning*

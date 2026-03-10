# Recommendation: Python Security Guardrails for raise-cli

> Actionable security guidelines based on triangulated evidence from 25 sources

---

## Recommendation

**Decision**: Adopt a comprehensive Python security checklist as mandatory guardrails for raise-cli development, integrated into pre-commit hooks and CI pipeline.

**Confidence**: HIGH

**Rationale**:
- All 10 major claims are triangulated with 3+ sources
- OWASP Top 10:2025 emphasizes supply chain and input validation
- Bandit + pip-audit provide automated enforcement
- Pydantic already in stack provides natural validation layer

---

## Trade-offs

| Accepting | Because |
|-----------|---------|
| Slightly slower CI (security scans) | Prevents vulnerabilities before production |
| No pickle/yaml.load flexibility | JSON provides safe alternative; security over convenience |
| Stricter subprocess patterns | Command injection is a critical vulnerability |
| Memory for secrets not perfectly secure | Python limitation; minimize exposure time instead |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positives from Bandit | Medium | Low | Configure skips for test files; baseline file |
| Dependency vulnerabilities in transitive deps | Medium | High | pin versions; regular pip-audit runs |
| Developer friction with strict rules | Low | Medium | Document "why" for each rule; provide examples |
| Supply chain attack on dev tools | Low | Critical | Use trusted sources; verify hashes |

---

## Implementation Plan

### Phase 1: Immediate (This Week)

1. **Update `governance/solution/guardrails.md`** with security section
2. **Add to pre-commit hooks**:
   - `bandit -r src/ -ll`
   - `detect-secrets scan --baseline .secrets.baseline`
3. **Create `.secrets.baseline`** file

### Phase 2: CI Integration (Next Sprint)

1. **Add pip-audit to CI pipeline**
2. **Add dependency review for PRs**
3. **Configure security scanning in GitLab CI**

### Phase 3: Documentation (Ongoing)

1. **Add security checklist to CONTRIBUTING.md**
2. **Document patterns with examples**
3. **Create ADR for security decisions**

---

## Alternatives Considered

| Alternative | Decision | Reason |
|-------------|----------|--------|
| Semgrep instead of Bandit | Not now | Bandit is simpler, sufficient for CLI; revisit if complexity grows |
| Safety instead of pip-audit | Use both | Different databases; complementary coverage |
| Vault for all secrets | Not now | Overkill for CLI; keyring + env vars sufficient |
| Custom security linter | No | Bandit + Ruff cover 95% of cases |

---

## Next Steps

1. Review and approve this research
2. Merge security checklist into guardrails.md
3. Update pre-commit-config.yaml
4. Create ADR-023 for security architecture decisions

---

## Governance Linkage

| Artifact | Action |
|----------|--------|
| `governance/solution/guardrails.md` | UPDATE with security section |
| `.pre-commit-config.yaml` | UPDATE with Bandit, detect-secrets |
| `CONTRIBUTING.md` | UPDATE with security checklist reference |
| `dev/decisions/` | CREATE ADR-023 Security Guardrails |

---

*Generated: 2026-02-05*

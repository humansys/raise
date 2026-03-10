# E18 Research Synthesis — Pre-Launch Repo Readiness

> 4 parallel research streams, 70+ sources consulted, 2026-02-12
> Confidence: High (strong convergence across streams)

---

## Stream 1: Open-Core Model

**Key findings:**
- **Buyer-Based Open Core (BBOC)** is the consensus framework (GitLab, PostHog, OCV). Features placed by *who* buys, not technical complexity.
- Individual developer features = open. Team/manager/compliance features = paid.
- Apache 2.0 is the right license for a CLI tool — cloud-provider risk is negligible (not a hosted service).
- PostHog pattern: monorepo with `ee/` directory under separate proprietary license.
- The "crippled core" trap: >90% of users should never need to pay. Free version must be genuinely useful in production.

**Decision confirmed:** Apache 2.0 for open core. No license change needed.

**Sources:** OCV Handbook, GitLab Stewardship, PostHog repo, Supabase repo, Grafana relicensing, HashiCorp BSL analysis (18 sources)

---

## Stream 2: Security Audit

**Key findings:**
- **Dual-tool scan:** Gitleaks (highest recall 86-88%) + TruffleHog (verifies live secrets). No single tool catches everything.
- **Fresh start recommended** for public mirror: squashed initial commit. Full history stays in private GitLab.
  - Security risk of missing a secret in history rewrite is asymmetric (downside >>> upside)
  - No external contributors whose attribution would be lost
  - Public repo accumulates its own history going forward
- **.gitignore gaps to fix:** `.env`, `*.pem`, `*.key`, `.pypirc`, `credentials.json`, `*.sqlite`, `.netrc`
- **Pre-commit:** `detect-secrets` as hook going forward
- **Post-publication:** Enable GitHub Secret Scanning + Push Protection + Dependabot

**Decision needed:** Full history vs fresh start for GitHub mirror.

**Sources:** Arxiv academic study, GitHub docs, Microsoft Tech Community, GitGuardian, Mozilla Wiki (17 sources)

---

## Stream 3: README Conversion

**Key findings:**
- **30-second test:** In 30 seconds, developer must answer: What? Why? How to try? What does it look like?
- **Above the fold:** Name → one-liner → badges (3-4) → value prop → install command
- **Code example is the #1 conversion signal.** For rai-cli: a session transcript showing the "aha moment"
- **Positioning against alternatives:** "You've tried Cursor, Copilot, raw ChatGPT..." — tells developers where tool fits
- **Progressive disclosure:** Minimal example → expanded example
- **Target length:** 150-250 lines. Move 60% of current content to docs site.
- **GIF/visual:** VHS (Charmbracelet) for reproducible terminal GIFs. But for Claude Code interaction, a session transcript may be more authentic.
- **Badges that matter:** PyPI version, CI status, License, Python versions. Skip cargo-cult badges.

**Exemplar patterns:** FastAPI (code example IS the sales pitch), Ruff/uv (benchmark chart + "replaces X"), Pydantic (extreme brevity, delegates to docs)

**Sources:** 7 exemplar READMEs analyzed, 6 guide articles, 1 academic study (18 sources)

---

## Stream 4: Community Files + GitHub Setup

**Essential for day 1:**
| File | Notes |
|------|-------|
| CONTRIBUTING.md | How to report bugs, suggest features, dev setup, PR process |
| CODE_OF_CONDUCT.md | Contributor Covenant v2.1 |
| SECURITY.md | Email-based CVD policy, response timeline, safe harbor (OpenSSF baseline requires it) |
| CHANGELOG.md | Keep a Changelog format (hand-written, not auto-generated) |
| Issue templates (YAML) | bug-report.yml, feature-request.yml, config.yml |

**GitHub repo settings:**
- Description + topics, disable wiki, enable issues, enable secret scanning + Dependabot

**Defer to post-alpha:**
- FUNDING.yml, SUPPORT.md, GitHub Discussions, PR template, social preview image

**Mirror strategy:** GitLab CI pipeline (free tier compatible, precise control) over built-in mirror (requires Premium) or manual push (guaranteed to drift).

**Sources:** GitHub docs, OpenSSF baseline, OSSF vulnerability guide, Keep a Changelog, GitLab docs (27 sources)

---

## Cross-Stream Decisions

| # | Decision | Recommendation | Confidence | Rationale |
|---|----------|---------------|------------|-----------|
| D1 | License | Apache 2.0 (keep current) | High | Patent grant, CLI tool = low cloud risk, enterprise-friendly |
| D2 | History strategy | Fresh start (squashed initial commit) | High | Asymmetric risk, no external contributors to attribute |
| D3 | Mirror mechanism | GitLab CI pipeline job | Medium | Free tier, auditable, precise branch control |
| D4 | README structure | FastAPI/Ruff pattern (one-liner → code example → features) | High | Convergent evidence from 7 exemplars |
| D5 | Community files | Full set day 1 (incl. SECURITY.md) | High | OpenSSF baseline, GitHub community profile |
| D6 | CHANGELOG format | Keep a Changelog (manual) | High | Auto-generated from commits is poor DX per evidence |
| D7 | Badges | 3-4 max (PyPI, CI, license, Python) | High | More = noise per research |
| D8 | GIF/visual | Session transcript first, VHS GIF as nice-to-have | Medium | Claude Code interaction is text-based, not visual terminal |

---

*Research conducted: 2026-02-12*
*4 agents, ~140K tokens of research, 70+ sources*

# Research: Typer CLI Design Best Practices

> Research ID: TYPER-CLI-BP-20260205
> Created: 2026-02-05
> Researcher: Rai
> Depth: Standard (4-8h, 15-30 sources)

---

## Research Question

**Primary:** What are the best practices for designing Typer-based CLI applications, specifically for command structure, option design, output formatting, error handling, and testing?

**Secondary Questions:**
1. When should commands be nested vs flattened?
2. What output formats should be supported and how?
3. How should exceptions map to exit codes?
4. What are common anti-patterns to avoid?

**Decision Context:** This research informs the ongoing development of the RaiSE CLI (`rai` command) to ensure it follows industry best practices and provides excellent developer experience.

---

## Quick Navigation

| Artifact | Purpose | Time |
|----------|---------|------|
| [synthesis.md](./synthesis.md) | Triangulated claims with evidence | 10 min |
| [recommendation.md](./recommendation.md) | Actionable patterns for RaiSE CLI | 15 min |
| [sources/evidence-catalog.md](./sources/evidence-catalog.md) | All 22 sources with ratings | 5 min |

---

## Executive Summary

Research across 22 sources (5 Very High, 9 High, 7 Medium, 1 Low evidence) reveals strong consensus on Typer CLI best practices:

### Key Findings

1. **Prefer flags over positional arguments** - More explicit, future-proof, enables any order
2. **Support multiple output formats** - human (default), json (stable), table (scannable)
3. **Map exceptions to exit codes** - Catch at CLI boundary, distinct codes per error type
4. **One file per command group** - Use `add_typer()` for composition
5. **Test with CliRunner** - Parametrize, test user perspective, cover error paths
6. **Human-first design** - Examples in help, suggestions, actionable errors
7. **Respect TTY detection** - Rich handles this; honor NO_COLOR
8. **Thin commands** - Orchestrate calls to service layer, don't contain logic
9. **Use callbacks for global options** - --verbose, --format via ctx.obj
10. **Avoid anti-patterns** - Ambiguous names, catch-all commands, abbreviations

### Confidence Assessment

| Topic | Confidence | Source Count |
|-------|------------|--------------|
| Command structure | HIGH | 6 sources |
| Option design | HIGH | 5 sources |
| Output formatting | HIGH | 6 sources |
| Error handling | HIGH | 5 sources |
| Testing | HIGH | 4 sources |
| Anti-patterns | HIGH | 4 sources |

---

## Recommendation Summary

Adopt the patterns documented in [recommendation.md](./recommendation.md):

1. **Structure:** Topic + Command (`rai context query`)
2. **Options:** `-f, --format` for output, standard flag names
3. **Output:** OutputFormat enum, Rich for human, stable JSON schema
4. **Errors:** Exception hierarchy with exit codes, catch at boundary
5. **Testing:** CliRunner + pytest.mark.parametrize

**Trade-offs accepted:** More code for output formatting and testing, but enables both human UX and automation.

---

## Research Metadata

- **Tool used:** WebSearch + Context7 + WebFetch
- **Search date:** 2026-02-05
- **Prompt version:** 1.0 (research-prompt-template.md)
- **Total sources:** 22
- **Evidence distribution:** Very High (23%), High (41%), Medium (32%), Low (4%)
- **Total time:** ~2 hours

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated
- [x] 22 sources consulted (target: 15-30)
- [x] Mix of academic, official, and practitioner sources
- [x] Sources include publication/update dates
- [x] Evidence catalog complete with all required fields
- [x] Major claims triangulated (3+ sources each)
- [x] Confidence levels explicitly stated for each claim
- [x] Contrary evidence acknowledged (none found)
- [x] Gaps and unknowns documented
- [x] Recommendation is specific and actionable
- [x] Trade-offs explicitly acknowledged
- [x] Risks identified with mitigations
- [x] Clear link to decision context

---

## Governance Linkage

This research informs:
- **Ongoing Development:** RaiSE CLI command design
- **Potential ADR:** CLI output formatting standards
- **Guardrails Update:** CLI testing requirements

---

*Research complete: 2026-02-05*

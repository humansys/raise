# Epic Brief: Agile HR Performance Management

## Hypothesis

For **HR Business Partners** who struggle with outdated annual performance reviews,
the **RaiSE Agile Performance toolkit** is a **methodology + AI-governed platform**
that **enables continuous performance enablement through structured katas, AI-assisted feedback, and governance-as-code**.
Unlike generic HR tools adapted from engineering (Jira, BambooHR), our solution
**embeds Agile HR methodology directly into AI-governed workflows designed for people processes**.

## Success Metrics

- **Leading:** HRBP completes first AI-assisted check-in cycle in < 15 minutes (first story)
- **Lagging:** JLS can demo a full performance cycle (check-in → OKR review → feedback) to a client within 2 sprints

## Appetite

**M** — 5-7 stories

## Scope Boundaries

### In (MUST)

- Agile Check-in kata: structured 1:1 preparation + capture
- AI-assisted feedback drafting with governance guardrails
- OKR progress analysis skill
- Performance cycle governance (frequency, quality, bias detection gates)
- Configurable by JLS consultants for each client context

### In (SHOULD)

- Feedback-360 multi-source collection kata
- Talent review / calibration kata
- Dashboard metrics for HRBP (check-in frequency, OKR health)

### No-Gos

- No replacing existing HRIS systems (Workday, SAP SuccessFactors) — integrate, don't compete
- No employee self-service portal — focus on HRBP and manager workflow
- No compensation/payroll linkage — pure performance enablement
- No building a SaaS product — this is a methodology toolkit JLS configures for clients

### Rabbit Holes

- **Over-engineering AI feedback:** AI drafts suggestions, humans own the words. Don't build an autonomous feedback bot.
- **HRIS integration scope creep:** Start file-based (CSV/JSON import), don't build API adapters to Workday in v1.
- **Gamification:** Tempting to add scores/badges — resist. Performance is about growth, not points.
- **Multi-language NLP:** Start English-only for feedback analysis. Localization is a separate epic.

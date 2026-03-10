# ADR-045: Doctor Check Protocol — Separate from Workflow Gates

**Status:** Accepted
**Date:** 2026-03-05
**Epic:** E352 (rai doctor)

## Context

RaiSE needs a diagnostic system (`rai doctor`) that validates the tool's own health. We already have a `WorkflowGate` protocol (ADR-039) for validating user products (tests, lint, types). The question is whether doctor checks should reuse the gate system or have their own protocol.

## Decision

**Create a separate `DoctorCheck` protocol** with its own entry point group (`rai.doctor.checks`), inspired by but independent from the gate system.

## Rationale

The domains are semantically different:

| Aspect | WorkflowGate | DoctorCheck |
|--------|-------------|-------------|
| **Validates** | User's product | RaiSE itself |
| **Severity** | Binary (pass/fail) | 3-level (pass/warn/error) |
| **Trigger** | Workflow transitions (pre-release, pre-commit) | On-demand (`rai doctor`) |
| **Failure meaning** | Block operation | Inform user, suggest fix |
| **Pipeline** | Independent gates | Ordered categories with dependencies |

Reusing gates would require:
- Adding severity to `GateResult` (contaminates gate semantics)
- Adding `category`, `fix_hint`, `requires_online` to gate protocol
- Overloading `workflow_point` for a non-workflow use case

The gate protocol is 45 lines. Duplicating the pattern (not the code) for a different domain is correct separation of concerns, not tech debt.

## Consequences

- New module: `src/rai_cli/doctor/` (~200 lines infrastructure)
- New entry point group: `rai.doctor.checks`
- Gate system unchanged — no risk of regression
- If patterns converge in the future, extract shared base (YAGNI today)

## Alternatives Considered

1. **Reuse WorkflowGate with `workflow_point="doctor"`** — Rejected: binary pass/fail insufficient, semantic mismatch.
2. **Extend GateResult with severity** — Rejected: contaminates gate model for all consumers.

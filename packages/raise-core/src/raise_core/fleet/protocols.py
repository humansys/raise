"""Fleet provisioning + pipeline-binding contracts — ADR-2026-08-05 §1/§2/§3.

§1 (RAISE-15764): `ProvisioningVerifier.verify()` checks a fleet worktree is
governed BEFORE the agent is launched — pure read of filesystem/env state,
no I/O side effects.

§2 amended (RAISE-15765): `FleetPipelineBinding.bind()` calls `pipeline_start`
before the fleet agent process launches. The `advance_token` is returned
ONLY into the fleet director's context (the `fleet_dispatch` tool result) —
never into a brief, an env var visible to the subagent, or storage
(RAISE-13580, RAISE-14555). The DIRECTOR advances on signal; subagents never
call `pipeline_advance`.

§3 amended (RAISE-15772): `FleetPromptBuilder.build()` assembles the full
BRIEF.md a fleet subagent receives — governance preamble, skill essential
rules, the `[RAI:...]` header, the target worktree (D10.b), task context,
and the completion protocol (D3). It is the single seam for brief content.

Per ADR-033 (graph-confirmed), raise-core publishes the `@runtime_checkable`
Protocols only and holds no concrete implementation; raise-cli implements
them (see `raise_cli.fleet.provisioning.DefaultProvisioningVerifier`,
`raise_cli.fleet.binding.PipelineBinder`,
`raise_cli.fleet.prompt_builder.DefaultFleetPromptBuilder`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ProvisioningCheck:
    """One named governance/workspace check result — ADR §1.

    name: e.g. "session_governance.hooks.pre_tool_use",
        "workspace_integrity.git_worktree". Dotted category prefix encodes
        which registry (D10) the check belongs to.
    satisfied: whether the check passed.
    detail: human-readable reason when not satisfied (empty when satisfied).
    """

    name: str
    satisfied: bool
    detail: str = ""


@dataclass(frozen=True)
class ProvisioningReport:
    """Result of `ProvisioningVerifier.verify()` — ADR §1, split per D10.

    The check registry splits into two categories because fleet subagents
    are `Agent()`/Task calls INSIDE the director's own session (ADR-107 §2,
    F12) — they inherit the DIRECTOR's hooks/settings, not a story
    worktree's `.claude/settings.json`. Verifying a worktree's hooks alone
    would check a file the in-band subagent never loads.

    session_governance: hook-array / cwd-binding-hook checks. BLOCKING when
        this report describes the DIRECTOR's own session
        (`verify_director_session()`, D10.1's `director_ungoverned` gate).
        ADVISORY when this report describes a per-story worktree (the
        `verify()` Protocol method) — D10 point 3: making it blocking there
        would refuse a story over a file its in-band subagent never reads,
        which is governance theater, not enforcement. It becomes the
        operative gate once out-of-band launch exists (RAISE-15882).
    workspace_integrity: git/venv/lease checks against the resolved
        worktree's files. ALWAYS blocking wherever reported — the
        subagent's Bash/Edit/Write calls touch those files regardless of
        which session governs it (D10 point 2).
    work_id: the story key this report describes, or a sentinel such as
        "__director__" for the pre-loop director-session report.
    """

    work_id: str
    session_governance: tuple[ProvisioningCheck, ...] = ()
    workspace_integrity: tuple[ProvisioningCheck, ...] = ()

    @property
    def checks(self) -> tuple[ProvisioningCheck, ...]:
        """ADR §1 compatibility: every check, session_governance then workspace_integrity."""
        return self.session_governance + self.workspace_integrity

    @property
    def is_governed(self) -> bool:
        """ADR §1: True iff every check across BOTH categories is satisfied.

        Do NOT use this to gate the fleet_dispatch per-story loop — D10
        makes per-worktree session_governance advisory there, so gating on
        this property would incorrectly block dispatch on a file the
        in-band subagent never loads. Use `workspace_integrity_satisfied`
        for the per-story gate and `session_governance_satisfied` for the
        director's own gate (D10.1).
        """
        return all(c.satisfied for c in self.checks)

    @property
    def workspace_integrity_satisfied(self) -> bool:
        """True iff every workspace_integrity check passed — the per-story gate (D10 pt2)."""
        return all(c.satisfied for c in self.workspace_integrity)

    @property
    def session_governance_satisfied(self) -> bool:
        """True iff every session_governance check passed — the director gate (D10.1)."""
        return all(c.satisfied for c in self.session_governance)


@runtime_checkable
class ProvisioningVerifier(Protocol):
    """Verifies a fleet worktree is governed BEFORE the agent is launched.

    Pure read of filesystem/env state — no I/O side effects (ADR §1).
    """

    def verify(self, worktree_path: str, work_id: str) -> ProvisioningReport:
        """Check `worktree_path`'s workspace_integrity and session_governance.

        workspace_integrity is blocking; session_governance is advisory on
        the fleet_dispatch path (D10).
        """
        ...


@dataclass(frozen=True)
class FleetRunBinding:
    """Result of `FleetPipelineBinding.bind()` — a minted run + its capability token.

    run_id: non-secret — safe to hand onward to `SubagentDispatcher` /
        `FleetPromptBuilder.build()` and to embed in a `[RAI:...]` header.
    advance_token: secret — stays with the fleet director; never handed to a
        subagent, storage, or a brief (RAISE-13580, RAISE-14555).
    """

    run_id: str
    advance_token: str


@runtime_checkable
class FleetPipelineBinding(Protocol):
    """Calls `pipeline_start` before the agent process launches.

    The `advance_token` is returned ONLY into the fleet director's context
    (the `fleet_dispatch` tool result) — never into a brief, an env var
    visible to the subagent, or storage (RAISE-13580, RAISE-14555). The
    DIRECTOR advances on signal; subagents never call `pipeline_advance`.

    Lives at the `mcp_tools_fleet` MCP-tool boundary, not inside
    `SubagentDispatcher` — `bind()` performs pipeline I/O, which
    `SubagentDispatcher`'s module contract explicitly forbids (D1/F7).
    """

    def bind(self, work_id: str) -> FleetRunBinding:
        """Start a pipeline run for `work_id`; return its (run_id, advance_token)."""
        ...


@runtime_checkable
class FleetPromptBuilder(Protocol):
    """Assembles the full BRIEF.md a fleet subagent receives — ADR §3 amended (D4/D10.b).

    `build()` is the single seam for brief content: governance preamble
    (`rai session context -s governance,behavioral` pattern), the target
    skill's essential rules (TDD, commit protocol, gate policy), the
    `[RAI:...]` header (`build_rai_header(run_id=..., phase=...)`), the
    absolute `worktree_path` with an explicit enter-the-worktree instruction
    (D10.b), task context, and the completion protocol (D3). Every
    brief-content addition (RAISE-15767 platform matrix, RAISE-15768
    graph-query contracts) becomes a section of THIS brief, not a separate
    constructor.

    *Constraint (type-level, D4):* `build()` receives `run_id` — the
    non-secret minted by `FleetPipelineBinding.bind()` — and MUST NOT
    accept `advance_token` or a `FleetRunBinding` as a parameter, and the
    rendered brief MUST NOT contain the token value or any instruction
    telling the subagent to advance the pipeline run itself. The DIRECTOR
    holds the token and advances on signal (RAISE-13580, RAISE-14555,
    RAISE-15766).
    """

    def build(
        self,
        work_id: str,
        skill: str,
        run_id: str,
        worktree_path: str,
    ) -> str:
        """Assemble and return the full BRIEF.md text for one subagent dispatch.

        Args:
            work_id: Jira issue key (e.g. "RAISE-15772").
            skill: Full skill name (e.g. "rai-story-implement").
            run_id: Non-secret pipeline run id from `FleetPipelineBinding.bind()`.
            worktree_path: Absolute path to the story's resolved worktree (D2.a).
        """
        ...

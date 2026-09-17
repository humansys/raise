"""Conservative validation policy for impact analysis."""

from __future__ import annotations

from pathlib import Path

from raise_cli.impact.models import (
    ChangedFileImpact,
    FileCategory,
    FullRunReason,
    ImpactConfidence,
    ImpactReport,
    OwnershipReport,
)

ReasonSpec = tuple[str, str]

HIGH_RISK_EXACT: dict[str, ReasonSpec] = {
    ".raise/manifest.yaml": (
        "manifest_changed",
        "Manifest changes can alter app ownership or gate commands; run broader validation.",
    ),
    "pyproject.toml": (
        "project_config_changed",
        "Project configuration changes can alter test, lint, type, or package behavior.",
    ),
    "uv.lock": (
        "lockfile_changed",
        "Lockfile changes can alter dependency resolution; run broader validation.",
    ),
}

HIGH_RISK_PREFIXES: tuple[tuple[str, ReasonSpec], ...] = (
    (
        ".github/workflows/",
        (
            "ci_workflow_changed",
            "CI workflow changes can alter validation behavior; run broader validation.",
        ),
    ),
    (
        "packages/raise-cli/src/raise_cli/gates/",
        (
            "gate_runner_changed",
            "Gate implementation changes can alter validation behavior; run broader validation.",
        ),
    ),
)

SHARED_APP_NAMES = {"raise-core"}


def _normalize_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").strip("/")


def classify_file_category(path: Path | str) -> FileCategory:
    """Classify a repository path into impact categories."""
    value = _normalize_path(path)
    name = Path(value).name
    if value.startswith(".github/workflows/"):
        return "ci"
    if value == "uv.lock":
        return "lockfile"
    if value.startswith("docs/"):
        return "docs"
    if value.startswith("governance/") or value.startswith("work/"):
        return "governance"
    if value.startswith(".raise/") or name in {"pyproject.toml", "tox.ini"}:
        return "config"
    if "/tests/" in value or name.startswith("test_"):
        return "test"
    if value.endswith(".py") and "/src/" in value:
        return "source"
    return "unknown"


def _high_risk_reason(path: str) -> FullRunReason | None:
    if path in HIGH_RISK_EXACT:
        code, message = HIGH_RISK_EXACT[path]
        return FullRunReason(code=code, message=message, paths=[path])
    for prefix, spec in HIGH_RISK_PREFIXES:
        if path.startswith(prefix):
            code, message = spec
            return FullRunReason(code=code, message=message, paths=[path])
    return None


def _reason_key(reason: FullRunReason) -> tuple[str, tuple[str, ...]]:
    return reason.code, tuple(reason.paths)


def _merge_reasons(reasons: list[FullRunReason]) -> list[FullRunReason]:
    by_code: dict[str, FullRunReason] = {}
    for reason in reasons:
        existing = by_code.get(reason.code)
        if existing is None:
            by_code[reason.code] = reason.model_copy(
                update={"paths": sorted(set(reason.paths))}
            )
        else:
            by_code[reason.code] = existing.model_copy(
                update={"paths": sorted(set(existing.paths) | set(reason.paths))}
            )
    return sorted(by_code.values(), key=_reason_key)


def _confidence(reasons: list[FullRunReason]) -> ImpactConfidence:
    codes = {reason.code for reason in reasons}
    if any(
        code
        in {
            "manifest_changed",
            "project_config_changed",
            "lockfile_changed",
            "ci_workflow_changed",
            "gate_runner_changed",
            "unknown_owner",
        }
        for code in codes
    ):
        return "low"
    if reasons:
        return "medium"
    return "high"


def build_policy_report(
    *,
    base_ref: str,
    head_ref: str,
    changed_files: list[Path],
    ownership: OwnershipReport,
) -> ImpactReport:
    """Build an advisory impact report from ownership and conservative policy."""
    high_risk_by_path: dict[str, FullRunReason] = {}
    reasons: list[FullRunReason] = []
    for raw_path in sorted({_normalize_path(path) for path in changed_files}):
        reason = _high_risk_reason(raw_path)
        if reason is not None:
            high_risk_by_path[raw_path] = reason
            reasons.append(reason)

    report_files: list[ChangedFileImpact] = []
    for item in ownership.files:
        high_risk_reason = high_risk_by_path.get(item.path)
        item_reasons = list(item.reasons)
        if high_risk_reason is not None:
            item_reasons.append(high_risk_reason.code)
        report_files.append(
            item.model_copy(
                update={
                    "category": classify_file_category(item.path),
                    "high_risk": high_risk_reason is not None,
                    "reasons": sorted(set(item_reasons)),
                }
            )
        )
        if item.owner_app is None and high_risk_reason is None:
            reasons.append(
                FullRunReason(
                    code="unknown_owner",
                    message="Changed file is outside known manifest app ownership; run broader validation.",
                    paths=[item.path],
                )
            )
        if item.owner_app in SHARED_APP_NAMES:
            reasons.append(
                FullRunReason(
                    code="shared_package_changed",
                    message="Shared package changes can affect downstream apps; run broader validation.",
                    paths=[item.path],
                )
            )

    full_run_reasons = _merge_reasons(reasons)
    return ImpactReport(
        base_ref=base_ref,
        head_ref=head_ref,
        changed_files=sorted(report_files, key=lambda item: item.path),
        affected_apps=ownership.affected_apps,
        full_run_reasons=full_run_reasons,
        confidence=_confidence(full_run_reasons),
    )

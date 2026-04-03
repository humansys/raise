"""Diagnostic report generation and email submission."""

from __future__ import annotations

import importlib.util
import platform
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.doctor.models import CheckResult, CheckStatus

SUPPORT_EMAIL = "support@raise.humansys.ai"


def _str_list() -> list[str]:
    return []


@dataclass
class DiagnosticReport:
    """Non-sensitive diagnostic snapshot."""

    timestamp: str
    rai_version: str
    python_version: str
    os_info: str
    check_results: list[CheckResult]
    raise_structure: list[str] = field(default_factory=_str_list)
    installed_extras: list[str] = field(default_factory=_str_list)


def generate_report(results: list[CheckResult], working_dir: Path) -> DiagnosticReport:
    """Collect non-sensitive data into report."""
    # Get rai version
    try:
        from importlib.metadata import version

        rai_ver = version("raise-cli")
    except Exception:  # noqa: BLE001
        rai_ver = "unknown"

    # Collect .raise/ file names (not contents)
    raise_dir = working_dir / ".raise"
    structure: list[str] = []
    if raise_dir.exists():
        for p in sorted(raise_dir.rglob("*")):
            if p.is_file():
                structure.append(str(p.relative_to(working_dir)))

    # Detect installed extras via find_spec (no actual import)
    extras: list[str] = []
    for pkg in ("mcp", "httpx"):
        if importlib.util.find_spec(pkg) is not None:
            extras.append(pkg)

    return DiagnosticReport(
        timestamp=datetime.now(UTC).isoformat(),
        rai_version=rai_ver,
        python_version=platform.python_version(),
        os_info=f"{platform.system()} {platform.release()} ({platform.machine()})",
        check_results=results,
        raise_structure=structure[:50],  # cap at 50 files
        installed_extras=extras,
    )


def report_to_markdown(report: DiagnosticReport) -> str:
    """Render report as markdown."""
    extras_str = (
        ", ".join(report.installed_extras) if report.installed_extras else "none"
    )
    lines = [
        "# rai doctor report",
        "",
        f"**Timestamp:** {report.timestamp}",
        f"**raise-cli:** {report.rai_version}",
        f"**Python:** {report.python_version}",
        f"**OS:** {report.os_info}",
        f"**Extras:** {extras_str}",
        "",
        "## Check Results",
        "",
    ]
    for r in report.check_results:
        icon = {"pass": "OK", "warn": "!!", "error": "XX"}[r.status.value]
        lines.append(f"- [{icon}] {r.category}: {r.message}")
        if r.fix_hint:
            lines.append(f"  - hint: {r.fix_hint}")

    if report.raise_structure:
        lines.extend(["", "## .raise/ structure", ""])
        for path in report.raise_structure:
            lines.append(f"- {path}")

    return "\n".join(lines)


def save_report(report: DiagnosticReport, working_dir: Path) -> Path:
    """Save report to .raise/rai/personal/report-{date}.md. Returns path."""
    personal_dir = working_dir / ".raise" / "rai" / "personal"
    personal_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    path = personal_dir / f"report-{date_str}.md"
    path.write_text(report_to_markdown(report))
    return path


def open_mailto(report: DiagnosticReport, to: str = SUPPORT_EMAIL) -> bool:
    """Open default email client via mailto: URI. Returns True if opened."""
    md = report_to_markdown(report)

    # Count issues for subject
    warns = sum(1 for r in report.check_results if r.status == CheckStatus.WARN)
    errors = sum(1 for r in report.check_results if r.status == CheckStatus.ERROR)
    parts: list[str] = []
    if errors:
        parts.append(f"{errors} error{'s' if errors > 1 else ''}")
    if warns:
        parts.append(f"{warns} warning{'s' if warns > 1 else ''}")
    issue_summary = ", ".join(parts) if parts else "all clear"

    subject = f"[rai-doctor] {report.rai_version} — {issue_summary}"

    # Truncate body for mailto (most clients cap at ~2000 chars in URL)
    body = md[:1800]
    if len(md) > 1800:
        body += "\n\n(truncated — full report in local file)"

    mailto_url = (
        f"mailto:{to}"
        f"?subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )

    try:
        return webbrowser.open(mailto_url)
    except Exception:  # noqa: BLE001
        return False

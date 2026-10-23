"""Instructions sync check — detect drift between generated and on-disk files (RAISE-16300).

Compares the output of InstructionsGenerator against existing instruction files
for each agent type listed in the project manifest. Used by pre-commit gate and
``rai init --check-instructions``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from raise_cli.config.agents import BUILTIN_AGENTS
from raise_cli.onboarding.detection import detect_project_type
from raise_cli.onboarding.instructions import generate_instructions
from raise_cli.onboarding.manifest import load_manifest


@dataclass(frozen=True)
class InstructionsDrift:
    """A single drifted instructions file."""

    agent_type: str
    instructions_file: str
    reason: Literal["missing", "content_differs"]


@dataclass
class InstructionsSyncResult:
    """Result of checking all configured agents' instruction files."""

    drifted: list[InstructionsDrift] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """True when no instruction files are drifted."""
        return len(self.drifted) == 0


def check_instructions_sync(project_path: Path) -> InstructionsSyncResult:
    """Check whether on-disk instruction files match the generated content.

    Only checks agents listed in the project manifest's ``agents.types``.
    Deduplicates shared files (e.g. multiple agents using AGENTS.md).
    Returns clean result for non-RaiSE projects (no .raise/ directory).
    """
    raise_dir = project_path / ".raise"
    if not raise_dir.is_dir():
        return InstructionsSyncResult()

    manifest = load_manifest(project_path)
    if manifest is None:
        return InstructionsSyncResult()

    agent_types: list[str] = manifest.agents.types
    if not agent_types:
        return InstructionsSyncResult()

    detection = detect_project_type(project_path)
    expected_content = generate_instructions(
        manifest.project.name or project_path.name,
        detection,
        project_path=project_path,
    )

    result = InstructionsSyncResult()
    checked_files: set[str] = set()

    for agent_type_str in agent_types:
        if agent_type_str not in BUILTIN_AGENTS:
            continue
        config = BUILTIN_AGENTS[agent_type_str]  # type: ignore[index]
        ifile = config.instructions_file

        if ifile in checked_files:
            continue
        checked_files.add(ifile)

        instructions_path = project_path / ifile
        if not instructions_path.exists():
            result.drifted.append(
                InstructionsDrift(
                    agent_type=agent_type_str,
                    instructions_file=ifile,
                    reason="missing",
                )
            )
            continue

        on_disk = instructions_path.read_text(encoding="utf-8")
        if on_disk.strip() != expected_content.strip():
            result.drifted.append(
                InstructionsDrift(
                    agent_type=agent_type_str,
                    instructions_file=ifile,
                    reason="content_differs",
                )
            )

    return result

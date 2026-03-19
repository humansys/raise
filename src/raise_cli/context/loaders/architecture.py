"""Architecture loader for the context graph.

Loads architecture and module nodes from governance/architecture/
YAML documents.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.compat import portable_path
from raise_core.graph.models import GraphNode


def load_architecture(project_root: Path) -> list[GraphNode]:
    """Load architecture nodes from YAML documentation.

    Scans both governance/architecture/*.yaml (architecture docs) and
    governance/architecture/modules/*.yaml (module docs). Type-dispatches
    by ``type`` field.

    Args:
        project_root: Root directory for the project.

    Returns:
        List of GraphNode for architecture and module concepts.
    """
    arch_dir = project_root / "governance" / "architecture"
    if not arch_dir.exists():
        return []

    nodes: list[GraphNode] = []

    for ext in ("*.yaml", "*.md"):
        for yaml_file in sorted(arch_dir.glob(ext)):
            node = _parse_architecture_doc(yaml_file, project_root)
            if node:
                nodes.append(node)

    modules_dir = arch_dir / "modules"
    if modules_dir.exists():
        for yaml_file in sorted(modules_dir.glob("*.yaml")):
            node = _parse_architecture_doc(yaml_file, project_root)
            if node:
                nodes.append(node)

    return nodes


def _parse_architecture_doc(file_path: Path, project_root: Path) -> GraphNode | None:
    """Parse a YAML architecture doc into a GraphNode.

    Dispatches by ``type`` field to produce the appropriate
    node type (module or architecture).

    Args:
        file_path: Path to the YAML file.
        project_root: Root directory for portable path computation.

    Returns:
        GraphNode if valid YAML found, None otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        # Handle .md files with YAML frontmatter
        if file_path.suffix == ".md" and content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end == -1:
                return None
            content = content[4:end]
        raw: Any = yaml.safe_load(content)
    except (OSError, yaml.YAMLError):
        return None

    if not isinstance(raw, dict):
        return None
    data = cast("dict[str, Any]", raw)

    try:
        source_file = portable_path(file_path, project_root)
    except ValueError:
        source_file = str(file_path)

    doc_type = data.get("type", "")

    if doc_type == "module":
        return _parse_module_doc(data, source_file)
    if doc_type == "architecture_context":
        return _parse_architecture_context(data, source_file)
    if doc_type == "architecture_design":
        return _parse_architecture_design(data, source_file)
    if doc_type == "architecture_domain_model":
        return _parse_architecture_domain_model(data, source_file)
    return None


def _parse_module_doc(
    frontmatter: dict[str, Any], source_file: str
) -> GraphNode | None:
    """Parse a module-type architecture doc.

    Args:
        frontmatter: Parsed YAML dict.
        source_file: Relative path to the source file.

    Returns:
        GraphNode with type "module", or None if invalid.
    """
    name = frontmatter.get("name", "")
    if not name:
        return None

    metadata: dict[str, Any] = {}
    for key in (
        "depends_on",
        "depended_by",
        "entry_points",
        "public_api",
        "components",
        "constraints",
        "status",
    ):
        if key in frontmatter:
            metadata[key] = frontmatter[key]

    return GraphNode(
        id=f"mod-{name}",
        type="module",
        content=frontmatter.get("purpose", ""),
        source_file=source_file,
        created=frontmatter.get("last_validated", datetime.now(tz=UTC).isoformat()),
        metadata=metadata,
    )


def _parse_architecture_context(
    frontmatter: dict[str, Any], source_file: str
) -> GraphNode:
    """Parse an architecture_context doc (system-context.yaml).

    Synthesizes content from tech stack and external dependencies.

    Args:
        frontmatter: Parsed YAML dict.
        source_file: Relative path to the source file.

    Returns:
        GraphNode with type "architecture".
    """
    tech_stack: dict[str, str] = frontmatter.get("tech_stack", {})
    tech_parts = [f"{k}: {v}" for k, v in tech_stack.items()]
    tech_summary = ", ".join(tech_parts) if tech_parts else "No tech stack defined"

    ext_deps: list[str] = frontmatter.get("external_dependencies", [])
    deps_summary = ", ".join(ext_deps) if ext_deps else "none"

    content = f"System context: {tech_summary}. External dependencies: {deps_summary}."

    metadata: dict[str, Any] = {"arch_type": "architecture_context"}
    for key in (
        "tech_stack",
        "external_dependencies",
        "users",
        "governed_by",
        "project",
        "version",
        "status",
    ):
        if key in frontmatter:
            metadata[key] = frontmatter[key]

    return GraphNode(
        id="arch-context",
        type="architecture",
        content=content,
        source_file=source_file,
        created=datetime.now(tz=UTC).isoformat(),
        metadata=metadata,
    )


def _parse_architecture_design(
    frontmatter: dict[str, Any], source_file: str
) -> GraphNode:
    """Parse an architecture_design doc (system-design.yaml).

    Synthesizes content from layers and their module assignments.

    Args:
        frontmatter: Parsed YAML dict.
        source_file: Relative path to the source file.

    Returns:
        GraphNode with type "architecture".
    """
    raw_layers: list[Any] = frontmatter.get("layers", [])
    layers: list[dict[str, Any]] = [
        layer for layer in raw_layers if isinstance(layer, dict)
    ]
    layer_parts: list[str] = []
    for layer in layers:
        name = layer.get("name", "unknown")
        modules: list[str] = layer.get("modules", [])
        layer_parts.append(f"{name}: {', '.join(modules)}")

    layers_summary = ". ".join(layer_parts) if layer_parts else "No layers defined"
    layer_names = ", ".join(layer.get("name", "") for layer in layers)
    content = f"System design: {len(layers)} layers ({layer_names}). {layers_summary}."

    metadata: dict[str, Any] = {"arch_type": "architecture_design"}
    for key in (
        "layers",
        "architectural_decisions",
        "distribution",
        "guardrails_reference",
        "constitution_reference",
        "project",
        "status",
    ):
        if key in frontmatter:
            metadata[key] = frontmatter[key]

    return GraphNode(
        id="arch-design",
        type="architecture",
        content=content,
        source_file=source_file,
        created=datetime.now(tz=UTC).isoformat(),
        metadata=metadata,
    )


def _parse_architecture_domain_model(
    frontmatter: dict[str, Any], source_file: str
) -> GraphNode:
    """Parse an architecture_domain_model doc (domain-model.yaml).

    Synthesizes content from bounded contexts and shared kernel.

    Args:
        frontmatter: Parsed YAML dict.
        source_file: Relative path to the source file.

    Returns:
        GraphNode with type "architecture".
    """
    bcs: list[Any] = frontmatter.get("bounded_contexts", [])
    bc_names: list[str] = [
        bc.get("name", "unknown") if isinstance(bc, dict) else str(bc) for bc in bcs
    ]
    bc_summary = ", ".join(bc_names) if bc_names else "none defined"

    shared: dict[str, Any] = frontmatter.get("shared_kernel", {})
    shared_modules: list[str] = shared.get("modules", [])
    shared_summary = ", ".join(shared_modules) if shared_modules else "none"

    content = (
        f"Domain model: {len(bcs)} bounded contexts — {bc_summary}. "
        f"Shared kernel: {shared_summary}."
    )

    metadata: dict[str, Any] = {"arch_type": "architecture_domain_model"}
    for key in (
        "bounded_contexts",
        "shared_kernel",
        "application_layer",
        "distribution",
        "project",
        "status",
    ):
        if key in frontmatter:
            metadata[key] = frontmatter[key]

    return GraphNode(
        id="arch-domain-model",
        type="architecture",
        content=content,
        source_file=source_file,
        created=datetime.now(tz=UTC).isoformat(),
        metadata=metadata,
    )

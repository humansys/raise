"""Cartridge extraction pipeline.

Reads extractors/config.yaml, resolves corpus paths, delegates to
registered extractors, and writes instances as GraphNode JSON.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Protocol

import yaml
from pydantic import BaseModel, Field, ValidationError

from raise_core.cartridges.hygiene import HygieneReport, apply_hygiene
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)


class RelationshipType(BaseModel):
    """A single relationship type allowed in a cartridge schema."""

    type: str
    description: str = ""


class RelationshipSchema(BaseModel):
    """Schema defining allowed relationship types for a cartridge."""

    relationship_types: list[RelationshipType] = Field(default_factory=list)


class ExtractorSpec(BaseModel):
    """Single extractor entry from extractors/config.yaml."""

    name: str
    type: str
    sources: list[str]
    node_type: str = "knowledge"
    schema_ref: str | None = None
    relationship_mode: Literal["none", "guided", "manual"] = "none"
    domain_context: str = ""


class ExtractorConfigError(Exception):
    """A config.yaml file exists but has invalid YAML syntax (RAISE-16153)."""

    def __init__(self, config_path: Path, reason: str) -> None:
        self.config_path = config_path
        self.reason = reason
        super().__init__(f"Invalid extractor config {config_path}: {reason}")


class ExtractorConfig(BaseModel):
    """Configuration for cartridge extraction pipeline."""

    extractors: list[ExtractorSpec] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> ExtractorConfig:
        """Load config from YAML file. Returns empty config if file missing."""
        if not path.exists():
            return cls()
        try:
            raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ExtractorConfigError(path, f"YAML syntax error: {exc}") from exc
        if not raw or not isinstance(raw, dict):
            return cls()
        return cls.model_validate(raw)


class CartridgeExtractionResult(BaseModel):
    """Result of cartridge extraction pipeline."""

    nodes: list[GraphNode] = Field(default_factory=list)
    node_count: int = 0
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    hygiene: HygieneReport = Field(default_factory=HygieneReport)


class CartridgeExtractor(Protocol):
    """Protocol for cartridge extractors."""

    def extract(  # noqa: D102
        self,
        paths: list[Path],
        node_type: str,
        cartridge_name: str,
        *,
        schema: RelationshipSchema | None = None,
        domain_context: str = "",
    ) -> list[GraphNode]: ...


class YAMLExtractor:
    """Built-in extractor for structured YAML files."""

    def extract(  # noqa: D102
        self,
        paths: list[Path],
        node_type: str,
        cartridge_name: str,
        *,
        schema: RelationshipSchema | None = None,
        domain_context: str = "",
    ) -> list[GraphNode]:
        nodes: list[GraphNode] = []
        now = datetime.now(tz=UTC).isoformat()
        for path in paths:
            nodes.extend(self._extract_file(path, node_type, cartridge_name, now))
        if schema is not None:
            for node in nodes:
                filter_relationships(node, schema)
        return nodes

    def _extract_file(
        self, path: Path, node_type: str, cartridge_name: str, now: str
    ) -> list[GraphNode]:
        try:
            raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Failed to parse %s", path)
            return []
        if not raw or not isinstance(raw, dict):
            return []
        return self._dict_to_nodes(raw, path, node_type, cartridge_name, now)

    def _dict_to_nodes(
        self,
        data: dict[str, Any],
        path: Path,
        node_type: str,
        cartridge_name: str,
        now: str,
    ) -> list[GraphNode]:
        nodes: list[GraphNode] = []
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        node = self._item_to_node(
                            item, key, path, node_type, cartridge_name, now
                        )
                        nodes.append(node)
            elif isinstance(value, dict):
                node = self._item_to_node(
                    {**value, "id": key}, key, path, node_type, cartridge_name, now
                )
                nodes.append(node)
        return nodes

    def _item_to_node(
        self,
        item: dict[str, Any],
        group: str,
        path: Path,
        node_type: str,
        cartridge_name: str,
        now: str,
    ) -> GraphNode:
        item_id = str(item.get("id", item.get("name", group)))
        content = str(
            item.get("description", item.get("content", json.dumps(item, default=str)))
        )
        return GraphNode(
            id=f"kc-{cartridge_name}-{item_id}",
            type=node_type,
            content=content,
            source_file=str(path),
            created=now,
            metadata={"cartridge": cartridge_name, "group": group, **item},
        )


def filter_relationships(node: GraphNode, schema: RelationshipSchema) -> None:
    """Drop relationships with types outside the schema or malformed entries.

    Modifies ``node.metadata["relationships"]`` in place. Valid entries must be
    dicts with a non-empty ``target`` string and a ``type`` present in the schema.
    """
    rels = node.metadata.get("relationships")
    if not isinstance(rels, list):
        return
    allowed = {rt.type for rt in schema.relationship_types}
    valid = [
        r
        for r in rels
        if isinstance(r, dict)
        and r.get("type") in allowed
        and isinstance(r.get("target"), str)
        and r.get("target")
    ]
    if len(valid) < len(rels):
        logger.warning(
            "Dropped %d relationships outside schema in node '%s'",
            len(rels) - len(valid),
            node.id,
        )
    node.metadata["relationships"] = valid


def _slugify(text: str) -> str:
    """Convert heading text to a URL-friendly slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")


class MarkdownExtractor:
    """Built-in extractor for markdown files — splits by ## headings."""

    def extract(  # noqa: D102
        self,
        paths: list[Path],
        node_type: str,
        cartridge_name: str,
        *,
        schema: RelationshipSchema | None = None,
        domain_context: str = "",
    ) -> list[GraphNode]:
        nodes: list[GraphNode] = []
        now = datetime.now(tz=UTC).isoformat()
        for path in paths:
            nodes.extend(self._extract_file(path, node_type, cartridge_name, now))
        return nodes

    def _extract_file(
        self, path: Path, node_type: str, cartridge_name: str, now: str
    ) -> list[GraphNode]:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            logger.warning("Failed to read %s", path)
            return []
        if not text.strip():
            return []
        sections = self._split_by_headings(text)
        nodes: list[GraphNode] = []
        for heading, content in sections:
            slug = _slugify(heading) if heading else path.stem
            nodes.append(
                GraphNode(
                    id=f"kc-{cartridge_name}-{slug}",
                    type=node_type,
                    content=content.strip(),
                    source_file=str(path),
                    created=now,
                    metadata={
                        "cartridge": cartridge_name,
                        "heading": heading or path.stem,
                    },
                )
            )
        return nodes

    @staticmethod
    def _split_by_headings(text: str) -> list[tuple[str, str]]:
        """Split markdown by ## headings. Returns (heading, content) pairs."""
        pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
        matches = list(pattern.finditer(text))
        if not matches:
            return [("", text)]
        sections: list[tuple[str, str]] = []
        pre = text[: matches[0].start()].strip()
        if pre:
            sections.append(("", pre))
        for i, match in enumerate(matches):
            heading = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end]
            sections.append((heading, content))
        return sections


def cartridge_project_root(cartridge_dir: Path) -> Path:
    """Resolve the project root a cartridge_dir is nested under.

    ``cartridge_dir`` is always three levels below the project root
    (``<project_root>/.raise/cartridges/<name>/``), so climbing three
    parents recovers it. This is the single canonical definition of that
    climb — both `resolve_sources`'s project-root fallback (RAISE-11835)
    and `raise-cli`'s `_corpus_base_dir()` delegate to it, so the "how far
    does cartridge_dir climb to reach project root" contract can't drift
    between the two packages (per this repo's "Canonical Resolver Callers"
    convention; same divergence class as RCA RAISE-7596/RAISE-8191).
    """
    return cartridge_dir.parents[2]


def resolve_sources(
    sources: list[str], base_dir: Path, *, project_root: Path | None = None
) -> list[Path]:
    """Resolve glob patterns to actual file paths.

    Tries each pattern relative to ``base_dir`` (cartridge-relative) first —
    this preserves vendored cartridges (files physically copied under
    ``<cartridge_dir>/corpus/``) and hand-authored ``../``-prefixed entries
    unchanged. Only when a pattern matches nothing under ``base_dir`` does it
    fall back to resolving against ``project_root`` (RAISE-11835): fixes
    cartridges scaffolded via `init`/`build`, which persist `sources:` globs
    verbatim as typed at the project root (RAISE-11617), without breaking
    any already-working cartridge-relative config. ``project_root`` is
    optional and omitted by default, keeping this function backward
    compatible.
    """
    resolved: list[Path] = []
    seen: set[Path] = set()
    for pattern in sources:
        matches = sorted(base_dir.glob(pattern))
        if not matches and project_root is not None:
            matches = sorted(project_root.glob(pattern))
        for match in matches:
            resolved_match = match.resolve()
            if resolved_match in seen:
                continue
            seen.add(resolved_match)
            resolved.append(match)
    return resolved


def write_instances(nodes: list[GraphNode], name: str, instances_dir: Path) -> None:
    """Write extracted nodes as JSON to instances directory."""
    if not nodes:
        return
    instances_dir.mkdir(parents=True, exist_ok=True)
    output = instances_dir / f"{name}.json"
    data = [n.model_dump(mode="json") for n in nodes]
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def generate_embeddings(
    nodes: list[GraphNode], provider: Any, instances_dir: Path
) -> list[str]:
    """Generate and persist embeddings. Returns warnings on failure."""
    try:
        from raise_core.cartridges.embedding import EmbeddingGenerator, write_embeddings

        generator = EmbeddingGenerator(provider=provider)
        embeddings = generator.generate(nodes)
        write_embeddings(embeddings, nodes, instances_dir)
    except Exception as exc:
        logger.warning("Embedding generation failed: %r", exc, exc_info=True)
        return [f"Embedding generation failed: {exc!r}"]
    return []


def read_cartridge_name(cartridge_dir: Path, *, default: str = "unknown") -> str:
    """Read the cartridge name from CARTRIDGE.yaml, falling back to *default*."""
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    if not manifest_path.exists():
        return default
    try:
        manifest_raw: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        logger.debug("Failed to read cartridge name from %s", manifest_path)
        return default
    if not isinstance(manifest_raw, dict):
        return default
    return manifest_raw.get("name", default)


def _run_extractors(
    config: ExtractorConfig,
    available: dict[str, CartridgeExtractor],
    cartridge_dir: Path,
    cartridge_name: str,
) -> tuple[list[GraphNode], list[str], list[str], list[str]]:
    """Run all configured extractors.

    Returns (nodes, spec_names, errors, warnings) where ``spec_names[i]``
    is the spec that produced ``nodes[i]``.
    """
    all_nodes: list[GraphNode] = []
    spec_names: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    for spec in config.extractors:
        extractor = available.get(spec.type)
        if extractor is None:
            warnings.append(f"No extractor registered for type '{spec.type}'")
            continue
        if spec.sources:
            paths = resolve_sources(
                spec.sources,
                cartridge_dir,
                project_root=cartridge_project_root(cartridge_dir),
            )
            if not paths:
                warnings.append(
                    f"No files matched sources {spec.sources} for "
                    f"extractor '{spec.name}'"
                )
                continue
        else:
            # RAISE-13911: an explicitly empty `sources: []` is a deliberate
            # signal that the extractor resolves its own scan root (e.g.
            # MemoryFrontmatterExtractor, which reads outside the cartridge/
            # repo tree) — not "no files matched", which would incorrectly
            # skip an extractor that never needed cartridge-relative globs.
            paths = []
        schema = None
        try:
            if spec.relationship_mode != "none":
                schema = load_relationship_schema(spec, cartridge_dir)
            nodes = _run_extractor(extractor, paths, spec, cartridge_name, schema)
            all_nodes.extend(nodes)
            spec_names.extend([spec.name] * len(nodes))
        except Exception as exc:
            errors.append(f"Extractor '{spec.name}' failed: {exc}")

    return all_nodes, spec_names, errors, warnings


def extract_cartridge(
    cartridge_dir: Path,
    *,
    extractors: dict[str, CartridgeExtractor] | None = None,
    embedding_provider: Any | None = None,
    dry_run: bool = False,
) -> CartridgeExtractionResult:
    """Run extraction pipeline on a cartridge.

    Reads extractors/config.yaml, resolves corpus paths, delegates to
    registered extractors, applies cross-spec hygiene (ID dedup, edge
    type normalization), and writes instances to instances/.
    """
    config_path = cartridge_dir / "extractors" / "config.yaml"
    config = ExtractorConfig.from_yaml(config_path)
    if not config.extractors:
        return CartridgeExtractionResult()

    cartridge_name = read_cartridge_name(cartridge_dir)
    all_nodes, spec_names, errors, warnings = _run_extractors(
        config, extractors or {}, cartridge_dir, cartridge_name
    )

    # Hygiene runs cross-spec: ID collisions span extractor specs, so dedup
    # must see the full node set before instances are partitioned per spec.
    hygiene = apply_hygiene(all_nodes, id_prefix=f"kc-{cartridge_name}-")
    clean_nodes = hygiene.nodes

    if not dry_run:
        by_spec: dict[str, list[GraphNode]] = {}
        for node, source_index in zip(clean_nodes, hygiene.kept_indices, strict=True):
            by_spec.setdefault(spec_names[source_index], []).append(node)
        for spec_name, spec_nodes in by_spec.items():
            write_instances(spec_nodes, spec_name, cartridge_dir / "instances")

    if clean_nodes and embedding_provider is not None and not dry_run:
        warnings.extend(
            generate_embeddings(
                clean_nodes, embedding_provider, cartridge_dir / "instances"
            )
        )

    return CartridgeExtractionResult(
        nodes=clean_nodes,
        node_count=len(clean_nodes),
        errors=errors,
        warnings=warnings,
        hygiene=hygiene.report,
    )


def _run_extractor(
    extractor: CartridgeExtractor,
    paths: list[Path],
    spec: ExtractorSpec,
    cartridge_name: str,
    schema: RelationshipSchema | None,
) -> list[GraphNode]:
    """Invoke an extractor, passing schema and domain_context when available.

    Keeps legacy extractors without these kwargs working for the
    default path by only passing them when non-default.
    """
    kwargs: dict[str, Any] = {}
    if schema is not None:
        kwargs["schema"] = schema
    if spec.domain_context:
        kwargs["domain_context"] = spec.domain_context
    if kwargs:
        return extractor.extract(paths, spec.node_type, cartridge_name, **kwargs)
    return extractor.extract(paths, spec.node_type, cartridge_name)


class RelationshipSchemaError(Exception):
    """A declared relationship schema file failed to load or validate.

    Raised — never laundered into ``None`` — when ``schema_ref`` points at a
    file that has content but is malformed (bad YAML syntax, a non-mapping
    top-level document, or a shape that doesn't match
    ``RelationshipSchema``). ``None`` is reserved for "no schema declared"
    (no ``schema_ref``), "file not found" and "file empty" (not yet
    created/filled in); all are legitimate states that callers already treat
    as "nothing to constrain against". A malformed file is a configuration
    error, not an empty schema, and conflating the two silently disables the
    entire relate pass while still exiting 0 (RAISE-15999).
    """

    def __init__(self, schema_path: Path, reason: str) -> None:
        self.schema_path = schema_path
        self.reason = reason
        super().__init__(f"Invalid relationship schema {schema_path}: {reason}")


def load_relationship_schema(
    spec: ExtractorSpec, cartridge_dir: Path
) -> RelationshipSchema | None:
    """Load a relationship schema from the cartridge directory.

    Returns None if schema_ref is not set, the file doesn't exist, or the
    file is empty — all three mean "nothing declared yet" and callers
    already handle that as such. Raises RelationshipSchemaError if the file
    has content but is malformed (bad YAML syntax, a non-mapping top-level
    document, or a shape that doesn't match RelationshipSchema): a declared,
    broken schema is a configuration error and must fail loudly rather than
    be treated as an empty-but-present schema (RAISE-15999).
    """
    if spec.schema_ref is None:
        return None
    schema_path = cartridge_dir / spec.schema_ref
    if not schema_path.exists():
        logger.warning("Relationship schema not found: %s", schema_path)
        return None
    try:
        raw: Any = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RelationshipSchemaError(
            schema_path, f"invalid YAML syntax: {exc}"
        ) from exc
    if not raw:
        logger.warning("Empty relationship schema: %s", schema_path)
        return None
    if not isinstance(raw, dict):
        raise RelationshipSchemaError(
            schema_path,
            f"expected a mapping at the top level, got {type(raw).__name__}",
        )
    try:
        return RelationshipSchema.model_validate(raw)
    except ValidationError as exc:
        raise RelationshipSchemaError(schema_path, f"invalid shape: {exc}") from exc


__all__ = [
    "CartridgeExtractionResult",
    "CartridgeExtractor",
    "ExtractorConfig",
    "ExtractorConfigError",
    "ExtractorSpec",
    "MarkdownExtractor",
    "RelationshipSchema",
    "RelationshipSchemaError",
    "RelationshipType",
    "YAMLExtractor",
    "cartridge_project_root",
    "extract_cartridge",
    "filter_relationships",
    "generate_embeddings",
    "load_relationship_schema",
    "read_cartridge_name",
    "resolve_sources",
    "write_instances",
]

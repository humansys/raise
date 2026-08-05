"""Cartridge packing — produce .cartridge.tar.gz with SHA-256 checksum."""

from __future__ import annotations

import hashlib
import shutil
import tarfile
from pathlib import Path

import yaml


def pack_cartridge(cartridge_dir: Path, output_dir: Path) -> Path:
    """Pack a cartridge directory into a .cartridge.tar.gz archive.

    External corpus files (referenced via relative paths that escape the
    cartridge directory) are resolved, copied into a ``corpus/`` subdirectory
    inside the archive, and the manifest is rewritten so the packed cartridge
    is self-contained.

    Returns the path to the created archive.
    """
    name = cartridge_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{name}.cartridge.tar.gz"

    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    manifest = (
        yaml.safe_load(manifest_path.read_text()) if manifest_path.exists() else {}
    )
    corpus_patterns: list[str] = manifest.get("corpus", [])

    external, rewritten = _resolve_external_corpus(corpus_patterns, cartridge_dir)

    staging_dir: Path | None = None
    try:
        if external:
            staging_dir = output_dir / f".pack-staging-{name}"
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            shutil.copytree(cartridge_dir, staging_dir, dirs_exist_ok=True)

            corpus_dest = staging_dir / "corpus"
            for rel_path, src_path in external.items():
                dest = corpus_dest / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest)

            packed_manifest = dict(manifest)
            packed_manifest["corpus"] = rewritten
            (staging_dir / "CARTRIDGE.yaml").write_text(
                yaml.dump(packed_manifest, default_flow_style=False, sort_keys=False)
            )
            pack_source = staging_dir
        else:
            pack_source = cartridge_dir

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(pack_source), arcname=name)
    finally:
        if staging_dir and staging_dir.exists():
            shutil.rmtree(staging_dir)

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path = archive_path.parent / f"{archive_path.name}.sha256"
    checksum_path.write_text(f"{digest}  {archive_path.name}\n")

    return archive_path


def _resolve_external_corpus(
    patterns: list[str], cartridge_dir: Path
) -> tuple[dict[str, Path], list[str]]:
    """Separate external corpus files from internal ones.

    Returns:
        external: mapping of {relative_dest_path: absolute_source_path}
        rewritten: new corpus list with external paths replaced by corpus/ paths
    """
    external: dict[str, Path] = {}
    rewritten: list[str] = []

    for pattern in patterns:
        resolved = sorted(cartridge_dir.glob(pattern))
        is_external = pattern.startswith("..") or any(
            not _is_inside(p.resolve(), cartridge_dir.resolve()) for p in resolved
        )

        if is_external and resolved:
            common = _find_common_prefix(resolved, cartridge_dir, pattern)
            for src in resolved:
                rel = src.resolve().relative_to(common)
                external[str(rel)] = src.resolve()
            rewritten.append(f"corpus/{_pattern_suffix(pattern)}")
        else:
            rewritten.append(pattern)

    return external, rewritten


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _find_common_prefix(paths: list[Path], cartridge_dir: Path, pattern: str) -> Path:
    """Find the common ancestor of resolved external paths."""
    parts = pattern.split("/")
    non_dots = [p for p in parts if p != ".."]
    if non_dots:
        first_dir = non_dots[0].replace("*", "")
        for p in paths:
            resolved = p.resolve()
            for parent in resolved.parents:
                if parent.name == first_dir:
                    return parent
    resolved_parents = [p.resolve().parent for p in paths]
    if resolved_parents:
        common = resolved_parents[0]
        for rp in resolved_parents[1:]:
            while not str(rp).startswith(str(common)):
                common = common.parent
        return common
    return cartridge_dir


def _pattern_suffix(pattern: str) -> str:
    """Extract the non-relative portion of a glob pattern."""
    parts = pattern.split("/")
    non_dots = [p for p in parts if p != ".."]
    return "/".join(non_dots) if non_dots else "*"

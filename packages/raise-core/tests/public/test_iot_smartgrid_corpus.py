"""Corpus qualification for the IoT Smart Grid fixture (RAISE-17099 T3).

Loads ``fixtures/iot-smartgrid-corpus/expected.json`` once and asserts the
fixture contract, the byte-exact encoding variants, the absence of secrets,
and that ``scan_directory``/``load_symbols`` recover the expected SQL
objects, dependencies, C# symbols, and the collision-pair fix (RAISE-17096).

This module runs on the public mirror (``ci-raise-core.yml``) and is the
file the ``windows-acceptance`` AC5 step in ``build.yml`` mirrors with a
pwsh JSON assertion block (RAISE-17099 T2) — the two must stay in sync via
``expected.json``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from raise_core.discovery.scanner import scan_directory
from raise_core.discovery.symbols import load_symbols

FIXTURE_DIR = (Path(__file__).parent / "fixtures" / "iot-smartgrid-corpus").resolve()
EXPECTED: dict[str, Any] = json.loads(
    (FIXTURE_DIR / "expected.json").read_text(encoding="utf-8")
)

# Text files scanned for secrets/private-URL patterns (mirror gates).
_TEXT_SUFFIXES = {".sql", ".cs", ".csproj", ".sqlproj", ".md", ".json"}
_SECRET_PATTERNS = (
    re.compile(r"password\s*=", re.IGNORECASE),
    re.compile(r"pwd\s*=", re.IGNORECASE),
    re.compile(r"data source\s*=", re.IGNORECASE),
    re.compile(r"humansys\.ai", re.IGNORECASE),
    re.compile(r"gitlab\.com/humansys-demos", re.IGNORECASE),
)


def _tail(name: str) -> str:
    """Normalize ``dbo.X`` / ``[dbo].[X]`` / ``X`` to the bare object name ``X``."""
    stripped = name.replace("[", "").replace("]", "")
    return stripped.rsplit(".", 1)[-1]


def _read_fixture_bytes(rel: str) -> bytes:
    return (FIXTURE_DIR / rel).read_bytes()


@pytest.fixture(scope="module")
def scan_result() -> Any:
    return scan_directory(FIXTURE_DIR)


@pytest.fixture(scope="module")
def graph_result() -> tuple[list[Any], list[Any]]:
    nodes, edges, _report = load_symbols(FIXTURE_DIR)
    return nodes, edges


def test_fixture_contract_files_present() -> None:
    """Every file referenced in expected.json exists; counts match on disk."""
    for entry in EXPECTED["sql_objects"]:
        assert (FIXTURE_DIR / entry["file"]).is_file(), entry["file"]
    for entry in EXPECTED["csharp_symbols"]:
        assert (FIXTURE_DIR / entry["file"]).is_file(), entry["file"]
    for rel in EXPECTED["encodings"]:
        assert (FIXTURE_DIR / rel).is_file(), rel

    cs_files = list(FIXTURE_DIR.rglob("*.cs"))
    sql_files = list(FIXTURE_DIR.rglob("*.sql"))
    sqlproj_files = list(FIXTURE_DIR.rglob("*.sqlproj"))
    assert len(cs_files) == EXPECTED["files"]["cs"]
    assert len(sql_files) == EXPECTED["files"]["sql"]
    assert len(sqlproj_files) == EXPECTED["files"]["sqlproj"]


def test_fixture_encodings_are_byte_exact() -> None:
    """BOM/UTF-16LE/CRLF bytes survive checkout untouched (.gitattributes '* -text')."""
    bom_file = _read_fixture_bytes("Database/Tables/MeterMeasurementHistory.sql")
    assert bom_file.startswith(b"\xef\xbb\xbf"), "UTF-8 BOM missing"

    utf16_file = _read_fixture_bytes("Database/Procedures/InsertMeterMeasurement.sql")
    assert utf16_file.startswith(b"\xff\xfe"), "UTF-16LE BOM missing"

    crlf_file = _read_fixture_bytes("Database/Triggers/trMeterMeasurementArchive.sql")
    assert b"\r\n" in crlf_file, "CRLF line endings missing"

    # Plain UTF-8 files must NOT carry a BOM (guards against editor/git normalization).
    plain_file = _read_fixture_bytes("Database/Tables/MeterMeasurement.sql")
    assert not plain_file.startswith(b"\xef\xbb\xbf")
    assert not plain_file.startswith(b"\xff\xfe")


def test_fixture_has_no_secrets_or_private_urls() -> None:
    """No credentials, connection strings, or private URLs (mirror gitleaks/forbidden-content gates)."""
    for path in FIXTURE_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = path.read_bytes().decode("utf-16")
        for pattern in _SECRET_PATTERNS:
            assert not pattern.search(text), (
                f"{path.relative_to(FIXTURE_DIR)} matched {pattern.pattern}"
            )


def test_scan_recovers_all_sql_objects(scan_result: Any) -> None:
    result = scan_result
    scanned = {
        (_tail(s.name), s.kind) for s in result.symbols if s.file.endswith(".sql")
    }
    expected_objects = {
        (entry["object"], entry["kind"]) for entry in EXPECTED["sql_objects"]
    }
    assert expected_objects <= scanned

    expected_total = sum(1 for p in FIXTURE_DIR.rglob("*") if p.is_file())
    assert result.files_found == expected_total
    assert result.files_found >= result.files_scanned + len(result.errors)
    assert result.errors == []


def test_sqlproj_counted_zero_symbols(scan_result: Any) -> None:
    result = scan_result
    assert not any(s.file.endswith(".sqlproj") for s in result.symbols)
    sqlproj_files = list(FIXTURE_DIR.rglob("*.sqlproj"))
    assert len(sqlproj_files) == EXPECTED["files"]["sqlproj"] == 1
    assert any(".sqlproj" in d for d in result.diagnostics)


def test_canonical_spike_subset(scan_result: Any) -> None:
    """The spike's original canonical 6 objects / 5 deps remain reproducible."""
    result = scan_result
    canonical = EXPECTED["canonical_subset"]
    scanned_names = {_tail(s.name) for s in result.symbols if s.file.endswith(".sql")}
    assert set(canonical["objects"]) <= scanned_names

    by_name = {_tail(s.name): s for s in result.symbols if s.file.endswith(".sql")}
    dep_count = 0
    for entry in EXPECTED["sql_dependencies"]:
        source_sym = by_name.get(entry["source"])
        if source_sym is None:
            continue
        deps = {_tail(d) for d in source_sym.depends_on}
        if (
            entry["target"] in deps
            and entry["source"] in canonical["objects"]
            and entry["target"] in canonical["objects"]
        ):
            dep_count += 1
    assert dep_count >= canonical["dependency_count"]


def test_sql_dependencies(scan_result: Any) -> None:
    result = scan_result
    by_name = {_tail(s.name): s for s in result.symbols if s.file.endswith(".sql")}

    for entry in EXPECTED["sql_dependencies"]:
        source_sym = by_name[entry["source"]]
        deps = {_tail(d) for d in source_sym.depends_on}
        assert entry["target"] in deps, (
            f"{entry['source']} missing dep {entry['target']}"
        )

    # Ephemeral @batch/table-variable references must never appear as a dependency.
    for sym in by_name.values():
        assert "batch" not in {_tail(d).lower() for d in sym.depends_on}

    assert len(result.unresolved_references) >= EXPECTED["sql_unresolved_min"]
    unresolved_tails = {_tail(r) for r in result.unresolved_references}
    expected_unresolved_tails = {_tail(n) for n in EXPECTED["sql_unresolved_names"]}
    assert expected_unresolved_tails <= unresolved_tails


def test_csharp_symbols_present(scan_result: Any) -> None:
    result = scan_result
    scanned = {(s.file, s.name, s.kind) for s in result.symbols}
    for entry in EXPECTED["csharp_symbols"]:
        assert (entry["file"], entry["name"], entry["kind"]) in scanned


def test_collision_pair_distinct_ids(graph_result: tuple[list[Any], list[Any]]) -> None:
    nodes, _edges = graph_result
    sym_nodes = [n for n in nodes if n.type == "symbol"]

    ids = [n.id for n in sym_nodes]
    assert len(ids) == len(set(ids)), "duplicate sym-* node ids"

    collision_a, collision_b = EXPECTED["collision_pair"]
    id_a = next(
        n.id for n in sym_nodes if n.metadata.get("file", "").endswith(collision_a)
    )
    id_b = next(
        n.id for n in sym_nodes if n.metadata.get("file", "").endswith(collision_b)
    )
    assert id_a != id_b
    assert "--" in id_a
    assert "--" in id_b


def test_comment_masking_excludes_fake_objects(scan_result: Any) -> None:
    """W5 review fix: objects embedded in SQL comments must not appear as symbols or deps."""
    result = scan_result
    scanned_names = {_tail(s.name) for s in result.symbols if s.file.endswith(".sql")}
    assert "FakeObject" not in scanned_names
    assert "AlsoFake" not in scanned_names

    all_deps = set()
    for s in result.symbols:
        if s.file.endswith(".sql"):
            all_deps.update(_tail(d) for d in s.depends_on)
    assert "NotReal" not in all_deps
    assert "AlsoNotReal" not in all_deps


def test_dependency_edges_emitted(graph_result: tuple[list[Any], list[Any]]) -> None:
    """Every resolved SQL dependency in expected.json becomes a references/calls edge."""
    _nodes, edges = graph_result
    dep_edges = [e for e in edges if e.type in ("references", "calls")]
    assert len(dep_edges) >= len(EXPECTED["sql_dependencies"])

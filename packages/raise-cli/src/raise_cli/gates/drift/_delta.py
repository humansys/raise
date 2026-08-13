"""Shared AST-delta primitives for drift gates + capability-overlap (D3, S14263.3).

Extracted from `gates/capability/capability_overlap.py` (S14263.2, merged
`eafdaf7e2`) — the git-show/AST "newly added public symbol" mechanism now
has 3 consumers (capability-overlap, P1 `post_refactor_orphan`, P4
`dead_public_api`), meeting the rule-of-three (design D3/AG2). Behavior is
unchanged from the S2 originals; only the names and home module changed
(`_resolve_merge_base` -> `resolve_merge_base`, `_read_at_ref` ->
`read_at_ref`, `_public_symbols` -> `public_symbols`, `_new_symbols` ->
`new_public_symbols_in_file`). `capability_overlap.py` re-points its private
aliases at these in the same PR (Task 2, AC7).

Net-new for this story (not a port): `is_entry_point` (D5 — the hardcoded
wave-1 entry-point matcher) and `collect_delta` (the shared per-changed-file
orchestration P1 and P4 both need — plan §Plan-level decisions OQ-shared).

Design D1: this is AST-delta via `git show <ref>:<path>` + stdlib `ast`, NOT
`context.diff.diff_graphs()` — see the story design for why (diff_graphs()
needs a second materialized graph no environment has).

Design D4/Correction C: an unresolvable merge-base is a GATE-LEVEL
honest-skip decision (never "all HEAD symbols new" — that would reintroduce
the RAISE-14568 touch-tax). That decision lives in each gate's `evaluate()`,
before `collect_delta` is ever called — `resolve_merge_base` here only
reports "resolvable or not"; it never decides what to do about it.
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Wave-1 hardcoded entry-point matcher (D5/OQ3): HTTP verb decorators, CLI
# command decorators, and pytest fixture decorators. Deliberately NOT a
# separate filename/regex "factory"/"conftest" heuristic — conftest.py
# fixtures are already caught by the `fixture` rule, and a bare factory-name
# heuristic risks false-negatives without an evidenced FP case driving it
# (YAGNI — extend in wave 2 if dogfooding surfaces a real miss).
_ENTRY_POINT_DECORATOR_NAMES = frozenset(
    {
        "get",
        "post",
        "put",
        "delete",
        "patch",
        "websocket",
        "route",
        "command",
        "fixture",
    }
)


@dataclass(frozen=True)
class DeltaResult:
    """Aggregated AST-delta findings across a set of changed `.py` files.

    Attributes:
        added: Newly-added top-level public symbols, as `(file_path_str, name)`
            tuples — one entry per changed file that introduces that symbol,
            NOT a flat name union across all changed files. Keying by file
            closes a cross-file name-collision false positive (AR finding,
            RAISE-14669): a bare-name-only set would let a genuinely-new
            `handler` in file A "cover" an unrelated, pre-existing, untouched
            `handler` in file B, incorrectly exempting B's stale symbol from
            being flagged. `file_path_str` is a POSIX-relative path string
            passed through `normalize_file` (strips a leading `./`). It is
            NOT safe to compare against `symbol.metadata.get("file")` as raw
            strings without that normalization: the flat-layout discovery
            fallback (`raise_core/discovery/symbols.py`) can produce a
            `./`-prefixed graph path, while git-diff-relative paths here
            never carry one — `"./foo.py" != "foo.py"` as raw strings even
            though `Path("./foo.py") == Path("foo.py")`. `_base.is_file_in_
            scope` gets that tolerance for free via `Path` equality; this
            tuple-key comparison does NOT, so both the producing side
            (`collect_delta`, below) and the consuming sides
            (`post_refactor_orphan.py`, `dead_public_api.py`) run every
            file-path component through `normalize_file` before building
            or comparing keys (QR finding, RAISE-14669 follow-up).
        entry_points: The subset of `added` (same `(file, name)` shape) whose
            HEAD AST node is decorated as an architectural entry point (D5).
            Callers exclude these from flagging even though they qualify as
            "newly added" (AC2).
    """

    added: frozenset[tuple[str, str]]
    entry_points: frozenset[tuple[str, str]]


def resolve_merge_base(base_ref: str, cwd: Path) -> str | None:
    """Return the merge-base SHA of ``base_ref`` and HEAD, or None if unresolvable.

    Covers both "``base_ref`` has no local ref" (e.g. a shallow CI clone that
    never fetched the target branch) and "``cwd`` is not inside a usable git
    checkout." Never raises — an unresolvable base ref degrades the calling
    gate's ``evaluate()`` to a noisy advisory SKIP (D4), never a silent pass
    and never a false "all new."
    """
    try:
        result = subprocess.run(
            ["git", "merge-base", base_ref, "HEAD"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None


def read_at_ref(ref: str, path: str, cwd: Path) -> str | None:
    """Return the file content at ``ref:path`` via ``git show``, or None.

    None covers a path absent at that ref (a brand-new file — legitimate;
    ``new_public_symbols_in_file`` then treats every HEAD public symbol in
    it as new) and any other git-show failure. Never raises.
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, UnicodeDecodeError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def public_symbols(tree: ast.Module) -> dict[str, ast.AST]:
    """Return top-level public `def`/`class` nodes by name.

    Only ``tree.body`` (top-level statements) are considered — nested defs
    inside functions/classes are intentionally excluded so they never count
    as new public API (avoids false positives on refactors that add a
    private helper closure). A name starting with ``_`` is not public.
    """
    symbols: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ) and not node.name.startswith("_"):
            symbols[node.name] = node
    return symbols


def new_public_symbols_in_file(
    head_src: str, base_src: str | None
) -> dict[str, ast.AST]:
    """Return HEAD's public top-level symbols not present in ``base_src``, by name.

    ``base_src=None`` treats every HEAD public symbol as new — correct for a
    brand-new file (nothing existed at the base ref, so every public symbol
    in it is new). An *unresolvable base ref* (the whole merge-base can't be
    computed) is a different, gate-level honest-skip (D4) — callers
    short-circuit before ever reaching this function in that case, never
    treating "can't tell" as "all new."
    """
    head_symbols = public_symbols(ast.parse(head_src))
    if base_src is None:
        return head_symbols
    base_symbols = public_symbols(ast.parse(base_src))
    return {
        name: node for name, node in head_symbols.items() if name not in base_symbols
    }


def is_entry_point(node: ast.AST) -> bool:
    """Return True if ``node`` is decorated as an architectural entry point.

    Wave-1 (D5/OQ3), decorator-only, hardcoded set — matches when any
    decorator (as a bare ``Name``, an ``Attribute``, or a ``Call`` wrapping
    either) resolves to one of the HTTP-verb/CLI-command/fixture names.
    The base object (``router``/``app``/``cli``/``pytest``) is NOT checked —
    wave-1 over-inclusion is an acceptable residual-FP tradeoff (never a
    false-pass) per the design's own tolerance statement.
    """
    decorator_list = getattr(node, "decorator_list", None)
    if not decorator_list:
        return False
    for decorator in decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        name: str | None = None
        if isinstance(target, ast.Attribute):
            name = target.attr
        elif isinstance(target, ast.Name):
            name = target.id
        if name in _ENTRY_POINT_DECORATOR_NAMES:
            return True
    return False


def normalize_file(path_str: str) -> str:
    """Normalize a repo-relative file-path string for cross-source key comparison.

    Strips a leading `./` (and any other POSIX-normalizable noise) via
    `Path(...).as_posix()` so a `(file, name)` key built on one side of the
    added-set comparison always matches the equivalent key built on the
    other side, regardless of which one carries a `./` prefix. Needed
    because `collect_delta`'s `path_str` (derived from git-diff-relative
    `Path` objects) never has a leading `./` in practice, while graph
    symbol file paths (`symbol.metadata.get("file")`) CAN carry one when
    produced by the flat-layout discovery fallback
    (`raise_core/discovery/symbols.py`'s `rel="."` case) — `"./foo.py" ==
    "foo.py"` is `False` as raw strings. Applied on both the producing side
    (`collect_delta`) and both consuming sides (`post_refactor_orphan.py`,
    `dead_public_api.py`) for defense-in-depth — neither side may assume
    the other is already canonical. An empty string (no file metadata) is
    passed through unchanged rather than normalized to `"."`.
    """
    if not path_str:
        return path_str
    return Path(path_str).as_posix()


def bare_symbol_name(raw: str) -> str:
    """Extract the bare identifier from a signature/name string.

    Bridges the graph's `signature` metadata (e.g. `"def get_user(...)"` or
    a bare mocked `"orphaned_func()"`) to the AST-delta name sets in this
    module (plain identifiers like `"get_user"`) — used ONLY for the
    delta-membership comparison, never for the identity fingerprint
    (`f"{name} [{module}]"` / `f"P4: {name} [{module}]"`), which stays
    byte-identical to pre-story output (D6/AC5).

    Shared by `post_refactor_orphan.py` and `dead_public_api.py` (previously
    duplicated byte-for-byte in both — AR finding, rule-of-three/AG2, closed
    alongside the RAISE-14669 file-qualification fix).
    """
    name = raw.split("(", 1)[0].strip()
    for prefix in ("async def ", "def ", "class "):
        if name.startswith(prefix):
            return name[len(prefix) :].strip()
    return name


def collect_delta(
    changed_files: tuple[Path, ...] | None, merge_base: str, working_dir: Path
) -> DeltaResult:
    """Aggregate newly-added public symbols + entry points across changed `.py` files.

    Mirrors `capability_overlap.py`'s per-file orchestration (read HEAD
    source from disk, `read_at_ref` the base source, `new_public_symbols_in_file`)
    but aggregates `(file, name)` pairs only (P1/P4 need file-qualified
    name-sets to filter graph symbols by, not the AST violation-formatting
    `capability_overlap` does). Keying by file (not a flat name union) is
    what prevents a newly-added symbol in one changed file from incorrectly
    "covering" a same-named, pre-existing, untouched symbol in another
    changed file (RAISE-14669). A single malformed/non-UTF-8 file degrades
    per-file (skipped), never blinds the rest of the collection — same
    philosophy as `capability_overlap`'s existing per-file guard.

    ``merge_base`` must already be resolved (never None) — the caller's
    gate-level D4 honest-skip happens before this is invoked.
    """
    added: set[tuple[str, str]] = set()
    entry_points: set[tuple[str, str]] = set()
    for rel_path in changed_files or ():
        path_str = normalize_file(rel_path.as_posix())
        if not path_str.endswith(".py"):
            continue
        abs_path = working_dir / rel_path
        if not abs_path.is_file():
            continue  # deleted in HEAD — nothing new to report
        try:
            head_src = abs_path.read_text(encoding="utf-8")
            base_src = read_at_ref(merge_base, path_str, working_dir)
            new_syms = new_public_symbols_in_file(head_src, base_src)
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for name, node in new_syms.items():
            key = (path_str, name)
            added.add(key)
            if is_entry_point(node):
                entry_points.add(key)
    return DeltaResult(added=frozenset(added), entry_points=frozenset(entry_points))

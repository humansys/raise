"""Tests for SignalScanner."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from raise_cli.context.analyzers.signals import SignalScanner


class TestSignalScannerFile:
    """Tests for single-file signal scanning."""

    def test_finds_todo_in_ts_file(self, tmp_path: Path) -> None:
        """Should find TODO marker with message."""
        f = tmp_path / "index.ts"
        f.write_text("// TODO: fix this\nexport const x = 1;\n")

        scanner = SignalScanner()
        hits = scanner.scan_file(f)

        assert len(hits) == 1
        assert hits[0].tag == "TODO"
        assert hits[0].message == "fix this"
        assert hits[0].line == 1

    def test_finds_multiple_tags(self, tmp_path: Path) -> None:
        """Should find different signal tags in one file."""
        f = tmp_path / "index.ts"
        f.write_text(
            dedent("""\
            // TODO: add tests
            const x = 1;
            // HACK: workaround for bug
            // FIXME: broken on edge case
            """)
        )

        scanner = SignalScanner()
        hits = scanner.scan_file(f)

        tags = [h.tag for h in hits]
        assert "TODO" in tags
        assert "HACK" in tags
        assert "FIXME" in tags

    def test_returns_empty_for_no_signals(self, tmp_path: Path) -> None:
        """Should return empty list when no signals found."""
        f = tmp_path / "clean.ts"
        f.write_text("export const x = 1;\n")

        scanner = SignalScanner()
        hits = scanner.scan_file(f)

        assert hits == []

    def test_finds_xxxx_and_deprecated(self, tmp_path: Path) -> None:
        """Should find XXX and DEPRECATED markers."""
        f = tmp_path / "old.ts"
        f.write_text(
            dedent("""\
            // XXX: this is fragile
            /** @deprecated use newApi instead */
            export function oldApi() {}
            """)
        )

        scanner = SignalScanner()
        hits = scanner.scan_file(f)

        tags = [h.tag for h in hits]
        assert "XXX" in tags
        assert "@deprecated" in tags

    def test_custom_tags(self, tmp_path: Path) -> None:
        """Should support custom signal tags."""
        f = tmp_path / "index.ts"
        f.write_text("// NOTE: important detail\n")

        scanner = SignalScanner(extra_tags=["NOTE"])
        hits = scanner.scan_file(f)

        assert len(hits) == 1
        assert hits[0].tag == "NOTE"

    def test_handles_tag_with_colon(self, tmp_path: Path) -> None:
        """Should extract message after tag with colon separator."""
        f = tmp_path / "index.ts"
        f.write_text("// TODO: implement retry logic\n")

        scanner = SignalScanner()
        hits = scanner.scan_file(f)

        assert hits[0].message == "implement retry logic"

    def test_handles_tag_without_colon(self, tmp_path: Path) -> None:
        """Should extract message after tag without colon."""
        f = tmp_path / "index.ts"
        f.write_text("// TODO implement retry logic\n")

        scanner = SignalScanner()
        hits = scanner.scan_file(f)

        assert hits[0].tag == "TODO"
        assert "implement retry logic" in hits[0].message


class TestSignalScannerModule:
    """Tests for module-level signal aggregation."""

    def test_aggregates_hits_from_module(self, tmp_path: Path) -> None:
        """Should aggregate signal hits from all .ts files in a module dir."""
        mod_dir = tmp_path / "commands"
        mod_dir.mkdir()
        (mod_dir / "a.ts").write_text("// TODO: first\n// TODO: second\n")
        (mod_dir / "b.ts").write_text("// HACK: workaround\n")

        scanner = SignalScanner()
        result = scanner.scan_module(mod_dir, "commands")

        assert result.module_name == "commands"
        assert result.counts.get("TODO", 0) == 2
        assert result.counts.get("HACK", 0) == 1
        assert len(result.hits) == 3

    def test_empty_module(self, tmp_path: Path) -> None:
        """Module with no signals returns zero counts."""
        mod_dir = tmp_path / "utils"
        mod_dir.mkdir()
        (mod_dir / "index.ts").write_text("export const x = 1;\n")

        scanner = SignalScanner()
        result = scanner.scan_module(mod_dir, "utils")

        assert result.counts == {}
        assert result.hits == []


class TestSignalScannerProject:
    """Tests for project-level scanning."""

    def test_scans_all_modules(self, tmp_path: Path) -> None:
        """Should scan all top-level directories under src/."""
        src = tmp_path / "src"
        for name in ["commands", "core"]:
            mod = src / name
            mod.mkdir(parents=True)
            (mod / "index.ts").write_text(f"// TODO: fix {name}\n")

        scanner = SignalScanner()
        results = scanner.scan_project(src)

        names = sorted(r.module_name for r in results)
        assert names == ["commands", "core"]
        assert all(r.counts.get("TODO", 0) == 1 for r in results)

    def test_skips_non_module_dirs(self, tmp_path: Path) -> None:
        """Should skip node_modules and hidden directories."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text("// TODO: real\n")
        nm = src / "node_modules"
        nm.mkdir(parents=True)
        (nm / "index.ts").write_text("// TODO: ignored\n")

        scanner = SignalScanner()
        results = scanner.scan_project(src)

        assert len(results) == 1
        assert results[0].module_name == "core"

# IoT Smart Grid corpus (synthetic)

Reference fixture for RAISE-17095 (Windows Brownfield Onboarding: C# + T-SQL
Discovery Preview). Every file here is written for this repository — no
customer data, no connection strings, no credentials, no private URLs. The
shape (two C# client projects sharing a `Program` type name, plus a T-SQL
database project covering all six object kinds) is modeled after the class
of MIT-style IoT Smart Grid sample projects used to validate the discovery
spike (`work/epics/e17095-tsql-discovery/evidence/`), not copied from any
proprietary source.

## Purpose

1. Exercise the C# symbol-collision fix (RAISE-17096): `ConsoleClient/Program.cs`
   and `WinFormsClient/Program.cs` both declare a top-level `Program` class,
   with no `src/` directory to disambiguate them.
2. Exercise the T-SQL regex extractor (RAISE-17097) across all six object
   kinds (TABLE, VIEW, PROCEDURE, FUNCTION, TRIGGER, TYPE), a table-valued
   parameter dependency, an `EXEC` call dependency, and one deliberately
   unresolved reference.
3. Exercise the encoding fallback chain: one file is UTF-8 with a BOM (VS
   Code default), one is UTF-16LE with a BOM (SQL Server Management Studio
   default), and one uses CRLF line endings.
4. Provide the Windows binary acceptance corpus for `windows-acceptance`
   AC5 in `.github/workflows/build.yml` (RAISE-17099).

## Directory names

Deliberately avoid `src`, `lib`, `app`, `build`, `dist`, `obj`, `vendor` —
those names participate in scanner exclusion or source-root heuristics and
would change what gets scanned.

## `expected.json`

The single contract consumed by both the pytest qualification suite
(`packages/raise-core/tests/public/test_iot_smartgrid_corpus.py`) and the
`windows-acceptance` AC5 step in `build.yml`. If you add, rename, or remove a
fixture file, update `expected.json` in the same commit — `test_
fixture_contract_files_present` enforces that every referenced file exists.

`sql_unresolved_min` / a dependency on `dbo.MeterMeasurementAudit` (a table
that is intentionally never defined) exercises the "reference that does not
resolve to any extracted object" path — `inserted`/`deleted` (trigger
pseudo-tables) are filtered as SQL noise by the extractor itself and never
reach `depends_on`, so they cannot be used to test the unresolved path.

Total file counts (`files_found` in a scan) are **not** hardcoded here —
`scan_directory` counts every non-excluded file reached by the walk
(including `README.md`, `expected.json`, `.gitattributes`, and `.csproj`
files, per the `files_found == files_scanned + len(errors) +
sum(skipped_by_extension.values())` invariant), so both the pytest test and
the AC5 step derive the expected total by listing the fixture directory at
run time instead of pinning a number that would drift with every fixture
edit.

## Regenerating

There is no codegen step — this is a hand-written synthetic corpus. Edit the
`.sql`/`.cs` files directly, keep `expected.json` in sync, and re-run:

```
uv run pytest packages/raise-core/tests/public/test_iot_smartgrid_corpus.py -v
```

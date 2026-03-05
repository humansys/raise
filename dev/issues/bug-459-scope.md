# RAISE-459 Scope

WHAT:      svgo@4.0.0 (transitive via astro@5.18.0) vulnerable to XML Entity Expansion (Billion Laughs) — CVE-2026-29074, CVSS 8.7 High
WHEN:      Any SVG processing involving user-supplied files with DOCTYPE recursive entity refs
WHERE:     docs/package-lock.json — node_modules/svgo@4.0.0 via astro@5.18.0
EXPECTED:  svgo@4.0.1+ (patched) in the lockfile
Done when: `npm ls svgo` in docs/ reports 4.0.1+, snyk test passes clean

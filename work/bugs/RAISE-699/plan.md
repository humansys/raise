# RAISE-699 — Plan

## Tasks

### T1: Update/add npm overrides in site/package.json
- h3: `>=1.15.6` → `>=1.15.9`
- rollup: add `>=4.59.0`
- ajv: add `>=8.18.0`
- devalue: add `>=5.6.4`
- lodash: add `>=4.17.23`

Verify: `npm install` succeeds in site/

Commit: `fix(RAISE-699): pin vulnerable transitive JS deps via npm overrides`

### T2: Verify with snyk monitor
Run snyk monitor on site/ and confirm 0 vulnerabilities in raise-docs snapshot.

Commit: not needed (no code change)

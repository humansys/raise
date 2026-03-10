# RAISE-511: Analysis

## Classification: XS — single causal chain, cause evident

## 5 Whys

| Step | Statement |
|------|-----------|
| Problem | Users see `pip install rai-cli` on raiseframework.ai/docs/ |
| Why 1 | The docs site source files still contain `rai-cli` in install code blocks |
| Why 2 | The `rai-cli → raise-cli` rename (story s369.5 / s463.4) updated pyproject.toml and README but did not cover the Astro docs site under `docs/src/` |
| Why 3 | The rename scope did not include an explicit search across `docs/src/` |
| Why 4 | No automated gate checks that install commands in docs match the canonical package name in pyproject.toml |
| Root cause | The rename was incomplete: `docs/src/` was out of scope or overlooked during s369.5/s463.4 |

## Countermeasure

Replace all occurrences of `rai-cli` with `raise-cli` in:
- `docs/src/content/docs/docs/getting-started.mdx`
- `docs/src/content/docs/docs/index.mdx`
- `docs/src/content/docs/es/docs/getting-started.mdx`
- `docs/src/content/docs/es/docs/index.mdx`

No logic change — purely a text correction.

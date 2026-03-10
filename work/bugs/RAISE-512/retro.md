# RAISE-512: Retrospective

## Fix verified
- Root cause addressed: dark/light theme colors moved from `:root` to `[data-theme='dark']`; `[data-theme='light']` added with only accent color override (Starlight's inverted gray scale handles the rest)
- Logo adapts to light mode via `filter: brightness(0)` on `.site-title img`
- Header border removed (`border-bottom: none`)
- Mobile search icon ghost box fixed by removing overly broad `site-search button` override
- CHANGELOG updated under [Unreleased] for 2.2.3

## Learnings
1. Starlight has a **semantic inverted gray scale**: in light mode `--sl-color-white` is dark text and `--sl-color-black` is the white background. Overriding these values breaks component color semantics.
2. Custom CSS overrides should target only what differs from Starlight defaults — not replicate the full gray scale.
3. Broad selectors like `site-search button` affect both mobile and desktop variants; scope to media queries when needed.

## Pattern emitted
PAT-DU-002 (see below)

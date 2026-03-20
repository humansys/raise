# E615: raise-pro Secure Distribution — Brief

## Hypothesis

Publishing raise-pro to a private GitLab Package Registry with per-client deploy tokens
will enable controlled distribution to paying clients without building license infrastructure,
unblocking first Pro client onboarding within days.

## Problem

raise-pro is a workspace package with no distribution mechanism. The release workflow
publishes all workspace packages (including raise-pro) to public PyPI — anyone can
`pip install raise-pro`. First Pro clients are expected by 2026-03-22 and need a way
to install the package that is:
- Access-controlled (only authorized clients)
- Simple (standard pip/uv workflow)
- Revocable (per-client tokens)

## Appetite

XS — 1-2 stories. Config and pipeline work, minimal code. Must ship in hours, not days.

## Success Metrics

1. raise-pro published to GitLab Package Registry (not public PyPI)
2. Per-client deploy tokens issued and tested
3. Client can `uv pip install raise-pro --index-url https://...` successfully
4. Release workflow no longer publishes raise-pro to public PyPI
5. Installation documented for client onboarding

## Rabbit Holes

- Don't build license validation yet — that's E616
- Don't build a portal or automation for token management — manual is fine for <5 clients
- Don't change raise-cli distribution (stays on public PyPI)

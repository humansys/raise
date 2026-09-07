---
title: Support & Lifecycle Policy
description: Which RaiSE release lines are supported, what each lifecycle stage receives, and how to get help.
tags: [support, lifecycle, releases]
---

# Support & Lifecycle Policy

## 1. Version support matrix

| Release line | Status | Receives | Sunset |
|---|---|---|---|
| 3.2.x | active | features, bug fixes, security patches | not scheduled |
| 3.1.x | bugfix-only | bug fixes, security patches | 2027-03-06 |
| < 3.1.0 | unsupported | nothing | — |

Source of truth: `.raise/manifest.yaml` `branches.release_lines[]`. For the
latest published version see
[GitHub Releases](https://github.com/humansys/raise/releases/latest).

## 2. Lifecycle stages

- **active** — the current development line. Receives new features, bug
  fixes, and security patches.
- **bugfix-only** — no longer receives new features. Receives bug fixes and
  security patches until its sunset date.
- **sunset** — receives nothing. Users on a sunset line must upgrade to a
  supported line to get fixes.

## 3. End-of-life policy

Each release line's `sunset` date is recorded in
`.raise/manifest.yaml` `branches.release_lines[]`. A line moving to
bugfix-only carries a minimum notice of one full minor release cycle before
it reaches sunset. The 3.1.0 line's sunset date, 2027-03-06, illustrates how
the date is recorded — it is not a fixed rule that every line sunsets on a
6-month cadence.

## 4. Patch cadence

Active lines receive patches when the release SOP is run; there is no fixed
release calendar. Bugfix-only lines receive patches as needed, not on a
schedule.

## 5. Deprecation notice period

When a line moves from active to bugfix-only, at least one minor release
cycle separates that announcement from the line's sunset.

## 6. Coverage hours

Support is provided on a business-hours, best-effort basis. This is an
expectation, not a service-level agreement. No response time is guaranteed.

## 7. Escalation path

1. Open a [GitHub issue](https://github.com/humansys/raise/issues) for bugs,
   questions, and feature requests.
2. For security vulnerabilities only, contact emilio@humansys.ai directly —
   do not open a public issue.

## 8. Security response

Security reports follow the process and timelines defined in
[SECURITY.md](https://github.com/humansys/raise/blob/main/SECURITY.md); this
policy does not restate them.

## 9. Support channels

[GitHub Issues](https://github.com/humansys/raise/issues) is the primary
support channel. A dedicated support channel and any refund policy are
tracked separately (RAISE-14984) and are not part of this policy.

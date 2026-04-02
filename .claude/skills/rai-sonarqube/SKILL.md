---
description: 'Run SonarQube local static analysis (SAST) following the raise-commons
  SOP. Covers daily scan, issue listing, and comparison with SonarCloud. See dev/sops/sonarqube-local.md
  for first-time setup.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: ''
  raise.frequency: on-demand
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: ''
  raise.version: 1.0.0
  raise.visibility: internal
  raise.work_cycle: utility
name: rai-sonarqube
---

# SonarQube

## Purpose

Run static analysis (SAST) locally with SonarQube Community before pushing.
Detects logic bugs, code smells, and security hotspots in the raise-commons codebase.

**Not a substitute for Snyk** — SonarQube covers code quality; Snyk covers dependency vulnerabilities.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps; verify server is up before scanning
- **Ha**: Skip server check if machine was not restarted; filter issues by type directly
- **Ri**: Combine with SonarCloud diff to triage CI failures locally

## Context

**When to use:** Before creating a bug ticket (verify the issue exists in current scan),
after a refactor (confirm complexity dropped), or when CI flags a Sonar gate.

**When to skip:** Trivial one-liner fixes. Dependency vulnerabilities → use Snyk instead.

**Inputs:** None. Runs from repo root. Requires `LOCAL_SONAR_TOKEN` in `~/.env`
and Docker running. For first-time setup see `dev/sops/sonarqube-local.md`.

## Steps

### Step 1: Start the Server

If the machine was restarted since the last scan:

```bash
docker start sonarqube
```

Verify it is ready (~30–60 seconds):

```bash
curl -s http://localhost:9000/api/system/status
# Expected: {"status":"UP",...}
```

If `LOCAL_SONAR_TOKEN` is not in the shell, load it:

```bash
source ~/.env
```

<verification>
`curl` returns `"status":"UP"`. `echo $LOCAL_SONAR_TOKEN` shows the token (not empty).
</verification>

### Step 2: Scan

From the repo root:

```bash
docker run --rm --network host \
  -e SONAR_TOKEN=$LOCAL_SONAR_TOKEN \
  -e SONAR_HOST_URL=http://localhost:9000 \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli:latest \
  -Dsonar.scm.disabled=true
```

> `-Dsonar.scm.disabled=true` is required — this repo uses git worktrees.

Scan takes ~15 seconds.

<verification>
Scanner output ends without ERROR lines. Project appears at http://localhost:9000.
</verification>

### Step 3: List Issues

```bash
# All issues
sonar list issues -p humansys-demos_raise-commons --format table

# Filter by severity
sonar list issues -p humansys-demos_raise-commons --format table --severity CRITICAL

# Filter by type
sonar list issues -p humansys-demos_raise-commons --format table --type BUG
sonar list issues -p humansys-demos_raise-commons --format table --type VULNERABILITY
```

<verification>
Table lists issues. If empty and scan completed, the codebase is clean for that filter.
</verification>

### Step 4 (optional): Compare with SonarCloud

To diff local findings against CI (SonarCloud):

```bash
# Switch to SonarCloud
sonar auth login -s https://sonarcloud.io -t $SONAR_TOKEN --org test-raise
sonar list issues -p humansys-demos_raise-commons --format table

# Return to local
sonar auth login -s http://localhost:9000 -t $LOCAL_SONAR_TOKEN
```

<verification>
Both outputs available for comparison. Auth switched back to local.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Issue list | Terminal (table format) |
| Analysis results | http://localhost:9000 (UI) |

## Quality Checklist

- [ ] Server UP before scan (`curl` check)
- [ ] `LOCAL_SONAR_TOKEN` loaded in shell
- [ ] `-Dsonar.scm.disabled=true` included in scan command (worktree repo)
- [ ] Issues reviewed — not just "scan passed"
- [ ] Auth returned to local after SonarCloud comparison

## References

- SOP: `dev/sops/sonarqube-local.md`
- Project key: `humansys-demos_raise-commons`
- Dependency vulnerabilities: use Snyk (`/rai-bugfix` Step 4 verification)

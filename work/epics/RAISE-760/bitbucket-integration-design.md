# S760.6: Bitbucket Integration Design

**Epic:** RAISE-760
**Story:** S760.6
**Date:** 2026-03-27
**Status:** Draft
**Dependencies:** S760.2 (Taxonomy Design), ADR-033 (Branch Model)

---

## 1. Purpose

This document defines how RaiSE git conventions and development workflows map to Bitbucket Cloud features within the Atlassian stack. It is written for **partner teams using Bitbucket** and includes GitHub equivalents so teams on either platform can follow the same model.

RaiSE itself uses GitHub. This design ensures partner teams on Bitbucket get the same traceability, automation, and visibility that RaiSE achieves on GitHub — using native Bitbucket capabilities.

---

## 2. Design Principles

1. **Native integration over custom glue** — Use Bitbucket's built-in Jira integration (smart commits, development panel) before building automation rules.
2. **Branch name = traceability** — Every branch name contains a Jira issue key so the development panel links automatically.
3. **Pipeline = quality gate** — Bitbucket Pipelines enforces the same gates RaiSE requires: tests, types, lint.
4. **PR = lifecycle event** — Pull request creation, approval, and merge map directly to Jira status transitions.
5. **Zero manual linking** — Developers never copy-paste Jira URLs into PRs or vice versa. Naming conventions do all the work.

---

## 3. Branch Naming → Jira Auto-Linking

### 3.1 The Problem

Bitbucket's Jira integration automatically links branches, commits, and PRs to Jira issues when it detects a **Jira issue key** (e.g., `RAISE-760`) in the branch name, commit message, or PR title. RaiSE's current branch naming convention (`story/s760.6/bitbucket-design`) uses an internal story ID (`s760.6`) that Jira does not recognize.

### 3.2 Recommended Branch Naming Convention

Embed the Jira issue key in the branch name while preserving the RaiSE semantic structure.

| Branch Type | RaiSE Convention (Current) | Bitbucket Convention (Recommended) | Jira Auto-Link |
|---|---|---|---|
| Story (feature) | `story/s760.6/bitbucket-design` | `story/RAISE-NNN/s760.6/bitbucket-design` | Yes — `RAISE-NNN` detected |
| Hotfix | `hotfix/RAISE-720` | `hotfix/RAISE-720` | Yes — already contains key |
| Release | `release/2.4.0` | `release/2.4.0` | No key needed (long-lived) |

**Pattern:** `story/{JIRA_KEY}/s{EPIC}.{SEQ}/{slug}`

**Examples:**

```
story/RAISE-761/s760.1/forge-scaffold
story/RAISE-762/s760.2/taxonomy-design
story/RAISE-763/s760.6/bitbucket-design
hotfix/RAISE-720
release/2.4.0
```

### 3.3 Why This Works

- Bitbucket scans branch names for patterns matching `{PROJECT_KEY}-{NUMBER}` (e.g., `RAISE-761`).
- The issue key appears in the Jira development panel immediately upon branch creation.
- The RaiSE internal ID (`s760.6`) is preserved for human readability and RaiSE tooling.
- The slug provides context without requiring Jira lookup.

### 3.4 GitHub Equivalent

GitHub does not auto-link branches to Jira natively. Options:
- **GitHub for Jira app** (Atlassian-maintained): Scans branch names for Jira keys, same behavior as Bitbucket.
- **Manual:** Include Jira key in PR description; GitHub development sidebar shows linked issues.

### 3.5 Migration Note

Teams already using RaiSE's `story/s{N}.{M}/{name}` pattern add the Jira key as a path segment. The `rai story-start` skill can be configured to prompt for or auto-resolve the Jira key when creating the branch.

---

## 4. Smart Commits

### 4.1 What Are Smart Commits?

Bitbucket smart commits allow developers to transition Jira issues, add comments, and log time directly from commit messages. The syntax is:

```
<JIRA_KEY> #<command> <arguments>
```

Smart commits are processed when code is pushed to Bitbucket. They require:
1. The Jira-Bitbucket integration to be enabled (DVCS connector or native integration).
2. The committer's Bitbucket email to match their Jira account email.
3. The commit to be pushed (local commits have no effect until pushed).

### 4.2 Smart Commit Syntax

| Command | Syntax | Effect in Jira |
|---|---|---|
| **Comment** | `RAISE-761 #comment Fixed the config parser` | Adds comment to RAISE-761 |
| **Transition** | `RAISE-761 #in-progress` | Transitions to "In Progress" |
| **Time** | `RAISE-761 #time 2h 30m` | Logs 2h 30m of work |
| **Combined** | `RAISE-761 #time 1h #comment Refactored adapter #in-progress` | All three actions |

**Transition names** use the Jira transition name in lowercase, spaces replaced with hyphens:
- `#backlog` → Backlog
- `#selected-for-development` → Selected for Development
- `#in-progress` → In Progress
- `#done` → Done

### 4.3 Mapping RaiSE Commit Conventions to Smart Commits

RaiSE uses conventional commits (`feat`, `fix`, `docs`, etc.). Smart commit commands are **appended** to the conventional commit message — they do not replace it.

| RaiSE Lifecycle Event | Conventional Commit | Smart Commit Addition | Full Example |
|---|---|---|---|
| Story start (first commit) | `scope(sN.M): initial scope` | `RAISE-NNN #in-progress` | `scope(s760.6): initial scope RAISE-763 #in-progress` |
| Task completion | `feat(sN.M): description` | `RAISE-NNN #comment Task 3 complete` | `feat(s760.6): add pipeline config RAISE-763 #comment Task 3 complete` |
| Bug fix | `fix(sN.M): description` | `RAISE-NNN #comment Fixed root cause` | `fix(s760.6): null check on adapter RAISE-763 #comment Fixed null pointer in adapter init` |
| Documentation | `docs(sN.M): description` | (no transition needed) | `docs(s760.6): update API reference RAISE-763 #comment Updated API docs` |
| Story review commit | `review(sN.M): retrospective` | `RAISE-NNN #comment Review complete` | `review(s760.6): retrospective RAISE-763 #comment Retrospective and review complete` |

### 4.4 Practical Guidance

**Do:**
- Use smart commit transitions sparingly — PR merge is a better trigger for `#done` (see Section 6).
- Use `#comment` to leave breadcrumbs that appear in Jira's activity stream.
- Use `#in-progress` on the scope commit (story start) to auto-transition the issue.

**Do not:**
- Use `#done` in individual commits — the story is not done until the PR is merged.
- Rely solely on smart commits for transitions — Jira Automation rules (S760.3) provide more reliable lifecycle mapping.
- Put smart commit syntax in the commit title line — append it after the conventional commit message body or as a trailer.

### 4.5 GitHub Equivalent

GitHub does not support smart commits (no `#transition`, `#time`, `#comment`). Equivalents:
- **Closing keywords:** `Closes #123`, `Fixes #123` close GitHub Issues (not Jira issues).
- **GitHub for Jira app:** Syncs commit references to Jira development panel, but does not execute transitions.
- **Jira Automation:** Use "commit pushed" or "PR merged" triggers with webhook from GitHub Actions to transition Jira issues.

---

## 5. Pull Request → Jira Integration

### 5.1 PR Title Convention

Include the Jira issue key in the PR title for automatic linking:

```
RAISE-763: S760.6 — Bitbucket integration design
```

**Pattern:** `{JIRA_KEY}: S{EPIC}.{SEQ} — {description}`

This ensures:
- Bitbucket links the PR to the Jira issue in the development panel.
- The PR title is human-readable and searchable.
- The RaiSE story ID is preserved for internal traceability.

### 5.2 PR Description Template

Bitbucket supports PR description templates (stored in the repository). Create `.bitbucket/pull-request-template.md`:

```markdown
## Summary

<!-- What does this PR deliver? Link to design doc if applicable. -->

## Jira Issue

<!-- Auto-linked if key is in PR title. Manual link as backup: -->
[RAISE-NNN](https://your-domain.atlassian.net/browse/RAISE-NNN)

## RaiSE Story

- **Epic:** RAISE-{epic}
- **Story:** S{N}.{M}
- **Plan:** {link to plan artifact}

## Changes

<!-- Bullet list of key changes -->

## Quality Gates

- [ ] Tests pass (`pytest`)
- [ ] Type check pass (`pyright`)
- [ ] Lint pass (`ruff`)
- [ ] Story review complete (`/rai-story-review`)

## Test Plan

<!-- How to verify this PR -->
```

### 5.3 PR Lifecycle → Jira Transitions

| PR Event | Jira Effect | Mechanism |
|---|---|---|
| PR created | Issue appears as "In Review" in dev panel | Native Bitbucket-Jira integration |
| PR approved | Reviewer approval visible in dev panel | Native integration |
| PR merged | Transition issue to Done | Jira Automation rule (recommended) or smart commit `#done` in merge commit |
| PR declined | No auto-transition (manual review needed) | — |

### 5.4 PR Merge Strategy

RaiSE requires `--no-ff` merges to preserve story branch history (ADR-033). Configure Bitbucket:

**Repository Settings → Merge strategies:**
- Enable: **Merge commit** (equivalent to `--no-ff`)
- Disable: Squash, Fast-forward
- Default strategy: **Merge commit**

This preserves the full commit history per story, matching RaiSE's "commit after task" rule.

### 5.5 Code Review Alignment with RaiSE Story Lifecycle

| RaiSE Phase | Bitbucket Activity |
|---|---|
| `/rai-story-implement` | Commits pushed to story branch |
| `/rai-story-review` | PR created, review requested |
| Reviewer approves | PR approved in Bitbucket |
| `/rai-story-close` | PR merged to release branch |

**Recommended reviewer configuration:**
- Release branches (`release/*`): Require 1 approval minimum.
- `main`: Require 1 approval + passing pipeline.

### 5.6 GitHub Equivalent

| Bitbucket Feature | GitHub Equivalent |
|---|---|
| PR → Jira dev panel | GitHub for Jira app syncs PR status |
| PR description template | `.github/pull_request_template.md` |
| Merge strategy settings | Branch protection rules → merge method |
| Required approvals | Branch protection rules → required reviews |

---

## 6. Bitbucket Pipelines

### 6.1 Pipeline Configuration for RaiSE Projects

Bitbucket Pipelines uses `bitbucket-pipelines.yml` at the repository root. Below is the reference configuration for a RaiSE Python monorepo.

```yaml
# bitbucket-pipelines.yml — RaiSE reference configuration
image: python:3.12

definitions:
  caches:
    uv: ~/.cache/uv

  steps:
    - step: &quality-gates
        name: Quality Gates
        caches:
          - uv
        script:
          - pip install uv
          - uv sync --all-extras
          # RaiSE Gate: Tests pass
          - uv run pytest --tb=short -q
          # RaiSE Gate: Type checks pass
          - uv run pyright
          # RaiSE Gate: Linting passes
          - uv run ruff check .
          - uv run ruff format --check .

    - step: &forge-deploy
        name: Deploy Forge App
        caches:
          - node
        script:
          - cd packages/raise-forge
          - npm install
          - npm install -g @forge/cli
          - forge deploy --environment $FORGE_ENV --non-interactive
          - forge install --upgrade --non-interactive
        artifacts:
          - packages/raise-forge/dist/**

pipelines:
  # Run quality gates on every push to any branch
  default:
    - step: *quality-gates

  # Release branch pipelines
  branches:
    'release/*':
      - step: *quality-gates

    'main':
      - step: *quality-gates
      - step:
          <<: *forge-deploy
          deployment: production
          trigger: manual

  # PR pipelines — run on every PR
  pull-requests:
    '**':
      - step: *quality-gates

  # Custom pipelines triggered by RaiSE lifecycle
  custom:
    forge-deploy-staging:
      - variables:
          - name: FORGE_ENV
            default: staging
      - step:
          <<: *forge-deploy
          deployment: staging

    forge-deploy-production:
      - variables:
          - name: FORGE_ENV
            default: production
      - step:
          <<: *forge-deploy
          deployment: production
          trigger: manual
```

### 6.2 Pipeline → RaiSE Quality Gate Mapping

| RaiSE Quality Gate | Pipeline Step | Failure Behavior |
|---|---|---|
| Tests pass | `uv run pytest` | Block PR merge |
| Type checks pass | `uv run pyright` | Block PR merge |
| Linting passes | `uv run ruff check . && ruff format --check .` | Block PR merge |
| Story review complete | Manual check (PR checklist) | Reviewer responsibility |
| Retrospective complete | Manual check (PR checklist) | Reviewer responsibility |

### 6.3 Pipeline Triggers from RaiSE Lifecycle

| RaiSE Event | Pipeline Trigger | How |
|---|---|---|
| Push to story branch | Default pipeline (quality gates) | Automatic on push |
| PR created/updated | Pull request pipeline (quality gates) | Automatic on PR |
| Merge to release branch | Branch pipeline (quality gates) | Automatic on merge |
| Merge to main | Main pipeline (quality gates + deploy option) | Automatic; deploy is manual trigger |
| Epic close (deploy to staging) | Custom pipeline `forge-deploy-staging` | Manual trigger or API call from `rai epic-close` |
| Release (deploy to production) | Custom pipeline `forge-deploy-production` | Manual trigger from main branch |

### 6.4 Forge App Deployment from Pipelines

Deploying a Forge app from Bitbucket Pipelines requires:

1. **Repository variables** (Settings → Repository variables):
   - `FORGE_EMAIL`: Atlassian account email for Forge CLI.
   - `FORGE_API_TOKEN`: API token for the Forge CLI account.

2. **Deployment environments** (Settings → Deployments):
   - `staging`: Auto-deploy on merge to release branch (optional).
   - `production`: Manual trigger only, from main branch.

3. **Forge CLI in pipeline**: Install `@forge/cli` globally, then `forge deploy` + `forge install --upgrade`.

**Security note:** Use Bitbucket's secured repository variables (hidden in logs) for `FORGE_API_TOKEN`. Never commit credentials.

### 6.5 Monorepo Considerations

For the `raise-commons` monorepo structure:

```
raise-commons/
  packages/
    raise-core/        # Python package
    raise-pro/         # Python package
    raise-server/      # Python package
    raise-forge/       # Node.js (Forge app)
```

**Path-based triggers** avoid running all pipelines on every change:

```yaml
pipelines:
  branches:
    'release/*':
      - step:
          name: Python Quality Gates
          condition:
            changesets:
              includePaths:
                - "packages/raise-core/**"
                - "packages/raise-pro/**"
                - "packages/raise-server/**"
                - "tests/**"
          script:
            - pip install uv && uv sync --all-extras
            - uv run pytest --tb=short -q
            - uv run pyright
            - uv run ruff check .

      - step:
          name: Forge Quality Gates
          condition:
            changesets:
              includePaths:
                - "packages/raise-forge/**"
          script:
            - cd packages/raise-forge
            - npm install && npm test
```

### 6.6 GitHub Equivalent

| Bitbucket Pipelines Feature | GitHub Actions Equivalent |
|---|---|
| `bitbucket-pipelines.yml` | `.github/workflows/*.yml` |
| `default` pipeline | `on: push` trigger |
| `pull-requests` pipeline | `on: pull_request` trigger |
| `branches` pipeline | `on: push: branches: [release/*]` |
| `custom` pipeline (manual) | `workflow_dispatch` trigger |
| `condition: changesets: includePaths` | `paths` filter on trigger |
| Repository variables (secured) | Repository secrets |
| Deployment environments | GitHub Environments |
| `trigger: manual` | Environment protection rules (required reviewers) |

---

## 7. Development Panel in Jira

### 7.1 What Appears in the Development Panel

When Bitbucket-Jira integration is active, each Jira issue shows a **Development** section in the detail view containing:

| Element | What It Shows | Triggered By |
|---|---|---|
| **Branches** | Branch name, repository, creation time | Branch name contains Jira key |
| **Commits** | Commit message, author, timestamp | Commit message contains Jira key |
| **Pull Requests** | PR title, status (Open/Merged/Declined), reviewers | PR title or branch contains Jira key |
| **Builds** | Pipeline status (Pass/Fail), link to build | Pipeline runs on linked branch/PR |

### 7.2 Example: Full Story Lifecycle in Development Panel

For story RAISE-763 (S760.6 — Bitbucket integration design):

```
Development
──────────────────────────────────────
🔀 Branches (1)
   story/RAISE-763/s760.6/bitbucket-design
   in raise-commons · created 2h ago

📝 Commits (5)
   scope(s760.6): initial scope RAISE-763 #in-progress
   feat(s760.6): add branch naming section RAISE-763
   feat(s760.6): add pipeline configuration RAISE-763
   docs(s760.6): complete design document RAISE-763
   review(s760.6): retrospective RAISE-763

🔃 Pull Requests (1)
   RAISE-763: S760.6 — Bitbucket integration design
   ✅ MERGED · 1 approval · Pipeline passed

🔨 Builds (3)
   Pipeline #142 — ✅ Successful (quality-gates)
   Pipeline #143 — ✅ Successful (quality-gates)
   Pipeline #144 — ✅ Successful (quality-gates)
──────────────────────────────────────
```

### 7.3 Value for PMs and Stakeholders

The development panel gives non-developers **real-time visibility** without leaving Jira:

| Question | Answer from Dev Panel |
|---|---|
| "Has work started on this story?" | Branch exists → yes |
| "How many commits so far?" | Commit count shows progress |
| "Is the code being reviewed?" | PR status = Open |
| "Did the build pass?" | Build status = green/red |
| "Is the code merged?" | PR status = Merged |
| "When was the last activity?" | Commit/PR timestamps |

**No Jira comments, no status meetings, no Slack pings needed** for basic progress visibility.

### 7.4 Configuration Requirements

To enable the development panel:

1. **Connect Bitbucket to Jira:** Jira Settings → Apps → DVCS accounts → Add Bitbucket Cloud account. (Or use the native Bitbucket for Jira Cloud app from Marketplace.)
2. **Ensure email matching:** Each developer's Bitbucket email must match their Jira email for smart commits to work.
3. **Repository access:** The Jira site must have access to the Bitbucket repositories (configured during DVCS setup).

### 7.5 GitHub Equivalent

| Bitbucket Dev Panel Feature | GitHub Equivalent |
|---|---|
| Development section in Jira | Development section in Jira (via GitHub for Jira app) |
| Branch auto-linking | Same behavior with GitHub for Jira app |
| Commit linking | Same behavior with GitHub for Jira app |
| PR status in Jira | Same behavior with GitHub for Jira app |
| Build status in Jira | Requires GitHub Actions → Jira integration (via GitHub for Jira app or Jira Automation webhook) |

---

## 8. Repository Structure & Permissions

### 8.1 Monorepo Mapping to Bitbucket

The `raise-commons` monorepo maps to a **single Bitbucket repository** within a Bitbucket workspace:

```
Workspace: raise (or partner org name)
  └── Repository: raise-commons
        ├── packages/raise-core/
        ├── packages/raise-pro/
        ├── packages/raise-server/
        ├── packages/raise-forge/
        └── bitbucket-pipelines.yml
```

**Why a single repo:** Bitbucket Pipelines supports monorepo path-based triggers (Section 6.5). Splitting into multiple repos would break the shared dependency graph and require cross-repo pipeline orchestration.

### 8.2 Workspace & Project Structure

For partner teams with multiple RaiSE-managed repositories:

```
Workspace: {partner-org}
  └── Project: RaiSE
        ├── Repository: raise-commons       (framework core)
        ├── Repository: {product-name}      (partner product)
        └── Repository: raise-forge-{org}   (partner Forge app)
```

Bitbucket **Projects** group repositories and share default permissions — useful for applying RaiSE conventions across all repos in scope.

### 8.3 Branch Permissions

Configure branch restrictions to enforce ADR-033 protection rules.

**Repository Settings → Branch restrictions:**

| Branch Pattern | Permission | Effect |
|---|---|---|
| `main` | No direct pushes | All changes via PR only |
| `main` | Require 1 approval | Code review enforced |
| `main` | Require passing build | Quality gates enforced |
| `release/*` | No direct pushes | All changes via PR (story branches) or `--no-ff` merge |
| `release/*` | Require passing build | Quality gates enforced |
| `story/*` | No restrictions | Developers push freely to their story branches |

**Branch restriction API** (for automation):

```bash
# Example: protect main branch via Bitbucket REST API
curl -X POST \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/branch-restrictions" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "push",
    "pattern": "main",
    "users": [],
    "groups": []
  }'
```

### 8.4 Repository Permission Model

| Role | Bitbucket Permission | What They Can Do |
|---|---|---|
| Developer | Write | Push to story branches, create PRs |
| Tech Lead | Write + merge to release | Merge PRs to release branches |
| Release Manager | Admin | Merge to main, manage branch restrictions |
| PM / Stakeholder | Read | View code, PRs, pipelines (Jira dev panel preferred) |

### 8.5 GitHub Equivalent

| Bitbucket Feature | GitHub Equivalent |
|---|---|
| Workspace | Organization |
| Project (groups repos) | No direct equivalent (use topics/teams) |
| Branch restrictions | Branch protection rules |
| Required approvals | Required pull request reviews |
| Required passing build | Required status checks |
| Repository permissions (Read/Write/Admin) | Repository roles (Read/Triage/Write/Maintain/Admin) |

---

## 9. End-to-End Workflow Example

This section traces a complete story lifecycle through the Bitbucket-Jira integration.

### Story: RAISE-763 — S760.6 Bitbucket Integration Design

**1. Story Start (`/rai-story-start`)**

```bash
# Developer creates branch with Jira key
git checkout release/2.4.0 && git pull
git checkout -b story/RAISE-763/s760.6/bitbucket-design

# Scope commit with smart commit transition
git commit -m "scope(s760.6): initial scope — bitbucket integration design

RAISE-763 #in-progress"
git push -u origin story/RAISE-763/s760.6/bitbucket-design
```

**Jira effect:** RAISE-763 transitions to "In Progress". Branch appears in development panel.

**2. Implementation (`/rai-story-implement`)**

```bash
# Task commits reference Jira key
git commit -m "feat(s760.6): branch naming conventions

RAISE-763 #comment Branch naming section complete"

git commit -m "feat(s760.6): pipeline configuration reference

RAISE-763 #comment Pipeline YAML and gate mapping complete"

git push
```

**Jira effect:** Commits appear in development panel. Comments appear in activity stream.

**3. Story Review (`/rai-story-review`)**

```bash
# Create PR with Jira key in title
# Bitbucket UI or API:
curl -X POST \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/raise-commons/pullrequests" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "title": "RAISE-763: S760.6 — Bitbucket integration design",
    "source": {"branch": {"name": "story/RAISE-763/s760.6/bitbucket-design"}},
    "destination": {"branch": {"name": "release/2.4.0"}},
    "close_source_branch": true
  }'
```

**Jira effect:** PR appears in development panel with status "Open". Pipeline runs quality gates.

**4. Code Review**

Reviewer approves the PR in Bitbucket. Pipeline passes.

**Jira effect:** Approval visible in development panel.

**5. Story Close (`/rai-story-close`)**

PR is merged (merge commit, `--no-ff`). Source branch is deleted.

**Jira effect:** PR status changes to "Merged". Jira Automation rule transitions RAISE-763 to "Done".

**Jira Automation Rule (from S760.3):**
```
Trigger: Development — Pull request merged
Condition: Issue status = "In Progress"
Action: Transition issue → Done
```

---

## 10. Configuration Checklist

For partner teams setting up the Bitbucket-Jira integration:

### Phase 1: Connect & Configure

- [ ] Install "Jira for Bitbucket Cloud" or configure DVCS connector
- [ ] Verify developer email matching (Bitbucket ↔ Jira)
- [ ] Enable smart commits in Jira integration settings
- [ ] Configure branch restrictions on `main` and `release/*`
- [ ] Set default merge strategy to "Merge commit" (no squash, no fast-forward)
- [ ] Add PR description template (`.bitbucket/pull-request-template.md`)

### Phase 2: Pipelines

- [ ] Create `bitbucket-pipelines.yml` with quality gate steps
- [ ] Configure repository variables: `FORGE_EMAIL`, `FORGE_API_TOKEN`
- [ ] Set up deployment environments: staging, production
- [ ] Verify pipeline runs on PR creation and branch push

### Phase 3: Jira Automation (designed in S760.3)

- [ ] Create automation rule: PR merged → transition to Done
- [ ] Create automation rule: Branch created → transition to In Progress (alternative to smart commits)
- [ ] Verify development panel shows branches, commits, PRs, builds

### Phase 4: Validate

- [ ] Create a test story, run through full lifecycle
- [ ] Verify Jira development panel populates correctly
- [ ] Verify pipeline gates block PR merge on failure
- [ ] Verify smart commit transitions work

---

## 11. Summary: Feature Mapping (Bitbucket ↔ GitHub)

| Capability | Bitbucket | GitHub |
|---|---|---|
| Branch → Jira linking | Native (issue key in branch name) | GitHub for Jira app |
| Smart commits (transition/comment/time) | Native | Not supported; use Jira Automation webhooks |
| PR → Jira linking | Native (issue key in PR title) | GitHub for Jira app |
| CI/CD pipeline | Bitbucket Pipelines (`bitbucket-pipelines.yml`) | GitHub Actions (`.github/workflows/*.yml`) |
| Forge deployment | Pipelines + `forge deploy` | Actions + `forge deploy` |
| Development panel in Jira | Native integration | GitHub for Jira app |
| Branch restrictions | Branch restrictions (Settings) | Branch protection rules |
| PR merge strategy | Repository-level setting | Branch protection rules |
| PR templates | `.bitbucket/pull-request-template.md` | `.github/pull_request_template.md` |
| Monorepo path filtering | `condition: changesets: includePaths` | `paths` filter on workflow trigger |
| Manual pipeline trigger | Custom pipelines | `workflow_dispatch` |
| Deployment environments | Bitbucket Deployments | GitHub Environments |
| Repository variables (secrets) | Secured repository variables | Repository secrets |

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Smart commit email mismatch | Medium | Medium | Document email matching requirement in onboarding checklist |
| Branch name too long (with Jira key) | Low | Low | Keep slugs short; Bitbucket has no practical length limit for branch names |
| Pipeline minutes exhaustion | Medium | Low | Use path-based triggers for monorepo; cache dependencies |
| Forge CLI auth expires in pipeline | Low | Medium | Use API tokens with appropriate expiry; monitor in pipeline |
| Smart commit syntax errors silently ignored | Medium | Low | Prefer Jira Automation over smart commits for critical transitions |

---

## References

- [Bitbucket Smart Commits](https://support.atlassian.com/bitbucket-cloud/docs/use-smart-commits/) — official Atlassian documentation
- [Bitbucket Pipelines Configuration Reference](https://support.atlassian.com/bitbucket-cloud/docs/bitbucket-pipelines-configuration-reference/) — full YAML schema
- [Bitbucket Cloud REST API v2](https://developer.atlassian.com/cloud/bitbucket/rest/intro/) — API reference
- ADR-033: Release Branch Model for Parallel Version Development
- S760.2: Taxonomy Design (issue types, components, labels, versions)
- S760.3: Workflow, Automation & Lifecycle Mapping (Jira Automation rules)
- R1-RAISE-760: Atlassian API Landscape (Bitbucket API details, auth timeline)

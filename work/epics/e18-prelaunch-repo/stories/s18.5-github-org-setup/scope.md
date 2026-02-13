# Story S18.5: GitHub Organization Setup

> **Epic:** E18 (Pre-Launch Repo Readiness)
> **Size:** M
> **GTM Ref:** S7.4 (partial — GitHub mirror component)
> **Branch:** `story/s18.5/github-org-setup`

---

## Objective

Set up the humansys GitHub organization with the public `raise` repo, team structure, and repo configuration so the open-core codebase is properly hosted for the Feb launch.

---

## In Scope

- Create `raise` public repo under humansys org
- Configure repo settings (description, topics, homepage URL, default branch)
- Set up teams (engineering) with appropriate permissions
- Branch protection rules on main
- Issue templates (bug report, feature request)
- Labels for issue triage
- Push open-core content as initial commit / mirror
- Community files if not already present (CONTRIBUTING, CODE_OF_CONDUCT)

## Out of Scope

- CI/CD pipeline (GitHub Actions) — post-launch
- GitLab ↔ GitHub automated sync — manual mirror for now
- GitHub Pages / docs site — separate story
- Secrets management / environment config
- GitHub Projects board setup

## Done Criteria

- [ ] `humansys/raise` repo exists and is public
- [ ] Teams configured with correct member access
- [ ] Branch protection on main (require PR, no force push)
- [ ] Issue templates working
- [ ] Labels created
- [ ] Open-core code pushed and browsable
- [ ] `pip install rai-cli` README links point to correct repo

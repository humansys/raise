# RAISE-203: MEMORY.md hardcodes "v2" as development branch name

## Feature Scope

**Type:** Bug fix
**Priority:** Medium
**Labels:** memory, onboarding

## Problem

`rai memory generate` hardcodes `v2` as the development branch in MEMORY.md's Branch Model section. Other teams using RaiSE will have different conventions (`develop`, `dev`, `main`, etc.). The hardcoded value confuses adopters and may cause branch operations to target a non-existent branch.

## In Scope

- Find where `rai memory generate` produces the Branch Model section with hardcoded "v2"
- Make it read the development branch name from `manifest.yaml` (`branches.development`) dynamically
- Verify MEMORY.md output uses the configured branch name instead of literal "v2"

## Out of Scope

- Changing the branch model structure or conventions
- Modifying other hardcoded values in MEMORY.md unrelated to the branch name
- Manifest schema changes (the `branches.development` field already exists)

## Done Criteria

- [ ] `rai memory generate` reads branch name from `manifest.yaml → branches.development`
- [ ] Generated MEMORY.md shows the project-configured branch name, not "v2"
- [ ] Tests pass
- [ ] Retrospective complete

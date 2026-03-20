# E615: raise-pro Secure Distribution — Scope

**Jira:** RAISE-615
**Label:** pro-launch
**Branch:** dev (stories branch from dev)

## Objective

Establish private distribution of raise-pro via GitLab Package Registry with
per-client deploy tokens. Block public PyPI publication of proprietary packages.

## In Scope

- Separate raise-pro from public PyPI release workflow
- Publish raise-pro to GitLab Package Registry
- Create deploy tokens per client (manual, <5 clients)
- Client installation documentation
- FSL 1.1-ALv2 license header in raise-pro source files
- Verify uv/pip install with token authentication

## Out of Scope

- License key validation (E616)
- Token management portal/automation
- raise-server distribution
- raise-agent distribution
- Automated token rotation

## Stories (Planned)

### S615.1: Separate raise-pro from public PyPI and publish to GitLab Registry (S)

Modify release workflow to exclude raise-pro from public PyPI publish.
Configure GitLab Package Registry for raise-pro. Publish first version.
Create deploy token for first client. Verify install with uv.

**Dependencies:** None

### S615.2: Client onboarding documentation and FSL license headers (XS)

Add FSL 1.1-ALv2 license headers to raise-pro source files.
Create client installation guide (pip/uv config, token setup, verification).

**Dependencies:** S615.1

## Done Criteria

- [ ] raise-pro NOT published to public PyPI on release
- [ ] raise-pro available on GitLab Package Registry
- [ ] At least one deploy token created and tested
- [ ] Client can install raise-pro with token-authenticated index URL
- [ ] Installation guide exists
- [ ] FSL license headers on raise-pro source files

## Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S615.1 Registry setup | pending | |
| S615.2 Docs + license | pending | |

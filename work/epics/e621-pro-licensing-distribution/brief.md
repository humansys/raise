# E621: raise-pro CLI — Licensing & Distribution MVP — Brief

## Hypothesis

Configuring raise-pro to connect to raise-server (which handles license validation)
combined with GitLab Package Registry distribution will enable controlled onboarding
of paying clients with minimal CLI-side complexity.

## Problem

raise-pro is a functional CLI plugin with no distribution mechanism or server
connection setup. It publishes to public PyPI alongside raise-cli. Clients need:
- Private installation (access-controlled via GitLab deploy tokens)
- Server connection setup (`rai configure`) for pro features
- Clear feedback when their plan doesn't cover a feature
- Legal clarity (FSL license headers)

## Appetite

Small — 4 stories. Server connection, plan error handling, private distribution,
and legal/docs. Target: 2 weeks (after E616 delivers server auth).

## Success Metrics

1. `rai configure --server --key` sets up server connection
2. 403 from server → clear "Requires X plan" message in CLI
3. `rai license status` shows current plan info
4. raise-pro installable only via authenticated GitLab Package Registry
5. FSL 1.1-ALv2 headers on all raise-pro source files
6. Client onboarding documentation complete

## Rabbit Holes

- Don't build offline license validation — always-connected model (E616 validates)
- Don't build JWT/crypto in CLI — eliminated by always-connected
- Don't build admin tools in CLI — admin uses server API directly (E616)

## Dependencies

- **RAISE-616** S616.2: server must accept member API keys and return plan info

---
id: "ADR-026"
title: "OAuth Provider Choice for JIRA Sync"
date: "2026-02-14"
status: "Accepted"
epic: "E-DEMO"
---

# ADR-026: OAuth Provider Choice for JIRA Sync

## Contexto

JIRA sync requiere autenticación para acceder a JIRA Cloud API. Existen múltiples flujos OAuth 2.0:
1. Authorization Code + PKCE (web-based redirect)
2. Device Flow (CLI-friendly, no browser required)
3. Service Account (API tokens, no user consent)

Tensiones:
- **UX:** CLI tools should minimize browser interactions
- **Security:** PKCE prevents authorization code interception
- **Usability:** Device flow requires manual code entry
- **Enterprise:** Service accounts are simpler but lack user context

**Research foundation:** 32 sources from `/work/research/jira-bidirectional-sync/`

## Decisión

**Use Authorization Code + PKCE for initial authentication, with token refresh for subsequent operations.**

**Implementation:**
- Initial auth: Browser-based OAuth flow (one-time setup per developer)
- Token storage: Encrypted in `~/.rai/credentials.json` (XDG_CONFIG_HOME compliant)
- Token refresh: Automatic background refresh using refresh tokens
- Fallback: Clear error message with re-auth instructions if refresh fails

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Industry-standard flow (well-documented, library support) |
| ✅ Positivo | PKCE provides security without backend server |
| ✅ Positivo | Token refresh enables long-term usage without re-auth |
| ✅ Positivo | User-scoped tokens (auditability in JIRA) |
| ⚠️ Negativo | Requires browser for initial auth (not pure CLI) |
| ⚠️ Negativo | Token storage security (encrypted but local filesystem) |
| ⚠️ Negativo | Token expiration UX (need clear re-auth prompts) |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| **Device Flow** | Requires manual code entry (worse UX than browser redirect). Best for devices without browsers (not our case). |
| **Service Account (API Tokens)** | No user context (all actions appear as "bot"). Less secure (static tokens). Not suitable for user-level operations. |
| **Client Credentials** | Backend server required (adds complexity). Not applicable for CLI tool. |

---

<details>
<summary><strong>Referencias</strong></summary>

**Research:**
- `/work/research/jira-bidirectional-sync/recommendation.md` - Webhook-first architecture, OAuth best practices
- [Atlassian OAuth 2.0 (3LO)](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/) - Official docs (Very High evidence)
- [OAuth 2.0 for Native Apps (RFC 8252)](https://datatracker.ietf.org/doc/html/rfc8252) - PKCE specification

**Libraries:**
- `atlassian-python-api` - Supports OAuth 2.0 flows
- `authlib` - OAuth 2.0 client library with PKCE support

**Implementation:**
- Token storage location: `~/.rai/credentials.json` (follows XDG Base Directory spec)
- Encryption: Use `cryptography` library (Fernet symmetric encryption, key derived from machine ID)

</details>

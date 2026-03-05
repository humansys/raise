# RAISE-295 — Snyk Findings

**Source:** Snyk UI (text confirmed directly from Snyk report)
**Date captured:** 2026-02-26
**Project:** raise-commons (Python 3.12.3)
**Status:** Partial — 10 of 18 issues confirmed. Remaining 8 pending.

> All data marked ✓ was confirmed directly from Snyk report text.

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0     |
| High     | 8     |
| Medium   | 10    |
| Low      | ?     |
| **Total**| **18** |

All 18 issues have a fix available.

---

## Findings

### [HIGH · Score 731] cryptography — Insufficient Verification of Data Authenticity

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2026-26007 ✓ |
| CWE | CWE-345 ✓ |
| CVSS | 8.9 (v4.0) / 7.4 (v3.1) ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-15263096 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `46.0.5` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Insufficient Verification of Data Authenticity in public key functions `public_key_from_numbers`, `EllipticCurvePublicNumbers.public_key`, `load_der_public_key`, and `load_pem_public_key`. When using `sect*` binary curves for verification — a rare use case — these functions do not verify that the provided point belongs to the expected prime-order subgroup of the curve. An attacker supplying a malicious public key as input can expose partial private key bits or forge signatures.

**Remediation:** Upgrade `cryptography` to `>=46.0.5`.

---

### [HIGH · Score 696] cryptography — Observable Timing Discrepancy

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2023-50782 ✓ |
| CWE | CWE-203 ✓ |
| CVSS | 7.5 (v3.1) ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6126975 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.0` ✓ |
| Exploit maturity | Proof of concept ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to the "Marvin Attack" — an Observable Timing Discrepancy in RSA decryption. A remote attacker can measure timing differences in decryption operations on TLS servers that use RSA key exchanges, potentially decrypting captured messages and exposing confidential data. This vulnerability exists due to an incomplete fix for CVE-2020-25659.

**Remediation:** Upgrade `cryptography` to `>=42.0.0`.

---

### [HIGH · Score 659] urllib3 — Allocation of Resources Without Limits or Throttling

| Field | Value |
|-------|-------|
| Package | `urllib3` |
| CVE | CVE-2025-66418 ✓ |
| CWE | CWE-770 ✓ |
| CVSS | 8.9 (v4.0) / 6.8 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-URLLIB3-14192443 ✓ |
| Current version | `2.0.7` ✓ |
| Fixed in | `2.6.0` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › urllib3@2.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Allocation of Resources Without Limits or Throttling during the decompression of compressed response data. An attacker can cause excessive CPU and memory consumption by sending responses with a large number of chained compression steps.

**Remediation:** Upgrade `urllib3` to `>=2.6.0`.

---

### [HIGH · Score 659] urllib3 — Improper Handling of Highly Compressed Data (Data Amplification) — variant A

| Field | Value |
|-------|-------|
| Package | `urllib3` |
| CVE | CVE-2025-66471 ✓ |
| CWE | CWE-409 ✓ |
| CVSS | 8.9 (v4.0) / 6.8 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-URLLIB3-14192442 ✓ |
| Current version | `2.0.7` ✓ |
| Fixed in | `2.6.0` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › urllib3@2.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Improper Handling of Highly Compressed Data (Data Amplification) in the Streaming API. The `ContentDecoder` class can be forced to allocate disproportionate resources when processing a single chunk with very high compression, such as via the `stream()`, `read(amt=256)`, `read1(amt=256)`, `read_chunked(amt=256)`, and `readinto(b)` functions.

**Note:** It is recommended to also patch Brotli dependencies (upgrade to at least `1.2.0`) if installed outside of urllib3, to avoid other instances of the same vulnerability.

**Remediation:** Upgrade `urllib3` to `>=2.6.0`.

---

### [HIGH · Score 659] urllib3 — Improper Handling of Highly Compressed Data (Data Amplification) — variant B

| Field | Value |
|-------|-------|
| Package | `urllib3` |
| CVE | CVE-2026-21441 ✓ |
| CWE | CWE-409 ✓ |
| CVSS | 8.9 (v4.0) / 6.8 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-URLLIB3-14896210 ✓ |
| Current version | `2.0.7` ✓ |
| Fixed in | `2.6.3` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › urllib3@2.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Improper Handling of Highly Compressed Data (Data Amplification) via the streaming API when handling HTTP redirects. An attacker can cause excessive resource consumption by serving a specially crafted compressed response that triggers decompression of large amounts of data before any read limits are enforced.

**Note:** Only exploitable if content is streamed from untrusted sources with redirects enabled.

**Remediation:** Upgrade `urllib3` to `>=2.6.3` (higher than variant A — this sets the floor for urllib3).

---

### [MEDIUM · Score 626] certifi — Insufficient Verification of Data Authenticity

| Field | Value |
|-------|-------|
| Package | `certifi` |
| CVE | CVE-2024-39689 ✓ |
| CWE | CWE-345 ✓ |
| CVSS | 6.1 (v4.0) / 6.8 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-CERTIFI-7430173 ✓ |
| Current version | `2023.11.17` ✓ |
| Fixed in | `2024.7.4` ✓ |
| Exploit maturity | Proof of concept ✓ |
| Introduced via | `tmp@0.0.0 › certifi@2023.11.17` ✓ |

**Description:**
Affected versions are vulnerable to Insufficient Verification of Data Authenticity due to the presence of the root certificate for GLOBALTRUST in the root store. The root certificates are being removed pursuant to an investigation into non-compliance.

**Remediation:** Upgrade `certifi` to `>=2024.7.4`.

---

### [HIGH · Score 624] cryptography — Type Confusion

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2024-6119 ✓ |
| CWE | CWE-843 ✓ |
| CVSS | 8.2 (v4.0) / 5.9 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-7886970 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `43.0.1` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Type Confusion in the `do_x509_check()` function in `x509/v3_utl.c`, responsible for certificate name checks. An application that specifies an expected DNS name, email address, or IP address and performs a name check on an `otherName` subject alternative name of an X.509 certificate can be made to crash when it attempts to read an invalid memory address.

**Note:** Users building cryptography from source ("sdist") are responsible for upgrading their copy of OpenSSL.

**Remediation:** Upgrade `cryptography` to `>=43.0.1`.

---

### [MEDIUM · Score 606] requests — Insertion of Sensitive Information Into Sent Data

| Field | Value |
|-------|-------|
| Package | `requests` |
| CVE | CVE-2024-47081 ✓ |
| CWE | CWE-201 ✓ |
| CVSS | 5.7 (v4.0) / 4.8 (v3.1) / NVD: not yet published ✓ |
| Snyk ID | SNYK-PYTHON-REQUESTS-10305723 ✓ |
| Current version | `2.31.0` ✓ |
| Fixed in | `2.32.4` ✓ |
| Exploit maturity | Proof of concept ✓ |
| Introduced via | `tmp@0.0.0 › requests@2.31.0` ✓ |

**Description:**
Affected versions are vulnerable to Insertion of Sensitive Information Into Sent Data due to incorrect URL processing. An attacker can craft a malicious URL that tricks the library into sending the victim's `.netrc` credentials to an attacker-controlled server. Example: `http://example.com:@evil.com/` — the library sends the credentials for `example.com` to `evil.com`.

**Note:** Only exploitable if the `.netrc` file contains an entry for the hostname in the crafted URL's "intended" part.

**Remediation:** Upgrade `requests` to `>=2.32.4`.

---

### [MEDIUM · Score 524] idna — Resource Exhaustion

| Field | Value |
|-------|-------|
| Package | `idna` |
| CVE | CVE-2024-3651 ✓ |
| CWE | CWE-400 ✓ |
| CVSS | 6.2 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-IDNA-6597975 ✓ |
| Current version | `3.6` ✓ |
| Fixed in | `3.7` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › idna@3.6` ✓ |

**Description:**
Affected versions are vulnerable to Resource Exhaustion via the `idna.encode()` function. An attacker can consume significant CPU resources and potentially cause a denial-of-service by supplying specially crafted arbitrarily large inputs. Triggered only by inputs that would not occur in normal usage, but could be passed if the higher-level application does not apply preliminary input validation.

**Remediation:** Upgrade `idna` to `>=3.7`.

---

### [MEDIUM · Score 514] urllib3 — Improper Removal of Sensitive Information Before Storage or Transfer

| Field | Value |
|-------|-------|
| Package | `urllib3` |
| CVE | CVE-2024-37891 ✓ |
| CWE | CWE-212 ✓ |
| CVSS | 6.0 (v4.0) / 5.3 (v3.1) / NVD 6.5 ✓ |
| Snyk ID | SNYK-PYTHON-URLLIB3-7267250 ✓ |
| Current version | `2.0.7` ✓ |
| Fixed in | `1.26.19` or `2.2.2` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › urllib3@2.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Improper Removal of Sensitive Information Before Storage or Transfer due to improper handling of the `Proxy-Authorization` header during cross-origin redirects when `ProxyManager` is not in use. Under non-recommended configurations, the contents of this header can be forwarded in an automatic HTTP redirect.

**Conditions for exploitability (all three must be true):**
1. Setting the `Proxy-Authorization` header without using urllib3's built-in proxy support
2. Not disabling HTTP redirects (i.e., not using `redirects=False`)
3. Either not using an HTTPS origin server, or having a proxy/target origin that redirects to a malicious origin

**Remediation:** Upgrade `urllib3` to `>=1.26.19` or `>=2.2.2`. Note: since other urllib3 issues require `>=2.6.3`, that version covers this finding too.

---

## Findings (11–14)

### [MEDIUM · Score 514] urllib3 — Open Redirect

| Field | Value |
|-------|-------|
| Package | `urllib3` |
| CVE | CVE-2025-50181 ✓ |
| CWE | CWE-601 ✓ |
| CVSS | 6.0 (v4.0) / 5.3 (v3.1) / NVD 6.1 ✓ |
| Snyk ID | SNYK-PYTHON-URLLIB3-10390194 ✓ |
| Current version | `2.0.7` ✓ |
| Fixed in | `2.5.0` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › urllib3@2.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Open Redirect due to the `retries` parameter being ignored during `PoolManager` instantiation. An attacker can access unintended resources or endpoints by leveraging automatic redirects when the application expects redirects to be disabled at the connection pool level.

**Note:** `requests` and `botocore` users are not affected.

**Remediation:** Upgrade `urllib3` to `>=2.5.0`. Note: since other urllib3 issues require `>=2.6.3`, that version covers this finding too.

---

### [MEDIUM · Score 509] cryptography — NULL Pointer Dereference

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2024-26130 ✓ |
| CWE | CWE-476 ✓ |
| CVSS | 5.9 (v3.1) / NVD 7.5 ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6261585 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.4` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to NULL Pointer Dereference in the `pkcs12.serialize_key_and_certificates` function. An attacker can crash the Python process.

**Conditions for exploitability (both must be true):**
1. The function is called with a certificate whose public key does not match the provided private key
2. An `encryption_algorithm` with `hmac_hash` set via `PrivateFormat.PKCS12.encryption_builder().hmac_hash(...)`

**Remediation:** Upgrade `cryptography` to `>=42.0.4`. Note: since other cryptography issues require `>=46.0.5`, that version covers this finding too.

---

### [MEDIUM · Score 509] cryptography — Resource Exhaustion

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2023-6237 ✓ |
| CWE | CWE-400 ✓ |
| CVSS | 5.9 (v3.1) / NVD: not yet published ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6157248 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.2` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Resource Exhaustion via the `EVP_PKEY_public_check` function. When called on RSA public keys, the function computes whether the RSA modulus `n` is composite. For valid keys, `n` is a product of large primes and completes quickly. However, if `n` is itself a large prime, this computation takes a very long time. An attacker can cause a denial-of-service by supplying a specially crafted RSA key.

**Remediation:** Upgrade `cryptography` to `>=42.0.2`. Note: since other cryptography issues require `>=46.0.5`, that version covers this finding too.

---

### [MEDIUM · Score 494] requests — Always-Incorrect Control Flow Implementation

| Field | Value |
|-------|-------|
| Package | `requests` |
| CVE | CVE-2024-35195 ✓ |
| CWE | CWE-670 ✓ |
| CVSS | 5.6 (v3.1) / NVD: not yet published ✓ |
| Snyk ID | SNYK-PYTHON-REQUESTS-6928867 ✓ |
| Current version | `2.31.0` ✓ |
| Fixed in | `2.32.2` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › requests@2.31.0` ✓ |
| Snyk insight | Only applicable when first request is sent with `verify=False` ✓ |

**Description:**
Affected versions are vulnerable to Always-Incorrect Control Flow Implementation when making requests through a `Session`. If the first request to a host is made with `verify=False`, all subsequent requests in that session ignore certificate verification regardless of later changes to the `verify` value. An attacker can exploit this to bypass TLS certificate verification.

**Notes:**
- For `requests <2.32.0`: avoid setting `verify=False` for the first request to a host in a `Session`
- For `requests <2.32.0`: call `close()` on `Session` objects to clear existing connections if `verify=False` was used
- Version `2.32.0` was yanked; first safe version is `2.32.2`

**Remediation:** Upgrade `requests` to `>=2.32.2`. Note: since CVE-2024-47081 requires `>=2.32.4`, that version covers this finding too.

---

## Findings (15–18)

### [MEDIUM · Score 489] cryptography — NULL Pointer Dereference

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2024-0727 ✓ |
| CWE | CWE-476 ✓ |
| CVSS | 5.5 (v3.1) / NVD 5.5 ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6210214 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.2` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to NULL Pointer Dereference when processing a maliciously formatted PKCS12 file. The vulnerability exists due to improper handling of optional `ContentInfo` fields, which can be set to null. An attacker can cause a denial of service by sending crafted input, causing applications that load PKCS12 files from untrusted sources to terminate abruptly.

**Remediation:** Upgrade `cryptography` to `>=42.0.2`. Note: since other cryptography issues require `>=46.0.5`, that version covers this finding too.

---

### [MEDIUM · Score 479] cryptography — Denial of Service (DoS)

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2023-5678 ✓ |
| CWE | CWE-400 ✓ |
| CVSS | 5.3 (v3.1) / NVD 5.3 ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6050294 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.0` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Denial of Service when the `DH_generate_key()`, `DH_check_pub_key()`, `DH_check_pub_key_ex()`, `EVP_PKEY_public_check()`, and `EVP_PKEY_generate()` functions are used. An attacker can cause long delays and a potential DoS by supplying excessively long X9.42 DH keys or parameters from an untrusted source.

**Note:** Only exploitable if the application uses these functions to generate or check an X9.42 DH key or parameters. Also affects the `openssl pkey -pubcheck` and `openssl genpkey` CLI commands.

**Remediation:** Upgrade `cryptography` to `>=42.0.0`. Note: since other cryptography issues require `>=46.0.5`, that version covers this finding too.

---

### [LOW · Score 399] cryptography — Uncontrolled Resource Consumption (TLS Session Cache)

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2024-2511 ✓ |
| CWE | CWE-400 ✓ |
| CVSS | 3.7 (v3.1) / NVD: not yet published ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6592767 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.6` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Uncontrolled Resource Consumption due to the TLS session cache entering an incorrect state and failing to flush properly as it fills, leading to uncontrolled memory consumption. Triggered under certain server configurations when processing TLSv1.3 sessions. A malicious client can deliberately create this scenario to force a service disruption; it may also occur accidentally in normal operation.

**Conditions for exploitability:**
- Server supports TLSv1.3
- `SSL_OP_NO_TICKET` option is enabled
- Does NOT occur if early_data support is configured with default anti-replay protection

**Remediation:** Upgrade `cryptography` to `>=42.0.6`. Note: since other cryptography issues require `>=46.0.5`, that version covers this finding too.

---

### [LOW · Score 399] cryptography — Uncontrolled Resource Consumption (DSA Key Check)

| Field | Value |
|-------|-------|
| Package | `cryptography` |
| CVE | CVE-2024-4603 ✓ |
| CWE | CWE-400 ✓ |
| CVSS | 3.7 (v3.1) / NVD: not yet published ✓ |
| Snyk ID | SNYK-PYTHON-CRYPTOGRAPHY-6913422 ✓ |
| Current version | `41.0.7` ✓ |
| Fixed in | `42.0.8` ✓ |
| Exploit maturity | No known exploit ✓ |
| Introduced via | `tmp@0.0.0 › cryptography@41.0.7` ✓ |

**Description:**
Affected versions are vulnerable to Uncontrolled Resource Consumption due to improper input validation in the `EVP_PKEY_param_check` or `EVP_PKEY_public_check` functions. An attacker can cause a denial of service by supplying excessively long DSA keys or parameters from an untrusted source.

**Note:** OpenSSL does not call these functions on untrusted DSA keys by default — only applications that directly call them are vulnerable. Also affects the `openssl pkey -check` and `openssl pkeyparam -check` CLI commands.

**Remediation:** Upgrade `cryptography` to `>=42.0.8`. Note: since other cryptography issues require `>=46.0.5`, that version covers this finding too.

---

## Key Observations

**All 18 findings confirmed.** All resolvable via dependency upgrades — no changes to own code needed.

### Minimum versions to resolve everything

| Package | Min version | Findings covered |
|---------|-------------|-----------------|
| `cryptography` | `46.0.5` | 9 findings (#1,2,7,12,13,15,16,17,18) |
| `urllib3` | `2.6.3` | 5 findings (#3,4,5,10,11) |
| `requests` | `2.32.4` | 2 findings (#8,14) |
| `certifi` | `2024.7.4` | 1 finding (#6) |
| `idna` | `3.7` | 1 finding (#9) |

### Severity breakdown (confirmed)

| Severity | Count | Packages |
|----------|-------|---------|
| High | 6 | cryptography (3), urllib3 (3) |
| Medium | 10 | cryptography (4), urllib3 (2), requests (2), certifi (1), idna (1) |
| Low | 2 | cryptography (2) |
| **Total** | **18** | |

> Note: original PDF filter showed "8 High" — likely counted using a different CVSS version threshold. Confirmed badge counts from report text: 6 High, 10 Medium, 2 Low.

### Other observations
- `requests` pulls in `urllib3` transitively — coordinated upgrade needed
- PoC exploits confirmed for: `cryptography` Marvin attack (#2), `certifi` (#6), `requests` netrc leak (#8)
- `cryptography` is the most affected package: **9 of 18 findings**
- The two Low findings (#17, #18) require very specific server configurations — low practical risk

---

## Next Steps

- [ ] Check current pinned versions in `pyproject.toml` / `requirements*.txt`
- [ ] Create Jira Bug tickets as children of RAISE-295
- [ ] Apply upgrades and run full test suite

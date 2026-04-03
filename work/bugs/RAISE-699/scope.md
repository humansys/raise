# RAISE-699 — Fix JS dependency vulnerabilities in docs site

WHAT:      10 vulnerabilities in site/ (docs frontend) detected by Snyk monitor.
           Affected packages: h3 (3), rollup (1), ajv (1), devalue (4), lodash (1).
           Severity: 4 High, 5 Medium, 1 Low.
WHEN:      Present in current site/package-lock.json. Triggered on any npm install
           from package.json without overrides pinning safe versions.
WHERE:     site/package.json — overrides section (transitive deps, no direct dep fix needed)
EXPECTED:  All 10 Snyk findings resolved. snyk monitor reports 0 vulnerabilities in
           raise-docs project.
Done when: site/package.json overrides pin all affected packages to fixed versions,
           npm install succeeds, snyk monitor snapshot shows 0 vulnerabilities.

## Vulnerabilities

| Package  | ID                          | Severity | Fix version |
|----------|-----------------------------|----------|-------------|
| h3       | SNYK-JS-H3-15762218         | High     | >=1.15.9    |
| h3       | SNYK-JS-H3-15745711         | High     | >=1.15.9    |
| h3       | SNYK-JS-H3-15746329         | Medium   | >=1.15.9    |
| rollup   | CVE-2026-27606              | High     | >=4.59.0    |
| ajv      | CVE-2025-69873              | High     | >=8.18.0    |
| devalue  | SNYK-JS-DEVALUE-15479704    | Medium   | >=5.6.4     |
| devalue  | SNYK-JS-DEVALUE-15467451    | Medium   | >=5.6.4     |
| devalue  | SNYK-JS-DEVALUE-15322686    | Medium   | >=5.6.3     |
| devalue  | SNYK-JS-DEVALUE-15322689    | Low      | >=5.6.3     |
| lodash   | CVE-2025-13465              | Medium   | >=4.17.23   |

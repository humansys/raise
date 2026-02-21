# Evidence Catalog: Plugin & Extension Ecosystem Patterns

> Research context: How established ecosystems handle distributing updateable content
> that users can customize. Applicable to RaiSE CLI distributing markdown skill files.

---

## Ecosystem Analysis

### EC-1: VS Code Extensions

#### Separation Model
Extensions are installed as opaque packages from the Marketplace. User customizations live in separate layers:
- **Extension-provided snippets**: Bundled in the extension package, read-only to the user.
- **User-defined snippets**: Stored in `~/.config/Code/User/snippets/` (global) or `.vscode/` (workspace). Completely separate files.
- **Settings**: Extensions declare defaults via `contributes.configuration` in `package.json`. Users override in `settings.json` at user or workspace level.
- **Key insight**: Extension content and user content are *never in the same file*. They occupy separate layers in a cascade.

#### Override Mechanism
- Settings cascade: Default < Extension defaults < User settings < Workspace settings < Language-specific.
- Snippets: User snippets coexist with extension snippets; no override, just additive.
- Extensions can provide `configurationDefaults` to set defaults for *other* settings (e.g., language-specific editor behavior), but users always have final say.

#### Update Flow
- Extensions auto-update by default (checks Marketplace for new versions).
- Users can disable auto-update globally or per-extension.
- VSIX-installed extensions have auto-update disabled by default.
- User customizations are *never touched* by extension updates because they live in separate files.

#### Conflict Resolution
- No conflict is possible by design: extension content is read-only, user content is separate.
- When an extension updates its default settings, user overrides continue to take precedence.
- If an extension removes a setting key, the user's orphaned override is silently ignored.

#### Version Pinning
- "Install Another Version" UI lets users pick specific versions.
- VSIX sideloading pins to that exact version.
- `extensions.autoUpdate` setting controls global behavior.
- No lock file equivalent; version state is per-machine.

**Evidence Level**: High
**Sources**:
- [VS Code Snippets Documentation](https://code.visualstudio.com/docs/editing/userdefinedsnippets)
- [VS Code Contribution Points API](https://code.visualstudio.com/api/references/contribution-points)
- [VS Code Extension Marketplace](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace)
- [VS Code User and Workspace Settings](https://code.visualstudio.com/docs/configure/settings)
- [Prevent VS Code Extensions Auto-Updates](https://www.nicoespeon.com/en/2020/10/prevent-vscode-extensions-automatic-updates/)

---

### EC-2: Terraform Providers

#### Separation Model
- **Provider code**: Downloaded to `.terraform/providers/` during `terraform init`. Never edited by users.
- **User configuration**: `.tf` files declare `required_providers` with version constraints. Users write resource blocks; providers supply the schema.
- **Lock file**: `.terraform.lock.hcl` records exact versions + checksums. Committed to VCS.
- **Key insight**: Providers are pure dependencies. The "framework content" is the provider binary; the "user content" is the `.tf` configuration. They never overlap.

#### Override Mechanism
- Users don't customize provider internals. They configure *behavior* via resource arguments.
- Provider schemas define what's configurable; users fill in the blanks.
- No concept of "patching" a provider — you either use it or fork it.

#### Update Flow
1. User updates version constraint in `required_providers` block.
2. Runs `terraform init -upgrade`.
3. Terraform downloads newest version matching constraints.
4. Lock file is updated with new version + checksums.
5. User reviews lock file diff in VCS.

#### Conflict Resolution
- Lock file vs. constraints: Lock file wins by default. `-upgrade` flag overrides.
- If a provider introduces breaking changes, `terraform plan` fails with clear errors.
- Major version upgrade guides are published per-provider (e.g., AWS provider v3 -> v4).
- No automatic migration; users must update their `.tf` files manually.

#### Version Pinning
- Constraint syntax: `~> 4.0` (pessimistic, allows 4.x), `>= 4.0, < 5.0` (range), `= 4.67.0` (exact).
- Lock file provides exact-version reproducibility across team.
- Best practice: Commit lock file, use `-upgrade` intentionally, review changes.

**Evidence Level**: Very High
**Sources**:
- [HashiCorp: Lock and Upgrade Provider Versions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/provider-versioning)
- [HashiCorp: Dependency Lock File](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [Terraform AWS Provider v4 Upgrade Guide](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/guides/version-4-upgrade)
- [Terraform Versioning Best Practices — Dustin Dortch](https://dustindortch.com/2024/02/29/terraform-best-practices-versioning/)

---

### EC-3: ESLint Shared Configs

#### Separation Model
- **Shared config**: npm package (`eslint-config-*`) exports an array of config objects.
- **User config**: `eslint.config.js` (flat config) — a JavaScript array where entries are merged top-to-bottom.
- **Key insight**: Both shared and user configs are *the same data structure* (arrays of config objects). Separation is by position in the array, not by file boundary.

#### Override Mechanism
- **Array composition**: Later entries in the flat config array win over earlier entries.
- **`extends` keyword** (reintroduced March 2025): Allows declaring a shared config inline with overrides in the same config object.
- **File-scoped overrides**: Config objects with `files` glob patterns apply only to matching files.
- Pattern: Import shared config first, add your overrides after. Last writer wins.

```javascript
// User's eslint.config.js
import sharedConfig from "eslint-config-mycompany";
export default [
  ...sharedConfig,           // Framework rules (base)
  {
    rules: {
      "no-console": "off",   // User override — wins because it's later
    },
  },
];
```

#### Update Flow
- `npm update eslint-config-*` pulls new version.
- User overrides are untouched because they're in a separate file (`eslint.config.js`).
- If shared config adds new rules, they apply automatically.
- If shared config changes severity of existing rules, user overrides still win.

#### Conflict Resolution
- No merge conflicts — it's runtime composition, not file merging.
- If a rule is removed from the shared config, user overrides of that rule become no-ops (orphaned but harmless).
- Breaking changes (new rule that errors) are communicated via semver major bumps.

#### Version Pinning
- Standard npm versioning: `^2.0.0`, `~2.1.0`, `2.1.3` (exact).
- `package-lock.json` provides reproducibility.
- No special mechanism beyond npm.

**Evidence Level**: Very High
**Sources**:
- [ESLint: Share Configurations](https://eslint.org/docs/latest/extend/shareable-configs)
- [ESLint: Configuration Files (Flat Config)](https://eslint.org/docs/latest/use/configure/configuration-files)
- [ESLint: Evolving Flat Config with Extends (March 2025)](https://eslint.org/blog/2025/03/flat-config-extends-define-config-global-ignores/)
- [ESLint: Flat Config Introduction](https://eslint.org/blog/2022/08/new-config-system-part-2/)

---

### EC-4: Prettier Shared Configs

#### Separation Model
- **Shared config**: npm package exporting a Prettier config object.
- **User config**: `.prettierrc.js` or similar, imports and spreads the shared config.
- **Key insight**: No native `extends` mechanism. User must explicitly import and spread.

#### Override Mechanism
- Object spread / `Object.assign`: User imports shared config, spreads it, then overrides specific keys.
- This is manual composition — the user is responsible for the merge.

```javascript
// .prettierrc.js
module.exports = {
  ...require("@mycompany/prettier-config"),
  semi: false,  // local override
};
```

#### Update Flow
- `npm update @mycompany/prettier-config` pulls new version.
- User's spread-then-override pattern means new keys from upstream are automatically inherited.
- Changed keys in upstream are overridden by user's explicit settings.

#### Conflict Resolution
- No automatic conflict resolution — it's JavaScript object spread.
- If upstream adds a key the user also sets, user's value wins (spread order).
- If upstream removes a key, user's override becomes the sole source (no conflict).

#### Version Pinning
- Standard npm versioning via `package.json` + lock file.
- Shared configs must list plugins as `dependencies` (not `devDependencies`) for child project installation.

**Evidence Level**: High
**Sources**:
- [Prettier: Sharing Configurations](https://prettier.io/docs/sharing-configurations)
- [Prettier Issue #7763: Extending Shared Config in JSON](https://github.com/prettier/prettier/issues/7763)
- [Toby Smith: Keep Prettier Configurations in Sync](https://tobysmith.uk/blog/prettier-config)

---

### EC-5: GitHub Actions (Reusable Workflows)

#### Separation Model
- **Action/workflow definition**: Lives in the action's repository (action.yml + scripts).
- **Caller workflow**: Lives in the consuming repository. References action by `owner/repo@ref`.
- **Inputs/outputs**: Actions declare inputs with defaults in `action.yml`; callers override via `with:`.
- **Key insight**: Action code is *remote and immutable* from the caller's perspective. Customization is only through declared input parameters.

#### Override Mechanism
- Callers pass `with:` parameters to override action defaults.
- No way to "patch" an action's internal logic — only configure it through its declared interface.
- Reusable workflows accept `inputs` via `workflow_call`; callers override with `with:`.
- If more customization is needed, fork the action.

#### Update Flow
- **Tag reference** (`@v2`): Gets latest commit on that tag. Tag can be moved (mutable).
- **Branch reference** (`@main`): Always gets HEAD. Maximum drift risk.
- **SHA reference** (`@a1b2c3d...`): Immutable. Only way to guarantee reproducibility.
- Updates are explicit: user changes the ref in their workflow file.
- Dependabot/Renovate can automate SHA/tag updates with PRs.

#### Conflict Resolution
- No merge conflict possible — action code is remote, caller code is local.
- If an action removes an input, caller's workflow fails at parse time (clear error).
- Breaking changes communicated via major version tags (`@v2` -> `@v3`).

#### Version Pinning
- **SHA pinning** (recommended for security): `uses: actions/checkout@a1b2c3d4...  # v4.1.0`
- **Tag pinning**: `uses: actions/checkout@v4` (major version floating) or `@v4.1.0` (exact).
- **Branch pinning**: `uses: actions/checkout@main` (never for production).
- Enterprise policies can enforce SHA pinning.
- Common pattern: SHA pin + comment with tag for readability.

**Evidence Level**: Very High
**Sources**:
- [GitHub Docs: Workflow Syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Docs: Reusing Workflow Configurations](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [GitHub Well-Architected: Actions Security](https://wellarchitected.github.com/library/application-security/recommendations/actions-security/)
- [StepSecurity: Pinning GitHub Actions for Enhanced Security](https://www.stepsecurity.io/blog/pinning-github-actions-for-enhanced-security-a-complete-guide)
- [Rafael GSS: Why You Should Pin by Commit Hash](https://blog.rafaelgss.dev/why-you-should-pin-actions-by-commit-hash)

---

### EC-6: Helm Charts

#### Separation Model
- **Chart templates**: `.tpl` and YAML templates in `templates/` directory. Owned by chart maintainer.
- **Default values**: `values.yaml` in chart root. Maintainer's defaults.
- **User values**: Separate file (e.g., `my-values.yaml`) passed via `-f` flag. User-owned.
- **Key insight**: Clean separation between *template logic* (chart author) and *configuration values* (chart user). Users never edit templates directly.

#### Override Mechanism
- **Values cascade** (lowest to highest priority):
  1. `values.yaml` (chart defaults)
  2. Parent chart's `values.yaml`
  3. User-supplied values file (`-f my-values.yaml`)
  4. `--set` / `--set-string` / `--set-json` command-line flags
- Multiple `-f` files can be layered: `helm install -f base.yaml -f env.yaml -f secrets.yaml` (rightmost wins).
- Deep merge for nested objects; last value wins for scalars.
- `values.schema.json` validates user-supplied values against a JSON Schema.

#### Update Flow
1. Chart maintainer publishes new version to chart repository.
2. User runs `helm repo update` to refresh index.
3. User runs `helm upgrade myrelease mychart --version X.Y.Z -f my-values.yaml`.
4. Templates are re-rendered with new chart logic + user's existing values.
5. User's values file is *never modified* by the upgrade.

#### Conflict Resolution
- If new chart version adds a required value, `helm upgrade` fails with schema validation error.
- If new chart version changes default structure, user's overrides may become stale (orphaned keys).
- `helm diff` plugin shows what would change before applying.
- Major version bumps signal breaking value schema changes.

#### Version Pinning
- `--version X.Y.Z` in helm commands.
- `Chart.lock` for dependency charts (like package-lock.json).
- Charts follow SemVer: MAJOR for values schema breaks, MINOR for new optional values, PATCH for fixes.

**Evidence Level**: Very High
**Sources**:
- [Helm: Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Helm: Charts](https://helm.sh/docs/topics/charts/)
- [Helm: Best Practices — Conventions](https://helm.sh/docs/chart_best_practices/conventions/)
- [Helm Advanced Guide: Values, Overrides, Dependencies](https://medium.com/@bavicnative/helm-advanced-values-overrides-and-dependencies-35976b996143)
- [Helm Chart Versioning Strategies](https://oneuptime.com/blog/post/2026-01-17-helm-chart-versioning-strategies/view)

---

### EC-7: Kustomize

#### Separation Model
- **Base**: Directory with vanilla Kubernetes manifests + `kustomization.yaml`. Can be a remote git URL.
- **Overlay**: Directory that references a base and applies patches/transforms. User-owned.
- **Key insight**: The base is *never modified*. All customization happens in overlays via declarative patches. This is the purest "upstream content + user overrides" pattern.

#### Override Mechanism
- **Strategic merge patches**: YAML fragments that are deep-merged into base resources. Only specify fields you want to change.
- **JSON 6902 patches**: Precise add/remove/replace operations on specific JSON paths.
- **Transformers**: Cross-cutting changes (add namespace, add labels, change image tags) applied to all resources.
- **Generators**: Create new resources (ConfigMaps, Secrets) from files or literals.
- Overlays compose: `base/` -> `overlays/staging/` -> `overlays/production/`.

#### Update Flow
- **Local base**: `git pull` upstream changes. Overlays are in separate directories — no file conflicts.
- **Remote base**: Reference via URL with `?ref=v1.2.0` (git tag/SHA). Change ref to update.
- Kustomize re-applies patches on each `kustomize build`. If base changes, patches merge with new base.
- Stated philosophy: "Ingest any base file updates while keeping use-case specific customization overrides intact."

#### Conflict Resolution
- If a patch targets a field that no longer exists in the base, the build fails with a clear error.
- If base adds a field that a patch also sets, the patch wins (overlay priority).
- Strategic merge patches are more resilient to base changes than JSON patches (they match by kind+name, not by array index).
- No automatic "three-way merge" — patches are applied fresh each time.

#### Version Pinning
- Remote bases: `?ref=v1.0.0` (tag), `?ref=abc123` (SHA), `?ref=main` (branch).
- Local bases: Pinned by git commit in the same or referenced repository.
- No built-in lock file; version control of the base reference is manual.

**Evidence Level**: Very High
**Sources**:
- [Kustomize.io](https://kustomize.io/)
- [Kustomize GitHub: Remote Build](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md)
- [Replicated Docs: Patching with Kustomize](https://docs.replicated.com/enterprise/updating-patching-with-kustomize)
- [Glasskube: Complete Kustomize Tutorial](https://glasskube.dev/blog/patching-with-kustomize/)
- [Kustomize Overlays for Environment-Specific Configurations](https://oneuptime.com/blog/post/2026-02-09-kustomize-overlays-environments/view)

---

### EC-BONUS: Cookiecutter + Cruft (Template Distribution)

#### Separation Model
- **Template**: A git repository with Jinja2-templated files + `cookiecutter.json` (variables).
- **Generated project**: Output of running `cookiecutter` against the template. User-owned, editable.
- **Cruft metadata**: `.cruft.json` in generated project records template origin + commit hash.
- **Key insight**: Most template tools are "generate and abandon." Cruft solves the ongoing update problem.

#### Override Mechanism
- Users edit generated files freely — they own them completely.
- No runtime composition; the generated files ARE the user's files.
- Cruft tracks which template version generated the project.

#### Update Flow (Cruft)
1. `cruft check` — validates if project is up-to-date with template.
2. `cruft diff` — shows changes between current project and latest template (like `git diff`).
3. `cruft update` — applies template changes as a git merge. User resolves conflicts.
4. Can be added to CI pipelines for drift detection.

#### Conflict Resolution
- **Git-style three-way merge**: Cruft compares (a) user's current files, (b) what the template produced at generation time, (c) what the template produces now. Conflicts shown as git merge conflicts.
- This is the ONLY ecosystem studied that does true three-way merge on user-customized content.

#### Version Pinning
- `.cruft.json` records the template repo URL + commit SHA.
- `cruft update --checkout TAG` can target specific versions.
- No constraint syntax; it's always a specific commit or tag.

**Evidence Level**: High
**Sources**:
- [Cruft Documentation](https://cruft.github.io/cruft/)
- [Cruft GitHub](https://github.com/cruft/cruft)
- [Cookiecutter with Cruft for Platform Engineering — John Miller](https://john-miller.dev/posts/cookiecutter-with-cruft-for-platform-engineering/)
- [Cookiecutter Guide — Cortex](https://www.cortex.io/post/an-overview-of-cookiecutter)

---

## Cross-Ecosystem Pattern Summary

| Dimension | VS Code | Terraform | ESLint | Prettier | GH Actions | Helm | Kustomize | Cruft |
|-----------|---------|-----------|--------|----------|-------------|------|-----------|-------|
| **Separation** | Layered files | Dependency | Array position | Object spread | Remote ref | Values vs templates | Base vs overlay | Generated + metadata |
| **User edits upstream?** | Never | Never | Never | Never | Never | Never | Never | Always |
| **Override mechanism** | Settings cascade | Config args | Later-entry-wins | Spread + override | Input params | Values hierarchy | Patches | Direct edit |
| **Update conflicts** | Impossible | Plan fails | N/A (runtime) | N/A (runtime) | Parse fails | Schema validation | Build fails | 3-way merge |
| **Version pinning** | UI / VSIX | Constraints + lock | npm semver + lock | npm semver + lock | SHA / tag / branch | --version + Chart.lock | ?ref= param | .cruft.json SHA |

---

## Key Patterns for RaiSE Skill Distribution

### Pattern 1: "Layer Cake" (VS Code, Helm)
**Framework content and user content occupy separate layers/files.** User never edits framework files. Customization happens through a parallel override layer.
- **Applicability to RaiSE**: HIGH. Skills could have a "base" layer (from `rai`) and an "override" layer (user's `.raise/`).
- **Pros**: No merge conflicts ever. Clean updates.
- **Cons**: User can't modify framework logic, only configure it.

### Pattern 2: "Array Composition" (ESLint)
**Both framework and user content are the same data structure.** Composition order determines precedence (last writer wins).
- **Applicability to RaiSE**: MEDIUM. Would require skills to be composable units rather than monolithic markdown files.
- **Pros**: Very flexible. Users can insert content between framework entries.
- **Cons**: More complex mental model. Requires skills to be designed as composable fragments.

### Pattern 3: "Overlay / Patch" (Kustomize)
**Framework provides the base. User provides declarative patches that modify specific parts.** Patches are re-applied on every build.
- **Applicability to RaiSE**: MEDIUM-HIGH. Users could have "skill patches" that add/remove/modify sections of base skills.
- **Pros**: Very precise customization. Base updates are automatic.
- **Cons**: Patches can break when base structure changes. Requires a patch format specification.

### Pattern 4: "Generate + Track" (Cruft/Cookiecutter)
**Framework generates files into user's workspace. Metadata tracks origin version.** Updates use three-way merge.
- **Applicability to RaiSE**: HIGH. Most directly applicable — skills are generated markdown files that users might edit.
- **Pros**: Users have full editing freedom. Updates show diffs. Familiar git workflow.
- **Cons**: Merge conflicts are possible. Requires tracking metadata per file.

### Pattern 5: "Immutable Reference" (GitHub Actions, Terraform)
**Framework content is remote and immutable.** Users configure it through declared inputs but cannot modify internals.
- **Applicability to RaiSE**: LOW for skills (too rigid), but useful for version pinning model.
- **Pros**: Zero drift. Reproducible.
- **Cons**: No customization of content, only configuration.

---

## Recommendation for RaiSE

The most applicable patterns for a CLI distributing markdown skill files are:

1. **Primary: Layer Cake** (Pattern 1) — Separate `base/` skills (managed by `rai`, read-only) from `local/` skills (user-editable). Similar to Helm's values.yaml vs user values.

2. **Secondary: Generate + Track** (Pattern 4) — For users who need deep customization, allow "ejecting" a skill from base to local, tracking the origin version (like `.cruft.json`). Updates can offer three-way merge or diff review.

3. **Version pinning: Terraform-style constraints** — Users pin skill pack versions in config. Lock file records exact versions. `rai skill update` is explicit, not automatic.

This hybrid gives us: zero-conflict updates for most users (Layer Cake), full customization escape hatch (Generate + Track), and reproducibility (version pinning).

---
name: rai-mr-create
description: Create a governed GitLab MR or GitHub PR through provider-specific admission.
model: haiku

allowed-tools:
  - Bash
  - Read
  - Write

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "9"
  raise.prerequisites: epic-close
  raise.next: null
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.5.0"
  raise.visibility: public
  raise.inputs: |
    - source_branch: string, required, bound as RAI_SOURCE_BRANCH data
    - target_branch: string, required, bound as RAI_TARGET_BRANCH data
    - work_id: string, required, bound as RAI_WORK_ID data
    - quality_review_file: file_path, required, committed qr.md
    - title_file: file_path, required, exact MR title as data
    - description_file: file_path, required, human-readable MR body as data
  raise.outputs: |
    - mr_url: string, GitLab MR or GitHub PR URL
---

# MR Create

## Purpose

Create a reviewable MR/PR through the configured provider. THIN admission is GitLab-only:
GitLab `rules:changes` selects integration jobs, project policy
blocks a red pipeline, and daily-full owns complete release assurance. GitHub
retains the local full-gate path until equivalent remote enforcement exists.

## Mastery Levels

- **Shu:** Inspect every bound input and admission result.
- **Ha:** Execute autonomously; stop on the first failed control.
- **Ri:** Integrate this exact contract into release automation without bypasses.

## Context

Use after scoped lifecycle checks and independent quality review. Human text is
written to files with the Write tool, never interpolated into shell source.
The runtime binds the six inputs to the named `RAI_*` environment variables.

## Steps

### Step 1: Bind and validate data inputs

Bind source, target, work ID, committed QR path, title file, and description
file as environment data. Git validates both branch names. Invalid refs,
including refs with spaces, block. Git-valid metacharacters remain literal data.

### Step 2: Synchronize target

Require a clean expected branch, fetch the exact target ref, and merge it when
needed. A conflict or dirty result stops before any push.

### Step 3: Bind quality review

The committed QR must name the same issue and contain exact 40-character
`Reviewed implementation` and `Synchronized target` SHAs. The reviewed target
must still equal the fetched target. HEAD may follow the reviewed implementation
only through same-issue `qr`, `retro`, or `pir` Markdown/HTML commits. Any code,
configuration, skill, foreign-issue, merge, missing, or malformed evidence
requires a new review.

### Step 4: Local admission

Run governance artifact/trail gates, the scoped GitLab CI contract, GitLab CI
lint, successful-pipeline policy, and active target daily-full schedule checks.
Every command is fail-fast.

### Step 5: Push and create MR

Push only after admission. Build the MR body from data files and exact SHAs;
then create the MR through `glab`. No manual glab/gh bypass or push-only mode is
defined. The executable contract below is the GitLab path. When
`branches.scm: github` is configured, use the separate GitHub contract after it.

Execute the steps as one shell contract. Do not split it into independent shell
blocks: `set -euo pipefail` and ordering are part of the safety boundary.

```bash
# RAISE_MR_CREATE_CONTRACT_BEGIN
set -euo pipefail

die() {
  printf 'rai-mr-create: %s\n' "$1" >&2
  exit 1
}

: "${RAI_SOURCE_BRANCH:?RAI_SOURCE_BRANCH is required}"
: "${RAI_TARGET_BRANCH:?RAI_TARGET_BRANCH is required}"
: "${RAI_WORK_ID:?RAI_WORK_ID is required}"
: "${RAI_QR_FILE:?RAI_QR_FILE is required}"
: "${RAI_TITLE_FILE:?RAI_TITLE_FILE is required}"
: "${RAI_DESCRIPTION_FILE:?RAI_DESCRIPTION_FILE is required}"

SOURCE_BRANCH="$RAI_SOURCE_BRANCH"
TARGET_BRANCH="$RAI_TARGET_BRANCH"
WORK_ID="$RAI_WORK_ID"
QR_FILE="$RAI_QR_FILE"
TITLE_FILE="$RAI_TITLE_FILE"
DESCRIPTION_FILE="$RAI_DESCRIPTION_FILE"

[[ "$WORK_ID" =~ ^[A-Z][A-Z0-9]+-[0-9]+$ ]] || die "invalid work ID"
git check-ref-format --branch "$SOURCE_BRANCH" >/dev/null 2>&1 || die "invalid source branch"
git check-ref-format --branch "$TARGET_BRANCH" >/dev/null 2>&1 || die "invalid target branch"
case "$QR_FILE" in
  ""|/*|../*|*/../*|*/..|*$'\n'*) die "QR path must be repository-relative" ;;
esac
[[ "$QR_FILE" == work/*/qr.md ]] || die "QR path must end in work/.../qr.md"
[[ -f "$TITLE_FILE" && ! -L "$TITLE_FILE" ]] || die "title file is missing or unsafe"
[[ -f "$DESCRIPTION_FILE" && ! -L "$DESCRIPTION_FILE" ]] || die "description file is missing or unsafe"

REPO_ROOT=$(git rev-parse --show-toplevel)
cd -- "$REPO_ROOT"
CURRENT_BRANCH=$(git branch --show-current)
[[ "$CURRENT_BRANCH" == "$SOURCE_BRANCH" ]] || die "unexpected source branch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "working tree is dirty"
[[ -z "$(git diff --name-only --diff-filter=U)" ]] || die "unresolved conflicts exist"

TARGET_REF="refs/remotes/origin/$TARGET_BRANCH"
git fetch --no-tags origin "+refs/heads/$TARGET_BRANCH:$TARGET_REF"
git show-ref --verify --quiet "$TARGET_REF" || die "fetched target ref is missing"
if ! git merge-base --is-ancestor "$TARGET_REF" HEAD; then
  git merge --no-edit "$TARGET_REF"
fi
[[ -z "$(git diff --name-only --diff-filter=U)" ]] || die "target merge conflicted"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "synchronization left a dirty tree"

SOURCE_SHA=$(git rev-parse --verify "HEAD^{commit}")
TARGET_SHA=$(git rev-parse --verify "${TARGET_REF}^{commit}")
QR_TEXT=$(git show "${SOURCE_SHA}:${QR_FILE}")
QR_FIELDS=$(printf '%s\n' "$QR_TEXT" | RAI_QR_WORK_ID="$WORK_ID" python3 -c '
import os, re, sys
text = sys.stdin.read()
work_id = re.escape(os.environ["RAI_QR_WORK_ID"])
if re.search(rf"^# Quality Review: {work_id}\s*$", text, re.MULTILINE) is None:
    raise SystemExit("QR work ID is missing or mismatched")
implementation = re.search(r"^Reviewed implementation: `([0-9a-f]{40})`\s*$", text, re.MULTILINE)
target = re.search(r"^Synchronized target: `([0-9a-f]{40})`\s*$", text, re.MULTILINE)
if implementation is None or target is None:
    raise SystemExit("QR reviewed implementation/target SHA is missing or malformed")
print(f"{implementation.group(1)}\t{target.group(1)}")
')
IFS=$'\t' read -r REVIEWED_IMPLEMENTATION_SHA REVIEWED_TARGET_SHA <<< "$QR_FIELDS"
[[ "$REVIEWED_TARGET_SHA" == "$TARGET_SHA" ]] || die "target drifted after quality review"

GOVERNANCE_ROOT=$(dirname -- "$QR_FILE")
validate_reviewed_history() {
  local current_sha="$1"
  local commit_sha
  local changed_file
  local changed_files

  git merge-base --is-ancestor "$REVIEWED_TARGET_SHA" "$REVIEWED_IMPLEMENTATION_SHA" || die "reviewed target is not an ancestor of reviewed implementation"
  git merge-base --is-ancestor "$REVIEWED_IMPLEMENTATION_SHA" "$current_sha" \
    || die "reviewed implementation is not an ancestor"
  while IFS= read -r commit_sha; do
    [[ -n "$commit_sha" ]] || continue
    changed_files=$(git diff-tree --root -m --no-commit-id --name-only -r "$commit_sha" | sort -u)
    [[ -n "$changed_files" ]] || die "post-review commit has no allowed governance artifact"
    while IFS= read -r changed_file; do
      case "$changed_file" in
        "$GOVERNANCE_ROOT/qr.md"|"$GOVERNANCE_ROOT/qr.html"|\
        "$GOVERNANCE_ROOT/retro.md"|"$GOVERNANCE_ROOT/retro.html"|\
        "$GOVERNANCE_ROOT/pir.md"|"$GOVERNANCE_ROOT/pir.html") ;;
        *) die "post-review change requires re-review: $changed_file" ;;
      esac
    done <<< "$changed_files"
  done < <(git rev-list --reverse "$REVIEWED_IMPLEMENTATION_SHA..$current_sha")
}
validate_reviewed_history "$SOURCE_SHA"

rai gate check gate-governance-artifacts
rai gate check governance-trail-ci
rai gate check gate-tests --scope packages/raise-cli/tests/ci/test_gitlab_ci.py
glab ci lint .gitlab-ci.yml

PROJECT_JSON=$(glab api projects/:id)
MERGE_POLICY=$(printf '%s\n' "$PROJECT_JSON" | python3 -c '
import json, sys
print(str(json.load(sys.stdin).get("only_allow_merge_if_pipeline_succeeds", False)).lower())
')
[[ "$MERGE_POLICY" == true ]] || die "GitLab must require successful pipelines"

SCHEDULE_JSON=$(glab api 'projects/:id/pipeline_schedules?per_page=100')
SCHEDULE_IDS=$(printf '%s\n' "$SCHEDULE_JSON" | RAI_SCHEDULE_TARGET="$TARGET_BRANCH" python3 -c '
import json, os, sys
target = os.environ["RAI_SCHEDULE_TARGET"]
refs = {target, f"refs/heads/{target}"}
print(" ".join(str(item["id"]) for item in json.load(sys.stdin)
               if item.get("active") is True and item.get("ref") in refs))
')
DAILY_FULL=""
for schedule_id in $SCHEDULE_IDS; do
  [[ "$schedule_id" =~ ^[0-9]+$ ]] || die "invalid schedule ID"
  SCHEDULE_DETAIL=$(glab api "projects/:id/pipeline_schedules/$schedule_id")
  if printf '%s\n' "$SCHEDULE_DETAIL" | python3 -c '
import json, sys
variables = json.load(sys.stdin).get("variables", [])
raise SystemExit(0 if any(item.get("key") == "SCHEDULE_TYPE" and
                          item.get("value") == "daily-full" for item in variables) else 1)
'; then
    DAILY_FULL="daily-full"
    break
  fi
done
[[ "$DAILY_FULL" == daily-full ]] || die "active target lacks daily-full schedule"

# PRE_PUSH_RECHECK_BEGIN
PRE_PUSH_BRANCH=$(git branch --show-current)
[[ "$PRE_PUSH_BRANCH" == "$SOURCE_BRANCH" ]] || die "branch changed during admission"
PRE_PUSH_SOURCE_SHA=$(git rev-parse --verify "HEAD^{commit}")
[[ "$PRE_PUSH_SOURCE_SHA" == "$SOURCE_SHA" ]] || die "HEAD changed during admission"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] \
  || die "working tree changed during admission"
[[ -z "$(git diff --name-only --diff-filter=U)" ]] \
  || die "conflicts appeared during admission"
git fetch --no-tags origin "+refs/heads/$TARGET_BRANCH:$TARGET_REF"
PRE_PUSH_TARGET_SHA=$(git rev-parse --verify "${TARGET_REF}^{commit}")
[[ "$PRE_PUSH_TARGET_SHA" == "$TARGET_SHA" ]] || die "target changed during admission"
validate_reviewed_history "$PRE_PUSH_SOURCE_SHA"
# PRE_PUSH_RECHECK_END

MR_TITLE=$(cat -- "$TITLE_FILE")
[[ -n "$MR_TITLE" ]] || die "MR title is empty"
MR_BODY_FILE=$(mktemp)
trap 'rm -f -- "$MR_BODY_FILE"' EXIT
cat -- "$DESCRIPTION_FILE" > "$MR_BODY_FILE"
cat >> "$MR_BODY_FILE" <<EOF

## Admission evidence

- Reviewed implementation SHA: $REVIEWED_IMPLEMENTATION_SHA
- Reviewed target SHA: $REVIEWED_TARGET_SHA
- Admitted source SHA: $SOURCE_SHA
- Admitted target SHA: $TARGET_SHA
- Local admission checks: governance artifact PASS; governance trail PASS; GitLab CI contract/lint PASS; merge policy PASS; daily-full PASS
- Integration pipeline: PENDING — GitLab pipeline success required before merge
EOF

git push origin "$SOURCE_BRANCH"
MR_URL=$(rai scm create-mr \
  --source "$SOURCE_BRANCH" \
  --target "$TARGET_BRANCH" \
  --title "$MR_TITLE" \
  --description-file "$MR_BODY_FILE" \
  --harness claude_code)
printf '%s\n' "$MR_URL"
# RAISE_MR_CREATE_CONTRACT_END
```

### GitHub local full-gate contract

This is intentionally not the THIN path. Use it only when
`branches.scm: github` is configured. Until GitHub has an equivalent checked
remote-policy contract, all four local gates remain prerequisites to PR
existence.

```bash
# RAISE_GITHUB_FULL_GATE_BEGIN
set -euo pipefail

die() {
  printf 'rai-mr-create: %s\n' "$1" >&2
  exit 1
}

: "${RAI_SOURCE_BRANCH:?RAI_SOURCE_BRANCH is required}"
: "${RAI_TARGET_BRANCH:?RAI_TARGET_BRANCH is required}"
: "${RAI_TITLE_FILE:?RAI_TITLE_FILE is required}"
: "${RAI_DESCRIPTION_FILE:?RAI_DESCRIPTION_FILE is required}"
SOURCE_BRANCH="$RAI_SOURCE_BRANCH"
TARGET_BRANCH="$RAI_TARGET_BRANCH"
TITLE_FILE="$RAI_TITLE_FILE"
DESCRIPTION_FILE="$RAI_DESCRIPTION_FILE"

git check-ref-format --branch "$SOURCE_BRANCH" >/dev/null 2>&1 || die "invalid source branch"
git check-ref-format --branch "$TARGET_BRANCH" >/dev/null 2>&1 || die "invalid target branch"
[[ -f "$TITLE_FILE" && ! -L "$TITLE_FILE" ]] || die "title file is missing or unsafe"
[[ -f "$DESCRIPTION_FILE" && ! -L "$DESCRIPTION_FILE" ]] || die "description file is missing or unsafe"
[[ "$(git branch --show-current)" == "$SOURCE_BRANCH" ]] || die "unexpected source branch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "working tree is dirty"

TARGET_REF="refs/remotes/origin/$TARGET_BRANCH"
git fetch --no-tags origin "+refs/heads/$TARGET_BRANCH:$TARGET_REF"
if ! git merge-base --is-ancestor "$TARGET_REF" HEAD; then
  git merge --no-edit "$TARGET_REF"
fi
[[ -z "$(git diff --name-only --diff-filter=U)" ]] || die "target merge conflicted"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "synchronization left a dirty tree"

rai gate check gate-tests
rai gate check gate-lint
rai gate check gate-format
rai gate check gate-types

git push origin "$SOURCE_BRANCH"
MR_URL=$(rai scm create-mr \
  --source "$SOURCE_BRANCH" \
  --target "$TARGET_BRANCH" \
  --title "$(cat -- "$TITLE_FILE")" \
  --description-file "$DESCRIPTION_FILE" \
  --harness claude_code)
printf '%s\n' "$MR_URL"
# RAISE_GITHUB_FULL_GATE_END
```

## Output

- Exact reviewed and admitted source/target SHAs in the MR body
- Local admission results and pending integration status in the MR body
- MR or PR URL presented to the developer

## Quality Checklist

- [ ] Inputs passed as data; refs and paths quoted and validated
- [ ] Target synchronized before review binding and admission
- [ ] QR binds same-issue reviewed implementation and target SHAs
- [ ] Only same-issue QR/retro/PIR artifacts follow the reviewed SHA
- [ ] Every local and live GitLab check is fail-fast
- [ ] No unscoped release suite or diagram regeneration runs locally
- [ ] Push and MR creation occur only after admission
- [ ] GitHub runs the retained local full-gate path before push/PR
- [ ] MR/PR created via `rai scm create-mr` — NEVER by calling `glab`/`gh`
      directly, which skips the governance block

## Dispatch and error handling

Both paths create the MR/PR through `rai scm create-mr`, which routes to the
configured `ScmAdapter` (RAISE-16770) and appends the `<!-- rai: ... -->`
governance provenance block unconditionally. There is no suppression flag: the
block is what `validate-mr-provenance` checks in CI, so a direct `glab mr
create` / `gh pr create` call produces an MR that fails admission.

A non-zero exit from `rai scm create-mr` means **no MR was created**. Report the
stderr message and stop. Do not fall back to `glab`/`gh`; the branch is already
pushed, so re-running the contract after fixing the cause is safe.

## References

- Integration selection: `.gitlab-ci.yml` MR `rules:changes`
- Release assurance: active target `SCHEDULE_TYPE=daily-full` schedule
- Review evidence producer: `/rai-quality-review`

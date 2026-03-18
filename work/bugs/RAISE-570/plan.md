# RAISE-570 — Plan

## Tasks

### T1 — Fix .gitlab-ci.yml: agregar git al apt-get install
File: .gitlab-ci.yml, línea 21
Change: `libatomic1` → `libatomic1 git`
Commit: `fix(RAISE-570): add git to CI container apt-get install`

### T2 — Push branch y crear MR
Push: `git push -u origin bug/raise-570/git-not-in-ci-container`
MR: target dev, título "fix(RAISE-570): add git to CI container"
Verification: pipeline CI verde — 4 tests verdes en job `test`

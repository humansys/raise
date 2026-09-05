# SCM Provider Support

| Provider | Status | CLI Tool | Notes |
|----------|--------|----------|-------|
| GitLab | Full | `glab` 1.36.0+ | create_mr, merge_mr, get_mr_ci_status |
| GitHub | Full | `gh` 2.x+ | create_pr, merge_pr, get_pr_ci_status |
| Azure DevOps | Stub | `az devops` | Raises NotImplementedError — see RAISE-16775 |
| Bitbucket | Stub | Bitbucket API | Raises NotImplementedError — see RAISE-16775 |

Full providers: create + merge + CI status all implemented.
Stubs: NotImplementedError raised with instructions for implementers.

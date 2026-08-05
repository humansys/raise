"""Ontology type -> Jira issue-type mapping config (S3, RAISE-14642 T3).

`rai backlog create -t <type>` needs a mapping from the 5-level local
ontology (theme/initiative/epic/story/task) to whatever Jira issue-type
name backs it on the remote — projects vary (some have a "Theme" issue
type, most don't). `load_types_config` mirrors `backlog_config.py`'s
load-with-fallback shape: `.raise/types.yaml` if present, else embedded
defaults, so `rai backlog create -t epic ...` works out of the box with
zero manual config (AC6).

Defaults are **identity-preserving** (`epic -> Epic`, `story -> Story`,
`initiative -> Initiative`, `task -> Task`) with `theme` falling back to
the Jira `Initiative` issue-type too, since most Jira/Advanced-Roadmaps
projects (including RAISE's own) have no separate `Theme` issue type and
no runtime "does this project have a Theme issue type" introspection is
built (YAGNI, s3-plan.md "Plan-time clarification", D4). The local
`work_items.type` column still distinguishes theme vs. initiative rows
regardless of which Jira issue-type backs them.

Per-project override template — copy to `.raise/types.yaml` and adjust
`jira_issue_type` per row:

```yaml
types:
  theme:      {jira_issue_type: Initiative, parent_resolution: null,       no_portfolio_default: false}
  initiative: {jira_issue_type: Initiative, parent_resolution: theme,      no_portfolio_default: false}
  epic:       {jira_issue_type: Epic,       parent_resolution: initiative, no_portfolio_default: false}
  story:      {jira_issue_type: Story,      parent_resolution: epic,      no_portfolio_default: false}
  task:       {jira_issue_type: Task,       parent_resolution: story,      no_portfolio_default: true}
```
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

_TYPES_YAML_PATH = Path(".raise") / "types.yaml"


class TypeConfig(BaseModel):
    """Per-ontology-type mapping to a Jira issue-type + parent-resolution hint."""

    jira_issue_type: str
    parent_resolution: str | None = None
    no_portfolio_default: bool = False


class TypesConfig(BaseModel):
    """Ontology type name -> `TypeConfig`."""

    types: dict[str, TypeConfig]


_DEFAULT_TYPES_CONFIG = TypesConfig(
    types={
        "theme": TypeConfig(
            jira_issue_type="Initiative",
            parent_resolution=None,
            no_portfolio_default=False,
        ),
        "initiative": TypeConfig(
            jira_issue_type="Initiative",
            parent_resolution="theme",
            no_portfolio_default=False,
        ),
        "epic": TypeConfig(
            jira_issue_type="Epic",
            parent_resolution="initiative",
            no_portfolio_default=False,
        ),
        "story": TypeConfig(
            jira_issue_type="Story",
            parent_resolution="epic",
            no_portfolio_default=False,
        ),
        "task": TypeConfig(
            jira_issue_type="Task",
            parent_resolution="story",
            no_portfolio_default=True,
        ),
    }
)


def load_types_config(project_root: Path) -> TypesConfig:
    """Load `.raise/types.yaml` if present, else return embedded defaults.

    Never raises for a missing file (AC6 — the command works with zero
    manual config). Raises `pydantic.ValidationError` for a malformed
    section (e.g. a type entry missing `jira_issue_type`).
    """
    config_path = project_root / _TYPES_YAML_PATH
    if not config_path.exists():
        return _DEFAULT_TYPES_CONFIG

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return TypesConfig.model_validate(raw)

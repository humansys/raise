"""Jira configuration — legacy module.

RAISE-1052 (S1052.2) — original schema
RAISE-2316 (S2503.1) — CustomField
RAISE-2723 (S2503.12) — load_jira_config reads from backlog.yaml via migration
RAISE-2751 (S2503.14) — custom_fields: dict[str, list[CustomField]] (dynamic keys)
RAISE-3027 (S2503.15) — JiraConfig deprecated; PythonApiJiraAdapter now reads
                         BacklogAdapterConfig natively from backlog.yaml.

JiraConfig, JiraInstance, JiraProject, load_jira_config, _generic_to_jira
have been removed. Use BacklogAdapterConfig (raise_cli.adapters.models.pm)
and load_backlog_config (raise_cli.adapters.backlog_config) instead.
"""

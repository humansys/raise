"""Filesystem-based PM adapter with YAML file store.

Open-core fallback: provides read + write PM functionality without
external services. Each issue is a YAML file at
``.raise/backlog/items/{KEY}.yaml`` validated by Pydantic on load/dump.

Architecture: S347.2 (E347 Backlog Automation)
"""

from __future__ import annotations

import contextlib
import logging
import re
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.backlog_config import (
    get_configured_adapters,
    load_backlog_config,
    load_workflow_config,
)
from raise_cli.adapters.filesystem_models import (
    BacklogComment,
    BacklogItem,
    BacklogLink,
)
from raise_cli.adapters.models import (
    AdapterHealth,
    AttachmentDetail,
    AttachmentRef,
    BatchResult,
    Comment,
    CommentRef,
    CustomField,
    FailureDetail,
    FieldDefinition,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    IssueTypeInfo,
    LinkTypeDefinition,
    WorkflowState,
)
from raise_cli.adapters.models.pm import BacklogAdapterConfig
from raise_cli.developer_profile.profile import load_developer_profile
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.counter import next_counter
from raise_cli.storage.schema import create_all

logger = logging.getLogger(__name__)


def _seed_from_work_items(conn: sqlite3.Connection, prefix: str) -> int:
    """Return the max numeric suffix of work_items.local_key starting with prefix.

    Used to seed the SQLite counter on first use (replaces Ledger.bootstrap_seed).
    """
    rows = conn.execute(
        "SELECT local_key FROM work_items WHERE local_key LIKE ?",
        (f"{prefix}%",),
    ).fetchall()
    max_n = 0
    for row in rows:
        key: str = row[0]
        suffix = key[len(prefix) :]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return max_n


def _developer_name() -> str:
    """Return the developer's local staging prefix from developer.yaml.

    Uses local_prefix if set, otherwise name. Falls back to 'Local' if
    developer.yaml is absent or unreadable.
    """
    profile = load_developer_profile()
    if profile is None:
        return "Local"
    return profile.local_prefix or profile.name


class FilesystemPMAdapter:
    """PM adapter backed by YAML file store.

    New issues (epics) are stored as hierarchical folders:
      ``.raise/backlog/e{Name}-{seq:03d}/{key}.yaml``

    Legacy issues remain readable from ``.raise/backlog/items/{KEY}.yaml``
    via fallback until migrated.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()
        self._items_dir = self._root / ".raise" / "backlog" / "items"

    @property
    def _backlog_root(self) -> Path:
        return self._root / ".raise" / "backlog"

    def _epic_folder(self, key: str) -> Path:
        """Directory for an epic in the hierarchical store."""
        return self._backlog_root / key

    # -- YAML I/O helpers ---------------------------------------------------

    def _resolve_item_path(self, key: str) -> Path | None:
        """Find the YAML file for key: hierarchy-first, then items/ fallback.

        Scans all e*/ subdirectories of .raise/backlog/ and reads each yaml
        to find a matching key field. Falls back to items/{key}.yaml.
        Returns None if not found anywhere.
        """
        for epic_dir in sorted(self._backlog_root.glob("e*/")):
            if not epic_dir.is_dir():
                continue
            for yaml_path in sorted(epic_dir.glob("*.yaml")):
                try:
                    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                    if isinstance(raw, dict) and raw.get("key") == key:
                        return yaml_path
                except Exception:  # noqa: BLE001, S112
                    continue
        legacy = self._items_dir / f"{key}.yaml"
        if legacy.exists():
            return legacy
        return None

    def _item_path(self, key: str) -> Path:
        """Resolve path for key; raises KeyError if not found."""
        path = self._resolve_item_path(key)
        if path is None:
            raise KeyError(key)
        return path

    def _load_item(self, key: str) -> BacklogItem:
        """Load and validate a single YAML item. Raises KeyError if missing."""
        path = self._item_path(key)
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return BacklogItem.model_validate(raw)

    def _item_save_path(self, item: BacklogItem) -> Path:
        """Determine the correct save path for an item.

        Update case: save back to the existing path (hierarchy or items/).
        New epic: create a folder in the hierarchy.
        New non-epic: legacy items/ until T4 (child placement) lands.
        """
        # Update case: save back to wherever the item already lives
        existing = self._resolve_item_path(item.key)
        if existing is not None:
            return existing
        # New item: route by type
        prefix = self._resolve_key_prefix(item.issue_type)
        if prefix == "e":
            folder = self._epic_folder(item.key)
            folder.mkdir(parents=True, exist_ok=True)
            return folder / f"{item.key}.yaml"
        # Child with a known parent: save inside parent's epic folder if it exists.
        # Resolve the parent's yaml to find the actual folder (handles promoted parents
        # where folder name has an 'e' prefix, e.g. eRTEST-15/ for parent RTEST-15).
        if item.parent:
            parent_yaml = self._resolve_item_path(item.parent)
            if parent_yaml is not None:
                parent_folder = parent_yaml.parent
                if parent_folder != self._items_dir and parent_folder.is_dir():
                    return parent_folder / f"{item.key}.yaml"
        # New non-epic without hierarchy parent: legacy items/
        self._items_dir.mkdir(parents=True, exist_ok=True)
        return self._items_dir / f"{item.key}.yaml"

    def _save_item(self, item: BacklogItem) -> None:
        """Dump a BacklogItem to YAML, excluding None values for clean files."""
        data = item.model_dump(exclude_none=True)
        for field in ("comments", "links", "labels"):
            if field in data and not data[field]:
                del data[field]
        if "description" in data and not data["description"]:
            del data["description"]
        path = self._item_save_path(item)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def _load_all_items(self) -> list[BacklogItem]:
        """Load all YAML items from hierarchy + legacy items/ store."""
        seen: set[str] = set()
        items: list[BacklogItem] = []
        # Hierarchy: scan all e*/ folders
        for epic_dir in sorted(self._backlog_root.glob("e*/")):
            if not epic_dir.is_dir():
                continue
            for yaml_path in sorted(epic_dir.glob("*.yaml")):
                try:
                    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                    item = BacklogItem.model_validate(raw)
                    if item.key not in seen:
                        seen.add(item.key)
                        items.append(item)
                except Exception:  # noqa: BLE001, S112
                    continue
        # Legacy fallback
        if self._items_dir.is_dir():
            for yaml_path in sorted(self._items_dir.glob("*.yaml")):
                raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                item = BacklogItem.model_validate(raw)
                if item.key not in seen:
                    seen.add(item.key)
                    items.append(item)
        return items

    def load_all_items(self) -> list[BacklogItem]:
        """Return every backlog item visible to this adapter (D2, S16533.4).

        Thin public delegate to ``_load_all_items()`` — the canonical
        iterator (hierarchy `e*/` dirs + legacy `items/` fallback,
        deduplicated by key). Formalizes the contract for external callers
        (e.g. ``rai backlog migrate``) instead of reaching for the private
        method with a ``noqa: SLF001``.
        """
        return self._load_all_items()

    # -- Key generation helpers -----------------------------------------------

    def _next_staged_epic_key(self) -> str:
        """Allocate the next staged epic key: e{Name}-{seq:03d}.

        Uses developer.yaml name as prefix; falls back to 'Local'.
        Counter is per-developer, namespaced by name.
        """
        name = _developer_name()
        pid = get_project_id(self._root)
        db = get_project_db(self._root)
        create_all(db)
        n = next_counter(db, f"staged_epic_{name}", seed_fn=lambda: 0, project_id=pid)
        db.close()
        return f"e{name}-{n:03d}"

    def _next_staged_child_key(self, parent_key: str, type_prefix: str) -> str:
        """Allocate the next staged child key: {type_prefix}{Name}-{parent_seq}.{child_seq}.

        For staged parents (e{Name}-{seq}): embeds parent seq in key.
        For legacy/promoted parents (E{n}, RAISE-NNN, etc.): uses a flat counter.
        """
        name = _developer_name()
        # Try to extract parent seq from staged parent key (e.g. eFer-001 → 001)
        pid = get_project_id(self._root)
        m_staged = re.match(r"^e[A-Za-z]+-(\d+)$", parent_key)
        if m_staged:
            parent_seq = m_staged.group(1)
            counter_name = f"staged_child_{name}_{parent_seq}_{type_prefix}"
            db = get_project_db(self._root)
            create_all(db)
            n = next_counter(db, counter_name, seed_fn=lambda: 0, project_id=pid)
            db.close()
            return f"{type_prefix}{name}-{parent_seq}.{n}"
        counter_name = f"staged_child_{name}_{type_prefix}"
        db = get_project_db(self._root)
        create_all(db)
        n = next_counter(db, counter_name, seed_fn=lambda: 0, project_id=pid)
        db.close()
        return f"{type_prefix}{name}-{n:03d}"

    def _next_story_key(self, parent_key: str) -> str:
        """Allocate the next story key for a given epic from the SQLite counter.

        Supports legacy E{n} parents and staged e{Name}-{seq} parents.
        """
        m_legacy = re.match(r"E(\d+)", parent_key)
        if m_legacy:
            epic_num = m_legacy.group(1)
            prefix = f"S{epic_num}."
            pid = get_project_id(self._root)
            db = get_project_db(self._root)
            create_all(db)
            n = next_counter(
                db,
                f"story_{epic_num}",
                seed_fn=lambda: _seed_from_work_items(db, prefix),
                project_id=pid,
            )
            db.close()
            return f"S{epic_num}.{n}"
        # Staged or promoted parent: use new staging child key
        return self._next_staged_child_key(parent_key, "s")

    def _next_generic_key(self, prefix: str, parent_key: str | None = None) -> str:
        """Allocate the next key for a custom issue type.

        With a parent: uses staged child naming.
        Without a parent: legacy flat counter.
        """
        if parent_key:
            return self._next_staged_child_key(parent_key, prefix)
        pid = get_project_id(self._root)
        db = get_project_db(self._root)
        create_all(db)
        n = next_counter(
            db,
            f"type_{prefix}",
            seed_fn=lambda: _seed_from_work_items(db, prefix),
            project_id=pid,
        )
        db.close()
        return f"{prefix}{n}"

    def _resolve_key_prefix(self, issue_type: str) -> str:
        """Resolve issue_type → key prefix using backlog.yaml config.

        Applies alias resolution first (e.g. Historia → Story),
        then looks up issue_type_prefixes. Falls back to first char lowercase.
        """
        if not issue_type:
            return "x"
        try:
            config = load_backlog_config(self._root, "filesystem")
            canonical = config.issue_type_aliases.get(issue_type, issue_type)
            return config.issue_type_prefixes.get(canonical, canonical[0].lower())
        except (FileNotFoundError, KeyError):
            return issue_type[0].lower()

    def _status_category_adapter_names(self) -> list[str]:
        """Configured adapter sections that may carry workflow metadata."""
        adapter_names = ["filesystem"]
        with contextlib.suppress(FileNotFoundError, OSError):
            adapter_names.extend(
                name
                for name in sorted(get_configured_adapters(self._root))
                if name != "filesystem"
            )
        return adapter_names

    @staticmethod
    def _workflow_states_for_issue_type(
        config: BacklogAdapterConfig, issue_type: str
    ) -> list[dict[str, Any]]:
        workflow = config.workflow.get(issue_type)
        if workflow is None:
            for configured_type, candidate in config.workflow.items():
                if configured_type.casefold() == issue_type.casefold():
                    workflow = candidate
                    break
        return [] if workflow is None else workflow.states

    def _status_category_for(self, issue_type: str, status: str) -> str:
        """Resolve a stored status name to its workflow category when configured."""
        if not issue_type or not status:
            return ""

        for adapter_name in self._status_category_adapter_names():
            try:
                config = load_backlog_config(self._root, adapter_name)
            except (FileNotFoundError, KeyError, ValueError):
                continue

            for state in self._workflow_states_for_issue_type(config, issue_type):
                if str(state.get("name", "")).casefold() == status.casefold():
                    return str(state.get("status_category", ""))

        return ""

    # -- Search helper -------------------------------------------------------

    @staticmethod
    def _match_in(item: IssueSummary, field: str, values_lower: list[str]) -> bool:
        """Evaluate a single ``field in (values)`` JQL clause."""
        if field in ("issuetype", "issue_type"):
            return item.issue_type.lower() in values_lower
        if field in ("fixversion", "fix_version"):
            return any(fv.lower() in values_lower for fv in item.fix_versions)
        if field == "key":
            return item.key.lower() in values_lower
        return False

    @staticmethod
    def _match_eq(item: IssueSummary, field: str, value: str) -> bool:
        """Evaluate a single ``field = value`` JQL clause."""
        if field == "status":
            return item.status.lower() == value
        if field in ("issuetype", "issue_type"):
            return item.issue_type.lower() == value
        if field == "project":
            return True  # filesystem adapter is single-project by design
        if field == "name":
            return value in item.summary.lower()
        return False

    def _match(self, item: IssueSummary, query: str) -> bool:
        """Return True when *item* satisfies *query*.

        Supports compound JQL (AND/OR), parenthesized groups, field = value,
        field in (...), and bare text.  Handles the portfolio JQL pattern:
        ``project = X AND issuetype in (...) AND (fixVersion in (...) OR key in (...))``
        """
        query = query.strip()
        # Strip trailing ORDER BY clause (may be attached to the last AND/OR segment).
        query = re.sub(r"\s+ORDER\s+BY\s+.*$", "", query, flags=re.IGNORECASE).strip()
        if not query:
            return True
        # Strip a single layer of outer parentheses so (A OR B) recurses cleanly.
        if query.startswith("(") and query.endswith(")"):
            query = query[1:-1].strip()
        if re.search(r"\bAND\b", query, re.IGNORECASE):
            clauses = re.split(r"\bAND\b", query, flags=re.IGNORECASE)
            return all(self._match(item, c.strip()) for c in clauses if c.strip())
        if re.search(r"\bOR\b", query, re.IGNORECASE):
            clauses = re.split(r"\bOR\b", query, flags=re.IGNORECASE)
            return any(self._match(item, c.strip()) for c in clauses if c.strip())
        m_in = re.match(r"(\w+)\s+in\s*\((.+)\)", query, re.IGNORECASE)
        if m_in:
            field = m_in.group(1).lower()
            values = [v.strip().strip("\"'").lower() for v in m_in.group(2).split(",")]
            return self._match_in(item, field, values)
        m_eq = re.match(r"(\w+)\s*=\s*(.+)", query)
        if m_eq:
            return self._match_eq(
                item,
                m_eq.group(1).lower(),
                m_eq.group(2).strip().strip("\"'").lower(),
            )
        q = query.lower()
        return q in item.key.lower() or q in item.summary.lower()

    # -- Read operations ----------------------------------------------------

    def get_issue(self, key: str) -> IssueDetail:
        """Get issue detail by key."""
        item = self._load_item(key)
        return IssueDetail(
            key=item.key,
            summary=item.summary,
            status=item.status,
            status_category=self._status_category_for(item.issue_type, item.status),
            issue_type=item.issue_type,
            description=item.description,
            labels=item.labels,
            parent_key=item.parent,
            priority=item.priority,
            assignee=item.assignee,
            created=item.created,
            updated=item.updated,
            fix_versions=item.fix_versions,
        )

    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]:
        """Search issues."""
        items = self._load_all_items()
        summaries = [
            IssueSummary(
                key=it.key,
                summary=it.summary,
                status=it.status,
                issue_type=it.issue_type,
                parent_key=it.parent,
                fix_versions=it.fix_versions,
            )
            for it in items
        ]
        matched = [s for s in summaries if self._match(s, query)]
        if fetch_all:
            return matched[offset:]
        return matched[offset : offset + limit]

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        """Get comments for an issue. Returns [] if issue not found."""
        try:
            item = self._load_item(key)
        except KeyError:
            return []
        comments = [
            Comment(id=c.id, body=c.body, author=c.author, created=c.created)
            for c in item.comments
        ]
        if fetch_all:
            return comments[offset:]
        return comments[offset : offset + limit]

    def health(self) -> AdapterHealth:
        """Check adapter health."""
        if self._items_dir.is_dir():
            count = len(list(self._items_dir.glob("*.yaml")))
            return AdapterHealth(
                name="filesystem",
                healthy=True,
                message=f".raise/backlog/items/ ({count} items)",
            )
        return AdapterHealth(
            name="filesystem",
            healthy=False,
            message="YAML store not found (.raise/backlog/items/)",
        )

    # -- Write operations ---------------------------------------------------

    def create_issue(self, _project_key: str, issue: IssueSpec) -> IssueRef:
        """Create a new issue."""
        meta = issue.metadata or {}
        now = datetime.now(UTC).isoformat()
        prefix = self._resolve_key_prefix(issue.issue_type)
        if prefix == "e":
            key = self._next_staged_epic_key()
        elif prefix == "s":
            parent_key = issue.parent or meta.get("parent_key")
            if not parent_key:
                raise KeyError("Story creation requires parent_key")
            key = self._next_story_key(parent_key)
        else:
            parent_key = issue.parent or meta.get("parent_key")
            key = self._next_generic_key(prefix, parent_key)
        new_item = BacklogItem(
            key=key,
            summary=issue.summary,
            issue_type=issue.issue_type,
            status="pending",
            parent=issue.parent or meta.get("parent_key"),
            description=issue.description,
            labels=issue.labels,
            priority=meta.get("priority"),
            created=now,
            updated=now,
        )
        self._save_item(new_item)
        return IssueRef(key=new_item.key)

    def promote_key(self, old_key: str, new_key: str) -> None:
        """Rename a staged key to its permanent Jira key.

        For epics (folder exists): rename folder, rename yaml inside, update key field.
        For children (yaml only): rename yaml in its parent folder, update key field.
        Raises KeyError if old_key is not found anywhere in the hierarchy.
        """
        old_path = self._resolve_item_path(old_key)
        if old_path is None:
            raise KeyError(old_key)

        # Load, update key field, determine new path
        raw = yaml.safe_load(old_path.read_text(encoding="utf-8"))
        raw["key"] = new_key
        new_yaml_content = yaml.safe_dump(raw, sort_keys=False)

        old_folder = self._epic_folder(old_key)
        if old_folder.is_dir():
            # Epic promotion: rename folder and the yaml inside it
            new_folder = self._backlog_root / f"e{new_key}"
            shutil.move(str(old_folder), str(new_folder))
            # The yaml was renamed with the folder; now rename the yaml file inside
            old_yaml_in_new_folder = new_folder / f"{old_key}.yaml"
            new_yaml_path = new_folder / f"e{new_key}.yaml"
            if old_yaml_in_new_folder.exists():
                old_yaml_in_new_folder.rename(new_yaml_path)
            else:
                new_yaml_path = (
                    new_folder / f"{old_key}.yaml"
                )  # fallback: already renamed
            # Write updated key field
            new_yaml_path.write_text(new_yaml_content, encoding="utf-8")
        else:
            # Child promotion: rename yaml file in place, update key field
            type_prefix = self._resolve_key_prefix(raw.get("issue_type", ""))
            new_yaml_path = old_path.parent / f"{type_prefix}{new_key}.yaml"
            old_path.rename(new_yaml_path)
            new_yaml_path.write_text(new_yaml_content, encoding="utf-8")

    # Fields that must not be mutated via update_issue()
    _IMMUTABLE_FIELDS: frozenset[str] = frozenset(
        {"key", "created", "comments", "links"}
    )

    # Jira REST API field names that differ from their Python/YAML counterparts.
    # The CLI passes Jira names (e.g. ``fixVersions`` from ``-F fixVersions=[…]``);
    # ``model_dump()`` returns Python names (``fix_versions``).  Without this map,
    # every update with a Jira-named key is silently dropped — RAISE-15669.
    _JIRA_FIELD_ALIASES: dict[str, str] = {
        "fixVersions": "fix_versions",
        "issuetype": "issue_type",
    }

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update fields on an existing issue.

        RAISE-14593: field values are merged into a plain dict and re-validated
        via ``BacklogItem.model_validate`` before persisting. Raw ``setattr`` on
        a Pydantic model without ``validate_assignment`` bypasses coercion, so a
        wire-shaped value (e.g. a ``{"key": ...}`` dict for the ``str`` ``parent``
        field) would otherwise be written verbatim into the YAML mirror and break
        every subsequent read. Re-validation coerces or rejects at the boundary.
        """
        item = self._load_item(key)
        data = item.model_dump()
        for field_name, value in fields.items():
            canonical = self._JIRA_FIELD_ALIASES.get(field_name, field_name)
            if canonical in self._IMMUTABLE_FIELDS:
                continue
            if canonical in data:
                data[canonical] = value
        data["updated"] = datetime.now(UTC).isoformat()
        validated = BacklogItem.model_validate(data)
        self._save_item(validated)
        return IssueRef(key=key)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Update issue status.

        S4 (RAISE-15031): Validates the transition against the WorkflowStateMachine
        loaded from ``pipeline_workflow`` config. strict=False — advisory only.
        Illegal transitions emit a WARNING but are never blocked.
        """
        item = self._load_item(key)

        # Advisory-only state machine validation (strict=False — never blocks).
        machine = load_workflow_config().to_state_machine()
        if machine.states:  # fail-open: empty config → skip silently
            from_slug = machine.resolve(item.status)
            to_slug = machine.resolve(status)
            if (
                from_slug is not None
                and to_slug is not None
                and not machine.is_legal(from_slug, to_slug)
            ):
                logger.warning(
                    "Illegal transition %s → %s for %s (advisory)",
                    from_slug,
                    to_slug,
                    key,
                )

        item.status = status
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)
        return IssueRef(key=key)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition multiple issues."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []
        for key in keys:
            try:
                ref = self.transition_issue(key, status)
                succeeded.append(ref)
            except KeyError:
                failed.append(FailureDetail(key=key, error=f"{key} not found"))
        return BatchResult(succeeded=succeeded, failed=failed)

    # -- Relationship & comment operations ----------------------------------

    def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        """Set parent field on child issue."""
        item = self._load_item(child_key)
        item.parent = parent_key
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)
        return True

    def link_issues(self, source: str, target: str, link_type: str) -> bool:
        """Add a link from source to target."""
        item = self._load_item(source)
        item.links.append(BacklogLink(target=target, link_type=link_type))
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)
        return True

    def remove_link(self, link_id: str) -> None:
        """No-op — link IDs are remote-native; filesystem has no link ID index."""

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        """Create multiple issues with per-item fault isolation."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []
        for spec in issues:
            try:
                ref = self.create_issue(spec.project, spec)
                succeeded.append(ref)
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                failed.append(FailureDetail(key=spec.summary, error=str(exc)))
        return BatchResult(succeeded=succeeded, failed=failed)

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Add a comment to an issue."""
        item = self._load_item(key)
        next_n = len(item.comments) + 1
        comment_id = f"{key}-{next_n}"
        now = datetime.now(UTC).isoformat()
        item.comments.append(
            BacklogComment(id=comment_id, body=body, author="rai", created=now)
        )
        item.updated = now
        self._save_item(item)
        return CommentRef(id=comment_id)

    # -- Discovery (not supported — filesystem adapter is local/offline) ------

    def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        """Not supported — filesystem adapter is local/offline."""
        return []

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        """Not supported — filesystem adapter is local/offline."""
        return []

    def discover_link_types(self) -> list[LinkTypeDefinition]:
        """Not supported — filesystem adapter is local/offline."""
        return []

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Not supported — filesystem adapter is local/offline."""
        return []

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]:
        """Not supported — filesystem adapter is local/offline."""
        return []

    # ── Attachments (S2503.7) ────────────────────────────────────────

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        """Not supported — filesystem adapter is local/offline."""
        raise NotImplementedError("attach() not supported by filesystem adapter")

    def get_attachments(self, key: str) -> list[AttachmentDetail]:
        """Not supported — filesystem adapter is local/offline."""
        return []

    def download_attachment(self, attachment_id: str) -> bytes:
        """Not supported — filesystem adapter is local/offline."""
        raise NotImplementedError(
            "download_attachment() not supported by filesystem adapter"
        )

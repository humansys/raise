"""JIRA entity property storage and retrieval for sync metadata.

This module provides functions to store and retrieve RaiSE sync metadata on JIRA
issues via entity properties API. Implements ADR-028 schema with strict validation.

Functions:
    set_entity_property: Store sync metadata on JIRA issue
    get_entity_property: Retrieve sync metadata from JIRA issue
    has_rai_metadata: Check if issue has RaiSE metadata (idempotency helper)

Property key: com.humansys.raise.sync (namespaced to avoid collisions)
"""

from typing import Any

from rai_pro.providers.jira.client import JiraClient
from rai_pro.providers.jira.exceptions import JiraApiError
from rai_pro.providers.jira.models import EntityProperty, RaiSyncMetadata

# Namespaced property key from ADR-028
PROPERTY_KEY = "com.humansys.raise.sync"


def set_entity_property(
    client: JiraClient,
    issue_key: str,
    metadata: RaiSyncMetadata,
) -> None:
    """Store sync metadata on JIRA issue via entity properties.

    Uses JIRA entity properties API to store RaiSE-specific metadata on issues.
    Property is invisible to JIRA users but queryable via JQL and REST API.

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key (e.g., "DEMO-123")
        metadata: RaiSE sync metadata to store

    Raises:
        JiraApiError: If JIRA API call fails

    Example:
        >>> metadata = RaiSyncMetadata(
        ...     epic_id="E-DEMO",
        ...     story_id="S-DEMO.4",
        ...     last_sync_at=datetime.now(UTC),
        ...     rai_branch="demo/atlassian-webinar",
        ...     local_path="/home/emilio/Code/raise-commons"
        ... )
        >>> set_entity_property(client, "DEMO-123", metadata)
    """
    # Wrap in EntityProperty structure for JIRA API
    property_data = EntityProperty(rai_sync=metadata)

    # Serialize with mode='json' for proper datetime formatting
    payload = property_data.model_dump(mode="json")

    # PUT /rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}
    endpoint = f"/rest/api/3/issue/{issue_key}/properties/{PROPERTY_KEY}"

    # Access underlying Jira client for raw API call
    try:
        client._jira.put(endpoint, data=payload)  # type: ignore[attr-defined]
    except Exception as e:
        # Map to JiraApiError with status code if available
        status_code = getattr(e, "status_code", 500)
        raise JiraApiError(status_code=status_code, message=str(e)) from e


def get_entity_property(
    client: JiraClient,
    issue_key: str,
) -> RaiSyncMetadata | None:
    """Retrieve sync metadata from JIRA issue entity properties.

    Queries JIRA entity properties API and deserializes into RaiSyncMetadata.
    Uses strict validation to fail fast on malformed data.

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key (e.g., "DEMO-123")

    Returns:
        RaiSyncMetadata if property exists, None if not set

    Raises:
        JiraApiError: If JIRA API call fails (except 404)
        ValidationError: If stored data doesn't match schema (strict mode)

    Example:
        >>> metadata = get_entity_property(client, "DEMO-123")
        >>> if metadata:
        ...     print(f"Last synced: {metadata.last_sync_at}")
        ...     print(f"Epic: {metadata.epic_id}, Story: {metadata.story_id}")
    """
    # GET /rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}
    endpoint = f"/rest/api/3/issue/{issue_key}/properties/{PROPERTY_KEY}"

    try:
        response: Any = client._jira.get(endpoint)  # type: ignore[attr-defined]
    except Exception as e:
        # 404 means property not set yet (not an error for new issues)
        status_code = getattr(e, "status_code", 500)
        if status_code == 404:
            return None
        # Other errors (403, 500, etc.) are raised as JiraApiError
        raise JiraApiError(status_code=status_code, message=str(e)) from e

    # JIRA wraps entity property value in {"value": {...}}
    property_value: dict[str, Any] = response.get("value", response)

    # Strict validation (fail fast on malformed data)
    property_data = EntityProperty.model_validate(property_value)

    return property_data.rai_sync


def has_rai_metadata(
    client: JiraClient,
    issue_key: str,
) -> bool:
    """Check if JIRA issue has RaiSE sync metadata (idempotency helper).

    Convenience function for checking if an issue has already been synced
    from RaiSE. Used for duplicate detection in sync operations.

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key

    Returns:
        True if metadata exists, False otherwise

    Example:
        >>> if has_rai_metadata(client, "DEMO-123"):
        ...     print("Issue already synced from RaiSE")
        >>> else:
        ...     print("New issue, safe to sync")
    """
    metadata = get_entity_property(client, issue_key)
    return metadata is not None

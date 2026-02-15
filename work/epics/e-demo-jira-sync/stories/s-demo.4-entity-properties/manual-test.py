#!/usr/bin/env python3
"""Manual integration test for S-DEMO.4 entity properties.

End-to-end validation of entity property operations in realistic sync scenario.
Demonstrates that S-DEMO.4 enables idempotent sync operations (preview of S-DEMO.5).

Prerequisites:
    export JIRA_CLOUD_ID="<cloud-id>"
    export JIRA_API_TOKEN="<oauth-token>"
    export JIRA_TEST_ISSUE_KEY="<issue-key>"  # e.g., "DEMO-123"

Usage:
    python work/epics/e-demo-jira-sync/stories/s-demo.4-entity-properties/manual-test.py
"""

import os
import sys
from datetime import UTC, datetime

# Add src to path for local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))

from rai_pro.providers.jira.client import JiraClient
from rai_pro.providers.jira.models import RaiSyncMetadata
from rai_pro.providers.jira.properties import (
    get_entity_property,
    has_rai_metadata,
    set_entity_property,
)


def main() -> None:
    """Run manual integration test."""
    # Get environment variables
    cloud_id = os.getenv("JIRA_CLOUD_ID")
    token = os.getenv("JIRA_API_TOKEN")
    issue_key = os.getenv("JIRA_TEST_ISSUE_KEY")

    if not cloud_id or not token or not issue_key:
        print("❌ Missing required environment variables:")
        print("   JIRA_CLOUD_ID, JIRA_API_TOKEN, JIRA_TEST_ISSUE_KEY")
        sys.exit(1)

    print("🔧 S-DEMO.4 Manual Integration Test")
    print("=" * 60)
    print(f"Cloud ID: {cloud_id[:8]}...")
    print(f"Issue Key: {issue_key}")
    print()

    # Setup client
    print("1️⃣  Setting up JIRA client...")
    client = JiraClient(cloud_id=cloud_id, access_token=token)
    print("   ✓ Client created")
    print()

    # Create test metadata
    print("2️⃣  Creating test metadata...")
    metadata = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        task_id=None,
        last_sync_at=datetime.now(UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/home/emilio/Code/raise-commons",
        sync_version="1",
        sync_direction="push",
        last_modified_by="rai",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
    )
    print(f"   Epic: {metadata.epic_id}")
    print(f"   Story: {metadata.story_id}")
    print(f"   Branch: {metadata.rai_branch}")
    print(f"   Timestamp: {metadata.last_sync_at.isoformat()}")
    print()

    # Push metadata to JIRA
    print("3️⃣  Pushing metadata to JIRA...")
    set_entity_property(client, issue_key, metadata)
    print("   ✓ Property set successfully")
    print()

    # Retrieve and verify
    print("4️⃣  Retrieving metadata from JIRA...")
    retrieved = get_entity_property(client, issue_key)
    if retrieved is None:
        print("   ❌ FAILED: No metadata retrieved")
        sys.exit(1)

    print("   ✓ Metadata retrieved")
    print(f"   Epic: {retrieved.epic_id}")
    print(f"   Story: {retrieved.story_id}")
    print(f"   Branch: {retrieved.rai_branch}")
    print(f"   Timestamp: {retrieved.last_sync_at.isoformat()}")
    print()

    # Verify match
    print("5️⃣  Verifying roundtrip correctness...")
    assert retrieved.epic_id == metadata.epic_id
    assert retrieved.story_id == metadata.story_id
    assert retrieved.rai_branch == metadata.rai_branch
    assert retrieved.local_path == metadata.local_path
    assert retrieved.sync_version == metadata.sync_version
    print("   ✓ All fields match")
    print()

    # Idempotency check
    print("6️⃣  Testing idempotency (second write)...")
    has_meta = has_rai_metadata(client, issue_key)
    print(f"   has_rai_metadata: {has_meta}")
    if not has_meta:
        print("   ❌ FAILED: Metadata should exist")
        sys.exit(1)

    # Push again
    metadata_v2 = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        task_id=None,
        last_sync_at=datetime.now(UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/home/emilio/Code/raise-commons",
        sync_version="1",
        sync_direction="push",
        last_modified_by="rai",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
    )
    set_entity_property(client, issue_key, metadata_v2)
    retrieved_v2 = get_entity_property(client, issue_key)

    if retrieved_v2 is None:
        print("   ❌ FAILED: Second write failed")
        sys.exit(1)

    print("   ✓ Second write succeeded")
    print(f"   Updated timestamp: {retrieved_v2.last_sync_at.isoformat()}")
    print()

    # Final verification
    print("7️⃣  Final verification...")
    print(f"   API endpoint: /rest/api/3/issue/{issue_key}/properties/com.humansys.raise.sync")
    print("   Property key: com.humansys.raise.sync")
    print("   Structure: EntityProperty wraps RaiSyncMetadata")
    print()

    print("✅ SUCCESS: S-DEMO.4 entity properties working end-to-end")
    print()
    print("Next: S-DEMO.5 (sync engine integration)")


if __name__ == "__main__":
    main()

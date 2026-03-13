"""Manual integration tests for JIRA client.

These tests require a real JIRA Cloud instance with OAuth configured.
They are skipped by default and must be run explicitly with:

    pytest -m integration tests/providers/jira/test_integration.py -v -s

Prerequisites:
- JIRA Cloud test instance
- OAuth access token (obtain via: rai backlog auth jira)
- Test epic exists in JIRA project
- Environment variables:
  - JIRA_CLOUD_ID: Your Atlassian cloud ID
  - JIRA_ACCESS_TOKEN: OAuth access token
  - JIRA_TEST_EPIC_KEY: Test epic key (default: "DEMO-1")

Example:
    export JIRA_CLOUD_ID="abc123def456"
    export JIRA_ACCESS_TOKEN="eyJhbGc..."
    export JIRA_TEST_EPIC_KEY="DEMO-1"
    pytest -m integration tests/providers/jira/test_integration.py -v -s
"""

import os
import time

import pytest
from rai_pro.providers.jira.client import JiraClient
from rai_pro.providers.jira.models import StoryCreate


@pytest.mark.integration
@pytest.mark.skip(reason="Manual test - requires real JIRA instance")
def test_jira_client_integration():
    """End-to-end integration test with real JIRA API.

    Test flow:
    1. Get credentials from environment
    2. Read existing epic
    3. Read stories for epic
    4. Create test story
    5. Verify story appears
    6. Test rate limiting
    7. Cleanup test story
    """
    # Get test environment config
    cloud_id = os.getenv("JIRA_CLOUD_ID")
    access_token = os.getenv("JIRA_ACCESS_TOKEN")
    test_epic_key = os.getenv("JIRA_TEST_EPIC_KEY", "DEMO-1")

    if not cloud_id:
        pytest.skip("JIRA_CLOUD_ID environment variable required")

    if not access_token:
        pytest.skip("JIRA_ACCESS_TOKEN environment variable required")

    print(f"\n{'=' * 60}")
    print("JIRA Integration Test")
    print(f"Cloud ID: {cloud_id}")
    print(f"Test Epic: {test_epic_key}")
    print(f"{'=' * 60}\n")

    # Initialize client
    client = JiraClient(cloud_id=cloud_id, access_token=access_token)

    # Test 1: Read epic
    print("1. Reading epic...")
    epic = client.read_epic(test_epic_key)
    assert epic.key == test_epic_key
    assert epic.summary
    assert epic.status
    print(f"   ✓ Epic: {epic.key} - {epic.summary}")
    print(f"   ✓ Status: {epic.status}")
    print(f"   ✓ Labels: {epic.labels}")

    # Test 2: Read stories for epic
    print("\n2. Reading stories for epic...")
    stories_before = client.read_stories_for_epic(test_epic_key)
    print(f"   ✓ Found {len(stories_before)} existing stories")
    if stories_before:
        print(f"   ✓ Example: {stories_before[0].key} - {stories_before[0].summary}")

    # Test 3: Create story
    print("\n3. Creating test story...")
    story_data = StoryCreate(
        summary="[TEST] Integration test story - DELETE ME",
        description="Created by automated integration test.\n\n"
        "This story should be automatically deleted.\n"
        "If you see this, the cleanup step failed.",
        labels=["test", "automation", "integration"],
    )
    created_story = client.create_story(test_epic_key, story_data)
    assert created_story.key
    assert created_story.summary == story_data.summary
    assert created_story.epic_key == test_epic_key
    print(f"   ✓ Created: {created_story.key}")
    print(f"   ✓ Summary: {created_story.summary}")
    print(f"   ✓ Status: {created_story.status}")

    # Test 4: Verify story appears in epic
    print("\n4. Verifying story appears under epic...")
    stories_after = client.read_stories_for_epic(test_epic_key)
    assert len(stories_after) == len(stories_before) + 1
    assert any(s.key == created_story.key for s in stories_after)
    print(f"   ✓ Story count: {len(stories_before)} → {len(stories_after)}")
    print(f"   ✓ Story {created_story.key} found in epic")

    # Test 5: Read story status
    print("\n5. Testing status read operations...")
    epic_status = client.read_epic_status(test_epic_key)
    story_status = client.read_story_status(created_story.key)
    assert epic_status == epic.status
    assert story_status == created_story.status
    print(f"   ✓ Epic status: {epic_status}")
    print(f"   ✓ Story status: {story_status}")

    # Test 6: Rate limiting
    print("\n6. Testing rate limiting (20 requests)...")
    start = time.time()
    for i in range(20):
        client.read_epic_status(test_epic_key)
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start
            print(f"   • {i + 1}/20 requests in {elapsed:.2f}s")

    elapsed = time.time() - start
    expected_min = 1.8  # 20 requests / 10 req/sec = 2s, allow 10% tolerance
    assert elapsed >= expected_min, (
        f"Rate limiting not enforced: {elapsed:.2f}s < {expected_min}s"
    )
    print(f"   ✓ Total time: {elapsed:.2f}s (≥{expected_min}s)")
    print(f"   ✓ Rate limiting working: ~{20 / elapsed:.1f} req/sec")

    # Test 7: Cleanup - Delete test story
    print("\n7. Cleaning up test story...")
    try:
        client._jira.delete_issue(created_story.key)  # type: ignore[reportPrivateUsage]
        print(f"   ✓ Deleted: {created_story.key}")

        # Verify deletion
        stories_final = client.read_stories_for_epic(test_epic_key)
        assert len(stories_final) == len(stories_before)
        assert not any(s.key == created_story.key for s in stories_final)
        print("   ✓ Verified deletion")
    except Exception as e:
        print(f"   ✗ Cleanup failed: {e}")
        print(f"   ⚠ Manual cleanup required: {created_story.key}")
        raise

    print(f"\n{'=' * 60}")
    print("All integration tests passed! ✓")
    print(f"{'=' * 60}\n")


@pytest.mark.integration
@pytest.mark.skip(reason="Manual test - requires real JIRA instance")
def test_jira_client_error_handling():
    """Test error handling with real JIRA API.

    Tests invalid operations to verify error mapping works correctly.
    """
    # Get credentials from environment
    cloud_id = os.getenv("JIRA_CLOUD_ID")
    access_token = os.getenv("JIRA_ACCESS_TOKEN")

    if not cloud_id:
        pytest.skip("JIRA_CLOUD_ID environment variable required")

    if not access_token:
        pytest.skip("JIRA_ACCESS_TOKEN environment variable required")

    client = JiraClient(cloud_id=cloud_id, access_token=access_token)

    print(f"\n{'=' * 60}")
    print("JIRA Error Handling Test")
    print(f"{'=' * 60}\n")

    # Test 1: Not found error
    print("1. Testing 404 handling...")
    from rai_pro.providers.jira.exceptions import JiraNotFoundError

    with pytest.raises(JiraNotFoundError):
        client.read_epic("NONEXISTENT-99999")
    print("   ✓ JiraNotFoundError raised for non-existent epic")

    # Test 2: Invalid story creation
    print("\n2. Testing invalid story creation...")
    with pytest.raises(JiraNotFoundError):
        story = StoryCreate(summary="Test story", description=None)
        client.create_story("NONEXISTENT-99999", story)
    print("   ✓ JiraNotFoundError raised for non-existent parent epic")

    print(f"\n{'=' * 60}")
    print("Error handling tests passed! ✓")
    print(f"{'=' * 60}\n")

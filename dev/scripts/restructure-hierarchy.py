#!/usr/bin/env python3
"""Restructure flat Confluence pages into hierarchical structure.

Creates parent pages for epics and stories, then moves existing pages
under their correct parent.

Usage:
    python dev/scripts/restructure-hierarchy.py --dry-run
    python dev/scripts/restructure-hierarchy.py
    python dev/scripts/restructure-hierarchy.py --limit 5
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
import yaml


EPIC_ARCHIVES_ID = "3145269324"
STORY_ARCHIVES_ID = "3145728194"
BUG_ARCHIVES_ID = "3144319109"
RESEARCH_ID = "3074654209"

RATE_LIMIT = 0.5  # seconds between API calls


def load_auth() -> tuple[str, str, str]:
    result: dict[str, str] = {}
    for env_path in [".env", str(Path.home() / "Code" / "raise-commons" / ".env")]:
        if Path(env_path).exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        result[key.strip()] = value.strip().strip("'\"")
            break
    url = result.get("JIRA_URL", result.get("CONFLUENCE_URL", ""))
    user = result.get("CONFLUENCE_USERNAME", "")
    token = result.get("CONFLUENCE_API_TOKEN", "")
    if not all([url, user, token]):
        print("ERROR: No auth found", file=sys.stderr)
        sys.exit(1)
    return url.rstrip("/"), user, token


def create_parent_page(
    base_url: str, user: str, token: str,
    space_key: str, title: str, parent_id: str, description: str = "",
) -> str | None:
    """Create a lightweight parent page. Returns page ID."""
    body = f"<p>{description}</p>" if description else "<p></p>"
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "ancestors": [{"id": parent_id}],
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    resp = requests.post(
        f"{base_url}/wiki/rest/api/content",
        json=payload,
        auth=(user, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=60,
    )
    if resp.status_code == 400 and "already exists" in resp.text:
        # Page exists, find it
        return find_page(base_url, user, token, space_key, title)
    if not resp.ok:
        print(f"  ERROR creating '{title}': {resp.status_code} {resp.text[:200]}")
        return None
    return resp.json()["id"]


def find_page(base_url: str, user: str, token: str, space_key: str, title: str) -> str | None:
    """Find page by exact title in space."""
    resp = requests.get(
        f"{base_url}/wiki/rest/api/content",
        params={"title": title, "spaceKey": space_key, "type": "page", "limit": 1},
        auth=(user, token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if resp.ok:
        results = resp.json().get("results", [])
        if results:
            return results[0]["id"]
    return None


def move_page_under_parent(base_url: str, user: str, token: str, page_id: str, parent_id: str) -> bool:
    """Move page under a parent (same space)."""
    # Get current version + title
    resp = requests.get(
        f"{base_url}/wiki/rest/api/content/{page_id}?expand=version,ancestors",
        auth=(user, token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if not resp.ok:
        return False
    page = resp.json()
    version = page["version"]["number"]
    title = page["title"]

    # Check if already under correct parent
    ancestors = page.get("ancestors", [])
    if ancestors and ancestors[-1]["id"] == parent_id:
        return True  # Already correct

    resp2 = requests.put(
        f"{base_url}/wiki/rest/api/content/{page_id}",
        json={
            "type": "page",
            "title": title,
            "status": "current",
            "ancestors": [{"id": parent_id}],
            "version": {"number": version + 1},
        },
        auth=(user, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    return resp2.ok


def prettify_name(slug: str) -> str:
    """Convert directory slug to readable name."""
    # Remove leading ID patterns like f1.5-, s301.7-, etc.
    name = re.sub(r"^[fsFSbB]\d+\.?\d*-?", "", slug)
    # Replace hyphens with spaces, title case
    name = name.replace("-", " ").replace("_", " ").strip()
    if name:
        return name.title()
    return slug


def epic_display_name(epic_dir: str) -> str:
    """Convert epic directory name to display name."""
    # e01-foundation → E01: Foundation
    # e325-agent-orchestrated-workflow → E325: Agent Orchestrated Workflow
    # raise-211-adapter-foundation → RAISE-211: Adapter Foundation
    match = re.match(r"^e(\d+)-(.+)$", epic_dir)
    if match:
        num, name = match.groups()
        return f"E{num}: {prettify_name(name)}"

    match = re.match(r"^raise-(\d+)-(.+)$", epic_dir)
    if match:
        num, name = match.groups()
        return f"RAISE-{num}: {prettify_name(name)}"

    return prettify_name(epic_dir)


def story_display_name(story_dir: str, epic_name: str) -> str:
    """Convert story directory to display name."""
    match = re.match(r"^([fFsS]\d+\.?\d*)-(.+)$", story_dir)
    if match:
        sid, name = match.groups()
        return f"{sid.upper()}: {prettify_name(name)}"
    return prettify_name(story_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Restructure Confluence pages into hierarchy")
    parser.add_argument("--manifest", default="work/epics/e935-confluence-content-migration/manifest-raise-commons.yaml")
    parser.add_argument("--registry", default=".raise/confluence-pages.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, help="Limit number of epics to process")
    parser.add_argument("--section", default="Epic Archives", help="Section to restructure")
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = yaml.safe_load(f)
    with open(args.registry) as f:
        registry = yaml.safe_load(f) or {}

    base_url, user, token = load_auth()

    # Group entries by epic → sub-group
    section_parent = {
        "Epic Archives": EPIC_ARCHIVES_ID,
        "Story Archives": STORY_ARCHIVES_ID,
        "Bug Archives": BUG_ARCHIVES_ID,
        "Research": RESEARCH_ID,
    }

    parent_id = section_parent.get(args.section)
    if not parent_id:
        print(f"Unknown section: {args.section}")
        sys.exit(1)

    # Build hierarchy from manifest
    groups: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))

    for entry in manifest.get("entries", []):
        if entry.get("section") != args.section:
            continue
        source = entry["source"]
        parts = source.split("/")

        if args.section == "Epic Archives":
            if len(parts) < 4:
                continue
            top_dir = parts[2]  # epic dir
            rest = "/".join(parts[3:])
            if "/" in rest:
                sub_parts = rest.split("/")
                if sub_parts[0] == "stories" and len(sub_parts) > 2:
                    sub_group = sub_parts[1]
                elif sub_parts[0] != "stories":
                    sub_group = sub_parts[0]
                else:
                    sub_group = "_root"
            else:
                sub_group = "_root"
        elif args.section == "Research":
            if len(parts) < 4:
                sub_group = "_root"
                top_dir = "_root"
            else:
                top_dir = parts[2]  # research topic dir
                sub_group = "_root"
        elif args.section == "Bug Archives":
            if len(parts) >= 4:
                top_dir = parts[2]  # bug dir (RAISE-541, etc.)
                sub_group = "_root"
            else:
                top_dir = "_root"
                sub_group = "_root"
        else:
            top_dir = "_root"
            sub_group = "_root"

        groups[top_dir][sub_group].append(entry)

    epic_list = sorted(groups.keys())
    if args.limit:
        epic_list = epic_list[:args.limit]

    print(f"Section: {args.section}")
    print(f"Top-level groups: {len(epic_list)}")
    print(f"Total sub-groups: {sum(len(groups[e]) for e in epic_list)}")
    print()

    created_parents = 0
    moved_pages = 0
    failed = 0

    for ei, top_dir in enumerate(epic_list):
        sub_groups = groups[top_dir]
        display_name = epic_display_name(top_dir) if args.section == "Epic Archives" else prettify_name(top_dir)

        # Skip _root as a top-level group
        if top_dir == "_root":
            continue

        total_files = sum(len(v) for v in sub_groups.values())
        print(f"[{ei+1}/{len(epic_list)}] {display_name} ({total_files} files)")

        if args.dry_run:
            epic_parent_id = f"DRY-{top_dir}"
            print(f"  CREATE PARENT: {display_name} under {args.section}")
        else:
            epic_parent_id = create_parent_page(
                base_url, user, token, "RaiSE1", display_name, parent_id,
                f"Archived artifacts for {display_name}",
            )
            if not epic_parent_id:
                print(f"  FAILED to create parent for {display_name}")
                failed += 1
                continue
            created_parents += 1
            time.sleep(RATE_LIMIT)

        # Process sub-groups
        for sg_name, entries in sorted(sub_groups.items()):
            if sg_name == "_root":
                # Root files go directly under epic parent
                target_parent = epic_parent_id
            else:
                # Create sub-group parent
                sg_display = story_display_name(sg_name, display_name)
                if args.dry_run:
                    print(f"  CREATE SUB-PARENT: {sg_display}")
                    target_parent = f"DRY-{sg_name}"
                else:
                    target_parent = create_parent_page(
                        base_url, user, token, "RaiSE1", f"{display_name} — {sg_display}", epic_parent_id,
                    )
                    if not target_parent:
                        print(f"  FAILED to create sub-parent for {sg_display}")
                        target_parent = epic_parent_id  # fallback to epic parent
                    else:
                        created_parents += 1
                    time.sleep(RATE_LIMIT)

            # Move pages under target parent
            for entry in entries:
                page_id = registry.get(entry["source"])
                if not page_id:
                    continue
                title = entry.get("title", entry["source"])
                if args.dry_run:
                    print(f"    MOVE: {title}")
                    moved_pages += 1
                else:
                    ok = move_page_under_parent(base_url, user, token, page_id, target_parent)
                    if ok:
                        moved_pages += 1
                    else:
                        print(f"    FAILED MOVE: {title}")
                        failed += 1
                    time.sleep(RATE_LIMIT)

    print(f"\n{'='*60}")
    print(f"Done: {created_parents} parents created, {moved_pages} pages moved, {failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

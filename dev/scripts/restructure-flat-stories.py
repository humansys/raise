#!/usr/bin/env python3
"""Restructure flat story files into story sub-folders within epics.

Handles the pattern: stories/s338.1-scope.md → S338.1/ folder
Groups by story ID extracted from filename.

Usage:
    python dev/scripts/restructure-flat-stories.py --dry-run
    python dev/scripts/restructure-flat-stories.py
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
    return url.rstrip("/"), user, token


def find_page(base_url: str, user: str, token: str, space_key: str, title: str) -> str | None:
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


def create_parent_page(base_url: str, user: str, token: str, title: str, parent_id: str) -> str | None:
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": "RaiSE1"},
        "ancestors": [{"id": parent_id}],
        "body": {"storage": {"value": "<p></p>", "representation": "storage"}},
    }
    resp = requests.post(
        f"{base_url}/wiki/rest/api/content",
        json=payload,
        auth=(user, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=60,
    )
    if resp.status_code == 400 and "already exists" in resp.text:
        return find_page(base_url, user, token, "RaiSE1", title)
    if not resp.ok:
        print(f"  ERROR creating '{title}': {resp.status_code}")
        return None
    return resp.json()["id"]


def move_page(base_url: str, user: str, token: str, page_id: str, parent_id: str) -> bool:
    resp = requests.get(
        f"{base_url}/wiki/rest/api/content/{page_id}?expand=version,ancestors",
        auth=(user, token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if not resp.ok:
        return False
    page = resp.json()
    ancestors = page.get("ancestors", [])
    if ancestors and ancestors[-1]["id"] == parent_id:
        return True

    resp2 = requests.put(
        f"{base_url}/wiki/rest/api/content/{page_id}",
        json={
            "type": "page",
            "title": page["title"],
            "status": "current",
            "ancestors": [{"id": parent_id}],
            "version": {"number": page["version"]["number"] + 1},
        },
        auth=(user, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    return resp2.ok


def epic_display_name(epic_dir: str) -> str:
    match = re.match(r"^e(\d+)-(.+)$", epic_dir)
    if match:
        num, name = match.groups()
        return f"E{num}: {name.replace('-', ' ').title()}"
    match = re.match(r"^raise-(\d+)-(.+)$", epic_dir)
    if match:
        num, name = match.groups()
        return f"RAISE-{num}: {name.replace('-', ' ').title()}"
    return epic_dir


def extract_story_id(filename: str) -> str | None:
    """Extract story ID from filename like s338.1-scope.md → S338.1, s15-1-scope.md → S15.1"""
    # Pattern: s338.1-xxx or s15-1-xxx
    match = re.match(r"^(s\d+\.\d+)", filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    # Pattern: s15-1-xxx (hyphen instead of dot)
    match = re.match(r"^(s\d+)-(\d+)-", filename, re.IGNORECASE)
    if match:
        return f"{match.group(1).upper()}.{match.group(2)}"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="work/epics/e935-confluence-content-migration/manifest-raise-commons.yaml")
    parser.add_argument("--registry", default=".raise/confluence-pages.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, help="Limit number of epics")
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = yaml.safe_load(f)
    with open(args.registry) as f:
        registry = yaml.safe_load(f) or {}

    base_url, user, token = load_auth()

    # Find flat story files and group by epic → story_id
    # Structure: epics[epic_dir][story_id] = [entries]
    epics: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))

    for entry in manifest.get("entries", []):
        if entry.get("section") != "Epic Archives":
            continue
        source = entry["source"]
        parts = source.split("/")
        if len(parts) < 5:
            continue
        epic_dir = parts[2]
        # Check if it's stories/filename.md (flat, no subdirectory)
        if parts[3] == "stories" and len(parts) == 5:
            filename = parts[4]
            story_id = extract_story_id(filename)
            if story_id:
                epics[epic_dir][story_id].append(entry)

    epic_list = sorted(epics.keys())
    if args.limit:
        epic_list = epic_list[:args.limit]

    total_stories = sum(len(stories) for e in epic_list for stories in epics[e].values())
    total_groups = sum(len(epics[e]) for e in epic_list)
    print(f"Epics with flat stories: {len(epic_list)}")
    print(f"Story groups to create: {total_groups}")
    print(f"Pages to move: {total_stories}")
    print()

    created = 0
    moved = 0
    failed = 0

    for ei, epic_dir in enumerate(epic_list):
        epic_name = epic_display_name(epic_dir)
        story_groups = epics[epic_dir]

        # Find the epic parent page in Confluence
        epic_parent_id = find_page(base_url, user, token, "RaiSE1", epic_name) if not args.dry_run else "DRY"
        if not epic_parent_id and not args.dry_run:
            print(f"[{ei+1}/{len(epic_list)}] SKIP {epic_name} — parent page not found")
            continue

        print(f"[{ei+1}/{len(epic_list)}] {epic_name} ({len(story_groups)} stories)")

        for story_id, entries in sorted(story_groups.items()):
            story_parent_title = f"{epic_name} — {story_id}"

            if args.dry_run:
                print(f"  CREATE: {story_parent_title}")
                for entry in entries:
                    print(f"    MOVE: {entry['title']}")
                created += 1
                moved += len(entries)
                continue

            # Create story parent
            story_parent_id = create_parent_page(base_url, user, token, story_parent_title, epic_parent_id)
            if not story_parent_id:
                print(f"  FAILED creating {story_parent_title}")
                failed += 1
                continue
            created += 1
            time.sleep(0.5)

            # Move pages under story parent
            for entry in entries:
                page_id = registry.get(entry["source"])
                if not page_id:
                    continue
                ok = move_page(base_url, user, token, page_id, story_parent_id)
                if ok:
                    moved += 1
                else:
                    print(f"    FAILED MOVE: {entry['title']}")
                    failed += 1
                time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"Done: {created} story parents created, {moved} pages moved, {failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Restructure flat Research pages into topic hierarchy.

Groups pages by research topic directory, creates parent pages,
and moves children under them.

Usage:
    python dev/scripts/restructure-research.py --dry-run
    python dev/scripts/restructure-research.py
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
import yaml

RESEARCH_PARENT_ID = "3074654209"  # Research page in RaiSE1


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


def find_page(base_url: str, user: str, token: str, title: str) -> str | None:
    resp = requests.get(
        f"{base_url}/wiki/rest/api/content",
        params={"title": title, "spaceKey": "RaiSE1", "type": "page", "limit": 1},
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
        return find_page(base_url, user, token, title)
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


def prettify_topic(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="work/epics/e935-confluence-content-migration/manifest-fix-reclassify.yaml")
    parser.add_argument("--registry", default=".raise/confluence-pages.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = yaml.safe_load(f)
    with open(args.registry) as f:
        registry = yaml.safe_load(f) or {}

    base_url, user, token = load_auth()

    # Group by topic
    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in manifest.get("entries", []):
        source = entry["source"]
        parts = source.split("/")

        if source.startswith("dev/research/"):
            groups["Strategic Research"].append(entry)
        elif source.startswith("dev/product/"):
            groups["Product"].append(entry)
        elif source.startswith("work/problem-briefs/"):
            groups["Problem Briefs"].append(entry)
        elif source.startswith("work/research/"):
            if len(parts) >= 4:
                topic = parts[2]
                # Skip generic dirs
                if topic in ("outputs", "prompts"):
                    groups[f"Research — {prettify_topic(topic)}"].append(entry)
                else:
                    groups[f"Research — {prettify_topic(topic)}"].append(entry)
            else:
                groups["Research — General"].append(entry)
        else:
            groups["Other"].append(entry)

    # Only process groups with >1 file (single files stay flat)
    group_list = sorted(groups.keys())
    if args.limit:
        group_list = group_list[:args.limit]

    multi_file = [(g, groups[g]) for g in group_list if len(groups[g]) > 1]
    single_file = [(g, groups[g]) for g in group_list if len(groups[g]) == 1]

    print(f"Groups with 2+ files (will create folders): {len(multi_file)}")
    print(f"Single-file groups (stay flat): {len(single_file)}")
    print(f"Total files: {sum(len(groups[g]) for g in group_list)}")
    print()

    created = 0
    moved = 0
    failed = 0

    for gi, (group_name, entries) in enumerate(multi_file):
        print(f"[{gi+1}/{len(multi_file)}] {group_name} ({len(entries)} files)")

        if args.dry_run:
            print(f"  CREATE PARENT: {group_name}")
            for entry in entries:
                print(f"    MOVE: {entry['title']}")
            created += 1
            moved += len(entries)
            continue

        # Create topic parent
        parent_id = create_parent_page(base_url, user, token, group_name, RESEARCH_PARENT_ID)
        if not parent_id:
            print(f"  FAILED creating parent")
            failed += 1
            continue
        created += 1
        time.sleep(0.5)

        # Move children
        for entry in entries:
            page_id = registry.get(entry["source"])
            if not page_id:
                continue
            ok = move_page(base_url, user, token, page_id, parent_id)
            if ok:
                moved += 1
            else:
                print(f"    FAILED: {entry['title']}")
                failed += 1
            time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"Done: {created} parents created, {moved} pages moved, {failed} failed")
    print(f"Single-file groups left flat: {len(single_file)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

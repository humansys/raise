#!/usr/bin/env python3
"""Restructure any flat section into topic hierarchy.

Generic version — works for Bug Archives, Story Archives, or any section.

Usage:
    python dev/scripts/restructure-section.py --section "Bug Archives" --parent-id 3144319109 --source-prefix work/bugs,work/hotfixes,work/issues
    python dev/scripts/restructure-section.py --section "Story Archives" --parent-id 3145728194 --source-prefix work/stories
"""

from __future__ import annotations

import argparse
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


def prettify(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="work/epics/e935-confluence-content-migration/manifest-raise-commons.yaml")
    parser.add_argument("--registry", default=".raise/confluence-pages.yaml")
    parser.add_argument("--section", required=True)
    parser.add_argument("--parent-id", required=True)
    parser.add_argument("--source-prefix", required=True, help="Comma-separated source prefixes")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = yaml.safe_load(f)
    with open(args.registry) as f:
        registry = yaml.safe_load(f) or {}

    base_url, user, token = load_auth()
    prefixes = [p.strip() for p in args.source_prefix.split(",")]

    # Group by subdirectory
    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in manifest.get("entries", []):
        if entry.get("section") != args.section:
            continue
        source = entry["source"]
        parts = source.split("/")
        if len(parts) >= 4:
            group_name = prettify(parts[2])
            groups[group_name].append(entry)
        else:
            groups["_root"].append(entry)

    multi = [(g, entries) for g, entries in sorted(groups.items()) if len(entries) > 1 and g != "_root"]
    single = [(g, entries) for g, entries in groups.items() if len(entries) == 1]

    print(f"Section: {args.section}")
    print(f"Groups with 2+ files: {len(multi)}")
    print(f"Single-file (stay flat): {len(single)}")
    print(f"Total files: {sum(len(v) for v in groups.values())}")
    print()

    created = 0
    moved = 0
    failed = 0

    for gi, (group_name, entries) in enumerate(multi):
        print(f"[{gi+1}/{len(multi)}] {group_name} ({len(entries)} files)")

        if args.dry_run:
            created += 1
            moved += len(entries)
            for e in entries:
                print(f"    MOVE: {e['title']}")
            continue

        parent_id = create_parent_page(base_url, user, token, group_name, args.parent_id)
        if not parent_id:
            failed += 1
            continue
        created += 1
        time.sleep(0.5)

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
    print(f"Done: {created} parents, {moved} moved, {failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

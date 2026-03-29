#!/usr/bin/env python3
"""Delete orphaned pages from STRAT that should have been in RaiSE1."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import requests
import yaml


def load_auth():
    env_path = ".env"
    result = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip().strip("'\"")
    url = result.get("JIRA_URL", result.get("CONFLUENCE_URL", ""))
    user = result.get("CONFLUENCE_USERNAME", "")
    token = result.get("CONFLUENCE_API_TOKEN", "")
    return url.rstrip("/"), user, token


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=".raise/confluence-pages.yaml")
    parser.add_argument("--manifest", required=True, help="Reclassify manifest (entries to delete from STRAT)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = yaml.safe_load(f)
    with open(args.registry) as f:
        registry = yaml.safe_load(f) or {}

    entries = manifest.get("entries", [])
    base_url, user, token = load_auth()
    total = len(entries) if not args.limit else min(args.limit, len(entries))

    deleted = 0
    for i, entry in enumerate(entries[:total]):
        source = entry["source"]
        page_id = registry.get(source)
        if not page_id:
            print(f"[{i+1}/{total}] SKIP (not in registry): {entry.get('title', source)}")
            continue

        if args.dry_run:
            print(f"[{i+1}/{total}] DRY-RUN DELETE: {entry.get('title', source)} (id={page_id})")
            deleted += 1
            continue

        resp = requests.delete(
            f"{base_url}/wiki/rest/api/content/{page_id}",
            auth=(user, token),
            timeout=30,
        )
        if resp.ok:
            print(f"[{i+1}/{total}] DELETED: {entry.get('title', source)} (id={page_id})")
            del registry[source]
            deleted += 1
        else:
            print(f"[{i+1}/{total}] FAILED: {entry.get('title', source)} — {resp.status_code}")

        time.sleep(0.3)

    if not args.dry_run:
        with open(args.registry, "w") as f:
            yaml.dump(registry, f, default_flow_style=False, sort_keys=True, allow_unicode=True)

    print(f"\nDone: {deleted} deleted out of {total}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fix page parents after bulk migration.

Reads manifests + registry, moves pages to correct parents:
1. raise-commons STRAT pages → RaiSE1 with correct parent
2. raise-gtm STRAT pages → assign correct STRAT parent
3. raise-commons RaiSE1 pages without parent → assign parent

Usage:
    python dev/scripts/fix-page-parents.py --dry-run
    python dev/scripts/fix-page-parents.py
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests
import yaml

# Import auth from migration script
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module


# ---------------------------------------------------------------------------
# Config: Section → Parent Page ID mapping
# ---------------------------------------------------------------------------

# RaiSE1 sections
RAISE1_PARENTS = {
    "Epic Archives": "3145269324",
    "Story Archives": "3145728194",
    "Bug Archives": "3144319109",
    "Analysis": "3145957387",
    "Research": "3074654209",
    "Architecture": "3145498673",
    "Developer Docs": "3145596958",
    "Product": "3145465885",
}

# STRAT sections
STRAT_PARENTS = {
    "10. Research": "3146022913",
    "11. GTM Operations": "3145990148",
    "12. GTM Content": "3144483168",
    "13. Sources & Transcripts": "3145498728",
    "1. Visión e Identidad": "3144319001",
    "2. Modelo de Producto": "3144319001",  # fallback
    "5. GTM Metodología": "3144319021",
    "6. Partnerships e Integraciones": "3144319021",  # fallback
    "7. Clientes y Evidencia": "3144319021",  # fallback
    "8. Roadmap y Futuro": "3144319021",  # fallback
}

# raise-commons sections that should be in RaiSE1 instead of STRAT
RECLASSIFY_TO_RAISE1 = {
    "10. Research": "Research",
    "8. Roadmap y Futuro": "Research",  # problem briefs → Research in RaiSE1
    "2. Modelo de Producto": "Product",
}


def load_auth():
    """Load auth same as migration script."""
    env_paths = [".env", str(Path.home() / "Code" / "raise-commons" / ".env")]
    for env_path in env_paths:
        if Path(env_path).exists():
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
            user = result.get("CONFLUENCE_USERNAME", result.get("CONFLUENCE_USER", ""))
            token = result.get("CONFLUENCE_API_TOKEN", "")
            if url and user and token:
                return url.rstrip("/"), user, token
    print("ERROR: No auth found", file=sys.stderr)
    sys.exit(1)


def move_page(base_url: str, user: str, token: str, page_id: str, target_space: str, parent_id: str) -> bool:
    """Move a page to a new space/parent using v2 API."""
    version = get_page_version(base_url, user, token, page_id)
    # v2 API supports cross-space moves
    resp = requests.put(
        f"{base_url}/wiki/api/v2/pages/{page_id}",
        json={
            "id": page_id,
            "status": "current",
            "spaceId": get_space_id(base_url, user, token, target_space),
            "parentId": parent_id,
            "version": {"number": version + 1, "message": "Moved by E935 migration fix"},
        },
        auth=(user, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    return resp.ok


def set_parent(base_url: str, user: str, token: str, page_id: str, parent_id: str) -> bool:
    """Set parent for a page (same space)."""
    # Get current page info (need title for v1 API)
    info = requests.get(
        f"{base_url}/wiki/rest/api/content/{page_id}?expand=version",
        auth=(user, token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    info.raise_for_status()
    page_data = info.json()
    version = page_data["version"]["number"]
    title = page_data["title"]

    resp = requests.put(
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
    return resp.ok


def get_page_version(base_url: str, user: str, token: str, page_id: str) -> int:
    resp = requests.get(
        f"{base_url}/wiki/rest/api/content/{page_id}?expand=version",
        auth=(user, token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["version"]["number"]


_space_ids: dict[str, str] = {}


def get_space_id(base_url: str, user: str, token: str, space_key: str) -> str:
    if space_key not in _space_ids:
        resp = requests.get(
            f"{base_url}/wiki/rest/api/space/{space_key}",
            auth=(user, token),
            headers={"Accept": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        _space_ids[space_key] = str(resp.json()["id"])
    return _space_ids[space_key]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix page parents after migration")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", required=True, help="Manifest YAML to fix")
    parser.add_argument("--registry", default=".raise/confluence-pages.yaml")
    parser.add_argument("--repo", default="raise-commons", choices=["raise-commons", "raise-gtm"])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    # Load data
    with open(args.manifest) as f:
        manifest = yaml.safe_load(f)
    with open(args.registry) as f:
        registry = yaml.safe_load(f) or {}

    entries = manifest.get("entries", [])
    base_url, user, token = load_auth()

    moved = 0
    skipped = 0
    failed = 0
    total = len(entries) if not args.limit else min(args.limit, len(entries))

    for i, entry in enumerate(entries[:total]):
        source = entry["source"]
        section = entry.get("section", "")
        space = entry.get("space", "STRAT")
        page_id = registry.get(source)

        if not page_id:
            skipped += 1
            continue

        # Determine target
        if args.repo == "raise-commons" and section in RECLASSIFY_TO_RAISE1:
            # Move from STRAT → RaiSE1
            target_section = RECLASSIFY_TO_RAISE1[section]
            target_parent = RAISE1_PARENTS.get(target_section)
            target_space = "RaiSE1"
            action = f"MOVE STRAT→RaiSE1/{target_section}"
        elif space == "RaiSE1":
            # Fix parent within RaiSE1
            target_parent = RAISE1_PARENTS.get(section)
            target_space = "RaiSE1"
            action = f"SET PARENT RaiSE1/{section}"
        elif space == "STRAT":
            # Fix parent within STRAT
            target_parent = STRAT_PARENTS.get(section)
            target_space = "STRAT"
            action = f"SET PARENT STRAT/{section}"
        else:
            skipped += 1
            continue

        if not target_parent:
            print(f"[{i+1}/{total}] SKIP (no parent mapping): {entry['title']} section={section}")
            skipped += 1
            continue

        prefix = f"[{i+1}/{total}]"

        if args.dry_run:
            print(f"{prefix} DRY-RUN {action}: {entry['title']} (id={page_id})")
            moved += 1
            continue

        if section in RECLASSIFY_TO_RAISE1 and args.repo == "raise-commons":
            ok = move_page(base_url, user, token, page_id, target_space, target_parent)
        else:
            ok = set_parent(base_url, user, token, page_id, target_parent)

        if ok:
            print(f"{prefix} OK {action}: {entry['title']}")
            moved += 1
        else:
            print(f"{prefix} FAILED {action}: {entry['title']}")
            failed += 1

        time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"Done: {moved} moved, {skipped} skipped, {failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

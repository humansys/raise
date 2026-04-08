---
name: rai-adapter-setup
description: >
  Interactive adapter setup for Jira and Confluence. Detects available
  backends, discovers projects/spaces, generates validated YAML config.
  3-4 questions max.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: once
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: "rai-doctor"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.4.0"
  raise.visibility: public
---

# Adapter Setup

## Purpose

Guide the user through configuring Jira and/or Confluence adapters. Uses live discovery to auto-detect projects, workflows, issue types, and spaces — the user never needs to look up IDs manually. Generated config is validated before writing.

## Context

**When to use:** New project setup, after `rai init`, or when `/rai-doctor` reports missing adapter config.

**When to skip:** Adapter config already exists and is working. Use `/rai-doctor` to verify.

**Inputs:** Environment variables must be set for the backends to configure:
- Jira: `JIRA_API_TOKEN` + `JIRA_EMAIL`
- Confluence: `CONFLUENCE_API_TOKEN` + `CONFLUENCE_USERNAME`

## Steps

### Step 1: Detect Available Backends

Check which backends have credentials available:

```python
import os

jira_available = bool(os.environ.get("JIRA_API_TOKEN"))
confluence_available = bool(os.environ.get("CONFLUENCE_API_TOKEN"))
```

Check for existing config files:

```bash
ls .raise/jira.yaml .raise/confluence.yaml 2>/dev/null
```

**Report to user:**

| Condition | Message |
|-----------|---------|
| No credentials at all | "No adapter credentials found. Set JIRA_API_TOKEN or CONFLUENCE_API_TOKEN first." — stop here |
| Jira available | "Jira credentials detected (JIRA_API_TOKEN is set)" |
| Confluence available | "Confluence credentials detected (CONFLUENCE_API_TOKEN is set)" |
| Config already exists | "Existing config found at .raise/{name}.yaml — I'll offer to regenerate or skip" |

**Question 1:** "Which adapters would you like to configure? [jira/confluence/both]"
(Default to whatever has credentials. Skip the question if only one has credentials.)

### Step 2: Discover (per selected backend)

#### Jira Discovery

```python
from raise_cli.adapters.jira_client import JiraClient
from raise_cli.adapters.jira_config import load_jira_config, JiraConfig
from raise_cli.adapters.jira_discovery import JiraDiscovery

# If existing config, use it for connection; otherwise construct manually
client = JiraClient.from_config(existing_config, instance_name)
discovery = JiraDiscovery(client)
project_map = discovery.discover()
```

Report: "Found {N} projects: {list of project keys}"

**Question 2 (Jira):** "Which project(s) to include? [comma-separated keys or 'all']"

#### Confluence Discovery

```python
from raise_cli.adapters.confluence_client import ConfluenceClient
from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig
from raise_cli.adapters.confluence_discovery import ConfluenceDiscoveryService

inst = ConfluenceInstanceConfig(
    instance_name="default",
    url=f"https://{site}/wiki",
    space_key="",  # discovery doesn't need this
)
client = ConfluenceClient(inst)
discovery = ConfluenceDiscoveryService(client)
spaces = discovery.discover_spaces()
```

Report: "Found {N} spaces: {list of space keys with names}"

**Question 3 (Confluence):** "Which space to use? [space key]"

Optionally, discover the page tree for routing suggestions:

```python
page_tree = discovery.discover_page_tree(selected_space)
from raise_cli.adapters.confluence_config_gen import suggest_routing
routing_suggestions = suggest_routing(page_tree)
```

Show suggestions to the user and let them confirm or customize.

### Step 3: Generate Config

#### Jira Config Generation

```python
from raise_cli.adapters.jira_config_gen import generate_jira_config

config_dict = generate_jira_config(
    project_map=project_map,
    selected_projects=selected_keys,
    instance_name=instance_name,
    site=site,
)

# Validate
JiraConfig.model_validate(config_dict)
```

#### Confluence Config Generation

```python
from raise_cli.adapters.confluence_config_gen import generate_confluence_config

config_dict = generate_confluence_config(
    spaces=spaces,
    selected_space=selected_space,
    instance_url=f"https://{site}/wiki",
    instance_name=instance_name,  # e.g. site subdomain or "default"
    routing=routing_suggestions,  # from suggest_routing(), or None for defaults
)

# Validate
from raise_cli.adapters.confluence_config import ConfluenceConfig
ConfluenceConfig.from_dict(config_dict)
```

### Step 4: Preview & Write

Show the generated YAML to the user:

```python
import yaml
print(yaml.dump(config_dict, default_flow_style=False, sort_keys=False))
```

**Question 4:** "Write this config to .raise/{adapter}.yaml? [y/n]"

If yes, write the file. For Confluence, use the dedicated writer:

```python
from raise_cli.adapters.confluence_config_gen import write_confluence_config
from pathlib import Path

write_confluence_config(config_dict, project_root=Path("."), overwrite=confirmed_overwrite)
```

For Jira, write directly:

```python
config_path = Path(".raise") / "jira.yaml"
config_path.parent.mkdir(parents=True, exist_ok=True)
with open(config_path, "w") as f:
    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
```

If config already existed, confirm overwrite explicitly.

### Step 5: Verify

Run doctor check on the newly written config:

```bash
rai doctor --json
```

Report the adapter check results. If all pass, confirm success.

**If errors remain:** Guide the user through the specific issues (same as `/rai-doctor` Step 4).

## Output

| Artifact | Destination |
|----------|-------------|
| Jira config | `.raise/jira.yaml` |
| Confluence config | `.raise/confluence.yaml` |
| Verification | Via `rai doctor` |

## Important Notes

- **The Jira site domain** (e.g. `humansys.atlassian.net`) must come from the user or existing config. Discovery cannot determine this from credentials alone.
- **Instance name** is a logical label (e.g. "humansys") — the user chooses it, or default to the site subdomain.
- **Confluence URL** format is `https://{site}/wiki` for Atlassian Cloud.
- **Never write secrets** to config files — credentials come from environment variables.
- **Existing config:** Always warn, always ask before overwriting.

## Quality Checklist

- [ ] Never write config without showing preview first
- [ ] Never overwrite existing config without explicit confirmation
- [ ] Validate generated config before writing (model_validate / from_dict)
- [ ] Report discovery errors gracefully — don't crash on partial failures
- [ ] 3-4 questions maximum — discovery replaces manual input
- [ ] After writing, verify with `rai doctor`

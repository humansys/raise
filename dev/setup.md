# Dev Environment Setup — raise-commons

> Internal guide for HumanSys maintainers. Not for external contributors.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Miniconda / Miniforge | any | https://docs.conda.io/en/latest/miniconda.html |
| uv | 0.10+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | any | system package manager |
| Python | 3.12+ | via conda (managed per env) |

---

## Workspace Structure

```
raise-commons/                  ← workspace root (raise-cli package)
├── pyproject.toml              ← uv workspace root + hatchling build
├── src/raise_cli/              ← CLI source
├── src/raise_core/             ← core library (bundled in raise-cli wheel)
└── packages/
    ├── raise-core/             ← workspace member, editable in rai-dev
    ├── raise-pro/              ← enterprise adapters: Jira, Confluence
    └── raise-server/           ← MCP server, dev-only dependency
```

All packages use **editable installs** — source changes are live immediately, no reinstall needed.

---

## Environments

| | `base` (conda) | `rai-dev` (conda) | `.venv` (uv) |
|--|--|--|--|
| Python | 3.13 | 3.12 | 3.12 |
| Purpose | system `rai` command | full dev, cross-package | tests, linting, CI |
| raise-cli | editable ✓ | editable ✓ | editable ✓ |
| raise-core | wheel | editable ✓ | editable ✓ |
| raise-pro | editable ✓ | editable ✓ | via `[dev]` |
| raise-server | ✗ | editable ✓ | via `[dev]` |

---

## Initial Setup (one-time)

### 1. Clone

```bash
git clone <repo-url> ~/Documents/raise-commons
cd ~/Documents/raise-commons
```

### 2. Create `rai-dev` — full dev environment

```bash
conda create -n rai-dev python=3.12 -y
conda run -n rai-dev pip install -e packages/raise-pro -e packages/raise-server -e ".[dev]"
```

**Why the order matters:** `raise-pro` and `raise-server` are uv workspace members — pip cannot
resolve them from PyPI. They must be installed as local editable packages before `.[dev]` is
processed, otherwise pip fails with "No matching distribution found for raise-pro".

> **Note (Miniconda on fresh installs):** If `conda create` fails with a TOS error, accept first:
> ```bash
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
> ```

### 3. Install in conda `base` (produces the system `rai` command)

```bash
pip install -e ".[dev]"
```

Same command as rai-dev. Keeps both environments in sync.

### 4. Create `.venv` with uv (for CI and lockfile management)

```bash
uv sync
```

### 5. Expose `rai` system-wide

```bash
ln -sf ~/miniconda3/bin/rai ~/.local/bin/rai
# confirm ~/.local/bin is in PATH
```

### 6. Verify

```bash
rai --version                                        # raise-cli 2.x.x
pip show raise-cli raise-pro                         # Location shows editable path
conda run -n rai-dev pip show raise-cli raise-server # same
uv run rai --version                                 # also works via .venv
```

---

## How `rai` Resolves

```
rai
  → ~/.local/bin/rai           (symlink)
    → ~/miniconda3/bin/rai     (script, shebang: ~/miniconda3/bin/python3.13)
```

**Quirk:** `conda run -n rai-dev rai` also resolves to `~/.local/bin/rai` because
`~/.local/bin` has precedence in PATH over conda env bins. Both envs point to the
same editable source, so it doesn't matter in practice.

To explicitly use the rai-dev binary (python3.12):
```bash
~/miniconda3/envs/rai-dev/bin/rai --version
```

---

## Which `rai` to Use

| Situation | Command |
|-----------|---------|
| Daily use, any project | `rai ...` |
| raise-commons development | `rai ...` (base) or `conda run -n rai-dev rai ...` — equivalent today |
| Tests / linting | `uv run pytest` / `uv run ruff check .` |
| Jira / Confluence features | confirm raise-pro in base: `pip show raise-pro` |

---

## Daily Workflow

```bash
uv run pytest                   # run tests
uv run ruff check .             # lint
uv run ruff format .            # format  ← run BEFORE pyright
uv run pyright src/             # type check  ← always after format
```

> `ruff format` can shift `# type: ignore` comments when splitting long lines,
> introducing new pyright errors. Always run pyright after format, not before.

---

## Updating After `git pull`

**Editable installs reflect code changes immediately** — Python files are read directly
from source on every import. No reinstall needed for day-to-day code changes.

That said, **we recommend reinstalling after any non-trivial code change:**

```bash
pip install -e .                                                                   # base
conda run -n rai-dev pip install -e packages/raise-pro -e packages/raise-server -e ".[dev]"  # rai-dev
```

Some changes require it even with editable installs:
- New `[project.entry-points]` in `pyproject.toml` (adapters, gates, hooks)
- New packages added to the wheel (`[tool.hatch.build.targets.wheel]`)
- Changes to package metadata or scripts

Reinstalling is fast (~2s) and avoids subtle "why isn't my change showing up" issues.

**`pyproject.toml` changed** (new deps):

```bash
uv sync                                                                                      # update .venv
conda run -n rai-dev pip install -e packages/raise-pro -e packages/raise-server -e ".[dev]" # update rai-dev
pip install -e .                                                                             # update base
```

**`packages/raise-pro/pyproject.toml` changed:**

```bash
pip install -e packages/raise-pro
conda run -n rai-dev pip install -e packages/raise-pro
```

---

## Troubleshooting

**`rai backlog -a jira` → "PM adapter 'jira' not found"**
raise-pro must be installed in the same Python that runs `rai` (base, python3.13):
```bash
pip install -e packages/raise-pro
```

**`rai` returns wrong version after code change**
Not possible with editable installs — source is read directly. If version string is
wrong, it's defined in `pyproject.toml` and requires a manual bump.

**`uv sync` fails with workspace member errors**
Some packages may lack a `pyproject.toml`. Check `packages/` for incomplete members.

**`snyk monitor` fails on this project (PAT-F-043)**
uv venvs don't include pip by default. snyk needs pip to resolve deps:
```bash
uv pip install pip
pip freeze | grep -v '^-e' > req.txt
snyk monitor --file=req.txt --command=.venv/bin/python --package-manager=pip \
  --org=aquileslazaroh --project-name=raise-commons
```

---
title: Installation Guide
---

# Installation Guide

Step-by-step instructions for installing RaiSE CLI on macOS, Linux, and Windows (WSL).

## Prerequisites (all platforms)

- **Python 3.12+** — check with `python3 --version`
- **pipx** — recommended for CLI tools (isolates dependencies)
- **Git** — for cloning and working with repositories
- **Claude Code** — [install from Anthropic](https://claude.ai/claude-code) for AI-assisted workflow

## macOS

### 1. Install Python

If you use Homebrew:

```bash
brew install python@3.12
```

**Known pitfall:** If you have `asdf` or `pyenv` installed, they may intercept your `python3` and `pip` commands. Check which Python is active:

```bash
which python3
python3 --version
```

If it points to an asdf/pyenv shim, either use that Python (if 3.12+) or temporarily bypass:

```bash
# Use Homebrew Python directly
/opt/homebrew/bin/python3.12 --version
```

### 2. Install pipx

```bash
brew install pipx
pipx ensurepath
```

Close and reopen your terminal after `ensurepath`.

### 3. Install RaiSE CLI

```bash
pipx install rai-cli
```

### 4. Verify

```bash
rai --version
```

You should see `rai-cli version X.Y.Z`.

---

## Linux (Ubuntu/Debian)

### 1. Install Python

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip -y
```

On other distributions, use your package manager or build from source.

**Known pitfall:** Same asdf/pyenv issue as macOS. Verify `python3 --version` returns 3.12+.

### 2. Install pipx

```bash
sudo apt install pipx -y
pipx ensurepath
```

Close and reopen your terminal after `ensurepath`.

### 3. Install RaiSE CLI

```bash
pipx install rai-cli
```

### 4. Verify

```bash
rai --version
```

---

## Windows (WSL)

RaiSE requires Windows Subsystem for Linux. Native Windows is not supported.

### 1. Set up WSL

If you don't have WSL yet:

```powershell
# In PowerShell as Administrator
wsl --install
```

This installs Ubuntu by default. Restart your computer, then open the Ubuntu terminal.

### 2. Install Python

Inside WSL (Ubuntu):

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip -y
```

### 3. Install pipx

```bash
sudo apt install pipx -y
pipx ensurepath
```

Close and reopen your WSL terminal.

### 4. Install RaiSE CLI

```bash
pipx install rai-cli
```

### 5. Verify

```bash
rai --version
```

---

## Development Setup (from source)

For contributors working on raise-commons itself:

```bash
# Clone the repository
git clone https://github.com/humansys/raise.git
cd raise-commons

# Checkout development branch
git checkout dev

# Create venv and install in dev mode
uv venv
uv pip install -e ".[dev]"

# Verify
rai --version
```

---

## Known Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| `python3` points to wrong version | asdf/pyenv shim | Use `which python3` to check, use system Python or configure your version manager |
| `pipx install` can't find `rai` | Old package version | Ensure you're installing `rai-cli` (not `raise-cli`) |
| `rai backlog` can't find credentials | `.env` not loaded | From v2.2+, CLI loads `.env` automatically. For older versions, `export` vars manually |
| `ModuleNotFoundError` after install | Conflicting installs | `pipx uninstall rai-cli && pipx install rai-cli` for a clean install |

## Next Steps

After installation:

1. Open Claude Code in your project directory
2. Run `/rai-welcome` for guided onboarding
3. Run `/rai-session-start` to begin your first session

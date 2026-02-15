# Backend Setup Guide with uv

## Overview

This backend project uses **uv** for package management, which is significantly faster than pip and provides better dependency resolution.

## Prerequisites

- Python 3.8 or higher
- uv package manager

## Installation Steps

### 1. Install uv

If you don't have uv installed yet:

```bash
# Using pip
pip install uv

# Or using the official installer (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# For Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Create Virtual Environment

```bash
cd backend
uv venv
```

This creates a `.venv` directory with an isolated Python environment.

### 3. Install Dependencies

There are two ways to install dependencies:

#### Option A: Using requirements.txt (Traditional)
```bash
uv pip install -r requirements.txt
```

#### Option B: Using pyproject.toml (Recommended)
```bash
uv sync
```

This reads from `pyproject.toml` and installs all dependencies automatically.

### 4. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.venv\Scripts\activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 5. Run the Application

**Traditional way:**
```bash
uvicorn app:app --reload
```

**Using uv run (Recommended):**
```bash
uv run uvicorn app:app --reload
```

## Common uv Commands

### Managing Dependencies

```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Update all dependencies
uv sync --upgrade

# List installed packages
uv pip list
```

### Virtual Environment

```bash
# Create virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.11

# Remove virtual environment
rm -rf .venv
```

### Running Scripts

```bash
# Run Python script
uv run python script.py

# Run any command in the virtual environment
uv run <command>
```

## Project Files

- **pyproject.toml**: Main project configuration and dependencies (uv format)
- **requirements.txt**: Traditional requirements file (for compatibility)
- **app.py**: Main FastAPI application

## Troubleshooting

### uv command not found

Make sure uv is in your PATH. You can add it manually:

**Windows PowerShell:**
```powershell
$env:Path += ";$env:USERPROFILE\.local\bin"
```

### Virtual environment issues

If you encounter issues with the virtual environment:

```bash
# Remove and recreate
rm -rf .venv
uv venv
uv sync
```

### Dependency conflicts

uv handles dependency conflicts automatically. If you still have issues:

```bash
# Clean and reinstall
uv cache clean
uv sync --reinstall
```

## Benefits of Using uv

1. **Speed**: 10-100x faster than pip
2. **Reliability**: Better dependency resolution
3. **Compatibility**: Works with existing pip workflows
4. **Modern**: Built with Rust for performance
5. **Simple**: Easy to learn and use

## Migration from pip

If you're migrating from pip to uv:

```bash
# Old way (pip)
pip install -r requirements.txt
python app.py

# New way (uv)
uv sync
uv run python app.py
```

The transition is straightforward, and uv maintains compatibility with pip workflows.
# Discovery Phase B: New Tool Operations (`prescan` + `assemble`) Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add two new operations (`prescan` and `assemble`) to the existing `tool-dot-graph` module, enabling structural codebase scanning and hierarchical DOT assembly — the deterministic building blocks for the discovery pipeline.

**Architecture:** Both operations are pure Python, deterministic, no LLM. `prescan` walks a repo directory tree and produces a structured JSON inventory (languages, modules, build manifests, entry points). `assemble` takes per-module DOT files + a manifest, merges them into subsystem DOT files with subgraph clusters + a bounded overview.dot. Both follow the existing module pattern: standalone `.py` files with a public entry function returning `dict`, routed from `__init__.py`.

**Tech Stack:** Python 3.11+, `os.walk`/`pathlib` (prescan), `pydot` (assemble), pytest + pytest-asyncio (tests)

---

## Codebase Orientation

The tool module lives at:
```
modules/tool-dot-graph/
├── amplifier_module_tool_dot_graph/
│   ├── __init__.py      # DotGraphTool class + mount() — routes operations
│   ├── validate.py      # validate_dot() → dict
│   ├── render.py        # render_dot() → dict
│   ├── setup_helper.py  # check_environment() → dict
│   └── analyze.py       # analyze_dot() → dict
├── tests/
│   ├── test_validate.py
│   ├── test_render.py
│   ├── test_setup_helper.py
│   ├── test_analyze.py
│   ├── test_tool_integration.py  # DotGraphTool routing + mount tests
│   └── test_mount.py
└── pyproject.toml
```

**Key patterns from existing code:**

1. **Module entry functions** return plain `dict` — never raise on user errors:
   - Success: `{"success": True, "operation": "...", ...result fields}`
   - Failure: `{"success": False, "error": "descriptive message"}`

2. **`__init__.py` routing** — `DotGraphTool.execute()` reads `operation` from `input_data`, dispatches to the matching module. Unknown operations return `{"error": "...", "supported": [...]}`.

3. **Test style** — Direct function imports, module-level DOT fixtures as constants, descriptive docstrings, assertion messages explaining expected vs actual.

4. **Current version** — `0.3.0` (4 operations). Phase B bumps to `0.4.0` (6 operations).

**Test command:**
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

**Full test suite (includes bundle-level tests):**
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ tests/ -v --tb=short
```

---

## Task 1: `prescan.py` — Core Scanning Logic

**Files:**
- Create: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/prescan.py`
- Test: `modules/tool-dot-graph/tests/test_prescan.py`

### Step 1: Write the failing tests

Create `modules/tool-dot-graph/tests/test_prescan.py` with the full test suite. These tests use `tmp_path` fixtures to build fake repo directories.

```python
"""Tests for prescan.py — structural codebase scanner.

Tests covering:
- Error handling: nonexistent path, file instead of directory, empty directory
- Language detection: Python files, Rust files, mixed languages
- Module boundary detection: Python packages, Rust crates, Go modules, Node packages
- Monorepo detection: multiple packages at top level
- Single-package repo: one module entry for main source directory
- Entry point detection: main.py, cli.py, __main__.py, main.rs, etc.
- Directory tree: nested dict with directories only, limited depth
- Skip directories: .git, node_modules, __pycache__, .venv, target, build, dist
- Build manifest detection: pyproject.toml, Cargo.toml, package.json, go.mod
- File counting: total_files and per-module file counts

All tests use tmp_path fixtures to build fake repo directories.
"""

import os

import pytest

from amplifier_module_tool_dot_graph.prescan import prescan_repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _touch(path: str) -> None:
    """Create an empty file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("")


def _touch_with_content(path: str, content: str) -> None:
    """Create a file with content, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


def test_nonexistent_path_returns_error():
    """Nonexistent repo_path returns success=False with descriptive error."""
    result = prescan_repo("/nonexistent/path/that/does/not/exist")

    assert result["success"] is False, "Nonexistent path must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower(), (
        f"Error must mention path not found, got: {result['error']}"
    )


def test_file_instead_of_directory_returns_error(tmp_path):
    """File path (not directory) returns success=False with descriptive error."""
    file_path = tmp_path / "somefile.txt"
    file_path.write_text("hello")

    result = prescan_repo(str(file_path))

    assert result["success"] is False, "File path must return success=False"
    assert "error" in result, "Error result must have 'error' key"


def test_empty_directory_returns_valid_result(tmp_path):
    """Empty directory returns success=True with zero files and empty modules."""
    result = prescan_repo(str(tmp_path))

    assert result["success"] is True, f"Empty dir must return success=True, got: {result}"
    assert result["total_files"] == 0, f"Empty dir must have 0 files, got: {result['total_files']}"
    assert result["modules"] == [], f"Empty dir must have no modules, got: {result['modules']}"
    assert result["languages"] == {}, f"Empty dir must have no languages, got: {result['languages']}"


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------


def test_result_has_all_required_fields(tmp_path):
    """Prescan result includes all required top-level fields."""
    _touch(str(tmp_path / "main.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True, f"Prescan must succeed, got: {result}"
    required_fields = [
        "success",
        "repo_path",
        "languages",
        "total_files",
        "modules",
        "build_manifests",
        "entry_points",
        "directory_tree",
    ]
    for field in required_fields:
        assert field in result, (
            f"Result must include '{field}', got keys: {list(result.keys())}"
        )


# ---------------------------------------------------------------------------
# Language detection tests
# ---------------------------------------------------------------------------


def test_language_detection_python_files(tmp_path):
    """Python files (.py) are detected and counted."""
    _touch(str(tmp_path / "app.py"))
    _touch(str(tmp_path / "utils.py"))
    _touch(str(tmp_path / "README.md"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert "py" in result["languages"], f"Must detect Python, got: {result['languages']}"
    assert result["languages"]["py"] == 2, (
        f"Must count 2 .py files, got: {result['languages']['py']}"
    )
    assert "md" in result["languages"], f"Must detect Markdown, got: {result['languages']}"
    assert result["languages"]["md"] == 1


def test_language_detection_mixed(tmp_path):
    """Multiple languages are detected and counted correctly."""
    _touch(str(tmp_path / "main.rs"))
    _touch(str(tmp_path / "lib.rs"))
    _touch(str(tmp_path / "build.rs"))
    _touch(str(tmp_path / "Cargo.toml"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert "rs" in result["languages"], f"Must detect Rust, got: {result['languages']}"
    assert result["languages"]["rs"] == 3
    assert "toml" in result["languages"]


def test_total_files_counts_all_files(tmp_path):
    """total_files counts every file (not directories)."""
    _touch(str(tmp_path / "a.py"))
    _touch(str(tmp_path / "b.py"))
    _touch(str(tmp_path / "sub" / "c.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert result["total_files"] == 3, f"Must count 3 files, got: {result['total_files']}"


# ---------------------------------------------------------------------------
# Skip directories tests
# ---------------------------------------------------------------------------


def test_skip_git_directory(tmp_path):
    """Files inside .git/ are not counted."""
    _touch(str(tmp_path / "app.py"))
    _touch(str(tmp_path / ".git" / "config"))
    _touch(str(tmp_path / ".git" / "HEAD"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert result["total_files"] == 1, (
        f".git files must be skipped, got total_files={result['total_files']}"
    )


def test_skip_node_modules(tmp_path):
    """Files inside node_modules/ are not counted."""
    _touch(str(tmp_path / "index.js"))
    _touch(str(tmp_path / "node_modules" / "lodash" / "index.js"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert result["total_files"] == 1, (
        f"node_modules files must be skipped, got total_files={result['total_files']}"
    )


def test_skip_pycache(tmp_path):
    """Files inside __pycache__/ are not counted."""
    _touch(str(tmp_path / "app.py"))
    _touch(str(tmp_path / "__pycache__" / "app.cpython-311.pyc"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert result["total_files"] == 1, (
        f"__pycache__ files must be skipped, got total_files={result['total_files']}"
    )


def test_skip_venv(tmp_path):
    """Files inside .venv/ are not counted."""
    _touch(str(tmp_path / "app.py"))
    _touch(str(tmp_path / ".venv" / "lib" / "site.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert result["total_files"] == 1, (
        f".venv files must be skipped, got total_files={result['total_files']}"
    )


# ---------------------------------------------------------------------------
# Module boundary detection tests
# ---------------------------------------------------------------------------


def test_detect_python_package(tmp_path):
    """Directory with __init__.py is detected as python_package module."""
    pkg = tmp_path / "src" / "auth"
    _touch(str(pkg / "__init__.py"))
    _touch(str(pkg / "models.py"))
    _touch(str(pkg / "views.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    module_names = [m["name"] for m in result["modules"]]
    assert "auth" in module_names, f"Must detect 'auth' package, got modules: {module_names}"

    auth_module = next(m for m in result["modules"] if m["name"] == "auth")
    assert auth_module["type"] == "python_package", (
        f"auth must be python_package, got: {auth_module['type']}"
    )
    assert auth_module["indicator"] == "__init__.py", (
        f"indicator must be __init__.py, got: {auth_module['indicator']}"
    )


def test_detect_rust_crate(tmp_path):
    """Directory with Cargo.toml is detected as rust_crate module."""
    crate = tmp_path / "my-crate"
    _touch_with_content(str(crate / "Cargo.toml"), '[package]\nname = "my-crate"\n')
    _touch(str(crate / "src" / "lib.rs"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    module_names = [m["name"] for m in result["modules"]]
    assert "my-crate" in module_names, f"Must detect 'my-crate', got modules: {module_names}"

    crate_module = next(m for m in result["modules"] if m["name"] == "my-crate")
    assert crate_module["type"] == "rust_crate", (
        f"Must be rust_crate, got: {crate_module['type']}"
    )
    assert crate_module["indicator"] == "Cargo.toml"


def test_detect_go_module(tmp_path):
    """Directory with go.mod is detected as go_module module."""
    gomod = tmp_path / "myservice"
    _touch_with_content(str(gomod / "go.mod"), "module github.com/org/myservice\n")
    _touch(str(gomod / "main.go"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    module_names = [m["name"] for m in result["modules"]]
    assert "myservice" in module_names, f"Must detect 'myservice', got modules: {module_names}"

    go_mod = next(m for m in result["modules"] if m["name"] == "myservice")
    assert go_mod["type"] == "go_module"
    assert go_mod["indicator"] == "go.mod"


def test_detect_node_package(tmp_path):
    """Directory with package.json is detected as node_package module."""
    pkg = tmp_path / "frontend"
    _touch_with_content(str(pkg / "package.json"), '{"name": "frontend"}\n')
    _touch(str(pkg / "index.ts"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    module_names = [m["name"] for m in result["modules"]]
    assert "frontend" in module_names, f"Must detect 'frontend', got modules: {module_names}"

    node_mod = next(m for m in result["modules"] if m["name"] == "frontend")
    assert node_mod["type"] == "node_package"
    assert node_mod["indicator"] == "package.json"


def test_module_file_count(tmp_path):
    """Module entry includes accurate file_count and files_by_type."""
    pkg = tmp_path / "src" / "auth"
    _touch(str(pkg / "__init__.py"))
    _touch(str(pkg / "models.py"))
    _touch(str(pkg / "views.py"))
    _touch(str(pkg / "README.md"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    auth_module = next(m for m in result["modules"] if m["name"] == "auth")
    assert auth_module["file_count"] == 4, (
        f"auth must have 4 files, got: {auth_module['file_count']}"
    )
    assert auth_module["files_by_type"]["py"] == 3, (
        f"auth must have 3 .py files, got: {auth_module['files_by_type']}"
    )
    assert auth_module["files_by_type"]["md"] == 1


# ---------------------------------------------------------------------------
# Monorepo detection tests
# ---------------------------------------------------------------------------


def test_monorepo_multiple_packages(tmp_path):
    """Monorepo with multiple packages at top level detects all of them."""
    # Python package
    _touch(str(tmp_path / "auth-service" / "__init__.py"))
    _touch(str(tmp_path / "auth-service" / "main.py"))

    # Node package
    _touch_with_content(
        str(tmp_path / "frontend" / "package.json"),
        '{"name": "frontend"}\n',
    )
    _touch(str(tmp_path / "frontend" / "index.ts"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    module_names = [m["name"] for m in result["modules"]]
    assert len(result["modules"]) >= 2, (
        f"Monorepo must detect >= 2 modules, got: {module_names}"
    )
    assert "auth-service" in module_names, f"Must detect auth-service, got: {module_names}"
    assert "frontend" in module_names, f"Must detect frontend, got: {module_names}"


# ---------------------------------------------------------------------------
# Build manifest detection tests
# ---------------------------------------------------------------------------


def test_build_manifest_detection(tmp_path):
    """Build manifests at repo root are detected."""
    _touch_with_content(str(tmp_path / "pyproject.toml"), "[project]\nname = 'test'\n")
    _touch(str(tmp_path / "setup.py"))
    _touch(str(tmp_path / "main.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert "pyproject.toml" in result["build_manifests"], (
        f"Must detect pyproject.toml, got: {result['build_manifests']}"
    )


def test_build_manifest_detection_cargo(tmp_path):
    """Cargo.toml at repo root is detected as a build manifest."""
    _touch_with_content(str(tmp_path / "Cargo.toml"), "[package]\nname = 'test'\n")
    _touch(str(tmp_path / "src" / "main.rs"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert "Cargo.toml" in result["build_manifests"], (
        f"Must detect Cargo.toml, got: {result['build_manifests']}"
    )


# ---------------------------------------------------------------------------
# Entry point detection tests
# ---------------------------------------------------------------------------


def test_entry_point_detection_python(tmp_path):
    """Python entry points (main.py, cli.py, __main__.py) are detected."""
    _touch(str(tmp_path / "main.py"))
    _touch(str(tmp_path / "cli.py"))
    _touch(str(tmp_path / "utils.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    assert "main.py" in result["entry_points"], (
        f"Must detect main.py, got: {result['entry_points']}"
    )
    assert "cli.py" in result["entry_points"], (
        f"Must detect cli.py, got: {result['entry_points']}"
    )
    assert "utils.py" not in result["entry_points"], (
        f"utils.py is not an entry point, got: {result['entry_points']}"
    )


def test_entry_point_detection_nested(tmp_path):
    """Entry points in subdirectories are detected with relative path."""
    _touch(str(tmp_path / "src" / "main.py"))
    _touch(str(tmp_path / "src" / "helpers.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    # Should find main.py with its relative path
    entry_basenames = [os.path.basename(e) for e in result["entry_points"]]
    assert "main.py" in entry_basenames, (
        f"Must detect nested main.py, got: {result['entry_points']}"
    )


# ---------------------------------------------------------------------------
# Directory tree tests
# ---------------------------------------------------------------------------


def test_directory_tree_structure(tmp_path):
    """Directory tree is a nested dict with directories only (not files)."""
    _touch(str(tmp_path / "src" / "auth" / "models.py"))
    _touch(str(tmp_path / "src" / "payments" / "views.py"))
    _touch(str(tmp_path / "tests" / "test_auth.py"))
    _touch(str(tmp_path / "docs" / "README.md"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    tree = result["directory_tree"]
    assert "src" in tree, f"Tree must contain 'src', got: {tree}"
    assert "tests" in tree, f"Tree must contain 'tests', got: {tree}"
    assert "docs" in tree, f"Tree must contain 'docs', got: {tree}"
    # Nested directories
    assert "auth" in tree["src"], f"src must contain 'auth', got: {tree['src']}"
    assert "payments" in tree["src"], f"src must contain 'payments', got: {tree['src']}"


def test_directory_tree_excludes_skipped_dirs(tmp_path):
    """Directory tree excludes .git, node_modules, __pycache__, etc."""
    _touch(str(tmp_path / "src" / "app.py"))
    _touch(str(tmp_path / ".git" / "config"))
    _touch(str(tmp_path / "node_modules" / "lodash" / "index.js"))
    _touch(str(tmp_path / "__pycache__" / "app.cpython-311.pyc"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    tree = result["directory_tree"]
    assert ".git" not in tree, f".git must be excluded from tree, got: {tree}"
    assert "node_modules" not in tree, f"node_modules must be excluded, got: {tree}"
    assert "__pycache__" not in tree, f"__pycache__ must be excluded, got: {tree}"


def test_directory_tree_depth_limit(tmp_path):
    """Directory tree is limited to 4 levels of depth."""
    # Create 6 levels deep
    _touch(str(tmp_path / "a" / "b" / "c" / "d" / "e" / "f" / "file.py"))

    result = prescan_repo(str(tmp_path))

    assert result["success"] is True
    tree = result["directory_tree"]

    # Walk the tree to check depth doesn't exceed 4
    def _max_depth(d: dict, current: int = 0) -> int:
        if not d:
            return current
        return max(_max_depth(v, current + 1) for v in d.values())

    depth = _max_depth(tree)
    assert depth <= 4, f"Tree depth must be <= 4, got: {depth}"
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_prescan.py -v --tb=short 2>&1 | head -30
```
Expected: `ModuleNotFoundError: No module named 'amplifier_module_tool_dot_graph.prescan'`

### Step 3: Write the implementation

Create `modules/tool-dot-graph/amplifier_module_tool_dot_graph/prescan.py`:

```python
"""Structural codebase scanner for the discovery pipeline.

Walks a repository directory tree and produces a structured JSON inventory:
languages, file counts, detected modules/packages, build manifests,
entry points, and directory tree.

Pure Python — uses os.walk and pathlib. No LLM, no graphviz.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Directories to skip during scanning.
_SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        "target",
        "build",
        "dist",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".eggs",
        "egg-info",
    }
)

# Module boundary indicators — ordered by specificity.
# (indicator_filename, module_type)
_MODULE_INDICATORS: list[tuple[str, str]] = [
    ("Cargo.toml", "rust_crate"),
    ("go.mod", "go_module"),
    ("package.json", "node_package"),
    ("__init__.py", "python_package"),
]

# Build manifest filenames to detect at repo root.
_BUILD_MANIFESTS: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "Cargo.toml",
        "Cargo.lock",
        "go.mod",
        "go.sum",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Makefile",
        "CMakeLists.txt",
        "build.gradle",
        "pom.xml",
    }
)

# Entry point filenames (basenames).
_ENTRY_POINTS: frozenset[str] = frozenset(
    {
        "main.py",
        "cli.py",
        "__main__.py",
        "app.py",
        "main.rs",
        "main.go",
        "index.ts",
        "index.js",
        "index.tsx",
        "index.jsx",
        "server.py",
        "server.ts",
        "server.js",
    }
)

# Maximum depth for directory tree output.
_MAX_TREE_DEPTH: int = 4


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def prescan_repo(repo_path: str) -> dict:
    """Scan a repository directory and produce a structural inventory.

    Args:
        repo_path: Absolute or relative path to the repository root.

    Returns:
        On success:
            {
                success: True,
                repo_path: str,
                languages: {ext: count},
                total_files: int,
                modules: [{name, path, type, indicator, file_count, files_by_type}],
                build_manifests: [str],
                entry_points: [str],
                directory_tree: {nested dict of dirs},
            }
        On failure:
            {success: False, error: str}
    """
    repo = Path(repo_path).resolve()

    if not repo.exists():
        return {"success": False, "error": f"Path not found: {repo_path}"}

    if not repo.is_dir():
        return {"success": False, "error": f"Path is not a directory: {repo_path}"}

    # Walk the repo and collect all file paths (relative to repo root).
    all_files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        # Prune skipped directories in-place so os.walk doesn't descend.
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]

        for filename in filenames:
            rel = os.path.relpath(os.path.join(dirpath, filename), repo)
            all_files.append(rel)

    # Language detection by extension.
    languages: dict[str, int] = {}
    for f in all_files:
        ext = _get_extension(f)
        if ext:
            languages[ext] = languages.get(ext, 0) + 1

    # Module boundary detection.
    modules = _detect_modules(repo, all_files)

    # Build manifest detection (repo root only).
    build_manifests = _detect_build_manifests(repo)

    # Entry point detection.
    entry_points = _detect_entry_points(all_files)

    # Directory tree.
    directory_tree = _build_directory_tree(repo, max_depth=_MAX_TREE_DEPTH)

    return {
        "success": True,
        "repo_path": str(repo),
        "languages": languages,
        "total_files": len(all_files),
        "modules": modules,
        "build_manifests": build_manifests,
        "entry_points": entry_points,
        "directory_tree": directory_tree,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_extension(filepath: str) -> str:
    """Extract the file extension without the dot, or empty string if none."""
    _, ext = os.path.splitext(filepath)
    return ext.lstrip(".").lower() if ext else ""


def _detect_modules(repo: Path, all_files: list[str]) -> list[dict]:
    """Detect module boundaries using language-specific heuristics.

    Walks the directory tree looking for indicator files (__init__.py,
    Cargo.toml, go.mod, package.json). Each detected module gets a dict
    with name, path, type, indicator, file_count, and files_by_type.
    """
    modules: list[dict] = []
    seen_paths: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(repo):
        # Prune skipped directories.
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]

        rel_dir = os.path.relpath(dirpath, repo)
        if rel_dir == ".":
            # Skip repo root for module detection — root-level indicators
            # are captured as build manifests, not as modules.
            continue

        for indicator, module_type in _MODULE_INDICATORS:
            if indicator in filenames and rel_dir not in seen_paths:
                # Count files belonging to this module.
                module_files = [
                    f for f in all_files
                    if f.startswith(rel_dir + os.sep) or f.startswith(rel_dir + "/")
                ]
                # Also include files directly in the module directory.
                module_files_direct = [
                    f for f in all_files
                    if os.path.dirname(f) == rel_dir
                ]
                # Combine — module_files already includes direct, but let's be safe.
                module_file_set = set(module_files) | set(module_files_direct)

                files_by_type: dict[str, int] = {}
                for mf in module_file_set:
                    ext = _get_extension(mf)
                    if ext:
                        files_by_type[ext] = files_by_type.get(ext, 0) + 1

                modules.append(
                    {
                        "name": os.path.basename(dirpath),
                        "path": rel_dir,
                        "type": module_type,
                        "indicator": indicator,
                        "file_count": len(module_file_set),
                        "files_by_type": files_by_type,
                    }
                )
                seen_paths.add(rel_dir)
                break  # Only one indicator per directory.

    return modules


def _detect_build_manifests(repo: Path) -> list[str]:
    """Detect build manifest files at the repo root."""
    manifests: list[str] = []
    try:
        for entry in sorted(os.listdir(repo)):
            if entry in _BUILD_MANIFESTS:
                manifests.append(entry)
    except OSError:
        pass
    return manifests


def _detect_entry_points(all_files: list[str]) -> list[str]:
    """Detect entry point files by basename matching."""
    entry_points: list[str] = []
    for f in sorted(all_files):
        basename = os.path.basename(f)
        if basename in _ENTRY_POINTS:
            entry_points.append(f)
    return entry_points


def _build_directory_tree(repo: Path, max_depth: int = 4) -> dict:
    """Build a nested dict representing the directory structure.

    Only includes directories (not files). Limited to max_depth levels.
    Skips directories in _SKIP_DIRS.
    """
    tree: dict = {}

    for dirpath, dirnames, _filenames in os.walk(repo):
        # Prune skipped directories.
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)

        rel_dir = os.path.relpath(dirpath, repo)
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1

        if depth >= max_depth:
            dirnames.clear()  # Stop descending.
            continue

        if rel_dir == ".":
            # Top level — add each direct subdirectory.
            for d in dirnames:
                tree[d] = {}
        else:
            # Navigate to the correct nested dict and add subdirectories.
            parts = rel_dir.replace(os.sep, "/").split("/")
            node = tree
            for part in parts:
                if part not in node:
                    node[part] = {}
                node = node[part]
            for d in dirnames:
                node[d] = {}

    return tree
```

### Step 4: Run tests to verify they pass

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_prescan.py -v --tb=short
```
Expected: All tests PASS.

### Step 5: Run the full test suite to verify no regressions

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ tests/ -v --tb=short 2>&1 | tail -20
```
Expected: All existing tests still pass.

### Step 6: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/prescan.py modules/tool-dot-graph/tests/test_prescan.py && git commit -m "feat: add prescan operation — structural codebase scanner"
```

---

## Task 2: `assemble.py` — Hierarchical DOT Assembly

**Files:**
- Create: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py`
- Test: `modules/tool-dot-graph/tests/test_assemble.py`

### Step 1: Write the failing tests

Create `modules/tool-dot-graph/tests/test_assemble.py`:

```python
"""Tests for assemble.py — hierarchical DOT assembly.

Tests covering:
- Error handling: missing manifest, empty manifest, missing DOT files
- Subsystem assembly: modules grouped into subgraph clusters
- Overview assembly: subsystems as subgraph clusters in overview.dot
- Overview bounds: <=250 lines, <=80 nodes (collapse when exceeded)
- Cross-module edge preservation
- Ancestor invalidation: only regenerate affected subsystems
- Result structure: outputs dict, stats
- Legend injection: every output has subgraph cluster_legend

All tests use tmp_path fixtures for DOT file I/O.
"""

import os

import pydot
import pytest

from amplifier_module_tool_dot_graph.assemble import assemble_hierarchy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_dot(path: str, content: str) -> None:
    """Write DOT content to a file, creating parent directories."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def _make_module_dot(name: str, nodes: list[str], edges: list[tuple[str, str]]) -> str:
    """Generate a simple digraph DOT string for a module."""
    lines = [f"digraph {name} {{"]
    for node in nodes:
        lines.append(f'    {node} [label="{node}"];')
    for src, dst in edges:
        lines.append(f"    {src} -> {dst};")
    lines.append("}")
    return "\n".join(lines)


def _simple_manifest(tmp_path, modules_config: dict) -> dict:
    """Build a manifest and write DOT files for the given modules config.

    modules_config: {
        "module_name": {
            "subsystem": "subsystem_name",
            "nodes": ["a", "b"],
            "edges": [("a", "b")],
        },
        ...
    }

    Returns the manifest dict ready for assemble_hierarchy().
    """
    manifest: dict = {"modules": {}, "subsystems": {}}
    subsystem_modules: dict[str, list[str]] = {}

    for mod_name, config in modules_config.items():
        dot_content = _make_module_dot(mod_name, config["nodes"], config["edges"])
        dot_path = str(tmp_path / "modules" / mod_name / "diagram.dot")
        _write_dot(dot_path, dot_content)

        manifest["modules"][mod_name] = {
            "dot_path": dot_path,
            "subsystem": config["subsystem"],
        }

        subsystem = config["subsystem"]
        if subsystem not in subsystem_modules:
            subsystem_modules[subsystem] = []
        subsystem_modules[subsystem].append(mod_name)

    for ss_name, mods in subsystem_modules.items():
        manifest["subsystems"][ss_name] = {"modules": mods}

    return manifest


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


def test_missing_manifest_returns_error(tmp_path):
    """None or empty manifest returns success=False."""
    result = assemble_hierarchy({}, str(tmp_path / "output"))

    assert result["success"] is False, "Empty manifest must return success=False"
    assert "error" in result, "Error result must have 'error' key"


def test_manifest_missing_modules_key_returns_error(tmp_path):
    """Manifest without 'modules' key returns success=False."""
    result = assemble_hierarchy({"subsystems": {}}, str(tmp_path / "output"))

    assert result["success"] is False, "Missing 'modules' key must return success=False"
    assert "error" in result


def test_missing_dot_file_warns_and_skips(tmp_path):
    """When a module DOT file doesn't exist, that module is skipped with a warning."""
    manifest = {
        "modules": {
            "auth": {
                "dot_path": str(tmp_path / "nonexistent.dot"),
                "subsystem": "identity",
            },
        },
        "subsystems": {
            "identity": {"modules": ["auth"]},
        },
    }

    result = assemble_hierarchy(manifest, str(tmp_path / "output"))

    assert result["success"] is True, (
        f"Missing DOT file should warn, not fail, got: {result}"
    )
    assert "warnings" in result, "Result must include warnings for missing files"
    assert len(result["warnings"]) > 0, "Must have at least one warning"


# ---------------------------------------------------------------------------
# Subsystem assembly tests
# ---------------------------------------------------------------------------


def test_subsystem_dot_contains_module_clusters(tmp_path):
    """Subsystem DOT file wraps each module in a subgraph cluster."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login", "logout"],
            "edges": [("login", "logout")],
        },
        "sessions": {
            "subsystem": "identity",
            "nodes": ["create_session", "destroy_session"],
            "edges": [("create_session", "destroy_session")],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True, f"Assembly must succeed, got: {result}"
    assert "identity" in result["outputs"]["subsystems"], (
        f"Must produce identity subsystem, got: {result['outputs']}"
    )

    # Read the subsystem DOT and verify it has cluster subgraphs.
    identity_path = result["outputs"]["subsystems"]["identity"]
    assert os.path.exists(identity_path), f"Subsystem file must exist at {identity_path}"

    with open(identity_path) as f:
        dot_content = f.read()

    assert "cluster_auth" in dot_content, (
        f"Subsystem DOT must contain cluster_auth, got:\n{dot_content}"
    )
    assert "cluster_sessions" in dot_content, (
        f"Subsystem DOT must contain cluster_sessions, got:\n{dot_content}"
    )


def test_subsystem_dot_is_valid(tmp_path):
    """Subsystem DOT output is parseable by pydot."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login", "logout"],
            "edges": [("login", "logout")],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    identity_path = result["outputs"]["subsystems"]["identity"]

    with open(identity_path) as f:
        dot_content = f.read()

    parsed = pydot.graph_from_dot_data(dot_content)
    assert parsed is not None and len(parsed) > 0, (
        f"Subsystem DOT must be parseable, got:\n{dot_content}"
    )


def test_subsystem_preserves_nodes(tmp_path):
    """Subsystem DOT contains the original module nodes."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login", "logout", "verify"],
            "edges": [("login", "verify"), ("verify", "logout")],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    identity_path = result["outputs"]["subsystems"]["identity"]

    with open(identity_path) as f:
        dot_content = f.read()

    assert "login" in dot_content, f"Must preserve 'login' node, got:\n{dot_content}"
    assert "logout" in dot_content, f"Must preserve 'logout' node, got:\n{dot_content}"
    assert "verify" in dot_content, f"Must preserve 'verify' node, got:\n{dot_content}"


# ---------------------------------------------------------------------------
# Overview assembly tests
# ---------------------------------------------------------------------------


def test_overview_dot_is_produced(tmp_path):
    """Assembly produces an overview.dot file."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login"],
            "edges": [],
        },
        "payments": {
            "subsystem": "billing",
            "nodes": ["charge"],
            "edges": [],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    assert "overview" in result["outputs"], f"Must produce overview, got: {result['outputs']}"
    assert os.path.exists(result["outputs"]["overview"]), "overview.dot must exist on disk"


def test_overview_contains_subsystem_clusters(tmp_path):
    """Overview DOT contains subgraph clusters for each subsystem."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login"],
            "edges": [],
        },
        "payments": {
            "subsystem": "billing",
            "nodes": ["charge"],
            "edges": [],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    with open(result["outputs"]["overview"]) as f:
        dot_content = f.read()

    assert "cluster_identity" in dot_content, (
        f"Overview must contain cluster_identity, got:\n{dot_content}"
    )
    assert "cluster_billing" in dot_content, (
        f"Overview must contain cluster_billing, got:\n{dot_content}"
    )


def test_overview_is_valid_dot(tmp_path):
    """Overview DOT is parseable by pydot."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login", "logout"],
            "edges": [("login", "logout")],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    with open(result["outputs"]["overview"]) as f:
        dot_content = f.read()

    parsed = pydot.graph_from_dot_data(dot_content)
    assert parsed is not None and len(parsed) > 0, (
        f"Overview DOT must be parseable, got:\n{dot_content}"
    )


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------


def test_result_has_all_required_fields(tmp_path):
    """Assembly result includes success, outputs, and stats."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login"],
            "edges": [],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    assert "outputs" in result, f"Must have 'outputs', got keys: {list(result.keys())}"
    assert "stats" in result, f"Must have 'stats', got keys: {list(result.keys())}"
    assert "overview" in result["outputs"]
    assert "subsystems" in result["outputs"]


def test_stats_are_accurate(tmp_path):
    """Stats report correct total_nodes, total_edges, subsystems, modules counts."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login", "logout"],
            "edges": [("login", "logout")],
        },
        "sessions": {
            "subsystem": "identity",
            "nodes": ["create", "destroy"],
            "edges": [("create", "destroy")],
        },
        "payments": {
            "subsystem": "billing",
            "nodes": ["charge", "refund"],
            "edges": [("charge", "refund")],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    stats = result["stats"]
    assert stats["total_nodes"] == 6, f"Must have 6 nodes, got: {stats['total_nodes']}"
    assert stats["total_edges"] == 3, f"Must have 3 edges, got: {stats['total_edges']}"
    assert stats["subsystems"] == 2, f"Must have 2 subsystems, got: {stats['subsystems']}"
    assert stats["modules"] == 3, f"Must have 3 modules, got: {stats['modules']}"


# ---------------------------------------------------------------------------
# Ancestor invalidation tests
# ---------------------------------------------------------------------------


def test_invalidation_only_regenerates_affected(tmp_path):
    """With invalidated_modules, only affected subsystems + overview are regenerated."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login"],
            "edges": [],
        },
        "payments": {
            "subsystem": "billing",
            "nodes": ["charge"],
            "edges": [],
        },
    })
    manifest["invalidated_modules"] = ["auth"]

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    assert "regenerated" in result, f"Must report regenerated, got keys: {list(result.keys())}"
    assert "identity" in result["regenerated"], (
        f"identity must be regenerated, got: {result['regenerated']}"
    )
    assert "skipped" in result, f"Must report skipped, got keys: {list(result.keys())}"
    assert "billing" in result["skipped"], (
        f"billing must be skipped, got: {result['skipped']}"
    )


def test_full_regeneration_without_invalidation(tmp_path):
    """Without invalidated_modules, all subsystems are regenerated."""
    manifest = _simple_manifest(tmp_path, {
        "auth": {
            "subsystem": "identity",
            "nodes": ["login"],
            "edges": [],
        },
        "payments": {
            "subsystem": "billing",
            "nodes": ["charge"],
            "edges": [],
        },
    })

    output_dir = str(tmp_path / "output")
    result = assemble_hierarchy(manifest, output_dir)

    assert result["success"] is True
    # Both subsystems should be in outputs.
    assert "identity" in result["outputs"]["subsystems"]
    assert "billing" in result["outputs"]["subsystems"]
    # No skipped when no invalidation specified.
    assert result.get("skipped", []) == [], (
        f"Without invalidation, nothing should be skipped, got: {result.get('skipped')}"
    )
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_assemble.py -v --tb=short 2>&1 | head -30
```
Expected: `ModuleNotFoundError: No module named 'amplifier_module_tool_dot_graph.assemble'`

### Step 3: Write the implementation

Create `modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py`:

```python
"""Hierarchical DOT assembly for the discovery pipeline.

Takes per-module DOT files and a manifest describing the hierarchy,
and produces subsystem DOT files (modules as subgraph clusters)
and a bounded overview.dot (subsystems as subgraph clusters).

Pure pydot graph manipulation — deterministic, no LLM.
"""

from __future__ import annotations

import contextlib
import io
import os
from datetime import datetime, timezone

import pydot


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Overview bounds — if exceeded, collapse module detail.
_MAX_OVERVIEW_LINES: int = 250
_MAX_OVERVIEW_NODES: int = 80


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assemble_hierarchy(
    manifest: dict,
    output_dir: str,
) -> dict:
    """Assemble per-module DOT files into subsystem and overview graphs.

    Args:
        manifest: Hierarchy manifest with 'modules' and 'subsystems' keys.
            Optional 'invalidated_modules' list for incremental regeneration.
        output_dir: Directory to write output DOT files.

    Returns:
        On success:
            {
                success: True,
                outputs: {overview: str, subsystems: {name: path}},
                stats: {total_nodes, total_edges, subsystems, modules},
                warnings: [str],
                regenerated: [str],  # subsystem names that were regenerated
                skipped: [str],      # subsystem names skipped due to invalidation
            }
        On failure:
            {success: False, error: str}
    """
    # Validate manifest.
    if not manifest or not isinstance(manifest, dict):
        return {"success": False, "error": "Manifest is empty or not a dict"}

    if "modules" not in manifest:
        return {"success": False, "error": "Manifest missing required 'modules' key"}

    if "subsystems" not in manifest:
        return {"success": False, "error": "Manifest missing required 'subsystems' key"}

    modules_def = manifest["modules"]
    subsystems_def = manifest["subsystems"]
    invalidated_modules: list[str] | None = manifest.get("invalidated_modules")

    warnings: list[str] = []
    total_nodes = 0
    total_edges = 0
    modules_processed = 0

    # Parse all module DOT files.
    parsed_modules: dict[str, pydot.Dot] = {}
    for mod_name, mod_info in modules_def.items():
        dot_path = mod_info.get("dot_path", "")
        if not dot_path or not os.path.exists(dot_path):
            warnings.append(
                f"Module '{mod_name}': DOT file not found at '{dot_path}', skipping"
            )
            continue

        graph = _parse_dot_file(dot_path)
        if graph is None:
            warnings.append(
                f"Module '{mod_name}': Failed to parse DOT file at '{dot_path}', skipping"
            )
            continue

        parsed_modules[mod_name] = graph
        modules_processed += 1

        # Count nodes and edges.
        node_count, edge_count = _count_graph_elements(graph)
        total_nodes += node_count
        total_edges += edge_count

    # Determine which subsystems to regenerate.
    if invalidated_modules is not None:
        # Find which subsystems contain invalidated modules.
        affected_subsystems: set[str] = set()
        for mod_name in invalidated_modules:
            mod_info = modules_def.get(mod_name)
            if mod_info:
                affected_subsystems.add(mod_info["subsystem"])
        regen_subsystems = affected_subsystems
        skipped_subsystems = set(subsystems_def.keys()) - regen_subsystems
    else:
        regen_subsystems = set(subsystems_def.keys())
        skipped_subsystems = set()

    # Create output directory.
    os.makedirs(output_dir, exist_ok=True)

    # Generate subsystem DOT files.
    subsystem_outputs: dict[str, str] = {}
    for ss_name, ss_info in subsystems_def.items():
        if ss_name not in regen_subsystems:
            continue

        ss_modules = ss_info.get("modules", [])
        ss_dot = _build_subsystem_dot(ss_name, ss_modules, parsed_modules)
        ss_path = os.path.join(output_dir, f"{ss_name}.dot")

        with open(ss_path, "w") as f:
            f.write(ss_dot)

        subsystem_outputs[ss_name] = ss_path

    # Generate overview DOT.
    overview_dot = _build_overview_dot(subsystems_def, parsed_modules)
    overview_path = os.path.join(output_dir, "overview.dot")

    with open(overview_path, "w") as f:
        f.write(overview_dot)

    return {
        "success": True,
        "outputs": {
            "overview": overview_path,
            "subsystems": subsystem_outputs,
        },
        "stats": {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "subsystems": len(subsystems_def),
            "modules": modules_processed,
        },
        "warnings": warnings,
        "regenerated": sorted(regen_subsystems),
        "skipped": sorted(skipped_subsystems),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_dot_file(dot_path: str) -> pydot.Dot | None:
    """Parse a DOT file into a pydot graph. Returns None on failure."""
    try:
        with open(dot_path) as f:
            content = f.read()
    except OSError:
        return None

    if not content.strip():
        return None

    captured = io.StringIO()
    graphs: list[pydot.Dot] | None = None
    with contextlib.redirect_stdout(captured):
        try:
            graphs = pydot.graph_from_dot_data(content)
        except Exception:  # noqa: BLE001
            return None

    if not graphs:
        return None

    return graphs[0]


def _count_graph_elements(graph: pydot.Dot) -> tuple[int, int]:
    """Count nodes and edges in a pydot graph (including subgraphs)."""
    pseudo = frozenset({"node", "edge", "graph"})
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []

    def _collect(g: pydot.Dot | pydot.Subgraph) -> None:
        for node in g.get_node_list():
            name = str(node.get_name()).strip('"')
            if name and name not in pseudo:
                nodes.add(name)
        for edge in g.get_edge_list():
            src = str(edge.get_source()).strip('"')
            dst = str(edge.get_destination()).strip('"')
            edges.append((src, dst))
            nodes.add(src)
            nodes.add(dst)
        for sg in g.get_subgraph_list():
            _collect(sg)

    _collect(graph)
    nodes -= pseudo
    return len(nodes), len(edges)


def _build_subsystem_dot(
    subsystem_name: str,
    module_names: list[str],
    parsed_modules: dict[str, pydot.Dot],
) -> str:
    """Build a subsystem DOT string with module subgraph clusters.

    Each module becomes a `subgraph cluster_<module>` containing
    that module's nodes and edges.
    """
    graph = pydot.Dot(graph_type="digraph", graph_name=subsystem_name)
    graph.set_label(f'"{subsystem_name}"')
    graph.set_compound("true")

    for mod_name in module_names:
        mod_graph = parsed_modules.get(mod_name)
        if mod_graph is None:
            continue

        cluster = pydot.Cluster(mod_name, label=f'"{mod_name}"', style="dashed")

        # Copy nodes into the cluster.
        for node in mod_graph.get_node_list():
            name = str(node.get_name()).strip('"')
            if name and name not in {"node", "edge", "graph"}:
                new_node = pydot.Node(name)
                # Copy attributes.
                for attr_key, attr_val in node.get_attributes().items():
                    new_node.set(attr_key, attr_val)
                cluster.add_node(new_node)

        # Copy edges into the cluster.
        for edge in mod_graph.get_edge_list():
            new_edge = pydot.Edge(edge.get_source(), edge.get_destination())
            for attr_key, attr_val in edge.get_attributes().items():
                new_edge.set(attr_key, attr_val)
            cluster.add_edge(new_edge)

        graph.add_subgraph(cluster)

    # Add legend.
    _add_legend(graph, f"Subsystem: {subsystem_name}")

    return graph.to_string()


def _build_overview_dot(
    subsystems_def: dict,
    parsed_modules: dict[str, pydot.Dot],
) -> str:
    """Build overview DOT with subsystem subgraph clusters.

    Each subsystem becomes a `subgraph cluster_<subsystem>` containing
    representative nodes for each module in that subsystem.

    If the overview exceeds bounds (250 lines / 80 nodes), module nodes
    are collapsed into single representative nodes.
    """
    graph = pydot.Dot(graph_type="digraph", graph_name="overview")
    graph.set_label('"Architecture Overview"')
    graph.set_compound("true")
    graph.set_rankdir("TB")

    total_nodes = 0

    for ss_name, ss_info in subsystems_def.items():
        cluster = pydot.Cluster(ss_name, label=f'"{ss_name}"', style="rounded")

        module_names = ss_info.get("modules", [])
        for mod_name in module_names:
            mod_graph = parsed_modules.get(mod_name)
            if mod_graph is None:
                # Still add a placeholder node.
                placeholder = pydot.Node(
                    mod_name,
                    label=f'"{mod_name}"',
                    shape="box",
                    style="filled",
                    fillcolor="lightyellow",
                )
                cluster.add_node(placeholder)
                total_nodes += 1
                continue

            # Count module nodes to decide on collapse.
            node_count, _ = _count_graph_elements(mod_graph)
            total_nodes += node_count

            if total_nodes > _MAX_OVERVIEW_NODES:
                # Collapse: single representative node per module.
                rep_node = pydot.Node(
                    mod_name,
                    label=f'"{mod_name} ({node_count} nodes)"',
                    shape="box",
                    style="filled",
                    fillcolor="lightblue",
                )
                cluster.add_node(rep_node)
            else:
                # Include actual module nodes.
                for node in mod_graph.get_node_list():
                    name = str(node.get_name()).strip('"')
                    if name and name not in {"node", "edge", "graph"}:
                        new_node = pydot.Node(name)
                        for attr_key, attr_val in node.get_attributes().items():
                            new_node.set(attr_key, attr_val)
                        cluster.add_node(new_node)

                for edge in mod_graph.get_edge_list():
                    new_edge = pydot.Edge(edge.get_source(), edge.get_destination())
                    for attr_key, attr_val in edge.get_attributes().items():
                        new_edge.set(attr_key, attr_val)
                    cluster.add_edge(new_edge)

        graph.add_subgraph(cluster)

    # Add legend.
    _add_legend(graph, "Architecture Overview")

    # Check line count — if over limit, rebuild in collapsed mode.
    overview_str = graph.to_string()
    line_count = len(overview_str.splitlines())

    if line_count > _MAX_OVERVIEW_LINES:
        return _build_collapsed_overview(subsystems_def, parsed_modules)

    return overview_str


def _build_collapsed_overview(
    subsystems_def: dict,
    parsed_modules: dict[str, pydot.Dot],
) -> str:
    """Build a collapsed overview where each module is a single node."""
    graph = pydot.Dot(graph_type="digraph", graph_name="overview")
    graph.set_label('"Architecture Overview (collapsed)"')
    graph.set_compound("true")
    graph.set_rankdir("TB")

    for ss_name, ss_info in subsystems_def.items():
        cluster = pydot.Cluster(ss_name, label=f'"{ss_name}"', style="rounded")

        for mod_name in ss_info.get("modules", []):
            mod_graph = parsed_modules.get(mod_name)
            node_count = 0
            if mod_graph:
                node_count, _ = _count_graph_elements(mod_graph)

            rep_node = pydot.Node(
                mod_name,
                label=f'"{mod_name} ({node_count} nodes)"',
                shape="box",
                style="filled",
                fillcolor="lightblue",
            )
            cluster.add_node(rep_node)

        graph.add_subgraph(cluster)

    _add_legend(graph, "Architecture Overview (collapsed)")
    return graph.to_string()


def _add_legend(graph: pydot.Dot, title: str) -> None:
    """Add a legend subgraph cluster to the graph."""
    legend = pydot.Cluster(
        "legend",
        label='"Legend"',
        style="solid",
        color="gray",
        fontcolor="gray",
    )

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    legend.add_node(
        pydot.Node(
            "legend_info",
            label=f'"Generated: {timestamp}\\n{title}"',
            shape="note",
            style="filled",
            fillcolor="lightyellow",
            fontsize="10",
        )
    )

    graph.add_subgraph(legend)
```

### Step 4: Run tests to verify they pass

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_assemble.py -v --tb=short
```
Expected: All tests PASS.

### Step 5: Run the full test suite to verify no regressions

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ tests/ -v --tb=short 2>&1 | tail -20
```
Expected: All existing tests still pass.

### Step 6: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py modules/tool-dot-graph/tests/test_assemble.py && git commit -m "feat: add assemble operation — hierarchical DOT assembly"
```

---

## Task 3: Wire `prescan` and `assemble` into `__init__.py`

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`
- Modify: `modules/tool-dot-graph/tests/test_tool_integration.py` (add new routing tests)

### Step 1: Write the failing tests

Add the following tests to `modules/tool-dot-graph/tests/test_tool_integration.py`. Append them after the existing `test_mounted_tool_can_validate` test at the bottom of the file.

```python
# ---------------------------------------------------------------------------
# Phase B: prescan and assemble operation tests (6 tests)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prescan_operation_routes_correctly(tmp_path):
    """prescan operation calls prescan.prescan_repo and returns structured inventory."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    # Create a minimal fake repo.
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("pass")

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "prescan", "options": {"repo_path": str(tmp_path)}}
    )

    assert result.success is True, f"prescan must return success=True, got: {result.output!r}"
    data = _parse_output(result)
    assert data["success"] is True, f"prescan result must have success=True, got: {data}"
    assert "languages" in data, "prescan must return 'languages'"
    assert "total_files" in data, "prescan must return 'total_files'"
    assert data["total_files"] == 2, f"Must find 2 files, got: {data['total_files']}"


@pytest.mark.asyncio
async def test_prescan_missing_repo_path_returns_error():
    """prescan without repo_path in options returns success=False."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "prescan", "options": {}})

    assert result.success is False, "prescan without repo_path must return success=False"
    data = _parse_output(result)
    assert "error" in data, "Missing repo_path must return 'error' in response"


@pytest.mark.asyncio
async def test_assemble_operation_routes_correctly(tmp_path):
    """assemble operation calls assemble.assemble_hierarchy and returns outputs."""
    import os

    from amplifier_module_tool_dot_graph import DotGraphTool

    # Create a minimal module DOT file.
    mod_dir = tmp_path / "modules" / "auth"
    mod_dir.mkdir(parents=True)
    (mod_dir / "diagram.dot").write_text("digraph auth { login -> logout }")

    manifest = {
        "modules": {
            "auth": {
                "dot_path": str(mod_dir / "diagram.dot"),
                "subsystem": "identity",
            },
        },
        "subsystems": {
            "identity": {"modules": ["auth"]},
        },
    }

    output_dir = str(tmp_path / "output")

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "assemble",
            "options": {"manifest": manifest, "output_dir": output_dir},
        }
    )

    assert result.success is True, f"assemble must return success=True, got: {result.output!r}"
    data = _parse_output(result)
    assert data["success"] is True, f"assemble result must have success=True, got: {data}"
    assert "outputs" in data, "assemble must return 'outputs'"
    assert os.path.exists(data["outputs"]["overview"]), "overview.dot must exist"


@pytest.mark.asyncio
async def test_assemble_missing_manifest_returns_error(tmp_path):
    """assemble without manifest in options returns success=False."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "assemble", "options": {"output_dir": str(tmp_path)}}
    )

    assert result.success is False, "assemble without manifest must return success=False"
    data = _parse_output(result)
    assert "error" in data, "Missing manifest must return 'error' in response"


def test_input_schema_includes_prescan_and_assemble():
    """input_schema operation enum includes prescan and assemble."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    op_enum = schema["properties"]["operation"]["enum"]
    assert "prescan" in op_enum, f"Schema enum must include 'prescan', got: {op_enum}"
    assert "assemble" in op_enum, f"Schema enum must include 'assemble', got: {op_enum}"


@pytest.mark.asyncio
async def test_mount_returns_version_040_phase_b():
    """mount() metadata version is 0.4.0 after Phase B."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    result = await mount(coordinator)

    assert result["version"] == "0.4.0", (
        f"Expected version 0.4.0 after Phase B, got: {result['version']!r}"
    )
```

### Step 2: Run the new tests to verify they fail

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_tool_integration.py::test_prescan_operation_routes_correctly modules/tool-dot-graph/tests/test_tool_integration.py::test_input_schema_includes_prescan_and_assemble modules/tool-dot-graph/tests/test_tool_integration.py::test_mount_returns_version_040_phase_b -v --tb=short 2>&1 | head -30
```
Expected: FAIL — `prescan` not in enum, version is 0.3.0.

### Step 3: Update `__init__.py`

Apply the following changes to `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`:

**Change 1:** Update the import line (line 16):

Replace:
```python
from amplifier_module_tool_dot_graph import analyze, render, setup_helper, validate
```
With:
```python
from amplifier_module_tool_dot_graph import analyze, assemble, prescan, render, setup_helper, validate
```

**Change 2:** Update class docstring (lines 22-31):

Replace:
```python
    """DOT graph tool routing validate, render, setup, and analyze operations.

    Provides:
    - Validation: three-layer syntax, structural, and render-quality checks via pydot
    - Rendering: graphviz CLI wrapper for SVG/PNG/PDF output
    - Setup: environment check for graphviz, pydot, and networkx availability
    - Analysis: reachability, cycle detection, critical path, and structural diff via networkx
      Operations: stats, reachability, unreachable, cycles, paths,
                  critical_path, subgraph_extract, diff
    """
```
With:
```python
    """DOT graph tool routing validate, render, setup, analyze, prescan, and assemble operations.

    Provides:
    - Validation: three-layer syntax, structural, and render-quality checks via pydot
    - Rendering: graphviz CLI wrapper for SVG/PNG/PDF output
    - Setup: environment check for graphviz, pydot, and networkx availability
    - Analysis: reachability, cycle detection, critical path, and structural diff via networkx
      Operations: stats, reachability, unreachable, cycles, paths,
                  critical_path, subgraph_extract, diff
    - Prescan: structural codebase scanner for discovery pipeline
    - Assemble: hierarchical DOT assembly (modules -> subsystems -> overview)
    """
```

**Change 3:** Update the `description` property (lines 39-53):

Replace:
```python
    @property
    def description(self) -> str:
        return """DOT graph tool — validate, render, and analyze DOT-format graphs.

Operations:
- validate: Parse and validate DOT content through up to three layers (syntax, structural, render)
- render: Render DOT content to SVG, PNG, PDF, or other formats via graphviz CLI
- setup: Check environment for graphviz, pydot, and networkx availability
- analyze: Structural graph analysis via networkx
  - stats: Node count, edge count, density, DAG detection, connected components
  - reachability: All nodes reachable from a source node
  - unreachable: Nodes with no incoming edges (excluding known entry points)
  - cycles: Detect all simple cycles in a directed graph
  - paths: All simple paths between two nodes (capped at 100)
  - critical_path: Longest path in a DAG
  - subgraph_extract: Extract a named cluster subgraph into standalone DOT
  - diff: Structural differences between two DOT graphs"""
```
With:
```python
    @property
    def description(self) -> str:
        return """DOT graph tool — validate, render, analyze, prescan, and assemble DOT-format graphs.

Operations:
- validate: Parse and validate DOT content through up to three layers (syntax, structural, render)
- render: Render DOT content to SVG, PNG, PDF, or other formats via graphviz CLI
- setup: Check environment for graphviz, pydot, and networkx availability
- analyze: Structural graph analysis via networkx
  - stats: Node count, edge count, density, DAG detection, connected components
  - reachability: All nodes reachable from a source node
  - unreachable: Nodes with no incoming edges (excluding known entry points)
  - cycles: Detect all simple cycles in a directed graph
  - paths: All simple paths between two nodes (capped at 100)
  - critical_path: Longest path in a DAG
  - subgraph_extract: Extract a named cluster subgraph into standalone DOT
  - diff: Structural differences between two DOT graphs
- prescan: Structural codebase scan — walk a repo and produce language/module/file inventory
- assemble: Hierarchical DOT assembly — merge per-module DOTs into subsystem + overview graphs"""
```

**Change 4:** Update the `input_schema` operation enum (lines 60-64):

Replace:
```python
                "operation": {
                    "type": "string",
                    "enum": ["validate", "render", "setup", "analyze"],
                    "description": "Operation to perform on the DOT graph",
                },
```
With:
```python
                "operation": {
                    "type": "string",
                    "enum": ["validate", "render", "setup", "analyze", "prescan", "assemble"],
                    "description": "Operation to perform on the DOT graph",
                },
```

**Change 5:** Add prescan and assemble options to `input_schema` `options.properties` (after the `dot_content_b` property, before the closing `},` of `properties` inside `options`):

Add these properties alongside the existing ones inside `options.properties`:
```python
                        "repo_path": {
                            "type": "string",
                            "description": (
                                "Repository path for prescan operation "
                                "(absolute or relative path to repo root)"
                            ),
                        },
                        "manifest": {
                            "type": "object",
                            "description": (
                                "Hierarchy manifest for assemble operation "
                                "(modules, subsystems, optional invalidated_modules)"
                            ),
                        },
                        "output_dir": {
                            "type": "string",
                            "description": (
                                "Output directory for assemble operation "
                                "(where subsystem and overview DOT files are written)"
                            ),
                        },
                        "invalidated_modules": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of module names that changed, for incremental "
                                "assembly (assemble operation, optional)"
                            ),
                        },
```

**Change 6:** Add routing for prescan and assemble in `execute()` (after the `analyze` block, before the `# Unknown operation` block):

Add this code after `return ToolResult(success=result["success"], output=json.dumps(result))` (the analyze return) and before `# Unknown operation`:
```python
        if operation == "prescan":
            repo_path = options.get("repo_path")
            if not repo_path:
                error_result = {
                    "success": False,
                    "error": "Missing required 'repo_path' in options for prescan operation",
                }
                return ToolResult(success=False, output=json.dumps(error_result))
            result = prescan.prescan_repo(repo_path)
            return ToolResult(success=result["success"], output=json.dumps(result))

        if operation == "assemble":
            manifest = options.get("manifest")
            output_dir = options.get("output_dir")
            if not manifest:
                error_result = {
                    "success": False,
                    "error": "Missing required 'manifest' in options for assemble operation",
                }
                return ToolResult(success=False, output=json.dumps(error_result))
            if not output_dir:
                error_result = {
                    "success": False,
                    "error": "Missing required 'output_dir' in options for assemble operation",
                }
                return ToolResult(success=False, output=json.dumps(error_result))
            # Merge invalidated_modules into manifest if provided separately.
            invalidated = options.get("invalidated_modules")
            if invalidated is not None:
                manifest["invalidated_modules"] = invalidated
            result = assemble.assemble_hierarchy(manifest, output_dir)
            return ToolResult(success=result["success"], output=json.dumps(result))

```

**Change 7:** Update the unknown operation fallback (the `supported` list):

Replace:
```python
        # Unknown operation
        result = {
            "error": f"Unknown operation '{operation}'",
            "supported": ["validate", "render", "setup", "analyze"],
        }
```
With:
```python
        # Unknown operation
        result = {
            "error": f"Unknown operation '{operation}'",
            "supported": ["validate", "render", "setup", "analyze", "prescan", "assemble"],
        }
```

**Change 8:** Update `mount()` version and log message (lines 209-218):

Replace:
```python
    logger.info(
        "tool-dot-graph mounted: registered 'dot_graph' tool "
        "with validate/render/setup/analyze routing (v0.3.0)"
    )

    return {
        "name": "tool-dot-graph",
        "version": "0.3.0",
        "provides": ["dot_graph"],
    }
```
With:
```python
    logger.info(
        "tool-dot-graph mounted: registered 'dot_graph' tool "
        "with validate/render/setup/analyze/prescan/assemble routing (v0.4.0)"
    )

    return {
        "name": "tool-dot-graph",
        "version": "0.4.0",
        "provides": ["dot_graph"],
    }
```

### Step 4: Update existing tests that check the old version or operation list

In `modules/tool-dot-graph/tests/test_tool_integration.py`, update these existing tests:

**Update `test_input_schema_includes_setup_operation`** — the assertion list must now include prescan and assemble. Add these two lines after the existing assertions:
```python
    assert "prescan" in op_enum, "Schema enum must include 'prescan'"
    assert "assemble" in op_enum, "Schema enum must include 'assemble'"
```

**Update `test_mount_registers_real_tool`** — change the version assertion:
```python
    assert result["version"] == "0.4.0", (
        f"Expected version 0.4.0 (prescan+assemble added), got: {result['version']!r}"
    )
```

**Update `test_mount_returns_version_030`** — change the version assertion (keep the function name or rename):
```python
    assert result["version"] == "0.4.0", (
        f"Expected version 0.4.0, got: {result['version']!r}"
    )
```

### Step 5: Run all tests to verify everything passes

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```
Expected: All tests PASS (existing + new).

### Step 6: Run the full test suite including bundle-level tests

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ tests/ -v --tb=short 2>&1 | tail -30
```
Expected: All tests PASS.

### Step 7: Run linting/type checks

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m ruff check modules/tool-dot-graph/ --fix && python -m ruff format modules/tool-dot-graph/
```
Expected: Clean (no errors).

### Step 8: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py modules/tool-dot-graph/tests/test_tool_integration.py && git commit -m "feat: wire prescan and assemble into tool-dot-graph (v0.4.0)"
```

---

## Summary

| Task | Files Created | Files Modified | Tests Added | Description |
|------|--------------|----------------|-------------|-------------|
| 1 | `prescan.py`, `test_prescan.py` | — | ~25 | Structural codebase scanner |
| 2 | `assemble.py`, `test_assemble.py` | — | ~16 | Hierarchical DOT assembly |
| 3 | — | `__init__.py`, `test_tool_integration.py` | ~6 | Wire routing, schema, version bump |

**Version:** 0.3.0 -> 0.4.0
**Operations:** 4 -> 6 (added `prescan` and `assemble`)
**Dependencies:** No new dependencies — `pydot` already in `pyproject.toml`

After Phase B, the tool module has all the deterministic building blocks needed by the discovery pipeline. Phase C adds the investigation agents, Phase D adds the recipes that orchestrate everything.

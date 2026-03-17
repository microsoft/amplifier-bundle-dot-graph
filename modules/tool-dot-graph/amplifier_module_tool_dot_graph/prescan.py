"""Structural codebase scanner for repository prescan.

Walks a repository directory tree and produces a structured JSON inventory
including languages, modules, build manifests, entry points, and directory tree.

Pure Python — uses os.walk and pathlib only. No LLM, no graphviz.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

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

# (indicator_filename, module_type) — order matters for priority
_MODULE_INDICATORS: list[tuple[str, str]] = [
    ("Cargo.toml", "rust_crate"),
    ("go.mod", "go_module"),
    ("package.json", "node_package"),
    ("__init__.py", "python_package"),
]

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

_MAX_TREE_DEPTH: int = 4


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def prescan_repo(repo_path: str) -> dict:
    """Scan a repository directory tree and produce a structured inventory.

    Args:
        repo_path: Absolute or relative path to the repository root directory.

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
    # Validate path
    repo = Path(repo_path)

    if not repo.exists():
        return {"success": False, "error": f"Path does not exist: {repo_path}"}

    if not repo.is_dir():
        return {"success": False, "error": f"Path is not a directory: {repo_path}"}

    # Collect all files (respecting skip dirs)
    all_files = _collect_all_files(repo)

    # Detect languages (extension → count)
    languages: dict[str, int] = {}
    for filepath in all_files:
        ext = _get_extension(filepath)
        if ext:
            languages[ext] = languages.get(ext, 0) + 1

    total_files = len(all_files)

    # Detect modules
    modules = _detect_modules(repo, all_files)

    # Detect build manifests (repo root only)
    build_manifests = _detect_build_manifests(repo)

    # Detect entry points (returns absolute Paths; convert to relative strings)
    entry_point_paths = _detect_entry_points(all_files)
    entry_points = sorted(str(p.relative_to(repo)) for p in entry_point_paths)

    # Build directory tree
    directory_tree = _build_directory_tree(repo, max_depth=_MAX_TREE_DEPTH)

    return {
        "success": True,
        "repo_path": str(repo_path),
        "languages": languages,
        "total_files": total_files,
        "modules": modules,
        "build_manifests": build_manifests,
        "entry_points": entry_points,
        "directory_tree": directory_tree,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_extension(filepath: Path) -> str:
    """Extract file extension without leading dot.

    Args:
        filepath: Path object for a file.

    Returns:
        Extension string without dot (e.g. "py"), or empty string if none.
    """
    suffix = filepath.suffix
    return suffix[1:] if suffix else ""


def _collect_all_files(repo: Path) -> list[Path]:
    """Walk the repo tree and collect all files, skipping _SKIP_DIRS.

    Args:
        repo: Repository root path.

    Returns:
        List of Path objects for all non-skipped files.
    """
    all_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(repo):
        # Prune skipped directories in-place so os.walk won't descend into them
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]

        for filename in filenames:
            all_files.append(Path(dirpath) / filename)

    return all_files


def _detect_modules(repo: Path, all_files: list[Path]) -> list[dict]:
    """Detect module boundaries by looking for indicator files.

    Skips the repo root itself — only subdirectories qualify as modules.
    For each indicator file found, the containing directory is treated as
    one module boundary. Higher-priority indicators (earlier in _MODULE_INDICATORS)
    win when multiple indicators exist in the same directory.

    Args:
        repo: Repository root path.
        all_files: List of all file paths (pre-filtered for _SKIP_DIRS).

    Returns:
        List of module dicts with keys: name, path, type, indicator,
        file_count, files_by_type.
    """
    # Build a map from directory → indicator info using first-match priority.
    # Priority is determined by _MODULE_INDICATORS order.
    dir_to_indicator: dict[Path, tuple[str, str]] = {}

    for indicator_name, module_type in _MODULE_INDICATORS:
        for filepath in all_files:
            if filepath.name == indicator_name:
                parent = filepath.parent
                # Skip repo root
                if parent == repo:
                    continue
                # Only record first match (by indicator priority)
                if parent not in dir_to_indicator:
                    dir_to_indicator[parent] = (indicator_name, module_type)

    # Build module dicts
    modules: list[dict] = []

    for module_dir, (indicator_name, module_type) in sorted(
        dir_to_indicator.items(), key=lambda x: str(x[0])
    ):
        # Collect files that belong to this module directory (recursively).
        # A file belongs to this module if its path starts with module_dir
        # and it's not in a nested module.
        module_files = [
            f for f in all_files if _is_file_in_module(f, module_dir, dir_to_indicator)
        ]

        # Count files by extension
        files_by_type: dict[str, int] = {}
        for f in module_files:
            ext = _get_extension(f)
            if ext:
                files_by_type[ext] = files_by_type.get(ext, 0) + 1

        # Use relative path from repo root
        rel_path = str(module_dir.relative_to(repo))

        modules.append(
            {
                "name": module_dir.name,
                "path": rel_path,
                "type": module_type,
                "indicator": indicator_name,
                "file_count": len(module_files),
                "files_by_type": files_by_type,
            }
        )

    return modules


def _is_file_in_module(
    filepath: Path,
    module_dir: Path,
    dir_to_indicator: dict[Path, tuple[str, str]],
) -> bool:
    """Check if a file belongs to a module (is under module_dir but not a nested module).

    A file belongs to module_dir if:
    1. It is a descendant of module_dir.
    2. No ancestor directory between module_dir (exclusive) and the file's parent
       (inclusive) is itself a module root.

    Args:
        filepath: The file path to check.
        module_dir: The candidate module directory.
        dir_to_indicator: Map of all known module directories.

    Returns:
        True if the file belongs to this module.
    """
    # Must be under module_dir
    try:
        relative = filepath.relative_to(module_dir)
    except ValueError:
        return False

    # Check if any intermediate directory is another module root
    current = module_dir
    for part in relative.parts[:-1]:  # exclude the filename itself
        current = current / part
        if current in dir_to_indicator and current != module_dir:
            return False

    return True


def _detect_build_manifests(repo: Path) -> list[str]:
    """Detect build manifest files at the repo root only.

    Args:
        repo: Repository root path.

    Returns:
        List of relative paths to found manifest files (relative to repo).
    """
    manifests: list[str] = []

    for item in repo.iterdir():
        if item.is_file() and item.name in _BUILD_MANIFESTS:
            manifests.append(item.name)

    return sorted(manifests)


def _detect_entry_points(all_files: list[Path]) -> list[Path]:
    """Detect entry point files by basename matching against _ENTRY_POINTS.

    Args:
        all_files: List of all file paths (pre-filtered for _SKIP_DIRS).

    Returns:
        List of absolute Path objects for matching entry point files.
        Callers are responsible for converting to relative paths if needed.
    """
    entry_points: list[Path] = []

    for filepath in all_files:
        if filepath.name in _ENTRY_POINTS:
            entry_points.append(filepath)

    return entry_points


def _build_directory_tree(repo: Path, max_depth: int = _MAX_TREE_DEPTH) -> dict:
    """Build a nested dict of directories, limited to max_depth levels.

    Only directories are represented in the tree (not files).
    Directories in _SKIP_DIRS are excluded.

    Args:
        repo: Repository root path.
        max_depth: Maximum depth of directory nesting to include.

    Returns:
        Nested dict where keys are directory names and values are dicts
        of subdirectories (or empty dicts at the depth limit).
    """
    return _build_tree_recursive(repo, current_depth=0, max_depth=max_depth)


def _build_tree_recursive(
    current_dir: Path, current_depth: int, max_depth: int
) -> dict:
    """Recursively build directory tree dict.

    Args:
        current_dir: Current directory to enumerate.
        current_depth: Current depth level (0 = repo root's children).
        max_depth: Maximum depth to recurse into.

    Returns:
        Dict of {dirname: subtree_dict} for subdirectories.
    """
    if current_depth >= max_depth:
        return {}

    tree: dict = {}

    try:
        entries = sorted(current_dir.iterdir())
    except PermissionError:
        return {}

    for entry in entries:
        if entry.is_dir() and entry.name not in _SKIP_DIRS:
            tree[entry.name] = _build_tree_recursive(
                entry, current_depth + 1, max_depth
            )

    return tree

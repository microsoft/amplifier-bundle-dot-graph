"""Tests for prescan.py — Structural codebase scanner.

~25 tests covering:
- Error handling: nonexistent path, file instead of directory, empty directory
- Result structure: all required fields present
- Language detection: Python files, mixed languages, total file counting
- Skip directories: .git, node_modules, __pycache__, .venv
- Module boundary detection: Python packages, Rust crates, Go modules, Node packages,
  file counts per module
- Monorepo detection: multiple packages at top level
- Build manifest detection: pyproject.toml, Cargo.toml
- Entry point detection: Python entry points, nested entry points
- Directory tree: structure correctness, excludes skipped dirs, depth limit of 4
"""

import os
import tempfile
from pathlib import Path

from amplifier_module_tool_dot_graph.prescan import prescan_repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_files(base: Path, file_map: dict[str, str]) -> None:
    """Create files in a temp directory from a {relative_path: content} dict."""
    for rel_path, content in file_map.items():
        full_path = base / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


def test_prescan_nonexistent_path_returns_error():
    """prescan_repo with a nonexistent path returns success=False with descriptive error."""
    result = prescan_repo("/this/path/definitely/does/not/exist/xyz123")

    assert result["success"] is False, "Nonexistent path must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"
    assert len(result["error"]) > 0, "'error' must be non-empty"


def test_prescan_file_path_returns_error():
    """prescan_repo with a file path (not directory) returns success=False."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        file_path = f.name

    try:
        result = prescan_repo(file_path)
        assert result["success"] is False, "File path must return success=False"
        assert "error" in result, "Error result must have 'error' key"
        assert isinstance(result["error"], str), "'error' must be a string"
    finally:
        os.unlink(file_path)


def test_prescan_empty_directory_returns_success():
    """prescan_repo on an empty directory returns success=True with zero counts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = prescan_repo(tmpdir)

    assert result["success"] is True, (
        f"Empty dir must return success=True, got: {result}"
    )
    assert result["total_files"] == 0, (
        f"Empty dir must have 0 files, got: {result['total_files']}"
    )
    assert result["languages"] == {}, (
        f"Empty dir must have empty languages, got: {result['languages']}"
    )
    assert result["modules"] == [], (
        f"Empty dir must have empty modules, got: {result['modules']}"
    )
    assert result["build_manifests"] == [], (
        f"Empty dir must have empty build_manifests, got: {result['build_manifests']}"
    )
    assert result["entry_points"] == [], (
        f"Empty dir must have empty entry_points, got: {result['entry_points']}"
    )


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------


def test_prescan_result_has_all_required_fields():
    """prescan_repo returns a dict with all required fields on success."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(Path(tmpdir), {"README.md": "# Hello"})
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"

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

    assert result["repo_path"] == tmpdir, (
        f"repo_path must match input, got: {result['repo_path']}"
    )
    assert isinstance(result["languages"], dict), "'languages' must be a dict"
    assert isinstance(result["total_files"], int), "'total_files' must be an int"
    assert isinstance(result["modules"], list), "'modules' must be a list"
    assert isinstance(result["build_manifests"], list), (
        "'build_manifests' must be a list"
    )
    assert isinstance(result["entry_points"], list), "'entry_points' must be a list"
    assert isinstance(result["directory_tree"], dict), "'directory_tree' must be a dict"


# ---------------------------------------------------------------------------
# Language detection tests
# ---------------------------------------------------------------------------


def test_prescan_detects_python_files():
    """prescan_repo counts Python files by 'py' extension."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "foo.py": "x = 1",
                "bar.py": "y = 2",
                "baz.py": "z = 3",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert result["languages"].get("py") == 3, (
        f"Must detect 3 Python files, got: {result['languages']}"
    )


def test_prescan_detects_mixed_languages():
    """prescan_repo counts files by extension across multiple language types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "main.py": "pass",
                "lib.rs": "fn main() {}",
                "go.mod": "module example",
                "index.ts": "export {}",
                "README.md": "# Docs",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    langs = result["languages"]
    assert langs.get("py") == 1, f"Must detect 1 .py file, got: {langs}"
    assert langs.get("rs") == 1, f"Must detect 1 .rs file, got: {langs}"
    assert langs.get("ts") == 1, f"Must detect 1 .ts file, got: {langs}"
    assert langs.get("md") == 1, f"Must detect 1 .md file, got: {langs}"


def test_prescan_counts_total_files():
    """prescan_repo total_files matches the actual number of files created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "a.py": "",
                "b.py": "",
                "c.rs": "",
                "README.md": "",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert result["total_files"] == 4, (
        f"Must count 4 total files, got: {result['total_files']}"
    )


# ---------------------------------------------------------------------------
# Skip directory tests
# ---------------------------------------------------------------------------


def test_prescan_skips_git_dir():
    """prescan_repo excludes .git directory from language counts and total files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "main.py": "pass",
                ".git/HEAD": "ref: refs/heads/main",
                ".git/config": "[core]",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert result["total_files"] == 1, (
        f"Only main.py should be counted, got total_files={result['total_files']}"
    )
    assert result["languages"].get("py") == 1, (
        f"Only 1 .py file should be counted, got: {result['languages']}"
    )


def test_prescan_skips_node_modules():
    """prescan_repo excludes node_modules from language counts and total files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "index.js": "console.log('hello')",
                "node_modules/lodash/index.js": "module.exports = {}",
                "node_modules/lodash/README.md": "# lodash",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert result["total_files"] == 1, (
        f"Only index.js should be counted, got total_files={result['total_files']}"
    )


def test_prescan_skips_pycache():
    """prescan_repo excludes __pycache__ from language counts and total files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "app.py": "pass",
                "__pycache__/app.cpython-311.pyc": "bytecode",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert result["total_files"] == 1, (
        f"Only app.py should be counted, got total_files={result['total_files']}"
    )


def test_prescan_skips_venv():
    """prescan_repo excludes .venv directory from language counts and total files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "app.py": "pass",
                ".venv/lib/python3.11/site-packages/requests/__init__.py": "pass",
                ".venv/bin/python": "#!/usr/bin/env python",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert result["total_files"] == 1, (
        f"Only app.py should be counted, got total_files={result['total_files']}"
    )


# ---------------------------------------------------------------------------
# Module boundary detection tests
# ---------------------------------------------------------------------------


def test_prescan_detects_python_package():
    """prescan_repo detects Python packages via __init__.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "mylib/__init__.py": "# mylib",
                "mylib/core.py": "pass",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    modules = result["modules"]
    assert len(modules) == 1, f"Must detect 1 module, got: {modules}"
    mod = modules[0]
    assert mod["type"] == "python_package", (
        f"Module type must be 'python_package', got: {mod['type']}"
    )
    assert mod["name"] == "mylib", f"Module name must be 'mylib', got: {mod['name']}"
    assert mod["indicator"] == "__init__.py", (
        f"Indicator must be '__init__.py', got: {mod['indicator']}"
    )


def test_prescan_detects_rust_crate():
    """prescan_repo detects Rust crates via Cargo.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "mycrate/Cargo.toml": "[package]\nname = 'mycrate'",
                "mycrate/src/main.rs": "fn main() {}",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    modules = result["modules"]
    assert len(modules) == 1, f"Must detect 1 module, got: {modules}"
    mod = modules[0]
    assert mod["type"] == "rust_crate", (
        f"Module type must be 'rust_crate', got: {mod['type']}"
    )
    assert mod["name"] == "mycrate", (
        f"Module name must be 'mycrate', got: {mod['name']}"
    )


def test_prescan_detects_go_module():
    """prescan_repo detects Go modules via go.mod."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "mygoapp/go.mod": "module mygoapp\ngo 1.21",
                "mygoapp/main.go": "package main",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    modules = result["modules"]
    assert len(modules) == 1, f"Must detect 1 module, got: {modules}"
    mod = modules[0]
    assert mod["type"] == "go_module", (
        f"Module type must be 'go_module', got: {mod['type']}"
    )


def test_prescan_detects_node_package():
    """prescan_repo detects Node packages via package.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "myapp/package.json": '{"name": "myapp"}',
                "myapp/index.js": "module.exports = {}",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    modules = result["modules"]
    assert len(modules) == 1, f"Must detect 1 module, got: {modules}"
    mod = modules[0]
    assert mod["type"] == "node_package", (
        f"Module type must be 'node_package', got: {mod['type']}"
    )


def test_prescan_module_file_counts():
    """prescan_repo reports file_count and files_by_type per detected module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "mypkg/__init__.py": "# pkg",
                "mypkg/core.py": "pass",
                "mypkg/utils.py": "pass",
                "mypkg/README.md": "# docs",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    modules = result["modules"]
    assert len(modules) == 1, f"Must detect 1 module, got: {modules}"
    mod = modules[0]

    assert mod["file_count"] == 4, f"Module must have 4 files, got: {mod['file_count']}"
    assert isinstance(mod["files_by_type"], dict), "'files_by_type' must be a dict"
    assert mod["files_by_type"].get("py") == 3, (
        f"Must have 3 .py files, got: {mod['files_by_type']}"
    )
    assert mod["files_by_type"].get("md") == 1, (
        f"Must have 1 .md file, got: {mod['files_by_type']}"
    )


def test_prescan_module_has_required_fields():
    """Each module dict contains name, path, type, indicator, file_count, files_by_type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "mypkg/__init__.py": "",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    assert len(result["modules"]) == 1, "Must detect 1 module"
    mod = result["modules"][0]

    required_module_fields = [
        "name",
        "path",
        "type",
        "indicator",
        "file_count",
        "files_by_type",
    ]
    for field in required_module_fields:
        assert field in mod, (
            f"Module must include '{field}', got keys: {list(mod.keys())}"
        )


# ---------------------------------------------------------------------------
# Monorepo detection tests
# ---------------------------------------------------------------------------


def test_prescan_detects_multiple_packages_monorepo():
    """prescan_repo detects multiple packages in a monorepo layout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "packages/alpha/__init__.py": "# alpha",
                "packages/beta/__init__.py": "# beta",
                "packages/gamma/Cargo.toml": "[package]\nname = 'gamma'",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    modules = result["modules"]
    assert len(modules) == 3, f"Must detect 3 modules, got: {modules}"

    types_found = {m["type"] for m in modules}
    assert "python_package" in types_found, (
        f"Must include python_package, got types: {types_found}"
    )
    assert "rust_crate" in types_found, (
        f"Must include rust_crate, got types: {types_found}"
    )


# ---------------------------------------------------------------------------
# Build manifest detection tests
# ---------------------------------------------------------------------------


def test_prescan_detects_pyproject_toml_at_root():
    """prescan_repo detects pyproject.toml at repo root as a build manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "pyproject.toml": "[project]\nname = 'mypkg'",
                "src/mypkg/__init__.py": "pass",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    manifests = result["build_manifests"]
    assert any("pyproject.toml" in m for m in manifests), (
        f"Must detect pyproject.toml, got: {manifests}"
    )


def test_prescan_detects_cargo_toml_at_root():
    """prescan_repo detects Cargo.toml at repo root as a build manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "Cargo.toml": "[package]\nname = 'mypkg'",
                "src/main.rs": "fn main() {}",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    manifests = result["build_manifests"]
    assert any("Cargo.toml" in m for m in manifests), (
        f"Must detect Cargo.toml, got: {manifests}"
    )


def test_prescan_build_manifests_not_in_subdirs():
    """prescan_repo only detects build manifests at repo root, not in subdirectories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "subdir/pyproject.toml": "[project]\nname = 'sub'",
                "README.md": "# root",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    manifests = result["build_manifests"]
    assert len(manifests) == 0, (
        f"Must NOT detect pyproject.toml in subdir, got: {manifests}"
    )


# ---------------------------------------------------------------------------
# Entry point detection tests
# ---------------------------------------------------------------------------


def test_prescan_detects_python_entry_points():
    """prescan_repo detects Python entry points: main.py, cli.py, __main__.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "main.py": "if __name__ == '__main__': pass",
                "cli.py": "import click",
                "__main__.py": "# main",
                "utils.py": "pass",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    entry_points = result["entry_points"]
    basenames = [os.path.basename(ep) for ep in entry_points]
    assert "main.py" in basenames, (
        f"main.py must be an entry point, got: {entry_points}"
    )
    assert "cli.py" in basenames, f"cli.py must be an entry point, got: {entry_points}"
    assert "__main__.py" in basenames, (
        f"__main__.py must be an entry point, got: {entry_points}"
    )
    assert "utils.py" not in basenames, (
        f"utils.py must NOT be an entry point, got: {entry_points}"
    )


def test_prescan_detects_nested_entry_points():
    """prescan_repo detects entry points in subdirectories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "src/main.py": "pass",
                "cmd/server.py": "pass",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    entry_points = result["entry_points"]
    basenames = [os.path.basename(ep) for ep in entry_points]
    assert "main.py" in basenames, (
        f"Nested main.py must be an entry point, got: {entry_points}"
    )
    assert "server.py" in basenames, (
        f"Nested server.py must be an entry point, got: {entry_points}"
    )


def test_prescan_entry_points_use_relative_paths():
    """prescan_repo entry_points list contains relative (not absolute) paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "main.py": "pass",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    entry_points = result["entry_points"]
    assert len(entry_points) > 0, "Must detect at least 1 entry point"
    for ep in entry_points:
        assert not os.path.isabs(ep), (
            f"Entry point must be relative path, got absolute: {ep}"
        )


# ---------------------------------------------------------------------------
# Directory tree tests
# ---------------------------------------------------------------------------


def test_prescan_directory_tree_structure():
    """prescan_repo builds a nested dict for the directory tree."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "src/lib/utils.py": "pass",
                "src/lib/core.py": "pass",
                "docs/guide.md": "# Guide",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    tree = result["directory_tree"]
    assert isinstance(tree, dict), "'directory_tree' must be a dict"
    assert "src" in tree, f"Tree must include 'src', got: {list(tree.keys())}"
    assert "docs" in tree, f"Tree must include 'docs', got: {list(tree.keys())}"
    assert isinstance(tree["src"], dict), "Nested dir must be a dict"
    assert "lib" in tree["src"], f"'src' must contain 'lib', got: {tree['src']}"


def test_prescan_directory_tree_excludes_skipped_dirs():
    """prescan_repo directory_tree does not include .git, node_modules, __pycache__, .venv."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_files(
            Path(tmpdir),
            {
                "src/app.py": "pass",
                ".git/HEAD": "ref: refs/heads/main",
                "node_modules/pkg/index.js": "module.exports = {}",
                "__pycache__/app.pyc": "bytecode",
                ".venv/pyvenv.cfg": "python=3.11",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    tree = result["directory_tree"]
    assert ".git" not in tree, (
        f".git must be excluded from tree, got: {list(tree.keys())}"
    )
    assert "node_modules" not in tree, (
        f"node_modules must be excluded from tree, got: {list(tree.keys())}"
    )
    assert "__pycache__" not in tree, (
        f"__pycache__ must be excluded from tree, got: {list(tree.keys())}"
    )
    assert ".venv" not in tree, (
        f".venv must be excluded from tree, got: {list(tree.keys())}"
    )
    assert "src" in tree, f"src must be in tree, got: {list(tree.keys())}"


def test_prescan_directory_tree_depth_limited_to_4():
    """prescan_repo directory_tree is limited to 4 levels of depth."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a 6-level deep directory structure
        _make_files(
            Path(tmpdir),
            {
                "a/b/c/d/e/f/deep.txt": "deep file",
            },
        )
        result = prescan_repo(tmpdir)

    assert result["success"] is True, f"Must succeed, got: {result}"
    tree = result["directory_tree"]

    # Navigate to depth 4
    level1 = tree.get("a", {})
    level2 = level1.get("b", {})
    level3 = level2.get("c", {})
    level4 = level3.get("d", {})

    # Level 4 should exist
    assert "a" in tree, "Level 1 'a' must exist"
    assert "b" in level1, "Level 2 'b' must exist"
    assert "c" in level2, "Level 3 'c' must exist"
    assert "d" in level3, "Level 4 'd' must exist"

    # Level 5 should NOT exist (depth limit = 4)
    assert "e" not in level4, (
        f"Level 5 'e' must NOT be in tree (depth limit=4), got level4={level4}"
    )

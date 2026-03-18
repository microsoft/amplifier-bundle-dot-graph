"""Tests for assemble.py — Filesystem plumbing (copy DOTs, write manifest).

16 tests covering:
- Error handling: empty/missing manifest, missing 'modules'/'subsystems' key, missing DOT (warn and skip)
- Directory creation: subsystems/ subdir, nested output_dir
- File copying: module DOT files copied to subsystems/
- Manifest I/O: manifest.json written with correct structure
- Result structure: success, outputs, stats, warnings; outputs has overview, subsystems
- Stats: module and subsystem counts (no pydot-era total_nodes/total_edges)
- Agent-produced DOT discovery: overview.dot discovered / None when absent
- render_png parameter: no PNG files when render_png=False
"""

import json
import tempfile
from pathlib import Path

import pytest

from amplifier_module_tool_dot_graph.assemble import assemble_hierarchy


# ---------------------------------------------------------------------------
# DOT fixtures (module-level constants)
# ---------------------------------------------------------------------------

# Simple 3-node, 2-edge module graph: a->b->c
MOD_ALPHA_DOT = "digraph alpha { a -> b; b -> c; }"

# Simple 2-node, 1-edge module graph: x->y
MOD_BETA_DOT = "digraph beta { x -> y; }"

# 3-node module: p->q->r
MOD_GAMMA_DOT = "digraph gamma { p -> q; q -> r; }"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def dot_dir(tmp_path: Path) -> str:
    """Temp directory pre-populated with alpha.dot, beta.dot, and gamma.dot.

    Uses pytest's tmp_path to guarantee cleanup after each test.
    """
    (tmp_path / "alpha.dot").write_text(MOD_ALPHA_DOT)
    (tmp_path / "beta.dot").write_text(MOD_BETA_DOT)
    (tmp_path / "gamma.dot").write_text(MOD_GAMMA_DOT)
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_minimal_manifest(dot_dir: str) -> dict:
    """Build a minimal 2-module, 2-subsystem manifest.

    Args:
        dot_dir: Directory containing alpha.dot and beta.dot.

    Returns:
        manifest dict.
    """
    return {
        "modules": {
            "alpha": {"dot_path": str(Path(dot_dir) / "alpha.dot"), "subsystem": "ss1"},
            "beta": {"dot_path": str(Path(dot_dir) / "beta.dot"), "subsystem": "ss2"},
        },
        "subsystems": {
            "ss1": {"modules": ["alpha"]},
            "ss2": {"modules": ["beta"]},
        },
    }


# ---------------------------------------------------------------------------
# Error handling tests (5)
# ---------------------------------------------------------------------------


def test_assemble_empty_manifest_returns_error():
    """Empty dict manifest returns success=False with descriptive error."""
    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy({}, out)

    assert result["success"] is False, "Empty manifest must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"
    assert len(result["error"]) > 0, "'error' must be non-empty"


def test_assemble_none_manifest_returns_error():
    """None manifest returns success=False with descriptive error."""
    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(None, out)  # type: ignore[arg-type]

    assert result["success"] is False, "None manifest must return success=False"
    assert "error" in result, "Error result must have 'error' key"


def test_assemble_missing_modules_key_returns_error():
    """Manifest without 'modules' key returns success=False."""
    manifest = {"subsystems": {"ss1": {"modules": ["alpha"]}}}
    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is False, "Missing 'modules' key must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert "modules" in result["error"].lower(), (
        f"Error must mention 'modules', got: {result['error']}"
    )


def test_assemble_missing_subsystems_key_returns_error():
    """Manifest without 'subsystems' key returns success=False."""
    manifest = {"modules": {"alpha": {"dot_path": "/tmp/a.dot", "subsystem": "ss1"}}}
    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is False, (
        "Missing 'subsystems' key must return success=False"
    )
    assert "error" in result, "Error result must have 'error' key"
    assert "subsystems" in result["error"].lower(), (
        f"Error must mention 'subsystems', got: {result['error']}"
    )


def test_assemble_missing_dot_file_warns_and_skips():
    """Missing DOT file emits a warning (not failure); module is skipped."""
    manifest = {
        "modules": {
            "alpha": {"dot_path": "/nonexistent/alpha.dot", "subsystem": "ss1"},
        },
        "subsystems": {
            "ss1": {"modules": ["alpha"]},
        },
    }
    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, "Missing DOT file must not cause failure"
    assert "warnings" in result, "Result must have 'warnings' key"
    assert isinstance(result["warnings"], list), "'warnings' must be a list"
    assert len(result["warnings"]) > 0, (
        "Missing DOT file must produce at least one warning"
    )


# ---------------------------------------------------------------------------
# Directory creation tests (2)
# ---------------------------------------------------------------------------


def test_subsystems_subdir_created(dot_dir: str):
    """assemble_hierarchy must create the subsystems/ subdirectory."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        subsystems_dir = Path(out) / "subsystems"
        exists = subsystems_dir.exists()

    assert exists, "subsystems/ subdir must be created"


def test_output_dir_created_when_missing(dot_dir: str):
    """output_dir is created automatically when it doesn't exist (nested path OK)."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as base:
        nested_out = str(Path(base) / "deep" / "nested" / "output")
        result = assemble_hierarchy(manifest, nested_out)

    assert result["success"] is True, (
        f"assemble_hierarchy must succeed with missing nested output_dir, got: {result}"
    )
    assert result["outputs"]["subsystems"], "subsystems must not be empty"


# ---------------------------------------------------------------------------
# File copying tests (2)
# ---------------------------------------------------------------------------


def test_module_dot_copied_to_output(dot_dir: str):
    """alpha.dot and beta.dot are copied to subsystems/ directory."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        alpha_exists = (Path(out) / "subsystems" / "alpha.dot").exists()
        beta_exists = (Path(out) / "subsystems" / "beta.dot").exists()

    assert alpha_exists, "alpha.dot must be copied to subsystems/"
    assert beta_exists, "beta.dot must be copied to subsystems/"


def test_copied_dot_has_correct_content(dot_dir: str):
    """Copied DOT file content matches the source module DOT."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        alpha_content = (Path(out) / "subsystems" / "alpha.dot").read_text()

    assert alpha_content == MOD_ALPHA_DOT, (
        f"Copied alpha.dot must have original content.\n"
        f"Expected: {MOD_ALPHA_DOT!r}\nGot: {alpha_content!r}"
    )


# ---------------------------------------------------------------------------
# Manifest I/O tests (2)
# ---------------------------------------------------------------------------


def test_manifest_json_written(dot_dir: str):
    """manifest.json is written to the output directory."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        manifest_exists = (Path(out) / "manifest.json").exists()

    assert manifest_exists, "manifest.json must exist in output_dir"


def test_manifest_json_has_modules_and_subsystems(dot_dir: str):
    """manifest.json contains 'modules' and 'subsystems' top-level keys."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        data = json.loads((Path(out) / "manifest.json").read_text())

    assert "modules" in data, (
        f"manifest.json must have 'modules' key, got: {list(data)}"
    )
    assert "subsystems" in data, (
        f"manifest.json must have 'subsystems' key, got: {list(data)}"
    )


# ---------------------------------------------------------------------------
# Result structure tests (2)
# ---------------------------------------------------------------------------


def test_result_structure_has_required_fields(dot_dir: str):
    """Success result has success, outputs, stats, warnings; outputs has overview, subsystems."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"

    required_fields = ["success", "outputs", "stats", "warnings"]
    for field in required_fields:
        assert field in result, (
            f"Result must include '{field}', got keys: {list(result.keys())}"
        )

    assert "overview" in result["outputs"], "outputs must contain 'overview' key"
    assert "subsystems" in result["outputs"], "outputs must contain 'subsystems' key"
    assert isinstance(result["outputs"]["subsystems"], dict), (
        "'subsystems' must be a dict"
    )


def test_stats_has_module_and_subsystem_counts(dot_dir: str):
    """Stats reports 'modules' and 'subsystems' counts (no pydot-era total_nodes/total_edges)."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"

    stats = result["stats"]
    assert stats["modules"] == 2, f"modules count must be 2, got: {stats['modules']}"
    assert stats["subsystems"] == 2, (
        f"subsystems count must be 2, got: {stats['subsystems']}"
    )
    assert "total_nodes" not in stats, (
        "stats must NOT have 'total_nodes' (pydot era removed)"
    )
    assert "total_edges" not in stats, (
        "stats must NOT have 'total_edges' (pydot era removed)"
    )


# ---------------------------------------------------------------------------
# Agent-produced DOT discovery tests (2)
# ---------------------------------------------------------------------------


def test_discovers_existing_overview_dot(dot_dir: str):
    """Pre-created overview.dot in output_dir is reported in outputs['overview']."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        overview_path = Path(out) / "overview.dot"
        overview_path.write_text("digraph overview { ss1 -> ss2; }")

        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        overview_out = result["outputs"]["overview"]

    assert overview_out is not None, (
        "outputs['overview'] must not be None when overview.dot exists"
    )
    assert "overview.dot" in overview_out, (
        f"outputs['overview'] must point to overview.dot, got: {overview_out}"
    )


def test_overview_is_none_when_absent(dot_dir: str):
    """outputs['overview'] is None when no overview.dot is present."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"
    assert result["outputs"]["overview"] is None, (
        f"outputs['overview'] must be None when no overview.dot, "
        f"got: {result['outputs']['overview']}"
    )


# ---------------------------------------------------------------------------
# render_png parameter tests (2)
# ---------------------------------------------------------------------------


def test_render_png_false_does_not_call_renderer(dot_dir: str):
    """render_png=False (default) completes without raising and no PNG is produced."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out, render_png=False)
        assert result["success"] is True, (
            f"assemble_hierarchy with render_png=False must succeed, got: {result}"
        )
        # No .png files should exist in the output directory
        png_files = list(Path(out).rglob("*.png"))

    assert png_files == [], (
        f"render_png=False must produce no PNG files, found: {png_files}"
    )


def test_render_png_default_is_false(dot_dir: str):
    """Default render_png=False — calling without the parameter must not produce PNGs."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        png_files = list(Path(out).rglob("*.png"))

    assert png_files == [], (
        f"Default render_png=False must produce no PNG files, found: {png_files}"
    )

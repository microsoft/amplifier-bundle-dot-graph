"""Tests for assemble.py — Hierarchical DOT Assembly.

~16 tests covering:
- Error handling: empty/missing manifest, missing 'modules' key, missing DOT files (warn and skip)
- Subsystem assembly: module clusters present, valid DOT output, nodes preserved
- Overview assembly: overview.dot produced, contains subsystem clusters, valid DOT
- Result structure: success, outputs, stats fields present
- Stats accuracy: correct total_nodes, total_edges, subsystems, modules counts
- Ancestor invalidation: only affected subsystems regenerated, unaffected skipped
- Full regeneration: without invalidation, all subsystems generated, nothing skipped
"""

import tempfile
from pathlib import Path

import pydot
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
# Error handling tests
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
# Subsystem assembly tests
# ---------------------------------------------------------------------------


def test_subsystem_dot_contains_module_clusters(dot_dir: str):
    """Subsystem DOT file must contain subgraph cluster_<module> for each module."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        ss1_path = result["outputs"]["subsystems"]["ss1"]
        content = Path(ss1_path).read_text()

    assert "cluster_alpha" in content, (
        f"Subsystem ss1 DOT must contain 'cluster_alpha', got:\n{content}"
    )


def test_subsystem_dot_is_valid(dot_dir: str):
    """Subsystem DOT file is parseable by pydot."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        ss1_path = result["outputs"]["subsystems"]["ss1"]
        content = Path(ss1_path).read_text()

    graphs = pydot.graph_from_dot_data(content)
    assert graphs is not None and len(graphs) > 0, (
        f"Subsystem ss1 DOT must be parseable, got:\n{content}"
    )


def test_subsystem_dot_preserves_nodes(dot_dir: str):
    """Subsystem DOT contains the nodes from its modules."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        ss1_path = result["outputs"]["subsystems"]["ss1"]
        content = Path(ss1_path).read_text()

    # alpha module has nodes a, b, c
    assert "a" in content, f"ss1 DOT must contain node 'a' from alpha, got:\n{content}"
    assert "b" in content, f"ss1 DOT must contain node 'b' from alpha, got:\n{content}"


# ---------------------------------------------------------------------------
# Overview assembly tests
# ---------------------------------------------------------------------------


def test_overview_dot_is_produced(dot_dir: str):
    """overview.dot is produced in the output directory."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        assert "overview" in result["outputs"], (
            "Result must contain outputs['overview']"
        )
        overview_path = result["outputs"]["overview"]
        exists = Path(overview_path).exists()

    assert exists, f"overview.dot must exist at {overview_path}"


def test_overview_dot_contains_subsystem_clusters(dot_dir: str):
    """overview.dot contains subgraph cluster_<subsystem> for each subsystem."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        overview_path = result["outputs"]["overview"]
        content = Path(overview_path).read_text()

    assert "cluster_ss1" in content, (
        f"overview.dot must contain 'cluster_ss1', got:\n{content}"
    )
    assert "cluster_ss2" in content, (
        f"overview.dot must contain 'cluster_ss2', got:\n{content}"
    )


def test_overview_dot_is_valid(dot_dir: str):
    """overview.dot is parseable by pydot."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        overview_path = result["outputs"]["overview"]
        content = Path(overview_path).read_text()

    graphs = pydot.graph_from_dot_data(content)
    assert graphs is not None and len(graphs) > 0, (
        f"overview.dot must be parseable, got:\n{content}"
    )


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------


def test_result_structure_has_required_fields(dot_dir: str):
    """Success result has all required top-level fields."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"

    required_fields = [
        "success",
        "outputs",
        "stats",
        "warnings",
        "regenerated",
        "skipped",
    ]
    for field in required_fields:
        assert field in result, (
            f"Result must include '{field}', got keys: {list(result.keys())}"
        )

    assert "overview" in result["outputs"], "outputs must contain 'overview' key"
    assert "subsystems" in result["outputs"], "outputs must contain 'subsystems' key"
    assert isinstance(result["outputs"]["subsystems"], dict), (
        "'subsystems' must be a dict"
    )


def test_stats_accuracy(dot_dir: str):
    """Stats report accurate total_nodes, total_edges, subsystems, modules counts."""
    manifest = {
        "modules": {
            "alpha": {
                "dot_path": str(Path(dot_dir) / "alpha.dot"),
                "subsystem": "ss1",
            },  # 3 nodes, 2 edges
            "beta": {
                "dot_path": str(Path(dot_dir) / "beta.dot"),
                "subsystem": "ss1",
            },  # 2 nodes, 1 edge
            "gamma": {
                "dot_path": str(Path(dot_dir) / "gamma.dot"),
                "subsystem": "ss2",
            },  # 3 nodes, 2 edges
        },
        "subsystems": {
            "ss1": {"modules": ["alpha", "beta"]},
            "ss2": {"modules": ["gamma"]},
        },
    }

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"
    stats = result["stats"]

    assert stats["total_nodes"] == 8, (
        f"total_nodes must be 8 (3+2+3), got: {stats['total_nodes']}"
    )
    assert stats["total_edges"] == 5, (
        f"total_edges must be 5 (2+1+2), got: {stats['total_edges']}"
    )
    assert stats["subsystems"] == 2, (
        f"subsystems count must be 2, got: {stats['subsystems']}"
    )
    assert stats["modules"] == 3, f"modules count must be 3, got: {stats['modules']}"


# ---------------------------------------------------------------------------
# Invalidation / incremental regeneration tests
# ---------------------------------------------------------------------------


def test_full_regeneration_without_invalidation(dot_dir: str):
    """Without invalidated_modules, all subsystems are regenerated, nothing skipped."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"
    assert "ss1" in result["regenerated"], (
        f"ss1 must be in regenerated, got: {result['regenerated']}"
    )
    assert "ss2" in result["regenerated"], (
        f"ss2 must be in regenerated, got: {result['regenerated']}"
    )
    assert result["skipped"] == [], (
        f"Without invalidation, skipped must be [], got: {result['skipped']}"
    )


def test_incremental_regeneration_with_invalidated_modules(dot_dir: str):
    """With invalidated_modules=[alpha], only ss1 is regenerated; ss2 is skipped."""
    manifest = {
        "modules": {
            "alpha": {"dot_path": str(Path(dot_dir) / "alpha.dot"), "subsystem": "ss1"},
            "beta": {"dot_path": str(Path(dot_dir) / "beta.dot"), "subsystem": "ss2"},
        },
        "subsystems": {
            "ss1": {"modules": ["alpha"]},
            "ss2": {"modules": ["beta"]},
        },
        "invalidated_modules": ["alpha"],
    }

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"assemble_hierarchy must succeed, got: {result}"
    assert "ss1" in result["regenerated"], (
        f"ss1 must be regenerated (alpha is invalidated), got: {result['regenerated']}"
    )
    assert "ss2" in result["skipped"], (
        f"ss2 must be skipped (beta not invalidated), got: {result['skipped']}"
    )


# ---------------------------------------------------------------------------
# Legend tests
# ---------------------------------------------------------------------------


def test_legend_present_in_subsystem_output(dot_dir: str):
    """Every subsystem DOT output must contain a cluster_legend subgraph."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        ss1_path = result["outputs"]["subsystems"]["ss1"]
        content = Path(ss1_path).read_text()

    assert "cluster_legend" in content, (
        f"Subsystem ss1 DOT must contain 'cluster_legend', got:\n{content}"
    )


def test_legend_present_in_overview_output(dot_dir: str):
    """overview.dot must contain a cluster_legend subgraph."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        overview_path = result["outputs"]["overview"]
        content = Path(overview_path).read_text()

    assert "cluster_legend" in content, (
        f"overview.dot must contain 'cluster_legend', got:\n{content}"
    )


# ---------------------------------------------------------------------------
# Subsystems subdir layout tests (Improvement 1)
# ---------------------------------------------------------------------------


def test_subsystem_dot_written_in_subsystems_subdir(dot_dir: str):
    """Subsystem DOT files must be written to output_dir/subsystems/ not output_dir/."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        ss1_path = result["outputs"]["subsystems"]["ss1"]
        # Path must be inside subsystems/ subdirectory
        assert "subsystems" in ss1_path, (
            f"Subsystem path must be inside 'subsystems/' subdir, got: {ss1_path}"
        )
        # File must exist at the declared path
        assert Path(ss1_path).exists(), f"Subsystem ss1.dot must exist at {ss1_path}"


def test_subsystems_subdir_created(dot_dir: str):
    """assemble_hierarchy must create the subsystems/ subdirectory."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        subsystems_dir = Path(out) / "subsystems"
        assert subsystems_dir.exists(), (
            f"subsystems/ subdir must be created at {subsystems_dir}"
        )


# ---------------------------------------------------------------------------
# render_png parameter tests (Improvement 3)
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

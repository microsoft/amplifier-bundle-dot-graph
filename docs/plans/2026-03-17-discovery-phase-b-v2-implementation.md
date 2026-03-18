# Discovery Pipeline v2 — Phase B Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Strip `assemble.py` down to pure filesystem plumbing and create 3 building-block sub-recipes that delegate graph synthesis to agents.

**Architecture:** `assemble.py` loses all pydot graph manipulation (parsing, cluster wrapping, merging, legend generation) and keeps only directory creation, manifest I/O, file copying, and render triggering. Three new recipe YAML files (`synthesize-level.yaml`, `synthesize-subsystem.yaml`, `synthesize-overview.yaml`) each invoke one of the Phase A synthesizer agents. Each recipe follows the same quality-gate pattern established by `discovery-synthesize-module.yaml`.

**Tech Stack:** Python 3.11+, pydot (removed from assemble.py), PyYAML (tests), pytest, Amplifier recipe YAML format.

**Design doc:** `docs/plans/2026-03-17-discovery-pipeline-v2-design.md`

---

## Task 1: Strip assemble.py to plumbing-only

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py`

### Step 1: Write the new assemble.py

Replace the entire contents of `modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py` with:

```python
"""Hierarchical DOT Assembly — filesystem plumbing.

Creates the output directory structure, copies existing per-module DOT files
into it, writes manifest.json tracking what was produced, and optionally
triggers PNG rendering.

Semantic graph content (cluster wrapping, graph merging, overview generation)
is now the responsibility of synthesizer agents invoked via sub-recipes.

Public API: assemble_hierarchy(manifest, output_dir, render_png=False) -> dict
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path

from amplifier_module_tool_dot_graph import render as _render

logger = logging.getLogger(__name__)


def assemble_hierarchy(
    manifest: dict,
    output_dir: str,
    render_png: bool = False,
) -> dict:
    """Set up output directory structure and copy existing DOT files.

    Pure filesystem plumbing — no graph parsing or semantic manipulation.
    Agents produce subsystem and overview DOTs via synthesizer sub-recipes;
    this function handles the filesystem bookkeeping around those artifacts.

    Args:
        manifest: Dict with 'modules' and 'subsystems' keys.
            modules: {mod_name: {dot_path: str, subsystem: str}}
            subsystems: {ss_name: {modules: [mod_name]}}
        output_dir: Directory to write output files.
        render_png: If True, render each output DOT to PNG. Default: False.

    Returns:
        On success:
            {
                success: True,
                outputs: {overview: str | None, subsystems: {name: path}},
                stats: {subsystems: int, modules: int},
                warnings: [str],
            }
        On failure:
            {success: False, error: str}
    """
    # --- Validate manifest ---
    if not manifest or not isinstance(manifest, dict):
        return _error("Manifest must be a non-empty dict")

    if "modules" not in manifest:
        return _error("Manifest is missing required 'modules' key")

    if "subsystems" not in manifest:
        return _error("Manifest is missing required 'subsystems' key")

    modules_def: dict = manifest["modules"]
    subsystems_def: dict = manifest["subsystems"]
    warnings: list[str] = []

    # --- Create output directories ---
    os.makedirs(output_dir, exist_ok=True)
    subsystems_dir = str(Path(output_dir) / "subsystems")
    os.makedirs(subsystems_dir, exist_ok=True)

    # --- Copy per-module DOT files to output ---
    for mod_name, mod_info in modules_def.items():
        dot_path = mod_info.get("dot_path", "")
        if not dot_path or not Path(dot_path).is_file():
            if dot_path:
                warnings.append(
                    f"Module '{mod_name}': DOT file '{dot_path}' not found — skipped"
                )
            continue
        dest = str(Path(subsystems_dir) / f"{mod_name}.dot")
        shutil.copy2(dot_path, dest)

    # --- Discover agent-produced subsystem DOTs ---
    subsystem_paths: dict[str, str] = {}
    for ss_name in subsystems_def:
        ss_dot = Path(subsystems_dir) / f"{ss_name}.dot"
        if ss_dot.is_file():
            subsystem_paths[ss_name] = str(ss_dot)

    # --- Discover agent-produced overview DOT ---
    overview_path: str | None = None
    overview_dot = Path(output_dir) / "overview.dot"
    if overview_dot.is_file():
        overview_path = str(overview_dot)

    # --- Write manifest.json ---
    manifest_out = {
        "modules": {
            name: {
                "dot_path": info.get("dot_path", ""),
                "subsystem": info.get("subsystem", ""),
            }
            for name, info in modules_def.items()
        },
        "subsystems": {
            name: {
                "modules": info.get("modules", []),
                "dot_path": subsystem_paths.get(name, ""),
            }
            for name, info in subsystems_def.items()
        },
        "overview_path": overview_path or "",
    }
    Path(output_dir, "manifest.json").write_text(json.dumps(manifest_out, indent=2))

    # --- Optionally render DOT files to PNG ---
    if render_png:
        for dot_file in Path(output_dir).rglob("*.dot"):
            png_path = str(dot_file).replace(".dot", ".png")
            try:
                content = dot_file.read_text()
                result = _render.render_dot(content, "png", "dot", png_path)
                if not result.get("success"):
                    warnings.append(
                        f"PNG render failed for '{dot_file}': "
                        f"{result.get('error', 'unknown error')}"
                    )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"PNG render error for '{dot_file}': {exc}")
                logger.debug("PNG render exception for %s", dot_file, exc_info=True)

    return {
        "success": True,
        "outputs": {
            "overview": overview_path,
            "subsystems": subsystem_paths,
        },
        "stats": {
            "subsystems": len(subsystems_def),
            "modules": len(modules_def),
        },
        "warnings": warnings,
    }


def _error(message: str) -> dict:
    """Build a standardized error response dict."""
    return {"success": False, "error": message}
```

**What was removed** (all of these were pydot graph manipulation):
- `import pydot`, `import contextlib`, `import io`, `from datetime import datetime, timezone`
- Constants: `_MAX_OVERVIEW_LINES`, `_MAX_OVERVIEW_NODES`, `_PSEUDO_NODES`
- Functions: `_parse_dot_file`, `_count_graph_elements`, `_copy_module_elements_to_cluster`, `_build_subsystem_dot`, `_build_overview_dot`, `_build_full_overview`, `_build_collapsed_overview`, `_add_legend`
- All pydot graph parsing, cluster subgraph creation, graph merging, node/edge manipulation, cross-cluster edge routing, legend generation
- Return fields: `regenerated`, `skipped`
- Stats fields: `total_nodes`, `total_edges`
- Invalidation logic: `invalidated_modules` handling

**What was added:**
- `import json`, `import shutil`
- File copying via `shutil.copy2` for per-module DOTs
- Discovery of agent-produced subsystem and overview DOTs
- `manifest.json` writing

### Step 2: Run existing tests to confirm they fail (expected)

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_assemble.py -v --tb=short 2>&1 | tail -30
```

Expected: Many tests FAIL — the tests that tested pydot graph content (cluster subgraphs, node preservation, overview generation, legends, stats accuracy, invalidation) will fail because those behaviors no longer exist.

The following tests should still PASS (they test manifest validation, directory creation, render flag):
- `test_assemble_empty_manifest_returns_error`
- `test_assemble_none_manifest_returns_error`
- `test_assemble_missing_modules_key_returns_error`
- `test_assemble_missing_subsystems_key_returns_error`
- `test_assemble_missing_dot_file_warns_and_skips`
- `test_subsystems_subdir_created`
- `test_render_png_false_does_not_call_renderer`
- `test_render_png_default_is_false`

### Step 3: Do NOT commit yet — proceed to Task 2 to update the tests first

---

## Task 2: Update test_assemble.py for reduced assemble

**Files:**
- Modify: `modules/tool-dot-graph/tests/test_assemble.py`

### Step 1: Write the new test_assemble.py

Replace the entire contents of `modules/tool-dot-graph/tests/test_assemble.py` with:

```python
"""Tests for assemble.py — Hierarchical DOT Assembly (filesystem plumbing).

~16 tests covering:
- Error handling: empty/missing manifest, missing 'modules' key, missing DOT files (warn and skip)
- Directory creation: output dir, subsystems/ subdir
- File copying: per-module DOT files copied to output
- Manifest I/O: manifest.json written with correct structure
- Result structure: success, outputs, stats, warnings fields present
- Stats accuracy: correct subsystems and modules counts
- Render flag: render_png=False produces no PNGs
- Agent-produced DOT discovery: subsystem and overview DOTs found when present
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
    """Temp directory pre-populated with alpha.dot, beta.dot, and gamma.dot."""
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
# Directory creation tests
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
        assert subsystems_dir.exists(), (
            f"subsystems/ subdir must be created at {subsystems_dir}"
        )


def test_output_dir_created_when_missing():
    """assemble_hierarchy creates output_dir if it does not exist."""
    manifest = {
        "modules": {},
        "subsystems": {},
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "nested" / "output")
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True, f"Must succeed, got: {result}"


# ---------------------------------------------------------------------------
# File copying tests
# ---------------------------------------------------------------------------


def test_module_dot_copied_to_output(dot_dir: str):
    """Per-module DOT files are copied into subsystems/ output directory."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True, (
            f"assemble_hierarchy must succeed, got: {result}"
        )
        alpha_dest = Path(out) / "subsystems" / "alpha.dot"
        beta_dest = Path(out) / "subsystems" / "beta.dot"
        alpha_exists = alpha_dest.exists()
        beta_exists = beta_dest.exists()

    assert alpha_exists, "alpha.dot must be copied to subsystems/"
    assert beta_exists, "beta.dot must be copied to subsystems/"


def test_copied_dot_has_correct_content(dot_dir: str):
    """Copied DOT file content matches the source."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True
        content = (Path(out) / "subsystems" / "alpha.dot").read_text()

    assert content == MOD_ALPHA_DOT, (
        f"Copied alpha.dot content must match source, got:\n{content}"
    )


# ---------------------------------------------------------------------------
# Manifest I/O tests
# ---------------------------------------------------------------------------


def test_manifest_json_written(dot_dir: str):
    """manifest.json is written to output_dir."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True
        manifest_path = Path(out) / "manifest.json"
        exists = manifest_path.exists()

    assert exists, "manifest.json must be written to output_dir"


def test_manifest_json_has_modules_and_subsystems(dot_dir: str):
    """manifest.json contains modules and subsystems keys with correct structure."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)
        assert result["success"] is True
        manifest_data = json.loads((Path(out) / "manifest.json").read_text())

    assert "modules" in manifest_data, "manifest.json must have 'modules' key"
    assert "subsystems" in manifest_data, "manifest.json must have 'subsystems' key"
    assert "alpha" in manifest_data["modules"], "manifest.json must list alpha module"
    assert "ss1" in manifest_data["subsystems"], "manifest.json must list ss1 subsystem"


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


def test_stats_has_module_and_subsystem_counts(dot_dir: str):
    """Stats report correct subsystems and modules counts (no node/edge counts)."""
    manifest = {
        "modules": {
            "alpha": {
                "dot_path": str(Path(dot_dir) / "alpha.dot"),
                "subsystem": "ss1",
            },
            "beta": {
                "dot_path": str(Path(dot_dir) / "beta.dot"),
                "subsystem": "ss1",
            },
            "gamma": {
                "dot_path": str(Path(dot_dir) / "gamma.dot"),
                "subsystem": "ss2",
            },
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

    assert stats["subsystems"] == 2, (
        f"subsystems count must be 2, got: {stats['subsystems']}"
    )
    assert stats["modules"] == 3, f"modules count must be 3, got: {stats['modules']}"
    # Verify no pydot-era stats remain
    assert "total_nodes" not in stats, "total_nodes must not appear in reduced stats"
    assert "total_edges" not in stats, "total_edges must not appear in reduced stats"


# ---------------------------------------------------------------------------
# Agent-produced DOT discovery tests
# ---------------------------------------------------------------------------


def test_discovers_existing_overview_dot(dot_dir: str):
    """If overview.dot already exists in output_dir, it is reported in outputs."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        # Pre-create an agent-produced overview.dot
        (Path(out) / "overview.dot").write_text("digraph overview { a -> b; }")
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True
    assert result["outputs"]["overview"] is not None, (
        "overview must be reported when overview.dot exists"
    )
    assert "overview.dot" in result["outputs"]["overview"]


def test_overview_is_none_when_absent(dot_dir: str):
    """When no overview.dot exists, outputs['overview'] is None."""
    manifest = _build_minimal_manifest(dot_dir)

    with tempfile.TemporaryDirectory() as out:
        result = assemble_hierarchy(manifest, out)

    assert result["success"] is True
    assert result["outputs"]["overview"] is None, (
        "overview must be None when overview.dot does not exist"
    )


# ---------------------------------------------------------------------------
# render_png parameter tests
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
```

**Tests removed** (tested pydot graph manipulation that no longer exists):
- `test_subsystem_dot_contains_module_clusters` — tested cluster subgraph creation
- `test_subsystem_dot_is_valid` — tested pydot parsing of generated graph
- `test_subsystem_dot_preserves_nodes` — tested node preservation in clusters
- `test_overview_dot_is_produced` — tested generated overview
- `test_overview_dot_contains_subsystem_clusters` — tested cluster subgraphs
- `test_overview_dot_is_valid` — tested pydot parsing of generated overview
- `test_stats_accuracy` — tested `total_nodes`/`total_edges` (pydot element counting)
- `test_incremental_regeneration_with_invalidated_modules` — tested invalidation logic
- `test_full_regeneration_without_invalidation` — tested `regenerated`/`skipped` fields
- `test_legend_present_in_subsystem_output` — tested legend generation
- `test_legend_present_in_overview_output` — tested legend generation
- `test_subsystem_dot_written_in_subsystems_subdir` — tested graph-generated subsystem path

**Tests added** (test new plumbing behavior):
- `test_output_dir_created_when_missing` — nested output dir creation
- `test_module_dot_copied_to_output` — file copying to subsystems/
- `test_copied_dot_has_correct_content` — content fidelity of copy
- `test_manifest_json_written` — manifest.json existence
- `test_manifest_json_has_modules_and_subsystems` — manifest.json structure
- `test_stats_has_module_and_subsystem_counts` — simplified stats, no pydot-era fields
- `test_discovers_existing_overview_dot` — agent-produced overview discovery
- `test_overview_is_none_when_absent` — None when no overview exists

### Step 2: Run tests to verify all pass

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_assemble.py -v --tb=short
```

Expected: ALL 16 tests PASS.

### Step 3: Run the full module test suite to check for regressions

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short 2>&1 | tail -30
```

Expected: All tests pass. The integration test `test_assemble_routes_correctly` mocks `assemble_hierarchy` and is unaffected by internal changes.

### Step 4: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py modules/tool-dot-graph/tests/test_assemble.py && git commit -m "refactor: strip assemble.py to filesystem plumbing, remove all pydot graph manipulation

Remove all semantic graph content from assemble.py:
- pydot parsing, cluster subgraph creation, graph merging
- overview/subsystem graph generation, legend creation
- node/edge counting, invalidation logic

Keep only filesystem plumbing:
- directory creation, manifest.json I/O
- per-module DOT file copying, render triggering
- discovery of agent-produced subsystem/overview DOTs

Update test_assemble.py to match reduced scope (16 tests)."
```

---

## Task 3: Create synthesize-level.yaml + tests

**Files:**
- Create: `recipes/synthesize-level.yaml`
- Create: `tests/test_synthesize_level_recipe.py`

### Step 1: Write the failing test

Create `tests/test_synthesize_level_recipe.py`:

```python
"""Tests for recipes/synthesize-level.yaml existence and structure.

Validates:
- File existence and valid YAML parse
- Top-level metadata (name, description, version, author, tags)
- Context variables (level_path, child_dot_files, output_dir, level_slug, fidelity)
- Flat (non-staged) steps structure with 3 steps
- read-level step (bash, produces JSON inventory)
- synthesize step (agent: discovery-level-synthesizer)
- validate step (bash, runs dot_graph validate)
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-level.yaml"


# ---------------------------------------------------------------------------
# File existence and parse
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/synthesize-level.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/synthesize-level.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# Top-level metadata
# ---------------------------------------------------------------------------


def test_recipe_name():
    """Recipe must have name='synthesize-level'."""
    data = _load_recipe()
    assert data.get("name") == "synthesize-level", (
        f"Expected name='synthesize-level', got: {data.get('name')!r}"
    )


def test_recipe_description_non_empty():
    """Recipe must have a non-empty description."""
    data = _load_recipe()
    desc = data.get("description", "")
    assert isinstance(desc, str) and desc.strip(), (
        "Recipe must have a non-empty string description"
    )


def test_recipe_version():
    """Recipe must have version='1.0.0'."""
    data = _load_recipe()
    assert data.get("version") == "1.0.0"


def test_recipe_author():
    """Recipe must have author='DOT Graph Bundle'."""
    data = _load_recipe()
    assert data.get("author") == "DOT Graph Bundle"


def test_recipe_tags():
    """Recipe tags must include discovery, synthesis, sub-recipe, dot-graph, bottom-up."""
    data = _load_recipe()
    tags = data.get("tags", [])
    for expected_tag in ["discovery", "synthesis", "sub-recipe", "dot-graph", "bottom-up"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------


def test_context_has_level_path():
    """Context must declare 'level_path' variable."""
    ctx = _load_recipe().get("context", {})
    assert "level_path" in ctx


def test_context_has_child_dot_files():
    """Context must declare 'child_dot_files' variable."""
    ctx = _load_recipe().get("context", {})
    assert "child_dot_files" in ctx


def test_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    ctx = _load_recipe().get("context", {})
    assert "output_dir" in ctx


def test_context_has_level_slug():
    """Context must declare 'level_slug' variable."""
    ctx = _load_recipe().get("context", {})
    assert "level_slug" in ctx


def test_context_has_fidelity_default_standard():
    """Context must declare 'fidelity' with default 'standard'."""
    ctx = _load_recipe().get("context", {})
    assert "fidelity" in ctx
    assert ctx["fidelity"] == "standard"


# ---------------------------------------------------------------------------
# Steps structure
# ---------------------------------------------------------------------------


def test_recipe_has_flat_steps():
    """Recipe must use flat steps list, not staged."""
    data = _load_recipe()
    assert "steps" in data
    assert "stages" not in data
    assert isinstance(data["steps"], list)


def test_recipe_has_3_steps():
    """Recipe must have exactly 3 top-level steps: read-level, synthesize, validate."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 3, (
        f"Expected 3 steps, got {len(steps)}: {[s.get('id') for s in steps]}"
    )


def test_step_order():
    """Steps must be in order: read-level, synthesize, validate."""
    data = _load_recipe()
    ids = [s.get("id") for s in _get_steps(data)]
    assert ids == ["read-level", "synthesize", "validate"], (
        f"Step order must be [read-level, synthesize, validate], got: {ids}"
    )


# ---------------------------------------------------------------------------
# read-level step
# ---------------------------------------------------------------------------


def test_read_level_is_bash():
    """read-level step must have type='bash'."""
    step = _get_step_by_id(_load_recipe(), "read-level")
    assert step is not None
    assert step.get("type") == "bash"


def test_read_level_has_parse_json():
    """read-level step must have parse_json=true."""
    step = _get_step_by_id(_load_recipe(), "read-level")
    assert step is not None
    assert step.get("parse_json") is True


def test_read_level_references_level_path():
    """read-level command must reference level_path."""
    step = _get_step_by_id(_load_recipe(), "read-level")
    assert step is not None
    assert "level_path" in step.get("command", "")


# ---------------------------------------------------------------------------
# synthesize step
# ---------------------------------------------------------------------------


def test_synthesize_agent():
    """synthesize step must reference agent 'dot-graph:discovery-level-synthesizer'."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-level-synthesizer"


def test_synthesize_has_timeout():
    """synthesize step must have timeout >= 600."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    assert step.get("timeout", 0) >= 600


def test_synthesize_prompt_references_context():
    """synthesize prompt must reference level_path, child_dot_files, output_dir, level_slug."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    for var in ["level_path", "child_dot_files", "output_dir", "level_slug"]:
        assert var in prompt, f"synthesize prompt must reference {var}"


# ---------------------------------------------------------------------------
# validate step
# ---------------------------------------------------------------------------


def test_validate_is_bash():
    """validate step must have type='bash'."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert step.get("type") == "bash"


def test_validate_references_diagram_dot():
    """validate step command must reference diagram.dot."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "diagram.dot" in step.get("command", "")


def test_validate_uses_pydot():
    """validate step must invoke pydot for DOT validation."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "pydot" in step.get("command", "")
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_synthesize_level_recipe.py -v --tb=short 2>&1 | head -20
```

Expected: `test_recipe_file_exists` FAILS with "not found". All subsequent tests FAIL or ERROR.

### Step 3: Create the recipe

Create `recipes/synthesize-level.yaml`:

```yaml
name: "synthesize-level"
description: >
  Per-directory-level synthesis sub-recipe for the bottom-up discovery strategy.
  Invoked once per directory level during post-order traversal. Lists files at
  the level, delegates synthesis to the discovery-level-synthesizer agent, and
  validates the produced DOT diagram via pydot.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "synthesis", "sub-recipe", "dot-graph", "bottom-up"]

context:
  level_path: ""          # Required: absolute path to the directory being synthesized
  child_dot_files: "[]"   # Required: JSON list of absolute paths to child synthesis DOTs
  output_dir: ""          # Required: base output directory (.discovery/investigation/bottomup/)
  level_slug: ""          # Required: slug name for this level (from directory name)
  fidelity: "standard"    # Fidelity tier (quick | standard | deep)

steps:
  # -------------------------------------------------------------------------
  # Step 1: Read level — list files at this directory (one level deep)
  # Produces a JSON inventory of file names and types.
  # -------------------------------------------------------------------------
  - id: "read-level"
    type: "bash"
    output: "level_inventory"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      import os
      from pathlib import Path

      level_path = "{{level_path}}"
      entries = []

      if os.path.isdir(level_path):
          for entry in sorted(os.listdir(level_path)):
              full = os.path.join(level_path, entry)
              entries.append({
                  "name": entry,
                  "type": "dir" if os.path.isdir(full) else "file",
                  "extension": Path(entry).suffix if os.path.isfile(full) else "",
                  "size_bytes": os.path.getsize(full) if os.path.isfile(full) else 0,
              })

      result = {
          "level_path": level_path,
          "entry_count": len(entries),
          "entries": entries,
      }
      print(json.dumps(result))
      EOF

  # -------------------------------------------------------------------------
  # Step 2: Synthesize — agent produces diagram.dot and findings.md
  # Reads file inventory + child DOTs, writes to output_dir/level_slug/
  # -------------------------------------------------------------------------
  - id: "synthesize"
    agent: "dot-graph:discovery-level-synthesizer"
    output: "synthesis_result"
    timeout: 1200
    prompt: |
      You are the level synthesizer for directory: {{level_path}}
      Level slug: {{level_slug}}

      Your task: read the files at this directory level and the synthesis DOTs
      from child directories, then produce a DOT diagram representing this level.

      **File inventory** (from read-level step):
        {{level_inventory}}

      **Child synthesis DOT files** (from previously-synthesized child directories):
        {{child_dot_files}}

      Read each child DOT file listed above. These represent what the children
      already synthesized. Your job is to show what lives at THIS level directly,
      how it connects to what children found, and what only becomes visible at
      this boundary (cross-child connections, interfaces that span children).

      **Output directory:** {{output_dir}}/{{level_slug}}/
      Write the following files:
        - diagram.dot — DOT graph for this level
        - findings.md — what you found, connections, boundary observations

      Fidelity tier: {{fidelity}}

  # -------------------------------------------------------------------------
  # Step 3: Validate — check diagram.dot via pydot
  # -------------------------------------------------------------------------
  - id: "validate"
    type: "bash"
    output: "validation_result"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      import sys
      from pathlib import Path

      output_dir = "{{output_dir}}"
      level_slug = "{{level_slug}}"
      diagram_path = Path(output_dir) / level_slug / "diagram.dot"

      result = {
          "valid": False,
          "errors": [],
          "diagram_path": str(diagram_path),
      }

      if not diagram_path.exists():
          result["errors"].append(f"diagram.dot not found at {diagram_path}")
          print(json.dumps(result))
          sys.exit(0)

      try:
          import pydot

          graphs = pydot.graph_from_dot_file(str(diagram_path))
          if not graphs:
              result["errors"].append("pydot could not parse diagram.dot — empty result")
              print(json.dumps(result))
              sys.exit(0)

          graph = graphs[0]
          result["valid"] = True
          result["node_count"] = len(graph.get_nodes())
          result["edge_count"] = len(graph.get_edges())

      except Exception as e:
          result["errors"].append(f"pydot validation error: {e}")

      print(json.dumps(result))
      EOF
```

### Step 4: Run tests to verify they pass

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_synthesize_level_recipe.py -v --tb=short
```

Expected: ALL tests PASS.

### Step 5: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add recipes/synthesize-level.yaml tests/test_synthesize_level_recipe.py && git commit -m "feat: add synthesize-level.yaml sub-recipe for bottom-up directory synthesis

Building block recipe invoked once per directory level during post-order
traversal. Three steps: read-level (bash, JSON inventory), synthesize
(discovery-level-synthesizer agent), validate (pydot check)."
```

---

## Task 4: Create synthesize-subsystem.yaml + tests

**Files:**
- Create: `recipes/synthesize-subsystem.yaml`
- Create: `tests/test_synthesize_subsystem_recipe.py`

### Step 1: Write the failing test

Create `tests/test_synthesize_subsystem_recipe.py`:

```python
"""Tests for recipes/synthesize-subsystem.yaml existence and structure.

Validates:
- File existence and valid YAML parse
- Top-level metadata (name, description, version, author, tags)
- Context variables (subsystem_name, module_dot_files, source_dirs, output_dir)
- Flat (non-staged) steps structure with 2 steps
- synthesize step (agent: discovery-subsystem-synthesizer)
- validate step (bash, runs pydot validation)
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-subsystem.yaml"


# ---------------------------------------------------------------------------
# File existence and parse
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/synthesize-subsystem.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/synthesize-subsystem.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# Top-level metadata
# ---------------------------------------------------------------------------


def test_recipe_name():
    """Recipe must have name='synthesize-subsystem'."""
    data = _load_recipe()
    assert data.get("name") == "synthesize-subsystem"


def test_recipe_description_non_empty():
    """Recipe must have a non-empty description."""
    data = _load_recipe()
    desc = data.get("description", "")
    assert isinstance(desc, str) and desc.strip()


def test_recipe_version():
    """Recipe must have version='1.0.0'."""
    data = _load_recipe()
    assert data.get("version") == "1.0.0"


def test_recipe_author():
    """Recipe must have author='DOT Graph Bundle'."""
    data = _load_recipe()
    assert data.get("author") == "DOT Graph Bundle"


def test_recipe_tags():
    """Recipe tags must include discovery, synthesis, sub-recipe, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    for expected_tag in ["discovery", "synthesis", "sub-recipe", "dot-graph"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------


def test_context_has_subsystem_name():
    """Context must declare 'subsystem_name' variable."""
    ctx = _load_recipe().get("context", {})
    assert "subsystem_name" in ctx


def test_context_has_module_dot_files():
    """Context must declare 'module_dot_files' variable."""
    ctx = _load_recipe().get("context", {})
    assert "module_dot_files" in ctx


def test_context_has_source_dirs():
    """Context must declare 'source_dirs' variable."""
    ctx = _load_recipe().get("context", {})
    assert "source_dirs" in ctx


def test_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    ctx = _load_recipe().get("context", {})
    assert "output_dir" in ctx


# ---------------------------------------------------------------------------
# Steps structure
# ---------------------------------------------------------------------------


def test_recipe_has_flat_steps():
    """Recipe must use flat steps list, not staged."""
    data = _load_recipe()
    assert "steps" in data
    assert "stages" not in data


def test_recipe_has_2_steps():
    """Recipe must have exactly 2 top-level steps: synthesize, validate."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 2, (
        f"Expected 2 steps, got {len(steps)}: {[s.get('id') for s in steps]}"
    )


def test_step_order():
    """Steps must be in order: synthesize, validate."""
    data = _load_recipe()
    ids = [s.get("id") for s in _get_steps(data)]
    assert ids == ["synthesize", "validate"], (
        f"Step order must be [synthesize, validate], got: {ids}"
    )


# ---------------------------------------------------------------------------
# synthesize step
# ---------------------------------------------------------------------------


def test_synthesize_agent():
    """synthesize step must reference agent 'dot-graph:discovery-subsystem-synthesizer'."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-subsystem-synthesizer"


def test_synthesize_has_timeout():
    """synthesize step must have timeout >= 600."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    assert step.get("timeout", 0) >= 600


def test_synthesize_prompt_references_context():
    """synthesize prompt must reference subsystem_name, module_dot_files, source_dirs, output_dir."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    for var in ["subsystem_name", "module_dot_files", "source_dirs", "output_dir"]:
        assert var in prompt, f"synthesize prompt must reference {var}"


# ---------------------------------------------------------------------------
# validate step
# ---------------------------------------------------------------------------


def test_validate_is_bash():
    """validate step must have type='bash'."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert step.get("type") == "bash"


def test_validate_uses_pydot():
    """validate step must invoke pydot for DOT validation."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "pydot" in step.get("command", "")


def test_validate_references_subsystem_name():
    """validate step must reference subsystem_name for the output DOT path."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "subsystem_name" in step.get("command", "")
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_synthesize_subsystem_recipe.py -v --tb=short 2>&1 | head -20
```

Expected: `test_recipe_file_exists` FAILS. All others FAIL or ERROR.

### Step 3: Create the recipe

Create `recipes/synthesize-subsystem.yaml`:

```yaml
name: "synthesize-subsystem"
description: >
  Subsystem-level synthesis sub-recipe for the discovery pipeline.
  Invoked once per subsystem during the top-down strategy's assembly phase.
  Reads per-module consensus DOT files and source directories, delegates
  synthesis to the discovery-subsystem-synthesizer agent, and validates
  the produced DOT diagram via pydot.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "synthesis", "sub-recipe", "dot-graph"]

context:
  subsystem_name: ""       # Required: name of the subsystem
  module_dot_files: "[]"   # Required: JSON list of paths to per-module consensus DOT files
  source_dirs: "[]"        # Required: JSON list of source directories in this subsystem
  output_dir: ""           # Required: where to write (.discovery/output/subsystems/)

steps:
  # -------------------------------------------------------------------------
  # Step 1: Synthesize — agent reads module DOTs + source dirs, produces subsystem DOT
  # -------------------------------------------------------------------------
  - id: "synthesize"
    agent: "dot-graph:discovery-subsystem-synthesizer"
    output: "synthesis_result"
    timeout: 1200
    prompt: |
      You are the subsystem synthesizer for: {{subsystem_name}}

      Your task: read all per-module consensus DOT files and the source
      directories belonging to this subsystem, then produce a subsystem-level
      DOT diagram showing how modules interoperate.

      **Per-module consensus DOT files:**
        {{module_dot_files}}

      Read each DOT file listed above. These are the consensus diagrams from
      per-module synthesis — they represent each module's internal structure.

      **Source directories in this subsystem:**
        {{source_dirs}}

      Investigate the boundaries between modules. Look for:
      - Cross-module data flows and function calls
      - Shared interfaces and abstract types
      - Emergent subsystem-level patterns not visible in individual modules

      **Output:** Write {{subsystem_name}}.dot to {{output_dir}}/

      The diagram should show how modules within this subsystem relate to each
      other — not the internals of each module (those are in the per-module DOTs).
      Focus on the seams between modules.

  # -------------------------------------------------------------------------
  # Step 2: Validate — check the produced DOT via pydot
  # -------------------------------------------------------------------------
  - id: "validate"
    type: "bash"
    output: "validation_result"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      import sys
      from pathlib import Path

      output_dir = "{{output_dir}}"
      subsystem_name = "{{subsystem_name}}"
      diagram_path = Path(output_dir) / f"{subsystem_name}.dot"

      result = {
          "valid": False,
          "errors": [],
          "diagram_path": str(diagram_path),
      }

      if not diagram_path.exists():
          result["errors"].append(f"{subsystem_name}.dot not found at {diagram_path}")
          print(json.dumps(result))
          sys.exit(0)

      try:
          import pydot

          graphs = pydot.graph_from_dot_file(str(diagram_path))
          if not graphs:
              result["errors"].append("pydot could not parse DOT — empty result")
              print(json.dumps(result))
              sys.exit(0)

          graph = graphs[0]
          result["valid"] = True
          result["node_count"] = len(graph.get_nodes())
          result["edge_count"] = len(graph.get_edges())

      except Exception as e:
          result["errors"].append(f"pydot validation error: {e}")

      print(json.dumps(result))
      EOF
```

### Step 4: Run tests to verify they pass

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_synthesize_subsystem_recipe.py -v --tb=short
```

Expected: ALL tests PASS.

### Step 5: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add recipes/synthesize-subsystem.yaml tests/test_synthesize_subsystem_recipe.py && git commit -m "feat: add synthesize-subsystem.yaml sub-recipe for subsystem synthesis

Building block recipe invoked once per subsystem during assembly.
Two steps: synthesize (discovery-subsystem-synthesizer agent),
validate (pydot check)."
```

---

## Task 5: Create synthesize-overview.yaml + tests

**Files:**
- Create: `recipes/synthesize-overview.yaml`
- Create: `tests/test_synthesize_overview_recipe.py`

### Step 1: Write the failing test

Create `tests/test_synthesize_overview_recipe.py`:

```python
"""Tests for recipes/synthesize-overview.yaml existence and structure.

Validates:
- File existence and valid YAML parse
- Top-level metadata (name, description, version, author, tags)
- Context variables (subsystem_dot_files, repo_root, output_dir)
- Flat (non-staged) steps structure with 2 steps
- synthesize step (agent: discovery-overview-synthesizer)
- validate step (bash, pydot validation + node count warning)
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-overview.yaml"


# ---------------------------------------------------------------------------
# File existence and parse
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/synthesize-overview.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/synthesize-overview.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# Top-level metadata
# ---------------------------------------------------------------------------


def test_recipe_name():
    """Recipe must have name='synthesize-overview'."""
    data = _load_recipe()
    assert data.get("name") == "synthesize-overview"


def test_recipe_description_non_empty():
    """Recipe must have a non-empty description."""
    data = _load_recipe()
    desc = data.get("description", "")
    assert isinstance(desc, str) and desc.strip()


def test_recipe_version():
    """Recipe must have version='1.0.0'."""
    data = _load_recipe()
    assert data.get("version") == "1.0.0"


def test_recipe_author():
    """Recipe must have author='DOT Graph Bundle'."""
    data = _load_recipe()
    assert data.get("author") == "DOT Graph Bundle"


def test_recipe_tags():
    """Recipe tags must include discovery, synthesis, sub-recipe, dot-graph, overview."""
    data = _load_recipe()
    tags = data.get("tags", [])
    for expected_tag in ["discovery", "synthesis", "sub-recipe", "dot-graph", "overview"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------


def test_context_has_subsystem_dot_files():
    """Context must declare 'subsystem_dot_files' variable."""
    ctx = _load_recipe().get("context", {})
    assert "subsystem_dot_files" in ctx


def test_context_has_repo_root():
    """Context must declare 'repo_root' variable."""
    ctx = _load_recipe().get("context", {})
    assert "repo_root" in ctx


def test_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    ctx = _load_recipe().get("context", {})
    assert "output_dir" in ctx


# ---------------------------------------------------------------------------
# Steps structure
# ---------------------------------------------------------------------------


def test_recipe_has_flat_steps():
    """Recipe must use flat steps list, not staged."""
    data = _load_recipe()
    assert "steps" in data
    assert "stages" not in data


def test_recipe_has_2_steps():
    """Recipe must have exactly 2 top-level steps: synthesize, validate."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 2, (
        f"Expected 2 steps, got {len(steps)}: {[s.get('id') for s in steps]}"
    )


def test_step_order():
    """Steps must be in order: synthesize, validate."""
    data = _load_recipe()
    ids = [s.get("id") for s in _get_steps(data)]
    assert ids == ["synthesize", "validate"], (
        f"Step order must be [synthesize, validate], got: {ids}"
    )


# ---------------------------------------------------------------------------
# synthesize step
# ---------------------------------------------------------------------------


def test_synthesize_agent():
    """synthesize step must reference agent 'dot-graph:discovery-overview-synthesizer'."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-overview-synthesizer"


def test_synthesize_has_timeout():
    """synthesize step must have timeout >= 600."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    assert step.get("timeout", 0) >= 600


def test_synthesize_prompt_references_context():
    """synthesize prompt must reference subsystem_dot_files, repo_root, output_dir."""
    step = _get_step_by_id(_load_recipe(), "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    for var in ["subsystem_dot_files", "repo_root", "output_dir"]:
        assert var in prompt, f"synthesize prompt must reference {var}"


# ---------------------------------------------------------------------------
# validate step
# ---------------------------------------------------------------------------


def test_validate_is_bash():
    """validate step must have type='bash'."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert step.get("type") == "bash"


def test_validate_uses_pydot():
    """validate step must invoke pydot for DOT validation."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "pydot" in step.get("command", "")


def test_validate_checks_node_count_80():
    """validate step must check node count against 80 threshold (warn if exceeded)."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "80" in step.get("command", ""), (
        "validate step must check node count against 80 threshold"
    )


def test_validate_references_overview_dot():
    """validate step must reference overview.dot."""
    step = _get_step_by_id(_load_recipe(), "validate")
    assert step is not None
    assert "overview.dot" in step.get("command", "")
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_synthesize_overview_recipe.py -v --tb=short 2>&1 | head -20
```

Expected: `test_recipe_file_exists` FAILS. All others FAIL or ERROR.

### Step 3: Create the recipe

Create `recipes/synthesize-overview.yaml`:

```yaml
name: "synthesize-overview"
description: >
  Overview-level synthesis sub-recipe for the discovery pipeline.
  Invoked once to produce the top-level architecture overview. Reads all
  subsystem DOT files and repo root context, delegates synthesis to the
  discovery-overview-synthesizer agent, and validates the produced DOT
  diagram via pydot with a node count warning threshold of 80.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "synthesis", "sub-recipe", "dot-graph", "overview"]

context:
  subsystem_dot_files: "[]"  # Required: JSON list of paths to subsystem DOT files
  repo_root: ""              # Required: root path of the repository
  output_dir: ""             # Required: where to write (.discovery/output/)

steps:
  # -------------------------------------------------------------------------
  # Step 1: Synthesize — agent reads subsystem DOTs + repo root, produces overview.dot
  # -------------------------------------------------------------------------
  - id: "synthesize"
    agent: "dot-graph:discovery-overview-synthesizer"
    output: "synthesis_result"
    timeout: 1200
    prompt: |
      You are the overview synthesizer for the repository at: {{repo_root}}

      Your task: read all subsystem DOT files and the repo root structure,
      then produce a top-level overview DOT diagram showing how subsystems
      relate to each other.

      **Subsystem DOT files:**
        {{subsystem_dot_files}}

      Read each subsystem DOT file listed above. These represent the
      inter-module structure within each subsystem.

      **Repository root:** {{repo_root}}
      Examine top-level files (README, config, entry points) for context
      about the overall architecture.

      **Output:** Write overview.dot to {{output_dir}}/

      The overview should show:
      - How subsystems depend on and communicate with each other
      - Cross-subsystem data flows and shared interfaces
      - The governing architecture a newcomer should understand in 5 minutes

      IMPORTANT: Keep the overview concise. Aim for fewer than 80 nodes.
      Each subsystem should be a high-level cluster, not a detailed breakdown.

  # -------------------------------------------------------------------------
  # Step 2: Validate — check overview.dot via pydot, warn if >80 nodes
  # -------------------------------------------------------------------------
  - id: "validate"
    type: "bash"
    output: "validation_result"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      import sys
      from pathlib import Path

      output_dir = "{{output_dir}}"
      diagram_path = Path(output_dir) / "overview.dot"

      result = {
          "valid": False,
          "errors": [],
          "warnings": [],
          "diagram_path": str(diagram_path),
      }

      if not diagram_path.exists():
          result["errors"].append(f"overview.dot not found at {diagram_path}")
          print(json.dumps(result))
          sys.exit(0)

      try:
          import pydot

          graphs = pydot.graph_from_dot_file(str(diagram_path))
          if not graphs:
              result["errors"].append("pydot could not parse overview.dot — empty result")
              print(json.dumps(result))
              sys.exit(0)

          graph = graphs[0]
          node_count = len(graph.get_nodes())
          edge_count = len(graph.get_edges())

          result["valid"] = True
          result["node_count"] = node_count
          result["edge_count"] = edge_count

          if node_count > 80:
              result["warnings"].append(
                  f"Overview has {node_count} nodes (exceeds 80 threshold) — "
                  f"consider simplifying for readability"
              )

      except Exception as e:
          result["errors"].append(f"pydot validation error: {e}")

      print(json.dumps(result))
      EOF
```

### Step 4: Run tests to verify they pass

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_synthesize_overview_recipe.py -v --tb=short
```

Expected: ALL tests PASS.

### Step 5: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add recipes/synthesize-overview.yaml tests/test_synthesize_overview_recipe.py && git commit -m "feat: add synthesize-overview.yaml sub-recipe for overview synthesis

Building block recipe invoked once to produce top-level overview.
Two steps: synthesize (discovery-overview-synthesizer agent),
validate (pydot check with 80-node warning threshold)."
```

---

## Task 6: Update test_final_verification.py + full test suite

**Files:**
- Modify: `tests/test_final_verification.py`

### Step 1: Add 3 new recipe files to EXPECTED_FILES

In `tests/test_final_verification.py`, find the `EXPECTED_FILES` list and add the 3 new recipe files at the end (after the Phase A v2 entries). Also update the docstring and file count.

**Change the module docstring** (line 1-5) from:
```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 35 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files (total 35).
"""
```
to:
```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 38 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files.
Phase B v2: Updated to include 3 new synthesizer sub-recipes (total 38).
"""
```

**Add 3 entries to the end of `EXPECTED_FILES`** (after `"context/discovery-combiner-instructions.md"`):
```python
    # Phase B v2: synthesizer sub-recipes
    "recipes/synthesize-level.yaml",
    "recipes/synthesize-subsystem.yaml",
    "recipes/synthesize-overview.yaml",
```

**Update `test_total_file_count`** — change the expected count from 35 to 38:
```python
def test_total_file_count():
    """Step 6: Total bundle file count is exactly 38 (35 prior + 3 Phase B v2)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 38, (
        f"Expected 38 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )
```

### Step 2: Run the updated verification tests

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_final_verification.py -v --tb=short
```

Expected: ALL tests PASS (including the 3 new parametrized file-exists tests and the updated count test).

### Step 3: Run the FULL test suite

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ modules/tool-dot-graph/tests/ -v --tb=short 2>&1 | tail -20
```

Expected: ALL tests PASS. No regressions. The total test count should be approximately:
- Prior: 1088
- Removed: ~12 assemble tests (graph manipulation)
- Added: ~16 new assemble tests + ~27 level recipe tests + ~22 subsystem recipe tests + ~23 overview recipe tests + 3 final verification parametrized
- Net total: approximately 1167 tests

### Step 4: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add tests/test_final_verification.py && git commit -m "test: update test_final_verification.py to 38 files with 3 Phase B v2 recipes"
```

---

## Summary of all files changed

| File | Action | Description |
|---|---|---|
| `modules/tool-dot-graph/amplifier_module_tool_dot_graph/assemble.py` | Modify | Strip to filesystem plumbing — remove all pydot graph manipulation |
| `modules/tool-dot-graph/tests/test_assemble.py` | Modify | Replace with 16 plumbing-focused tests |
| `recipes/synthesize-level.yaml` | Create | 3-step sub-recipe: read-level → synthesize → validate |
| `tests/test_synthesize_level_recipe.py` | Create | 27 structure tests for synthesize-level recipe |
| `recipes/synthesize-subsystem.yaml` | Create | 2-step sub-recipe: synthesize → validate |
| `tests/test_synthesize_subsystem_recipe.py` | Create | 22 structure tests for synthesize-subsystem recipe |
| `recipes/synthesize-overview.yaml` | Create | 2-step sub-recipe: synthesize → validate (80-node warning) |
| `tests/test_synthesize_overview_recipe.py` | Create | 23 structure tests for synthesize-overview recipe |
| `tests/test_final_verification.py` | Modify | Add 3 recipe files to expected list, update count to 38 |

## Commit sequence

1. `refactor: strip assemble.py to filesystem plumbing, remove all pydot graph manipulation`
2. `feat: add synthesize-level.yaml sub-recipe for bottom-up directory synthesis`
3. `feat: add synthesize-subsystem.yaml sub-recipe for subsystem synthesis`
4. `feat: add synthesize-overview.yaml sub-recipe for overview synthesis`
5. `test: update test_final_verification.py to 38 files with 3 Phase B v2 recipes`
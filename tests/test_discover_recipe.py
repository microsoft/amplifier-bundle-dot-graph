"""
Tests for recipes/discover.yaml — unified top-level discovery entry point.

Task B5: Create a unified discovery recipe that routes to quick or deep pipeline
based on the mode context variable.

Validates:
- File existence and valid YAML parse (2)
- Context variables: repo_path, mode, fidelity, lens, node_target (5)
- Mode defaults to 'auto', lens defaults to 'architecture' (2)
- Flat steps structure (not staged) (1)
- resolve-mode step: id, type=bash, parse_json=true (3)
- resolve-mode routes to quick and deep pipeline (4)
- run-pipeline step: id, type=recipe (2)
- run-pipeline passes repo_path and fidelity (2)
- final_output declared (1)

Total: 21+ tests covering all spec requirements
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discover.yaml"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_steps(data: dict) -> list:
    """Get flat steps list (not staged)."""
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    """Find a step by its id in flat steps list."""
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
# ---------------------------------------------------------------------------


def test_discover_recipe_file_exists():
    """recipes/discover.yaml must exist."""
    assert RECIPE_PATH.exists(), f"recipes/discover.yaml not found at {RECIPE_PATH}"


def test_discover_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Context variables (9 tests)
# ---------------------------------------------------------------------------


def test_discover_recipe_context_has_repo_path():
    """Context must declare repo_path."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context missing 'repo_path'. Context keys: {list(ctx.keys())}"
    )


def test_discover_recipe_context_has_mode():
    """Context must declare mode."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "mode" in ctx, f"Context missing 'mode'. Context keys: {list(ctx.keys())}"


def test_discover_recipe_mode_default_auto():
    """mode must default to 'auto'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert ctx.get("mode") == "auto", (
        f"Expected mode default 'auto', got: {ctx.get('mode')!r}"
    )


def test_discover_recipe_context_has_fidelity():
    """Context must declare fidelity."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "fidelity" in ctx, (
        f"Context missing 'fidelity'. Context keys: {list(ctx.keys())}"
    )


def test_discover_recipe_context_has_lens():
    """Context must declare lens."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "lens" in ctx, f"Context missing 'lens'. Context keys: {list(ctx.keys())}"


def test_discover_recipe_lens_default_architecture():
    """lens must default to 'architecture'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert ctx.get("lens") == "architecture", (
        f"Expected lens default 'architecture', got: {ctx.get('lens')!r}"
    )


def test_discover_recipe_context_has_node_target():
    """Context must declare node_target."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "node_target" in ctx, (
        f"Context missing 'node_target'. Context keys: {list(ctx.keys())}"
    )


# ---------------------------------------------------------------------------
# Flat steps structure (1 test)
# ---------------------------------------------------------------------------


def test_discover_recipe_has_steps():
    """Recipe must use flat steps structure (not staged)."""
    data = _load_recipe()
    assert "steps" in data, "Recipe must have top-level 'steps' key (flat, not staged)"
    assert "stages" not in data, (
        "Recipe must NOT use staged structure — should be flat steps"
    )
    steps = data.get("steps", [])
    assert isinstance(steps, list) and len(steps) > 0, (
        "Recipe must have at least one step in flat steps list"
    )


# ---------------------------------------------------------------------------
# resolve-mode step (5 tests)
# ---------------------------------------------------------------------------


def test_discover_recipe_has_resolve_mode_step():
    """Recipe must have a step with id='resolve-mode'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "resolve-mode")
    assert step is not None, "No step with id='resolve-mode' found in flat steps list"


def test_resolve_mode_is_bash_with_parse_json():
    """resolve-mode step must be type=bash with parse_json=true."""
    data = _load_recipe()
    step = _get_step_by_id(data, "resolve-mode")
    assert step is not None, "Step 'resolve-mode' not found"
    assert step.get("type") == "bash", (
        f"Expected type='bash' for resolve-mode, got: {step.get('type')!r}"
    )
    assert step.get("parse_json") is True, (
        f"Expected parse_json=true for resolve-mode, got: {step.get('parse_json')!r}"
    )


def test_resolve_mode_routes_to_quick_pipeline():
    """resolve-mode command must reference quick/discovery-pipeline.yaml."""
    data = _load_recipe()
    step = _get_step_by_id(data, "resolve-mode")
    assert step is not None, "Step 'resolve-mode' not found"
    command = step.get("command", "")
    assert "quick/discovery-pipeline.yaml" in command, (
        "resolve-mode command must reference 'quick/discovery-pipeline.yaml'"
    )


def test_resolve_mode_routes_to_deep_pipeline():
    """resolve-mode command must reference deep/discovery-pipeline.yaml."""
    data = _load_recipe()
    step = _get_step_by_id(data, "resolve-mode")
    assert step is not None, "Step 'resolve-mode' not found"
    command = step.get("command", "")
    assert "deep/discovery-pipeline.yaml" in command, (
        "resolve-mode command must reference 'deep/discovery-pipeline.yaml'"
    )


def test_resolve_mode_handles_quick_mode_explicitly():
    """resolve-mode command must handle explicit 'quick' mode."""
    data = _load_recipe()
    step = _get_step_by_id(data, "resolve-mode")
    assert step is not None, "Step 'resolve-mode' not found"
    command = step.get("command", "")
    assert "quick" in command, (
        "resolve-mode command must handle explicit 'quick' mode routing"
    )


def test_resolve_mode_handles_deep_mode_explicitly():
    """resolve-mode command must handle explicit 'deep' mode."""
    data = _load_recipe()
    step = _get_step_by_id(data, "resolve-mode")
    assert step is not None, "Step 'resolve-mode' not found"
    command = step.get("command", "")
    assert "deep" in command, (
        "resolve-mode command must handle explicit 'deep' mode routing"
    )


# ---------------------------------------------------------------------------
# run-pipeline step (4 tests)
# ---------------------------------------------------------------------------


def test_discover_recipe_has_run_pipeline_step():
    """Recipe must have a step with id='run-pipeline'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "run-pipeline")
    assert step is not None, "No step with id='run-pipeline' found in flat steps list"


def test_run_pipeline_is_type_recipe():
    """run-pipeline step must be type='recipe'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "run-pipeline")
    assert step is not None, "Step 'run-pipeline' not found"
    assert step.get("type") == "recipe", (
        f"Expected type='recipe' for run-pipeline, got: {step.get('type')!r}"
    )


def test_run_pipeline_passes_repo_path():
    """run-pipeline step must pass repo_path in its context."""
    data = _load_recipe()
    step = _get_step_by_id(data, "run-pipeline")
    assert step is not None, "Step 'run-pipeline' not found"
    context = step.get("context", {})
    assert "repo_path" in context, (
        f"run-pipeline step must pass 'repo_path' in context. "
        f"Context keys: {list(context.keys())}"
    )


def test_run_pipeline_passes_fidelity():
    """run-pipeline step must pass fidelity in its context."""
    data = _load_recipe()
    step = _get_step_by_id(data, "run-pipeline")
    assert step is not None, "Step 'run-pipeline' not found"
    context = step.get("context", {})
    assert "fidelity" in context, (
        f"run-pipeline step must pass 'fidelity' in context. "
        f"Context keys: {list(context.keys())}"
    )


# ---------------------------------------------------------------------------
# final_output (1 test)
# ---------------------------------------------------------------------------


def test_discover_recipe_has_final_output():
    """Recipe must declare a non-empty final_output."""
    data = _load_recipe()
    final_output = data.get("final_output", "")
    assert final_output and isinstance(final_output, str) and final_output.strip(), (
        f"Recipe must have a non-empty final_output, got: {final_output!r}"
    )

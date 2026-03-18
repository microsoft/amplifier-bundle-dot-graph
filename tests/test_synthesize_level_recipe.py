"""
Tests for recipes/synthesize-level.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: level_path, child_dot_files, output_dir, level_slug,
  fidelity default 'standard' (5 tests)
- Steps structure: flat steps, 3 steps, correct order [read-level, synthesize, validate] (3 tests)
- read-level step: type=bash, parse_json=true, references level_path (3 tests)
- synthesize step: agent='dot-graph:discovery-level-synthesizer', timeout>=600,
  prompt references level_path, prompt references output_dir, prompt references fidelity (5 tests)
- validate step: type=bash, references diagram.dot, uses pydot, parse_json=true (4 tests)

Total: 2 + 5 + 5 + 3 + 3 + 5 + 4 = 27 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-level.yaml"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
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
# Top-level metadata (5 tests)
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
    assert data.get("version") == "1.0.0", (
        f"Expected version='1.0.0', got: {data.get('version')!r}"
    )


def test_recipe_author():
    """Recipe must have author='DOT Graph Bundle'."""
    data = _load_recipe()
    assert data.get("author") == "DOT Graph Bundle", (
        f"Expected author='DOT Graph Bundle', got: {data.get('author')!r}"
    )


def test_recipe_tags():
    """Recipe tags must include discovery, synthesis, sub-recipe, dot-graph, bottom-up."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in [
        "discovery",
        "synthesis",
        "sub-recipe",
        "dot-graph",
        "bottom-up",
    ]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (5 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_level_path():
    """Context must declare 'level_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "level_path" in ctx, (
        f"Context must declare 'level_path' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_child_dot_files():
    """Context must declare 'child_dot_files' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "child_dot_files" in ctx, (
        f"Context must declare 'child_dot_files' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_level_slug():
    """Context must declare 'level_slug' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "level_slug" in ctx, (
        f"Context must declare 'level_slug' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_fidelity_default_standard():
    """Context must declare 'fidelity' variable with default 'standard'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "fidelity" in ctx, (
        f"Context must declare 'fidelity' variable. Found keys: {list(ctx.keys())}"
    )
    assert ctx["fidelity"] == "standard", (
        f"fidelity default must be 'standard', got: {ctx['fidelity']!r}"
    )


# ---------------------------------------------------------------------------
# Steps structure (3 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_flat_steps_not_staged():
    """Recipe must use flat steps list (not a staged structure)."""
    data = _load_recipe()
    assert "steps" in data, "Recipe must have a top-level 'steps' key"
    assert "stages" not in data, (
        "Recipe must NOT have a 'stages' key — must be flat (non-staged)"
    )
    assert isinstance(data["steps"], list), "steps must be a list"


def test_recipe_has_exactly_3_steps():
    """Recipe must have exactly 3 flat steps."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 3, f"Expected exactly 3 steps, got {len(steps)}"


def test_recipe_steps_correct_order():
    """Steps must be in order: [read-level, synthesize, validate]."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 3, f"Expected 3 steps to check order, got {len(steps)}"
    step_ids = [s.get("id") for s in steps]
    assert step_ids == ["read-level", "synthesize", "validate"], (
        f"Steps must be in order [read-level, synthesize, validate], got: {step_ids}"
    )


# ---------------------------------------------------------------------------
# read-level step (3 tests)
# ---------------------------------------------------------------------------


def test_read_level_step_type_is_bash():
    """read-level step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "read-level")
    assert step is not None, (
        f"No step with id='read-level' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("type") == "bash", (
        f"read-level step must have type='bash', got: {step.get('type')!r}"
    )


def test_read_level_step_has_parse_json_true():
    """read-level step must have parse_json=true."""
    data = _load_recipe()
    step = _get_step_by_id(data, "read-level")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"read-level step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


def test_read_level_step_references_level_path():
    """read-level step command must reference level_path context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "read-level")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "level_path" in command_text, (
        "read-level step command must reference level_path context variable"
    )


# ---------------------------------------------------------------------------
# synthesize step (5 tests)
# ---------------------------------------------------------------------------


def test_synthesize_step_agent():
    """synthesize step must use agent='dot-graph:discovery-level-synthesizer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None, (
        f"No step with id='synthesize' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("agent") == "dot-graph:discovery-level-synthesizer", (
        f"synthesize step must use agent='dot-graph:discovery-level-synthesizer', "
        f"got: {step.get('agent')!r}"
    )


def test_synthesize_step_timeout_at_least_600():
    """synthesize step must have timeout >= 600."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    timeout = step.get("timeout", 0)
    assert isinstance(timeout, int) and timeout >= 600, (
        f"synthesize step timeout must be >= 600, got: {timeout!r}"
    )


def test_synthesize_step_prompt_references_level_path():
    """synthesize step prompt must reference level_path context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert isinstance(prompt, str) and prompt.strip(), (
        "synthesize step must have a non-empty prompt"
    )
    assert "level_path" in prompt, (
        "synthesize step prompt must reference 'level_path' context variable"
    )


def test_synthesize_step_prompt_references_output_dir():
    """synthesize step prompt must reference output_dir context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "output_dir" in prompt, (
        "synthesize step prompt must reference 'output_dir' context variable"
    )


def test_synthesize_step_prompt_references_fidelity():
    """synthesize step prompt must reference fidelity context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "fidelity" in prompt, (
        "synthesize step prompt must reference 'fidelity' context variable"
    )


# ---------------------------------------------------------------------------
# validate step (4 tests)
# ---------------------------------------------------------------------------


def test_validate_step_type_is_bash():
    """validate step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None, (
        f"No step with id='validate' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("type") == "bash", (
        f"validate step must have type='bash', got: {step.get('type')!r}"
    )


def test_validate_step_references_diagram_dot():
    """validate step command must reference diagram.dot."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "diagram.dot" in command_text, (
        "validate step command must reference diagram.dot"
    )


def test_validate_step_uses_pydot():
    """validate step command must use pydot for validation."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "pydot" in command_text, (
        "validate step command must use pydot for diagram validation"
    )


def test_validate_step_has_parse_json_true():
    """validate step must have parse_json=true."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"validate step must have parse_json=true, got: {step.get('parse_json')!r}"
    )

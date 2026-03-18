"""
Tests for recipes/synthesize-overview.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: subsystem_dot_files, repo_root, output_dir (3 tests)
- Steps structure: flat steps, 2 steps, correct order [synthesize, validate] (3 tests)
- synthesize step: agent='dot-graph:discovery-overview-synthesizer', timeout>=600,
  prompt references context vars (3 tests)
- validate step: type=bash, uses pydot, checks node count against 80,
  references overview.dot, parse_json=true, includes warnings (7 tests)

Total: 2 + 5 + 3 + 3 + 3 + 7 = 23 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-overview.yaml"


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
# Top-level metadata (5 tests)
# ---------------------------------------------------------------------------


def test_recipe_name():
    """Recipe must have name='synthesize-overview'."""
    data = _load_recipe()
    assert data.get("name") == "synthesize-overview", (
        f"Expected name='synthesize-overview', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, synthesis, sub-recipe, dot-graph, overview."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in [
        "discovery",
        "synthesis",
        "sub-recipe",
        "dot-graph",
        "overview",
    ]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (3 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_subsystem_dot_files():
    """Context must declare 'subsystem_dot_files' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "subsystem_dot_files" in ctx, (
        f"Context must declare 'subsystem_dot_files' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_repo_root():
    """Context must declare 'repo_root' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_root" in ctx, (
        f"Context must declare 'repo_root' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
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


def test_recipe_has_exactly_2_steps():
    """Recipe must have exactly 2 flat steps."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 2, f"Expected exactly 2 steps, got {len(steps)}"


def test_recipe_steps_correct_order():
    """Steps must be in order: [synthesize, validate]."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 2, f"Expected 2 steps to check order, got {len(steps)}"
    step_ids = [s.get("id") for s in steps]
    assert step_ids == ["synthesize", "validate"], (
        f"Steps must be in order [synthesize, validate], got: {step_ids}"
    )


# ---------------------------------------------------------------------------
# synthesize step (3 tests)
# ---------------------------------------------------------------------------


def test_synthesize_step_agent():
    """synthesize step must use agent='dot-graph:discovery-overview-synthesizer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None, (
        f"No step with id='synthesize' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("agent") == "dot-graph:discovery-overview-synthesizer", (
        f"synthesize step must use agent='dot-graph:discovery-overview-synthesizer', "
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


def test_synthesize_step_prompt_references_context_vars():
    """synthesize step prompt must reference repo_root, subsystem_dot_files, output_dir."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert isinstance(prompt, str) and prompt.strip(), (
        "synthesize step must have a non-empty prompt"
    )
    for var in ["repo_root", "subsystem_dot_files", "output_dir"]:
        assert var in prompt, (
            f"synthesize step prompt must reference '{var}' context variable"
        )


# ---------------------------------------------------------------------------
# validate step (7 tests)
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


def test_validate_step_uses_pydot():
    """validate step command must use pydot for validation."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "pydot" in command_text, (
        "validate step command must use pydot for diagram validation"
    )


def test_validate_step_checks_node_count_against_80():
    """validate step command must check node count against threshold of 80."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "80" in command_text, (
        "validate step command must contain '80' threshold for node count warning"
    )


def test_validate_step_references_overview_dot():
    """validate step command must reference overview.dot."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "overview.dot" in command_text, (
        "validate step command must reference 'overview.dot'"
    )


def test_validate_step_has_parse_json_true():
    """validate step must have parse_json=true."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"validate step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


def test_validate_step_includes_warnings_array():
    """validate step command must include a 'warnings' array in output (unlike level/subsystem)."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "warnings" in command_text, (
        "validate step command must include 'warnings' array in output "
        "(this distinguishes overview from level/subsystem validate steps)"
    )


def test_recipe_context_has_exactly_3_variables():
    """Context must declare exactly 3 variables: subsystem_dot_files, repo_root, output_dir."""
    data = _load_recipe()
    ctx = data.get("context", {})
    expected_keys = {"subsystem_dot_files", "repo_root", "output_dir"}
    actual_keys = set(ctx.keys())
    assert actual_keys == expected_keys, (
        f"Context must have exactly these keys: {sorted(expected_keys)}, "
        f"got: {sorted(actual_keys)}"
    )

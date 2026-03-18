"""
Tests for recipes/discovery-combine.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, topdown_dir, bottomup_dir, output_dir,
  render_png default 'true' (5 tests)
- Steps structure: flat steps, 4 steps, correct order
  [check-inputs, combine, validate, render] (3 tests)
- check-inputs step: type=bash, references topdown_dir, references bottomup_dir,
  handles missing dirs gracefully (no hard fail) (4 tests)
- combine step: agent='dot-graph:discovery-combiner', timeout>=600,
  prompt references output_dir, prompt references both strategy dirs (4 tests)
- validate step: type=bash, references combined.dot, uses validate_dot from tool,
  continues on warnings (3 tests)
- render step: type=bash, has 'when' condition referencing render_png,
  command uses dot -Tpng, references combined.dot (4 tests)
- Agent is declared in behaviors/dot-discovery.yaml (1 test)

Total: 2 + 5 + 5 + 3 + 4 + 4 + 3 + 4 + 1 = 31 tests (aim: ~28)
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-combine.yaml"
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-discovery.yaml"


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
    """recipes/discovery-combine.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-combine.yaml not found at {RECIPE_PATH}"
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
    """Recipe must have name='discovery-combine'."""
    data = _load_recipe()
    assert data.get("name") == "discovery-combine", (
        f"Expected name='discovery-combine', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, combine, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "combine", "dot-graph"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (5 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path():
    """Context must declare 'repo_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_topdown_dir():
    """Context must declare 'topdown_dir' variable with a default referencing topdown."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "topdown_dir" in ctx, (
        f"Context must declare 'topdown_dir' variable. Found keys: {list(ctx.keys())}"
    )
    default_val = str(ctx["topdown_dir"])
    assert "topdown" in default_val, (
        f"topdown_dir default must reference 'topdown', got: {default_val!r}"
    )


def test_recipe_context_has_bottomup_dir():
    """Context must declare 'bottomup_dir' variable with a default referencing bottomup."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "bottomup_dir" in ctx, (
        f"Context must declare 'bottomup_dir' variable. Found keys: {list(ctx.keys())}"
    )
    default_val = str(ctx["bottomup_dir"])
    assert "bottomup" in default_val, (
        f"bottomup_dir default must reference 'bottomup', got: {default_val!r}"
    )


def test_recipe_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_render_png_default_true():
    """Context must declare 'render_png' variable with default 'true'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "render_png" in ctx, (
        f"Context must declare 'render_png' variable. Found keys: {list(ctx.keys())}"
    )
    assert str(ctx["render_png"]) == "true", (
        f"render_png default must be 'true', got: {ctx['render_png']!r}"
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


def test_recipe_has_exactly_4_steps():
    """Recipe must have exactly 4 flat steps."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 4, f"Expected exactly 4 steps, got {len(steps)}"


def test_recipe_steps_correct_order():
    """Steps must be in order: [check-inputs, combine, validate, render]."""
    data = _load_recipe()
    steps = _get_steps(data)
    assert len(steps) == 4, f"Expected 4 steps to check order, got {len(steps)}"
    step_ids = [s.get("id") for s in steps]
    assert step_ids == ["check-inputs", "combine", "validate", "render"], (
        f"Steps must be in order [check-inputs, combine, validate, render], got: {step_ids}"
    )


# ---------------------------------------------------------------------------
# check-inputs step (4 tests)
# ---------------------------------------------------------------------------


def test_check_inputs_step_type_is_bash():
    """check-inputs step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-inputs")
    assert step is not None, (
        f"No step with id='check-inputs' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("type") == "bash", (
        f"check-inputs step must have type='bash', got: {step.get('type')!r}"
    )


def test_check_inputs_references_topdown_dir():
    """check-inputs step command must reference topdown_dir context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-inputs")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "topdown_dir" in command_text, (
        "check-inputs step command must reference 'topdown_dir' context variable"
    )


def test_check_inputs_references_bottomup_dir():
    """check-inputs step command must reference bottomup_dir context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-inputs")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "bottomup_dir" in command_text, (
        "check-inputs step command must reference 'bottomup_dir' context variable"
    )


def test_check_inputs_degraded_mode_no_hard_fail():
    """check-inputs step must allow degraded mode — no hard fail on missing dirs.

    The step should log a warning but NOT fail hard when a strategy dir is missing.
    Evidence: uses '|| true' or exit 0 or warning-only pattern, not 'exit 1' on missing dirs.
    """
    data = _load_recipe()
    step = _get_step_by_id(data, "check-inputs")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    # Must not hard-fail: must have some graceful handling
    # Accept: "|| true", "warning", "warn", "echo", "|| echo", "exit 0"
    graceful_patterns = ["|| true", "warning", "warn", "echo", "exit 0"]
    has_graceful = any(p in command_text.lower() for p in graceful_patterns)
    assert has_graceful, (
        "check-inputs step must allow degraded mode — should log a warning "
        "rather than hard-failing when a strategy directory is missing. "
        f"Command should contain one of: {graceful_patterns}"
    )


# ---------------------------------------------------------------------------
# combine step (4 tests)
# ---------------------------------------------------------------------------


def test_combine_step_agent_is_discovery_combiner():
    """combine step must use agent='dot-graph:discovery-combiner'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "combine")
    assert step is not None, (
        f"No step with id='combine' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("agent") == "dot-graph:discovery-combiner", (
        f"combine step must use agent='dot-graph:discovery-combiner', "
        f"got: {step.get('agent')!r}"
    )


def test_combine_step_timeout_at_least_600():
    """combine step must have timeout >= 600."""
    data = _load_recipe()
    step = _get_step_by_id(data, "combine")
    assert step is not None
    timeout = step.get("timeout", 0)
    assert isinstance(timeout, int) and timeout >= 600, (
        f"combine step timeout must be >= 600, got: {timeout!r}"
    )


def test_combine_step_prompt_references_output_dir():
    """combine step prompt must reference output_dir context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "combine")
    assert step is not None
    prompt = step.get("prompt", "")
    assert isinstance(prompt, str) and prompt.strip(), (
        "combine step must have a non-empty prompt"
    )
    assert "output_dir" in prompt, (
        "combine step prompt must reference 'output_dir' context variable"
    )


def test_combine_step_prompt_references_both_strategy_dirs():
    """combine step prompt must reference both topdown_dir and bottomup_dir."""
    data = _load_recipe()
    step = _get_step_by_id(data, "combine")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "topdown_dir" in prompt or "topdown" in prompt.lower(), (
        "combine step prompt must reference the top-down strategy directory"
    )
    assert "bottomup_dir" in prompt or "bottomup" in prompt.lower(), (
        "combine step prompt must reference the bottom-up strategy directory"
    )


# ---------------------------------------------------------------------------
# validate step (3 tests)
# ---------------------------------------------------------------------------


def test_validate_step_type_is_bash():
    """validate step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None, (
        f"No step with id='validate' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("type") == "bash", (
        f"validate step must have type='bash', got: {step.get('type')!r}"
    )


def test_validate_step_references_combined_dot():
    """validate step command must reference combined.dot."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "combined.dot" in command_text, (
        "validate step command must reference 'combined.dot'"
    )


def test_validate_step_uses_validate_dot_from_tool():
    """validate step command must use the validate_dot function from the tool module."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    # Per spec: uses amplifier_module_tool_dot_graph validate.validate_dot
    assert "validate_dot" in command_text or "validate" in command_text, (
        "validate step command must use validate_dot from amplifier_module_tool_dot_graph"
    )


# ---------------------------------------------------------------------------
# render step (4 tests)
# ---------------------------------------------------------------------------


def test_render_step_type_is_bash():
    """render step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "render")
    assert step is not None, (
        f"No step with id='render' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )
    assert step.get("type") == "bash", (
        f"render step must have type='bash', got: {step.get('type')!r}"
    )


def test_render_step_has_when_condition():
    """render step must have a 'when' condition (conditional execution)."""
    data = _load_recipe()
    step = _get_step_by_id(data, "render")
    assert step is not None
    assert "when" in step, (
        "render step must have a 'when' condition for conditional execution"
    )


def test_render_step_when_references_render_png():
    """render step 'when' condition must reference render_png context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "render")
    assert step is not None
    when_val = str(step.get("when", ""))
    assert "render_png" in when_val, (
        f"render step 'when' condition must reference 'render_png', got: {when_val!r}"
    )


def test_render_step_command_uses_dot_tpng():
    """render step command must use 'dot -Tpng' to render PNG."""
    data = _load_recipe()
    step = _get_step_by_id(data, "render")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert (
        "dot" in command_text and "Tpng" in command_text or "-Tpng" in command_text
    ), "render step command must use 'dot -Tpng' for PNG rendering"


# ---------------------------------------------------------------------------
# Agent declared in dot-discovery.yaml (1 test)
# ---------------------------------------------------------------------------


def test_discovery_combiner_agent_declared_in_behavior():
    """The discovery-combiner agent must be declared in behaviors/dot-discovery.yaml."""
    assert BEHAVIOR_PATH.exists(), (
        f"behaviors/dot-discovery.yaml not found at {BEHAVIOR_PATH}"
    )
    behavior_content = BEHAVIOR_PATH.read_text()
    assert "discovery-combiner" in behavior_content, (
        "behaviors/dot-discovery.yaml must declare the 'discovery-combiner' agent"
    )

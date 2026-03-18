"""
Tests for recipes/discovery-synthesize-module.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse
- Top-level metadata (name, description, version, author, tags)
- Context variables (module_name, module_dir, fidelity, output_dir)
- Flat (non-staged) steps structure
- Synthesize step with correct agent
- Validate step exists (bash type)
- Check-quality step exists
- Quality gate loop logic (while_condition/max_iterations/loop_back_to/break_when)
- Max retries of 3
- Synthesize prompt references module_dir and module_name
- Validate step is bash type invoking pydot validation
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"


# ---------------------------------------------------------------------------
# File existence and parse
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/discovery-synthesize-module.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-synthesize-module.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Top-level metadata
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
        # Search nested steps (e.g., while loop body steps)
        for nested_step in step.get("steps", []):
            if nested_step.get("id") == step_id:
                return nested_step
    return None


def _get_quality_gate_step(data: dict) -> dict | None:
    """Get the top-level quality-gate while-loop step."""
    return _get_step_by_id(data, "quality-gate")


def test_recipe_name():
    """Recipe must have name='discovery-synthesize-module'."""
    data = _load_recipe()
    assert data.get("name") == "discovery-synthesize-module", (
        f"Expected name='discovery-synthesize-module', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, synthesis, quality-gate, sub-recipe, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in [
        "discovery",
        "synthesis",
        "quality-gate",
        "sub-recipe",
        "dot-graph",
    ]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------


def test_recipe_context_has_module_name():
    """Context must declare 'module_name' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "module_name" in ctx, (
        f"Context must declare 'module_name' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_module_dir():
    """Context must declare 'module_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "module_dir" in ctx, (
        f"Context must declare 'module_dir' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_fidelity():
    """Context must declare 'fidelity' variable with default 'standard'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "fidelity" in ctx, (
        f"Context must declare 'fidelity' variable. Found keys: {list(ctx.keys())}"
    )
    assert ctx["fidelity"] == "standard", (
        f"fidelity default must be 'standard', got: {ctx['fidelity']!r}"
    )


def test_recipe_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
    )


# ---------------------------------------------------------------------------
# Flat (non-staged) steps structure
# ---------------------------------------------------------------------------


def test_recipe_has_flat_steps_not_staged():
    """Recipe must use flat steps list, not a staged structure."""
    data = _load_recipe()
    assert "steps" in data, "Recipe must have a top-level 'steps' key"
    assert "stages" not in data, (
        "Recipe must NOT have a 'stages' key — must be flat (non-staged)"
    )
    assert isinstance(data["steps"], list), "steps must be a list"


def test_recipe_has_3_steps():
    """Recipe must have 1 top-level quality-gate while-loop step containing exactly 3 inner steps."""
    data = _load_recipe()
    steps = data.get("steps", [])
    # The recipe uses a while-loop structure: 1 top-level quality-gate step
    # containing 3 inner steps (synthesize, validate, check-quality)
    assert len(steps) == 1, (
        f"Expected exactly 1 top-level step (quality-gate while loop), got {len(steps)}"
    )
    qg_step = steps[0]
    assert qg_step.get("id") == "quality-gate", (
        f"Top-level step must be 'quality-gate', got: {qg_step.get('id')!r}"
    )
    inner_steps = qg_step.get("steps", [])
    assert len(inner_steps) == 3, (
        f"quality-gate must contain exactly 3 inner steps "
        f"(synthesize, validate, check-quality), got {len(inner_steps)}"
    )


# ---------------------------------------------------------------------------
# Synthesize step
# ---------------------------------------------------------------------------


def test_synthesize_step_exists():
    """Must have a step with id='synthesize'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None, (
        f"No step with id='synthesize' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


def test_synthesize_agent_reference():
    """synthesize step must reference agent 'dot-graph:discovery-synthesizer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-synthesizer", (
        f"Expected agent='dot-graph:discovery-synthesizer', got: {step.get('agent')!r}"
    )


def test_synthesize_output_variable():
    """synthesize step must have output='synthesis_result'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    assert step.get("output") == "synthesis_result", (
        f"synthesize output must be 'synthesis_result', got: {step.get('output')!r}"
    )


def test_synthesize_timeout():
    """synthesize step must have timeout=1200."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    assert step.get("timeout") == 1200, (
        f"synthesize timeout must be 1200, got: {step.get('timeout')!r}"
    )


def test_synthesize_prompt_references_module_dir():
    """synthesize prompt must reference module_dir context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "module_dir" in prompt, (
        "synthesize prompt must reference module_dir context variable"
    )


def test_synthesize_prompt_references_module_name():
    """synthesize prompt must reference module_name context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "module_name" in prompt, (
        "synthesize prompt must reference module_name context variable"
    )


def test_synthesize_prompt_references_validation_errors():
    """synthesize prompt must reference _validation_errors for retry feedback."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "_validation_errors" in prompt, (
        "synthesize prompt must reference _validation_errors for retry feedback"
    )


def test_synthesize_prompt_has_no_fiat_reconciliation():
    """synthesize prompt must include cardinal rule: never reconcile discrepancies by fiat."""
    data = _load_recipe()
    step = _get_step_by_id(data, "synthesize")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "fiat" in prompt.lower() or "reconcile" in prompt.lower(), (
        "synthesize prompt must include cardinal rule about not reconciling by fiat"
    )


# ---------------------------------------------------------------------------
# Validate step
# ---------------------------------------------------------------------------


def test_validate_step_exists():
    """Must have a step with id='validate'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None, (
        f"No step with id='validate' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


def test_validate_step_is_bash_type():
    """validate step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    assert step.get("type") == "bash", (
        f"validate step must have type='bash', got: {step.get('type')!r}"
    )


def test_validate_step_output_variable():
    """validate step must have output='validation_result'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    assert step.get("output") == "validation_result", (
        f"validate output must be 'validation_result', got: {step.get('output')!r}"
    )


def test_validate_step_parse_json():
    """validate step must have parse_json=true."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"validate step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


def test_validate_step_timeout():
    """validate step must have timeout=30."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    assert step.get("timeout") == 30, (
        f"validate timeout must be 30, got: {step.get('timeout')!r}"
    )


def test_validate_step_invokes_pydot():
    """validate step command/script must invoke pydot for validation."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    # Check either 'command' or 'script' field
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "pydot" in command_text, (
        "validate step must invoke pydot for diagram validation"
    )


def test_validate_step_checks_diagram_dot_exists():
    """validate step must check that diagram.dot exists in module_dir."""
    data = _load_recipe()
    step = _get_step_by_id(data, "validate")
    assert step is not None
    command_text = step.get("command", "") or step.get("script", "") or ""
    assert "diagram.dot" in command_text, (
        "validate step must check for diagram.dot file"
    )
    assert "module_dir" in command_text, (
        "validate step must reference module_dir for diagram.dot path"
    )


# ---------------------------------------------------------------------------
# Check-quality step
# ---------------------------------------------------------------------------


def test_check_quality_step_exists():
    """Must have a step with id='check-quality'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-quality")
    assert step is not None, (
        f"No step with id='check-quality' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


def test_check_quality_step_is_bash_type():
    """check-quality step must have type='bash'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-quality")
    assert step is not None
    assert step.get("type") == "bash", (
        f"check-quality step must have type='bash', got: {step.get('type')!r}"
    )


def test_check_quality_output_variable():
    """check-quality step must have output='quality_check'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-quality")
    assert step is not None
    assert step.get("output") == "quality_check", (
        f"check-quality output must be 'quality_check', got: {step.get('output')!r}"
    )


def test_check_quality_parse_json():
    """check-quality step must have parse_json=true."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-quality")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"check-quality step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


def test_check_quality_timeout():
    """check-quality step must have timeout=10."""
    data = _load_recipe()
    step = _get_step_by_id(data, "check-quality")
    assert step is not None
    assert step.get("timeout") == 10, (
        f"check-quality timeout must be 10, got: {step.get('timeout')!r}"
    )


# ---------------------------------------------------------------------------
# Quality gate loop logic
# ---------------------------------------------------------------------------


def test_quality_gate_has_while_condition():
    """quality-gate step must have a while_condition for the loop."""
    data = _load_recipe()
    step = _get_quality_gate_step(data)
    assert step is not None, "No 'quality-gate' step found"
    assert "while_condition" in step, (
        "quality-gate step must have a 'while_condition' for the quality gate loop"
    )
    while_cond = step["while_condition"]
    assert isinstance(while_cond, str) and while_cond.strip(), (
        f"while_condition must be a non-empty string, got: {while_cond!r}"
    )


def test_quality_gate_has_max_iterations_3():
    """quality-gate step must have max_while_iterations=3."""
    data = _load_recipe()
    step = _get_quality_gate_step(data)
    assert step is not None, "No 'quality-gate' step found"
    assert step.get("max_while_iterations") == 3, (
        f"quality-gate max_while_iterations must be 3, got: {step.get('max_while_iterations')!r}"
    )


def test_quality_gate_has_loop_back_to_synthesize():
    """quality-gate while loop must have synthesize as the first inner step (loop body re-entry point)."""
    data = _load_recipe()
    step = _get_quality_gate_step(data)
    assert step is not None, "No 'quality-gate' step found"
    inner_steps = step.get("steps", [])
    assert len(inner_steps) > 0, "quality-gate must have inner steps (while loop body)"
    first_inner = inner_steps[0]
    assert first_inner.get("id") == "synthesize", (
        f"First inner step of quality-gate must be 'synthesize' (loop body re-entry point), "
        f"got: {first_inner.get('id')!r}"
    )


def test_quality_gate_has_break_when():
    """quality-gate step must have a break_when condition referencing quality_passed."""
    data = _load_recipe()
    step = _get_quality_gate_step(data)
    assert step is not None, "No 'quality-gate' step found"
    assert "break_when" in step, "quality-gate step must have a 'break_when' condition"
    break_cond = step["break_when"]
    assert "quality_passed" in break_cond, (
        f"break_when must reference 'quality_passed': {break_cond!r}"
    )


def test_quality_gate_while_and_break_are_complementary():
    """while_condition and break_when must be complementary: loop=true, break on quality_passed==true."""
    data = _load_recipe()
    step = _get_quality_gate_step(data)
    assert step is not None, "No 'quality-gate' step found"
    while_cond = step.get("while_condition", "")
    break_cond = step.get("break_when", "")
    # while loops continuously (while_condition="true"), break_when exits on quality_passed==true
    assert while_cond.strip().lower() == "true", (
        f"while_condition should be 'true' (loop runs until break_when triggers): {while_cond!r}"
    )
    assert "true" in break_cond.lower() or "== true" in break_cond.lower(), (
        f"break_when should break when quality_passed is true: {break_cond!r}"
    )

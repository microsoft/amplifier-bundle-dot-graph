"""
Tests for recipes/discovery-investigate-topic.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse
- Top-level metadata (name, description, version, author, tags)
- Context variables (topic_name, topic_slug, topic_description, fidelity, repo_path, output_dir)
- Flat (non-staged) steps structure
- Exactly 3 agent steps with correct IDs and agent references
- Fidelity-based conditions for each step
- Agent prompts reference topic_name/topic_slug and output_dir context variables
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"


# ---------------------------------------------------------------------------
# File existence and parse
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/discovery-investigate-topic.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-investigate-topic.yaml not found at {RECIPE_PATH}"
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


def test_recipe_name():
    """Recipe must have name='discovery-investigate-topic'."""
    data = _load_recipe()
    assert data.get("name") == "discovery-investigate-topic", (
        f"Expected name='discovery-investigate-topic', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, investigation, sub-recipe, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "investigation", "sub-recipe", "dot-graph"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------


def test_recipe_context_has_topic_name():
    """Context must declare 'topic_name' variable (flattened from topic object)."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "topic_name" in ctx, (
        f"Context must declare 'topic_name' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_topic_slug():
    """Context must declare 'topic_slug' variable (flattened from topic object)."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "topic_slug" in ctx, (
        f"Context must declare 'topic_slug' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_topic_description():
    """Context must declare 'topic_description' variable (flattened from topic object)."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "topic_description" in ctx, (
        f"Context must declare 'topic_description' variable. Found keys: {list(ctx.keys())}"
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


def test_recipe_context_has_repo_path():
    """Context must declare 'repo_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path' variable. Found keys: {list(ctx.keys())}"
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


def test_recipe_has_exactly_3_steps():
    """Recipe must have exactly 3 agent steps."""
    data = _load_recipe()
    steps = data.get("steps", [])
    assert len(steps) == 3, f"Expected exactly 3 steps, got {len(steps)}"


# ---------------------------------------------------------------------------
# Step IDs
# ---------------------------------------------------------------------------


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


def test_step_code_tracer_exists():
    """Must have a step with id='code-tracer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None, (
        f"No step with id='code-tracer' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


def test_step_behavior_observer_exists():
    """Must have a step with id='behavior-observer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None, (
        f"No step with id='behavior-observer' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


def test_step_integration_mapper_exists():
    """Must have a step with id='integration-mapper'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None, (
        f"No step with id='integration-mapper' found. Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


# ---------------------------------------------------------------------------
# Agent references
# ---------------------------------------------------------------------------


def test_code_tracer_agent_reference():
    """code-tracer step must reference agent 'dot-graph:discovery-code-tracer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-code-tracer", (
        f"Expected agent='dot-graph:discovery-code-tracer', got: {step.get('agent')!r}"
    )


def test_behavior_observer_agent_reference():
    """behavior-observer step must reference agent 'dot-graph:discovery-behavior-observer'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-behavior-observer", (
        f"Expected agent='dot-graph:discovery-behavior-observer', got: {step.get('agent')!r}"
    )


def test_integration_mapper_agent_reference():
    """integration-mapper step must reference agent 'dot-graph:discovery-integration-mapper'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-integration-mapper", (
        f"Expected agent='dot-graph:discovery-integration-mapper', got: {step.get('agent')!r}"
    )


# ---------------------------------------------------------------------------
# Fidelity-based conditions
# ---------------------------------------------------------------------------


def test_code_tracer_condition_not_quick():
    """code-tracer must have condition that excludes 'quick' fidelity."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "code-tracer step must have a condition"
    # Condition must express "not quick" — allow either != or not ==
    assert "quick" in condition, (
        f"code-tracer condition must reference 'quick': {condition!r}"
    )
    # Must be a "not quick" condition (runs at standard + deep)
    assert "!=" in condition or ("not" in condition and "==" in condition), (
        f"code-tracer condition must be a 'not quick' expression: {condition!r}"
    )


def test_behavior_observer_condition_deep_only():
    """behavior-observer must have condition that requires 'deep' fidelity."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "behavior-observer step must have a condition"
    assert "deep" in condition, (
        f"behavior-observer condition must reference 'deep': {condition!r}"
    )
    assert "==" in condition, (
        f"behavior-observer condition must use == to require deep: {condition!r}"
    )


def test_integration_mapper_condition_not_quick():
    """integration-mapper must have condition that excludes 'quick' fidelity."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "integration-mapper step must have a condition"
    assert "quick" in condition, (
        f"integration-mapper condition must reference 'quick': {condition!r}"
    )
    assert "!=" in condition or ("not" in condition and "==" in condition), (
        f"integration-mapper condition must be a 'not quick' expression: {condition!r}"
    )


# ---------------------------------------------------------------------------
# Agent prompts reference topic and output_dir
# ---------------------------------------------------------------------------


def test_code_tracer_prompt_references_topic():
    """code-tracer prompt must reference {{topic_name}} and {{topic_slug}} context variables."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "topic_name" in prompt, (
        "code-tracer prompt must reference {{topic_name}} context variable"
    )
    assert "topic_slug" in prompt, (
        "code-tracer prompt must reference {{topic_slug}} context variable"
    )


def test_code_tracer_prompt_references_output_dir():
    """code-tracer prompt must reference {{output_dir}} context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "output_dir" in prompt, (
        "code-tracer prompt must reference {{output_dir}} context variable"
    )


def test_behavior_observer_prompt_references_topic():
    """behavior-observer prompt must reference {{topic_name}} and {{topic_slug}} context variables."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "topic_name" in prompt, (
        "behavior-observer prompt must reference {{topic_name}} context variable"
    )
    assert "topic_slug" in prompt, (
        "behavior-observer prompt must reference {{topic_slug}} context variable"
    )


def test_behavior_observer_prompt_references_output_dir():
    """behavior-observer prompt must reference {{output_dir}} context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "output_dir" in prompt, (
        "behavior-observer prompt must reference {{output_dir}} context variable"
    )


def test_integration_mapper_prompt_references_topic():
    """integration-mapper prompt must reference {{topic_name}} and {{topic_slug}} context variables."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "topic_name" in prompt, (
        "integration-mapper prompt must reference {{topic_name}} context variable"
    )
    assert "topic_slug" in prompt, (
        "integration-mapper prompt must reference {{topic_slug}} context variable"
    )


def test_integration_mapper_prompt_references_output_dir():
    """integration-mapper prompt must reference {{output_dir}} context variable."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None
    prompt = step.get("prompt", "")
    assert "output_dir" in prompt, (
        "integration-mapper prompt must reference {{output_dir}} context variable"
    )


# ---------------------------------------------------------------------------
# Step timeouts and output variables
# ---------------------------------------------------------------------------


def test_code_tracer_timeout():
    """code-tracer step must have timeout=1800."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None
    assert step.get("timeout") == 1800, (
        f"code-tracer timeout must be 1800, got: {step.get('timeout')!r}"
    )


def test_behavior_observer_timeout():
    """behavior-observer step must have timeout=1800."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None
    assert step.get("timeout") == 1800, (
        f"behavior-observer timeout must be 1800, got: {step.get('timeout')!r}"
    )


def test_integration_mapper_timeout():
    """integration-mapper step must have timeout=1800."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None
    assert step.get("timeout") == 1800, (
        f"integration-mapper timeout must be 1800, got: {step.get('timeout')!r}"
    )


def test_code_tracer_output_variable():
    """code-tracer step must have output='code_tracer_result'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "code-tracer")
    assert step is not None
    assert step.get("output") == "code_tracer_result", (
        f"code-tracer output must be 'code_tracer_result', got: {step.get('output')!r}"
    )


def test_behavior_observer_output_variable():
    """behavior-observer step must have output='behavior_observer_result'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "behavior-observer")
    assert step is not None
    assert step.get("output") == "behavior_observer_result", (
        f"behavior-observer output must be 'behavior_observer_result', got: {step.get('output')!r}"
    )


def test_integration_mapper_output_variable():
    """integration-mapper step must have output='integration_mapper_result'."""
    data = _load_recipe()
    step = _get_step_by_id(data, "integration-mapper")
    assert step is not None
    assert step.get("output") == "integration_mapper_result", (
        f"integration-mapper output must be 'integration_mapper_result', got: {step.get('output')!r}"
    )

"""
Tests for recipes/discovery-pipeline.yaml — thin orchestrator structure.

Phase D Task 3: Rewrite as thin orchestrator calling strategy sub-recipes.

Validates:
- File existence and valid YAML parse (2)
- Top-level metadata: name, description, version, author, tags (5)
- Context variables: repo_path, fidelity, output_dir, render_png, strategies (6)
- 3 stages in correct order: scan → strategies → combine (4)
- scan stage: structural-scan step (bash), topic-select step (agent: discovery-prescan),
  approval gate (5)
- strategies stage: run-topdown step with correct sub-recipe and when condition,
  run-bottomup step with correct sub-recipe and when condition (6)
- combine stage: run-combine step with correct sub-recipe, has when condition (3)
- Output dir wiring: strategies write to investigation/topdown and investigation/bottomup,
  combine reads from both (4)
- All referenced sub-recipes exist on disk (3)
- final_output declared (1)

Total: 42 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-pipeline.yaml"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_stages(data: dict) -> list:
    return data.get("stages", [])


def _get_stage_by_name(data: dict, stage_name: str) -> dict | None:
    for stage in _get_stages(data):
        if stage.get("name") == stage_name:
            return stage
    return None


def _get_stage_steps(data: dict, stage_name: str) -> list:
    stage = _get_stage_by_name(data, stage_name)
    if stage is None:
        return []
    return stage.get("steps", [])


def _get_stage_step_by_id(data: dict, stage_name: str, step_id: str) -> dict | None:
    for step in _get_stage_steps(data, stage_name):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/discovery-pipeline.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-pipeline.yaml not found at {RECIPE_PATH}"
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
    """Recipe must have name='discovery-pipeline'."""
    data = _load_recipe()
    assert data.get("name") == "discovery-pipeline", (
        f"Expected name='discovery-pipeline', got: {data.get('name')!r}"
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


def test_recipe_tags_include_discovery_and_pipeline():
    """Recipe tags must include 'discovery' and 'pipeline'."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "pipeline"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (6 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path():
    """Context must declare 'repo_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_fidelity_default_standard():
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


def test_recipe_context_has_strategies():
    """Context must declare 'strategies' variable (new in v2)."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "strategies" in ctx, (
        f"Context must declare 'strategies' variable (new v2 field). "
        f"Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_strategies_default_both():
    """Context 'strategies' variable must default to 'both'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert ctx.get("strategies") == "both", (
        f"strategies default must be 'both', got: {ctx.get('strategies')!r}"
    )


# ---------------------------------------------------------------------------
# Staged structure + stage order (4 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_staged_structure_not_flat():
    """Recipe must use staged structure (stages key), not flat steps."""
    data = _load_recipe()
    assert "stages" in data, "Recipe must have a top-level 'stages' key (staged recipe)"
    assert "steps" not in data, (
        "Recipe must NOT have a top-level 'steps' key — must be staged"
    )
    assert isinstance(data["stages"], list), "stages must be a list"


def test_recipe_has_exactly_3_stages():
    """Recipe must have exactly 3 stages."""
    data = _load_recipe()
    stages = data.get("stages", [])
    assert len(stages) == 3, f"Expected exactly 3 stages, got {len(stages)}"


def test_all_three_stages_exist():
    """Recipe must have stages named 'scan', 'strategies', and 'combine'."""
    data = _load_recipe()
    stage_names = [s.get("name") for s in _get_stages(data)]
    for expected in ["scan", "strategies", "combine"]:
        assert expected in stage_names, (
            f"Stage '{expected}' not found. Stage names: {stage_names}"
        )


def test_stages_are_in_correct_order():
    """Stages must be in order: [scan, strategies, combine]."""
    data = _load_recipe()
    stages = _get_stages(data)
    assert len(stages) == 3, f"Expected 3 stages to check order, got {len(stages)}"
    stage_names = [s.get("name") for s in stages]
    assert stage_names == ["scan", "strategies", "combine"], (
        f"Stages must be in order [scan, strategies, combine], got: {stage_names}"
    )


# ---------------------------------------------------------------------------
# scan stage: steps and approval gate (5 tests)
# ---------------------------------------------------------------------------


def test_scan_stage_has_structural_scan_step():
    """Scan stage must have a step with id='structural-scan'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None, (
        f"No step with id='structural-scan' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


def test_scan_structural_scan_is_bash_type():
    """structural-scan step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None
    assert step.get("type") == "bash", (
        f"structural-scan step must have type='bash', got: {step.get('type')!r}"
    )


def test_scan_stage_has_topic_select_step():
    """Scan stage must have a step with id='topic-select'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None, (
        f"No step with id='topic-select' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


def test_scan_topic_select_uses_discovery_prescan_agent():
    """topic-select step must use the 'dot-graph:discovery-prescan' agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-prescan", (
        f"topic-select must use agent='dot-graph:discovery-prescan', "
        f"got: {step.get('agent')!r}"
    )


def test_scan_stage_has_approval_gate_required():
    """Scan stage must have an approval_gate with required=true."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    assert "approval_gate" in stage, "Scan stage must have an 'approval_gate' field"
    gate = stage["approval_gate"]
    assert gate.get("required") is True, (
        f"approval_gate.required must be true, got: {gate.get('required')!r}"
    )


# ---------------------------------------------------------------------------
# strategies stage: conditional sub-recipe calls (6 tests)
# ---------------------------------------------------------------------------


def test_strategies_stage_has_run_topdown_step():
    """strategies stage must have a step with id='run-topdown'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None, (
        f"No step with id='run-topdown' found in strategies stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'strategies')]}"
    )


def test_strategies_run_topdown_references_strategy_topdown():
    """run-topdown step must reference the strategy-topdown sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "strategy-topdown" in recipe_ref, (
        f"run-topdown must reference strategy-topdown sub-recipe, got: {recipe_ref!r}"
    )


def test_strategies_run_topdown_has_when_condition_referencing_strategies():
    """run-topdown step must have a 'when' condition referencing 'strategies' variable."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    when = str(step.get("when", step.get("condition", "")))
    assert when, "run-topdown step must have a 'when' or 'condition' field"
    assert "strategies" in when or "topdown" in when, (
        f"run-topdown when condition must reference 'strategies' or 'topdown': {when!r}"
    )


def test_strategies_stage_has_run_bottomup_step():
    """strategies stage must have a step with id='run-bottomup'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None, (
        f"No step with id='run-bottomup' found in strategies stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'strategies')]}"
    )


def test_strategies_run_bottomup_references_strategy_bottomup():
    """run-bottomup step must reference the strategy-bottomup sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "strategy-bottomup" in recipe_ref, (
        f"run-bottomup must reference strategy-bottomup sub-recipe, got: {recipe_ref!r}"
    )


def test_strategies_run_bottomup_has_when_condition_referencing_strategies():
    """run-bottomup step must have a 'when' condition referencing 'strategies' variable."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    when = str(step.get("when", step.get("condition", "")))
    assert when, "run-bottomup step must have a 'when' or 'condition' field"
    assert "strategies" in when or "bottomup" in when, (
        f"run-bottomup when condition must reference 'strategies' or 'bottomup': {when!r}"
    )


# ---------------------------------------------------------------------------
# strategies + combine stage: step type='recipe' assertions (3 tests)
# ---------------------------------------------------------------------------


def test_strategies_run_topdown_step_type_is_recipe():
    """run-topdown step must have type='recipe' to invoke the strategy-topdown sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-topdown step must have type='recipe', got: {step.get('type')!r}"
    )


def test_strategies_run_bottomup_step_type_is_recipe():
    """run-bottomup step must have type='recipe' to invoke the strategy-bottomup sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-bottomup step must have type='recipe', got: {step.get('type')!r}"
    )


def test_combine_run_combine_step_type_is_recipe():
    """run-combine step must have type='recipe' to invoke the discovery-combine sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-combine step must have type='recipe', got: {step.get('type')!r}"
    )


# ---------------------------------------------------------------------------
# combine stage: conditional sub-recipe call (3 tests)
# ---------------------------------------------------------------------------


def test_combine_stage_has_run_combine_step():
    """combine stage must have a step with id='run-combine'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None, (
        f"No step with id='run-combine' found in combine stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'combine')]}"
    )


def test_combine_run_combine_references_discovery_combine():
    """run-combine step must reference the discovery-combine sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "discovery-combine" in recipe_ref, (
        f"run-combine must reference discovery-combine sub-recipe, got: {recipe_ref!r}"
    )


def test_combine_run_combine_has_when_condition_referencing_strategies():
    """run-combine step must have a 'when' condition referencing 'strategies' == 'both'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    when = str(step.get("when", step.get("condition", "")))
    assert when, "run-combine step must have a 'when' or 'condition' field"
    assert "strategies" in when or "both" in when, (
        f"run-combine when condition must reference 'strategies' or 'both': {when!r}"
    )


# ---------------------------------------------------------------------------
# Output dir wiring between stages (4 tests)
# ---------------------------------------------------------------------------


def test_run_topdown_output_dir_contains_investigation_topdown():
    """run-topdown step context output_dir must use .../investigation/topdown path."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    ctx = step.get("context", {})
    output_dir_val = str(ctx.get("output_dir", ""))
    assert "topdown" in output_dir_val, (
        f"run-topdown output_dir must reference 'topdown' subpath, "
        f"got: {output_dir_val!r}"
    )


def test_run_bottomup_output_dir_contains_investigation_bottomup():
    """run-bottomup step context output_dir must use .../investigation/bottomup path."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    ctx = step.get("context", {})
    output_dir_val = str(ctx.get("output_dir", ""))
    assert "bottomup" in output_dir_val, (
        f"run-bottomup output_dir must reference 'bottomup' subpath, "
        f"got: {output_dir_val!r}"
    )


def test_combine_step_wires_topdown_dir():
    """run-combine step context must include 'topdown_dir' referencing topdown output."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    ctx = step.get("context", {})
    assert "topdown_dir" in ctx, (
        f"run-combine context must include 'topdown_dir'. Context keys: {list(ctx.keys())}"
    )
    topdown_val = str(ctx["topdown_dir"])
    assert "topdown" in topdown_val, (
        f"run-combine topdown_dir must reference 'topdown' subpath, got: {topdown_val!r}"
    )


def test_combine_step_wires_bottomup_dir():
    """run-combine step context must include 'bottomup_dir' referencing bottomup output."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    ctx = step.get("context", {})
    assert "bottomup_dir" in ctx, (
        f"run-combine context must include 'bottomup_dir'. Context keys: {list(ctx.keys())}"
    )
    bottomup_val = str(ctx["bottomup_dir"])
    assert "bottomup" in bottomup_val, (
        f"run-combine bottomup_dir must reference 'bottomup' subpath, got: {bottomup_val!r}"
    )


# ---------------------------------------------------------------------------
# All referenced sub-recipes exist on disk (3 tests)
# ---------------------------------------------------------------------------


def test_strategy_topdown_sub_recipe_exists():
    """Sub-recipe file strategy-topdown.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-topdown.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-topdown.yaml not found at {sub_recipe}"
    )


def test_strategy_bottomup_sub_recipe_exists():
    """Sub-recipe file strategy-bottomup.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-bottomup.yaml not found at {sub_recipe}"
    )


def test_discovery_combine_sub_recipe_exists():
    """Sub-recipe file discovery-combine.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-combine.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-combine.yaml not found at {sub_recipe}"
    )


# ---------------------------------------------------------------------------
# final_output declared (1 test)
# ---------------------------------------------------------------------------


def test_recipe_has_final_output():
    """Recipe must declare final_output for consistency with peer recipes."""
    data = _load_recipe()
    final_output = data.get("final_output", "")
    assert final_output == "combine_result", (
        f"final_output must be 'combine_result', got: {final_output!r}"
    )

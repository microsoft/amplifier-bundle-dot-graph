"""
Tests for recipes/strategy-sequential.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, output_dir default, fidelity default,
  render_png default (4 tests)
- Staged structure with exactly 3 stages (2 tests)
- Stage names in correct order: bottomup, topdown, combine (4 tests)
- Approval gate on bottomup stage only (2 tests)
- bottomup stage: run-bottomup step, type=recipe, strategy-bottomup reference (3 tests)
- topdown stage: run-topdown step, type=recipe, strategy-topdown reference (3 tests)
- topdown stage context includes bottomup_context variable (1 test)
- combine stage: run-combine step, type=recipe, discovery-combine reference (3 tests)
- Output dir paths wired correctly between stages (4 tests)
- Sub-recipe files exist on disk: strategy-bottomup, strategy-topdown,
  discovery-combine (3 tests)

Total: 36 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-sequential.yaml"


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
    """recipes/strategy-sequential.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/strategy-sequential.yaml not found at {RECIPE_PATH}"
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
    """Recipe must have name='strategy-sequential'."""
    data = _load_recipe()
    assert data.get("name") == "strategy-sequential", (
        f"Expected name='strategy-sequential', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, strategy, sequential, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "strategy", "sequential", "dot-graph"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (4 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path():
    """Context must declare 'repo_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_output_dir_with_default():
    """Context must declare 'output_dir' variable with a non-empty default."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
    )
    assert ctx["output_dir"], (
        f"output_dir must have a non-empty default value, got: {ctx['output_dir']!r}"
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
# Staged structure (2 tests)
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


# ---------------------------------------------------------------------------
# Stage names in correct order (3 tests)
# ---------------------------------------------------------------------------


def test_stage_bottomup_exists():
    """Must have a stage named 'bottomup'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "bottomup")
    assert stage is not None, (
        f"No stage named 'bottomup' found. Stage names: "
        f"{[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_topdown_exists():
    """Must have a stage named 'topdown'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "topdown")
    assert stage is not None, (
        f"No stage named 'topdown' found. Stage names: "
        f"{[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_combine_exists():
    """Must have a stage named 'combine'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "combine")
    assert stage is not None, (
        f"No stage named 'combine' found. Stage names: "
        f"{[s.get('name') for s in _get_stages(data)]}"
    )


def test_stages_are_in_correct_order():
    """Stages must be in order: [bottomup, topdown, combine]."""
    data = _load_recipe()
    stages = _get_stages(data)
    assert len(stages) == 3, f"Expected 3 stages to check order, got {len(stages)}"
    stage_names = [s.get("name") for s in stages]
    assert stage_names == ["bottomup", "topdown", "combine"], (
        f"Stages must be in order [bottomup, topdown, combine], got: {stage_names}"
    )


# ---------------------------------------------------------------------------
# Approval gate on bottomup stage only (2 tests)
# ---------------------------------------------------------------------------


def test_bottomup_stage_has_approval_gate():
    """bottomup stage must have an approval_gate (human review before top-down)."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "bottomup")
    assert stage is not None
    assert "approval_gate" in stage, (
        "bottomup stage must have an 'approval_gate' — human reviews bottom-up "
        "results before top-down investigation begins"
    )
    gate = stage["approval_gate"]
    assert gate.get("required") is True, (
        f"approval_gate must have required=true to block execution until approved, "
        f"got: {gate.get('required')!r}"
    )


def test_topdown_and_combine_stages_have_no_approval_gate():
    """topdown and combine stages must NOT have approval gates."""
    data = _load_recipe()
    for stage_name in ["topdown", "combine"]:
        stage = _get_stage_by_name(data, stage_name)
        assert stage is not None, f"Stage '{stage_name}' not found"
        assert "approval_gate" not in stage, (
            f"Stage '{stage_name}' must NOT have an 'approval_gate' — "
            "only bottomup stage has an approval gate"
        )


# ---------------------------------------------------------------------------
# bottomup stage: sub-recipe call (3 tests)
# ---------------------------------------------------------------------------


def test_bottomup_stage_has_run_bottomup_step():
    """bottomup stage must have a step with id='run-bottomup'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "bottomup", "run-bottomup")
    assert step is not None, (
        f"No step with id='run-bottomup' found in bottomup stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'bottomup')]}"
    )


def test_bottomup_run_bottomup_step_type_is_recipe():
    """run-bottomup step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "bottomup", "run-bottomup")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-bottomup step must have type='recipe', got: {step.get('type')!r}"
    )


def test_bottomup_run_bottomup_references_strategy_bottomup():
    """run-bottomup step must reference the strategy-bottomup sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "bottomup", "run-bottomup")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "strategy-bottomup" in recipe_ref, (
        f"run-bottomup must reference strategy-bottomup sub-recipe, got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# topdown stage: sub-recipe call (3 tests)
# ---------------------------------------------------------------------------


def test_topdown_stage_has_run_topdown_step():
    """topdown stage must have a step with id='run-topdown'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "topdown", "run-topdown")
    assert step is not None, (
        f"No step with id='run-topdown' found in topdown stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'topdown')]}"
    )


def test_topdown_run_topdown_step_type_is_recipe():
    """run-topdown step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "topdown", "run-topdown")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-topdown step must have type='recipe', got: {step.get('type')!r}"
    )


def test_topdown_run_topdown_references_strategy_topdown():
    """run-topdown step must reference the strategy-topdown sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "topdown", "run-topdown")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "strategy-topdown" in recipe_ref, (
        f"run-topdown must reference strategy-topdown sub-recipe, got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# topdown stage context includes bottomup_context (1 test)
# ---------------------------------------------------------------------------


def test_topdown_step_context_includes_bottomup_context():
    """run-topdown step context must include 'bottomup_context' variable pointing to
    the bottomup output directory so the top-down investigation can leverage it."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "topdown", "run-topdown")
    assert step is not None
    ctx = step.get("context", {})
    assert "bottomup_context" in ctx, (
        f"run-topdown step context must include 'bottomup_context'. "
        f"Context keys: {list(ctx.keys())}"
    )
    bottomup_ctx_val = str(ctx["bottomup_context"])
    assert "bottomup" in bottomup_ctx_val, (
        f"bottomup_context value must reference the bottomup output dir, "
        f"got: {bottomup_ctx_val!r}"
    )


# ---------------------------------------------------------------------------
# combine stage: sub-recipe call (3 tests)
# ---------------------------------------------------------------------------


def test_combine_stage_has_run_combine_step():
    """combine stage must have a step with id='run-combine'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None, (
        f"No step with id='run-combine' found in combine stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'combine')]}"
    )


def test_combine_run_combine_step_type_is_recipe():
    """run-combine step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-combine step must have type='recipe', got: {step.get('type')!r}"
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


# ---------------------------------------------------------------------------
# Output dir paths wired correctly between stages (4 tests)
# ---------------------------------------------------------------------------


def test_bottomup_step_output_dir_uses_investigation_bottomup():
    """run-bottomup step context output_dir must use .../investigation/bottomup path."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "bottomup", "run-bottomup")
    assert step is not None
    ctx = step.get("context", {})
    output_dir_val = str(ctx.get("output_dir", ""))
    assert "bottomup" in output_dir_val, (
        f"run-bottomup output_dir must reference 'bottomup' subpath, "
        f"got: {output_dir_val!r}"
    )


def test_topdown_step_output_dir_uses_investigation_topdown():
    """run-topdown step context output_dir must use .../investigation/topdown path."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "topdown", "run-topdown")
    assert step is not None
    ctx = step.get("context", {})
    output_dir_val = str(ctx.get("output_dir", ""))
    assert "topdown" in output_dir_val, (
        f"run-topdown output_dir must reference 'topdown' subpath, "
        f"got: {output_dir_val!r}"
    )


def test_combine_step_wires_topdown_dir_correctly():
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


def test_combine_step_wires_bottomup_dir_correctly():
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
# Sub-recipe files exist on disk (3 tests)
# ---------------------------------------------------------------------------


def test_strategy_bottomup_sub_recipe_exists():
    """Sub-recipe file strategy-bottomup.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-bottomup.yaml not found at {sub_recipe}"
    )


def test_strategy_topdown_sub_recipe_exists():
    """Sub-recipe file strategy-topdown.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-topdown.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-topdown.yaml not found at {sub_recipe}"
    )


def test_discovery_combine_sub_recipe_exists():
    """Sub-recipe file discovery-combine.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-combine.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-combine.yaml not found at {sub_recipe}"
    )

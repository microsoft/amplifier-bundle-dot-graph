"""
Tests for recipes/strategy-bottomup.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, output_dir, fidelity default, output_dir 'bottomup' (4 tests)
- Staged structure with exactly 3 stages (2 tests)
- Stage names: scan-and-plan, traverse, assemble (3 tests)
- scan-and-plan stage: prescan bash step, compute-traversal bash step, traversal plan output (3 tests)
- traverse stage: foreach over post_order, synthesize-level reference, type='recipe' (3 tests)
- assemble stage: identify-subsystems, subsystem-synthesis, overview-synthesis, update-metadata (4 tests)
- Sub-recipe files exist on disk: synthesize-level.yaml, synthesize-subsystem.yaml, synthesize-overview.yaml (3 tests)
- traversal-plan.json documentation: recipe must mention traversal-plan.json (1 test)

Total: 30 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"


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


def _get_full_yaml_text() -> str:
    """Return the raw YAML text of the recipe file."""
    return RECIPE_PATH.read_text()


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/strategy-bottomup.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/strategy-bottomup.yaml not found at {RECIPE_PATH}"
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
    """Recipe must have name='strategy-bottomup'."""
    data = _load_recipe()
    assert data.get("name") == "strategy-bottomup", (
        f"Expected name='strategy-bottomup', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, strategy, bottom-up, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "strategy", "bottom-up", "dot-graph"]:
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


def test_recipe_context_has_output_dir():
    """Context must declare 'output_dir' variable with a default value."""
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


def test_recipe_context_output_dir_references_bottomup():
    """Context output_dir default must reference 'bottomup' in its path."""
    data = _load_recipe()
    ctx = data.get("context", {})
    output_dir = str(ctx.get("output_dir", ""))
    assert "bottomup" in output_dir, (
        f"output_dir default must reference 'bottomup', got: {output_dir!r}"
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
# Stage names (3 tests)
# ---------------------------------------------------------------------------


def test_stage_scan_and_plan_exists():
    """Must have a stage named 'scan-and-plan'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan-and-plan")
    assert stage is not None, (
        f"No stage named 'scan-and-plan' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_traverse_exists():
    """Must have a stage named 'traverse'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "traverse")
    assert stage is not None, (
        f"No stage named 'traverse' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_assemble_exists():
    """Must have a stage named 'assemble'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "assemble")
    assert stage is not None, (
        f"No stage named 'assemble' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


# ---------------------------------------------------------------------------
# scan-and-plan stage (3 tests)
# ---------------------------------------------------------------------------


def test_scan_and_plan_has_prescan_bash_step():
    """scan-and-plan stage must have a bash step for prescan."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "scan-and-plan")
    bash_steps = [s for s in steps if s.get("type") == "bash"]
    assert len(bash_steps) > 0, (
        f"scan-and-plan stage must have at least one bash step for prescan. "
        f"Step IDs: {[s.get('id') for s in steps]}"
    )
    # At least one bash step should relate to prescan/scanning
    prescan_steps = [
        s
        for s in bash_steps
        if "prescan" in str(s.get("id", "")).lower()
        or "scan" in str(s.get("id", "")).lower()
    ]
    assert len(prescan_steps) > 0, (
        f"scan-and-plan stage must have a bash step with 'scan' or 'prescan' in its id. "
        f"Bash step IDs: {[s.get('id') for s in bash_steps]}"
    )


def test_scan_and_plan_has_compute_traversal_bash_step():
    """scan-and-plan stage must have a bash step with id='compute-traversal'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan-and-plan", "compute-traversal")
    assert step is not None, (
        f"No step with id='compute-traversal' found in scan-and-plan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan-and-plan')]}"
    )
    assert step.get("type") == "bash", (
        f"compute-traversal step must be type='bash', got: {step.get('type')!r}"
    )


def test_compute_traversal_output_references_traversal_plan():
    """compute-traversal step output must reference the traversal plan."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan-and-plan", "compute-traversal")
    assert step is not None, "compute-traversal step must exist in scan-and-plan stage"
    # The output key or command should reference the traversal plan
    output_val = str(step.get("output", ""))
    command_val = str(step.get("command", ""))
    assert "traversal" in output_val.lower() or "traversal" in command_val.lower(), (
        f"compute-traversal step must reference a traversal plan in its output or command. "
        f"output={output_val!r}, command snippet={command_val[:100]!r}"
    )


# ---------------------------------------------------------------------------
# traverse stage (3 tests)
# ---------------------------------------------------------------------------


def test_traverse_stage_has_foreach_over_post_order():
    """traverse stage must have a step with foreach iterating over post_order list."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "traverse")
    foreach_steps = [s for s in steps if "foreach" in s]
    assert len(foreach_steps) > 0, (
        f"traverse stage must have a step with 'foreach'. "
        f"Step IDs: {[s.get('id') for s in steps]}"
    )
    foreach_val = str(foreach_steps[0]["foreach"])
    assert "post_order" in foreach_val, (
        f"traverse foreach must iterate over post_order list, got: {foreach_val!r}"
    )


def test_traverse_stage_references_synthesize_level():
    """traverse stage must reference the synthesize-level sub-recipe."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "traverse")
    recipe_steps = [s for s in steps if "recipe" in s]
    assert len(recipe_steps) > 0, (
        "traverse stage must have a step with a 'recipe' reference"
    )
    recipe_ref = str(recipe_steps[0].get("recipe", ""))
    assert "synthesize-level" in recipe_ref, (
        f"traverse step must reference synthesize-level sub-recipe, got: {recipe_ref!r}"
    )


def test_traverse_foreach_step_type_is_recipe():
    """traverse foreach step must have type='recipe'."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "traverse")
    foreach_steps = [s for s in steps if "foreach" in s]
    assert len(foreach_steps) > 0, "traverse stage must have a foreach step"
    step = foreach_steps[0]
    assert step.get("type") == "recipe", (
        f"traverse foreach step must have type='recipe', got: {step.get('type')!r}"
    )


# ---------------------------------------------------------------------------
# assemble stage (4 tests)
# ---------------------------------------------------------------------------


def test_assemble_has_identify_subsystems_bash_step():
    """assemble stage must have a bash step with id='identify-subsystems'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "identify-subsystems")
    assert step is not None, (
        f"No step with id='identify-subsystems' found in assemble stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'assemble')]}"
    )
    assert step.get("type") == "bash", (
        f"identify-subsystems step must be type='bash', got: {step.get('type')!r}"
    )


def test_assemble_has_subsystem_synthesis_step_referencing_synthesize_subsystem():
    """assemble stage must have a step referencing synthesize-subsystem sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "subsystem-synthesis")
    assert step is not None, (
        f"No step with id='subsystem-synthesis' found in assemble stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'assemble')]}"
    )
    recipe_ref = step.get("recipe", "")
    assert "synthesize-subsystem" in recipe_ref, (
        f"subsystem-synthesis step must reference synthesize-subsystem sub-recipe, "
        f"got: {recipe_ref!r}"
    )


def test_assemble_has_overview_synthesis_step_referencing_synthesize_overview():
    """assemble stage must have a step referencing synthesize-overview sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "overview-synthesis")
    assert step is not None, (
        f"No step with id='overview-synthesis' found in assemble stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'assemble')]}"
    )
    recipe_ref = step.get("recipe", "")
    assert "synthesize-overview" in recipe_ref, (
        f"overview-synthesis step must reference synthesize-overview sub-recipe, "
        f"got: {recipe_ref!r}"
    )


def test_assemble_has_update_metadata_step():
    """assemble stage must have a step with id='update-metadata'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "update-metadata")
    assert step is not None, (
        f"No step with id='update-metadata' found in assemble stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'assemble')]}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe files exist on disk (3 tests)
# ---------------------------------------------------------------------------


def test_synthesize_level_sub_recipe_exists():
    """Sub-recipe file synthesize-level.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-level.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe synthesize-level.yaml not found at {sub_recipe}"
    )


def test_synthesize_subsystem_sub_recipe_exists():
    """Sub-recipe file synthesize-subsystem.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-subsystem.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe synthesize-subsystem.yaml not found at {sub_recipe}"
    )


def test_synthesize_overview_sub_recipe_exists():
    """Sub-recipe file synthesize-overview.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-overview.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe synthesize-overview.yaml not found at {sub_recipe}"
    )


# ---------------------------------------------------------------------------
# traversal-plan.json documentation (1 test)
# ---------------------------------------------------------------------------


def test_recipe_mentions_traversal_plan_json():
    """Recipe YAML must mention traversal-plan.json as a mutable state file."""
    text = _get_full_yaml_text()
    assert "traversal-plan.json" in text, (
        "Recipe must mention 'traversal-plan.json' as a mutable state file "
        "(used by compute-traversal and traverse stages)"
    )

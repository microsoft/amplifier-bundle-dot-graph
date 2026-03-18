"""
Tests for recipes/strategy-topdown.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, output_dir default, fidelity default, output_dir 'topdown' (4 tests)
- Staged structure with exactly 3 stages (2 tests)
- Stage names: scan, investigate, synthesize (3 tests)
- Scan stage steps: structural-scan, topic-select, agent, output, no approval gate (5 tests)
- Investigate stage: step exists, foreach, sub-recipe reference, type='recipe' (4 tests)
- Synthesize stage steps: step existence, foreach, type, and sub-recipe references (8 tests)
- Sub-recipe files exist on disk (5 tests)

Total: 38 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-topdown.yaml"


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
    """recipes/strategy-topdown.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/strategy-topdown.yaml not found at {RECIPE_PATH}"
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
    """Recipe must have name='strategy-topdown'."""
    data = _load_recipe()
    assert data.get("name") == "strategy-topdown", (
        f"Expected name='strategy-topdown', got: {data.get('name')!r}"
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
    """Recipe tags must include discovery, strategy, top-down, dot-graph."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "strategy", "top-down", "dot-graph"]:
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


def test_recipe_context_output_dir_references_topdown():
    """Context output_dir default must reference 'topdown' in its path."""
    data = _load_recipe()
    ctx = data.get("context", {})
    output_dir = str(ctx.get("output_dir", ""))
    assert "topdown" in output_dir, (
        f"output_dir default must reference 'topdown', got: {output_dir!r}"
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


def test_stage_scan_exists():
    """Must have a stage named 'scan'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None, (
        f"No stage named 'scan' found. Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_investigate_exists():
    """Must have a stage named 'investigate'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "investigate")
    assert stage is not None, (
        f"No stage named 'investigate' found. Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_synthesize_exists():
    """Must have a stage named 'synthesize'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "synthesize")
    assert stage is not None, (
        f"No stage named 'synthesize' found. Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


# ---------------------------------------------------------------------------
# Scan stage steps (5 tests)
# ---------------------------------------------------------------------------


def test_scan_step_structural_scan_exists():
    """Scan stage must have a step with id='structural-scan'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None, (
        f"No step with id='structural-scan' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


def test_scan_step_topic_select_exists():
    """Scan stage must have a step with id='topic-select'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None, (
        f"No step with id='topic-select' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


def test_topic_select_uses_agent_discovery_prescan():
    """topic-select step must use the 'dot-graph:discovery-prescan' agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-prescan", (
        f"topic-select must use agent='dot-graph:discovery-prescan', got: {step.get('agent')!r}"
    )


def test_topic_select_output_is_topics():
    """topic-select step must have output='topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("output") == "topics", (
        f"topic-select output must be 'topics', got: {step.get('output')!r}"
    )


def test_scan_stage_has_no_approval_gate():
    """Scan stage must NOT have an approval_gate (strategy-topdown is unattended)."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    assert "approval_gate" not in stage, (
        "Scan stage must NOT have an 'approval_gate' — strategy-topdown runs unattended"
    )


# ---------------------------------------------------------------------------
# Investigate stage (4 tests)
# ---------------------------------------------------------------------------


def test_investigate_stage_has_investigate_topics_step():
    """Investigate stage must have a step for iterating over topics."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    assert len(steps) > 0, (
        "Investigate stage must have at least one step for topic investigation"
    )
    # Check that at least one step has a foreach iterating over topics
    foreach_steps = [s for s in steps if "foreach" in s]
    assert len(foreach_steps) > 0, (
        f"Investigate stage must have a step with 'foreach'. "
        f"Step IDs: {[s.get('id') for s in steps]}"
    )


def test_investigate_topics_has_foreach():
    """Investigate stage must have a step with foreach iteration over topics."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    foreach_steps = [s for s in steps if "foreach" in s]
    assert len(foreach_steps) > 0, (
        "Investigate stage must have a step with 'foreach' for iteration over topics"
    )
    foreach_val = str(foreach_steps[0]["foreach"])
    assert "topics" in foreach_val, (
        f"investigate foreach must iterate over topics: {foreach_val!r}"
    )


def test_investigate_references_discovery_investigate_topic():
    """Investigate step must reference the discovery-investigate-topic sub-recipe."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    recipe_steps = [s for s in steps if "recipe" in s]
    assert len(recipe_steps) > 0, (
        "Investigate stage must have a step with a 'recipe' reference"
    )
    recipe_ref = str(recipe_steps[0].get("recipe", ""))
    assert "discovery-investigate-topic" in recipe_ref, (
        f"Investigate step must reference discovery-investigate-topic sub-recipe, got: {recipe_ref!r}"
    )


def test_investigate_step_type_is_recipe():
    """Investigate foreach step must have type='recipe'."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    foreach_steps = [s for s in steps if "foreach" in s]
    assert len(foreach_steps) > 0, "Investigate stage must have a foreach step"
    step = foreach_steps[0]
    assert step.get("type") == "recipe", (
        f"Investigate foreach step must have type='recipe', got: {step.get('type')!r}"
    )


# ---------------------------------------------------------------------------
# Synthesize stage steps (8 tests)
# ---------------------------------------------------------------------------


def test_synthesize_step_reconcile_modules_exists():
    """Synthesize stage must have a step with id='reconcile-modules'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None, (
        f"No step with id='reconcile-modules' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_step_subsystem_synthesis_exists():
    """Synthesize stage must have a step with id='subsystem-synthesis'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "subsystem-synthesis")
    assert step is not None, (
        f"No step with id='subsystem-synthesis' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_step_overview_synthesis_exists():
    """Synthesize stage must have a step with id='overview-synthesis'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "overview-synthesis")
    assert step is not None, (
        f"No step with id='overview-synthesis' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_reconcile_modules_has_foreach():
    """reconcile-modules step must have foreach iteration over topics."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    assert "foreach" in step, (
        "reconcile-modules step must have 'foreach' for iteration over topics"
    )
    foreach_val = str(step["foreach"])
    assert "topics" in foreach_val, (
        f"reconcile-modules foreach must iterate over topics: {foreach_val!r}"
    )


def test_reconcile_modules_is_recipe_type():
    """reconcile-modules step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"reconcile-modules step must have type='recipe', got: {step.get('type')!r}"
    )


def test_reconcile_modules_references_discovery_synthesize_module():
    """reconcile-modules step must reference the discovery-synthesize-module sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "discovery-synthesize-module" in recipe_ref, (
        f"reconcile-modules must reference discovery-synthesize-module sub-recipe, got: {recipe_ref!r}"
    )


def test_subsystem_synthesis_references_synthesize_subsystem():
    """subsystem-synthesis step must reference the synthesize-subsystem sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "subsystem-synthesis")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "synthesize-subsystem" in recipe_ref, (
        f"subsystem-synthesis must reference synthesize-subsystem sub-recipe, got: {recipe_ref!r}"
    )


def test_overview_synthesis_references_synthesize_overview():
    """overview-synthesis step must reference the synthesize-overview sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "overview-synthesis")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "synthesize-overview" in recipe_ref, (
        f"overview-synthesis must reference synthesize-overview sub-recipe, got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe files exist on disk (5 tests)
# ---------------------------------------------------------------------------


def test_discovery_investigate_topic_sub_recipe_exists():
    """Sub-recipe file discovery-investigate-topic.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-investigate-topic.yaml not found at {sub_recipe}"
    )


def test_discovery_synthesize_module_sub_recipe_exists():
    """Sub-recipe file discovery-synthesize-module.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-synthesize-module.yaml not found at {sub_recipe}"
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


def test_synthesize_level_sub_recipe_exists():
    """Sub-recipe file synthesize-level.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-level.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe synthesize-level.yaml not found at {sub_recipe}"
    )

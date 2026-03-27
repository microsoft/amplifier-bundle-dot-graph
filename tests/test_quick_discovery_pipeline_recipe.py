"""
Tests for recipes/quick/discovery-pipeline.yaml — quick pipeline structure.

Task 6: Write the quick pipeline recipe (fresh, using v1 as reference).

Validates:
- File existence at recipes/quick/discovery-pipeline.yaml and valid YAML parse (2)
- Top-level metadata: name, description, version, author, tags (5)
- Context variables: repo_path, fidelity, output_dir, render_png, node_target (5)
- 3 stages in correct order: scan → investigate → synthesize (4)
- scan stage: change-detect step (bash), structural-scan step (bash),
  topic-select step (agent: discovery-prescan), approval gate with required=true (5)
- investigate stage: prepare-topics step, investigate-topics (foreach, shared sub-recipe) (4)
- synthesize stage: reconcile-modules (shared sub-recipe), assemble, validate,
  hoist-outputs, summarize (agent: discovery-architecture-writer), update-metadata (7)
- Shared sub-recipe references (NOT quick/) (2)
- final_output declared (1)

Total: 35 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "quick" / "discovery-pipeline.yaml"


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
    """recipes/quick/discovery-pipeline.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/quick/discovery-pipeline.yaml not found at {RECIPE_PATH}"
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
    """Recipe must have name='quick-discovery-pipeline'."""
    data = _load_recipe()
    assert data.get("name") == "quick-discovery-pipeline", (
        f"Expected name='quick-discovery-pipeline', got: {data.get('name')!r}"
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


def test_recipe_tags_include_discovery_pipeline_quick():
    """Recipe tags must include 'discovery', 'pipeline', and 'quick'."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "pipeline", "quick"]:
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


def test_recipe_context_node_target_default_25():
    """Context must declare 'node_target' variable with default 25."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "node_target" in ctx, (
        f"Context must declare 'node_target' variable. Found keys: {list(ctx.keys())}"
    )
    assert str(ctx["node_target"]) == "25", (
        f"node_target default must be 25, got: {ctx['node_target']!r}"
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
    """Recipe must have stages named 'scan', 'investigate', and 'synthesize'."""
    data = _load_recipe()
    stage_names = [s.get("name") for s in _get_stages(data)]
    for expected in ["scan", "investigate", "synthesize"]:
        assert expected in stage_names, (
            f"Stage '{expected}' not found. Stage names: {stage_names}"
        )


def test_stages_are_in_correct_order():
    """Stages must be in order: [scan, investigate, synthesize]."""
    data = _load_recipe()
    stages = _get_stages(data)
    assert len(stages) == 3, f"Expected 3 stages to check order, got {len(stages)}"
    stage_names = [s.get("name") for s in stages]
    assert stage_names == ["scan", "investigate", "synthesize"], (
        f"Stages must be in order [scan, investigate, synthesize], got: {stage_names}"
    )


# ---------------------------------------------------------------------------
# scan stage: steps and approval gate (5 tests)
# ---------------------------------------------------------------------------


def test_scan_stage_has_change_detect_step():
    """Scan stage must have a step with id='change-detect'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "change-detect")
    assert step is not None, (
        f"No step with id='change-detect' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


def test_scan_stage_has_structural_scan_step():
    """Scan stage must have a step with id='structural-scan'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None, (
        f"No step with id='structural-scan' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
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
# investigate stage: prepare-topics + foreach investigate-topics (4 tests)
# ---------------------------------------------------------------------------


def test_investigate_stage_has_prepare_topics_step():
    """investigate stage must have a step with id='prepare-topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "prepare-topics")
    assert step is not None, (
        f"No step with id='prepare-topics' found in investigate stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'investigate')]}"
    )


def test_investigate_stage_has_investigate_topics_step():
    """investigate stage must have a step with id='investigate-topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None, (
        f"No step with id='investigate-topics' found in investigate stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'investigate')]}"
    )


def test_investigate_topics_is_foreach():
    """investigate-topics step must use foreach iteration."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    assert "foreach" in step, (
        "investigate-topics step must have a 'foreach' field for per-topic iteration"
    )


def test_investigate_topics_references_shared_sub_recipe_not_quick():
    """investigate-topics must reference shared @dot-graph:recipes/discovery-investigate-topic.yaml, NOT quick/."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "discovery-investigate-topic" in recipe_ref, (
        f"investigate-topics must reference discovery-investigate-topic sub-recipe, got: {recipe_ref!r}"
    )
    assert "quick/" not in recipe_ref, (
        f"investigate-topics must reference SHARED sub-recipe (not quick/), got: {recipe_ref!r}"
    )
    assert recipe_ref == "@dot-graph:recipes/discovery-investigate-topic.yaml", (
        f"investigate-topics recipe must be '@dot-graph:recipes/discovery-investigate-topic.yaml', "
        f"got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# synthesize stage: 6 required steps (7 tests)
# ---------------------------------------------------------------------------


def test_synthesize_stage_has_reconcile_modules_step():
    """synthesize stage must have a step with id='reconcile-modules'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None, (
        f"No step with id='reconcile-modules' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_reconcile_modules_references_shared_sub_recipe_not_quick():
    """reconcile-modules must reference shared @dot-graph:recipes/discovery-synthesize-module.yaml, NOT quick/."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "discovery-synthesize-module" in recipe_ref, (
        f"reconcile-modules must reference discovery-synthesize-module sub-recipe, got: {recipe_ref!r}"
    )
    assert "quick/" not in recipe_ref, (
        f"reconcile-modules must reference SHARED sub-recipe (not quick/), got: {recipe_ref!r}"
    )
    assert recipe_ref == "@dot-graph:recipes/discovery-synthesize-module.yaml", (
        f"reconcile-modules recipe must be '@dot-graph:recipes/discovery-synthesize-module.yaml', "
        f"got: {recipe_ref!r}"
    )


def test_synthesize_stage_has_assemble_step():
    """synthesize stage must have a step with id='assemble'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "assemble")
    assert step is not None, (
        f"No step with id='assemble' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_stage_has_validate_step():
    """synthesize stage must have a step with id='validate'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "validate")
    assert step is not None, (
        f"No step with id='validate' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_stage_has_hoist_outputs_step():
    """synthesize stage must have a step with id='hoist-outputs'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "hoist-outputs")
    assert step is not None, (
        f"No step with id='hoist-outputs' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_stage_has_summarize_step():
    """synthesize stage must have a step with id='summarize'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "summarize")
    assert step is not None, (
        f"No step with id='summarize' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_summarize_uses_discovery_architecture_writer_agent():
    """summarize step must use the 'dot-graph:discovery-architecture-writer' agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "summarize")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-architecture-writer", (
        f"summarize must use agent='dot-graph:discovery-architecture-writer', "
        f"got: {step.get('agent')!r}"
    )


def test_synthesize_stage_has_update_metadata_step():
    """synthesize stage must have a step with id='update-metadata'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "update-metadata")
    assert step is not None, (
        f"No step with id='update-metadata' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


# ---------------------------------------------------------------------------
# Shared sub-recipe files exist on disk (2 tests)
# ---------------------------------------------------------------------------


def test_shared_investigate_topic_sub_recipe_exists():
    """Shared sub-recipe discovery-investigate-topic.yaml must exist at recipes/ root."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"
    assert sub_recipe.exists(), f"Shared sub-recipe not found at {sub_recipe}"


def test_shared_synthesize_module_sub_recipe_exists():
    """Shared sub-recipe discovery-synthesize-module.yaml must exist at recipes/ root."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"
    assert sub_recipe.exists(), f"Shared sub-recipe not found at {sub_recipe}"


# ---------------------------------------------------------------------------
# final_output declared (1 test)
# ---------------------------------------------------------------------------


def test_recipe_has_final_output():
    """Recipe must declare final_output='metadata_result'."""
    data = _load_recipe()
    final_output = data.get("final_output", "")
    assert final_output == "metadata_result", (
        f"final_output must be 'metadata_result', got: {final_output!r}"
    )


# ---------------------------------------------------------------------------
# Parallelism: investigate-topics and reconcile-modules (2 tests)
# ---------------------------------------------------------------------------


def test_investigate_topics_is_parallel():
    """investigate-topics foreach step must have parallel: true for concurrent topic investigation."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None, "investigate-topics step must exist"
    assert step.get("parallel") is True, (
        f"investigate-topics step must have parallel=true for concurrent execution, "
        f"got: {step.get('parallel')!r}"
    )


def test_reconcile_modules_is_parallel():
    """reconcile-modules foreach step must have parallel: true for concurrent synthesis."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None, "reconcile-modules step must exist"
    assert step.get("parallel") is True, (
        f"reconcile-modules step must have parallel=true for concurrent execution, "
        f"got: {step.get('parallel')!r}"
    )


# ---------------------------------------------------------------------------
# write-overview-dot step in synthesize stage (5 regression tests)
# ---------------------------------------------------------------------------


def test_synthesize_stage_has_write_overview_dot_step():
    """synthesize stage must have a step with id='write-overview-dot'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "write-overview-dot")
    assert step is not None, (
        f"No step with id='write-overview-dot' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_write_overview_dot_uses_dot_author_agent():
    """write-overview-dot step must use the 'dot-graph:dot-author' agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "write-overview-dot")
    assert step is not None, "write-overview-dot step must exist"
    assert step.get("agent") == "dot-graph:dot-author", (
        f"write-overview-dot must use agent='dot-graph:dot-author', "
        f"got: {step.get('agent')!r}"
    )


def test_write_overview_dot_prompt_references_overview_dot_filename():
    """write-overview-dot prompt must reference 'overview.dot' filename."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "write-overview-dot")
    assert step is not None, "write-overview-dot step must exist"
    prompt = step.get("prompt", "")
    assert "overview.dot" in prompt, (
        "write-overview-dot prompt must reference 'overview.dot', "
        "but 'overview.dot' not found in prompt"
    )


def test_write_overview_dot_comes_after_summarize():
    """write-overview-dot step must appear after the summarize step."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "synthesize")
    step_ids = [s.get("id") for s in steps]
    assert "write-overview-dot" in step_ids, (
        f"'write-overview-dot' not found in synthesize stage steps: {step_ids}"
    )
    assert "summarize" in step_ids, (
        f"'summarize' not found in synthesize stage steps: {step_ids}"
    )
    summarize_idx = step_ids.index("summarize")
    write_dot_idx = step_ids.index("write-overview-dot")
    assert write_dot_idx > summarize_idx, (
        f"'write-overview-dot' (index {write_dot_idx}) must come AFTER "
        f"'summarize' (index {summarize_idx}) in synthesize stage"
    )


def test_write_overview_dot_comes_before_update_metadata():
    """write-overview-dot step must appear before the update-metadata step."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "synthesize")
    step_ids = [s.get("id") for s in steps]
    assert "write-overview-dot" in step_ids, (
        f"'write-overview-dot' not found in synthesize stage steps: {step_ids}"
    )
    assert "update-metadata" in step_ids, (
        f"'update-metadata' not found in synthesize stage steps: {step_ids}"
    )
    write_dot_idx = step_ids.index("write-overview-dot")
    update_metadata_idx = step_ids.index("update-metadata")
    assert write_dot_idx < update_metadata_idx, (
        f"'write-overview-dot' (index {write_dot_idx}) must come BEFORE "
        f"'update-metadata' (index {update_metadata_idx}) in synthesize stage"
    )

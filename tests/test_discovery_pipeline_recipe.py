"""
Tests for recipes/discovery-pipeline.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse
- Top-level metadata (name, description, version, author, tags)
- Context variables (repo_path, fidelity, output_dir, _approval_message)
- fidelity default is 'standard'
- Staged structure (not flat) with exactly 3 stages
- Stage names: scan, investigate, synthesize
- Scan stage has approval gate with required: true
- Scan steps: change-detect, structural-scan, topic-select
- topic-select uses agent 'dot-graph:discovery-prescan'
- Investigate stage has foreach iteration over topics
- Investigate references discovery-investigate-topic sub-recipe
- Synthesize stage has steps: reconcile-modules, assemble, final-validate, update-metadata
- Synthesize references discovery-synthesize-module sub-recipe
- Sub-recipe files exist (discovery-investigate-topic.yaml, discovery-synthesize-module.yaml)
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-pipeline.yaml"


# ---------------------------------------------------------------------------
# File existence and parse
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
# Top-level metadata
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


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


def test_recipe_tags():
    """Recipe tags must include discovery, pipeline, architecture, dot-graph, multi-agent."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in [
        "discovery",
        "pipeline",
        "architecture",
        "dot-graph",
        "multi-agent",
    ]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path():
    """Context must declare 'repo_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path' variable. Found keys: {list(ctx.keys())}"
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


def test_recipe_context_has_approval_message():
    """Context must declare '_approval_message' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "_approval_message" in ctx, (
        f"Context must declare '_approval_message' variable. Found keys: {list(ctx.keys())}"
    )


# ---------------------------------------------------------------------------
# Staged structure
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
# Stage names
# ---------------------------------------------------------------------------


def _get_stages(data: dict) -> list:
    return data.get("stages", [])


def _get_stage_by_name(data: dict, stage_name: str) -> dict | None:
    for stage in _get_stages(data):
        if stage.get("name") == stage_name:
            return stage
    return None


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
# Scan stage: approval gate
# ---------------------------------------------------------------------------


def test_scan_stage_has_approval_gate():
    """Scan stage must have an approval_gate field."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    assert "approval_gate" in stage, "Scan stage must have an 'approval_gate' field"


def test_scan_approval_gate_is_required():
    """Scan stage approval_gate must have required=true."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    gate = stage.get("approval_gate", {})
    assert gate.get("required") is True, (
        f"approval_gate.required must be true, got: {gate.get('required')!r}"
    )


def test_scan_approval_gate_has_prompt():
    """Scan stage approval_gate must have a prompt."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    gate = stage.get("approval_gate", {})
    prompt = gate.get("prompt", "")
    assert isinstance(prompt, str) and prompt.strip(), (
        "approval_gate must have a non-empty prompt"
    )


# ---------------------------------------------------------------------------
# Scan stage: steps
# ---------------------------------------------------------------------------


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


def test_scan_step_change_detect_exists():
    """Scan stage must have a step with id='change-detect'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "change-detect")
    assert step is not None, (
        f"No step with id='change-detect' found in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


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


def test_change_detect_is_bash_type():
    """change-detect step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "change-detect")
    assert step is not None
    assert step.get("type") == "bash", (
        f"change-detect step must have type='bash', got: {step.get('type')!r}"
    )


def test_change_detect_has_parse_json():
    """change-detect step must have parse_json=true."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "change-detect")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"change-detect step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


def test_change_detect_output_variable():
    """change-detect step must have output='change_result'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "change-detect")
    assert step is not None
    assert step.get("output") == "change_result", (
        f"change-detect output must be 'change_result', got: {step.get('output')!r}"
    )


def test_structural_scan_is_bash_type():
    """structural-scan step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None
    assert step.get("type") == "bash", (
        f"structural-scan step must have type='bash', got: {step.get('type')!r}"
    )


def test_structural_scan_has_condition():
    """structural-scan step must have a condition that checks change_result tier."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "structural-scan step must have a condition"
    assert "skip" in condition, (
        f"structural-scan condition must reference 'skip': {condition!r}"
    )


def test_structural_scan_output_variable():
    """structural-scan step must have output='scan_result'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None
    assert step.get("output") == "scan_result", (
        f"structural-scan output must be 'scan_result', got: {step.get('output')!r}"
    )


def test_topic_select_uses_agent():
    """topic-select step must use the 'dot-graph:discovery-prescan' agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-prescan", (
        f"topic-select must use agent='dot-graph:discovery-prescan', got: {step.get('agent')!r}"
    )


def test_topic_select_has_condition():
    """topic-select step must have a condition that checks change_result tier."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "topic-select step must have a condition"
    assert "skip" in condition, (
        f"topic-select condition must reference 'skip': {condition!r}"
    )


def test_topic_select_output_variable():
    """topic-select step must have output='topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("output") == "topics", (
        f"topic-select output must be 'topics', got: {step.get('output')!r}"
    )


def test_topic_select_parse_json():
    """topic-select step must have parse_json=true."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"topic-select step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


# ---------------------------------------------------------------------------
# Investigate stage: steps
# ---------------------------------------------------------------------------


def test_investigate_stage_has_prepare_topics_step():
    """Investigate stage must have a step with id='prepare-topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "prepare-topics")
    assert step is not None, (
        f"No step with id='prepare-topics' found in investigate stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'investigate')]}"
    )


def test_investigate_stage_has_investigate_topics_step():
    """Investigate stage must have a step with id='investigate-topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None, (
        f"No step with id='investigate-topics' found in investigate stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'investigate')]}"
    )


def test_investigate_topics_has_foreach():
    """investigate-topics step must have foreach iteration over topics."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    assert "foreach" in step, (
        "investigate-topics step must have 'foreach' for iteration over topics"
    )
    foreach_val = step["foreach"]
    assert "topics" in str(foreach_val), (
        f"investigate-topics foreach must iterate over topics: {foreach_val!r}"
    )


def test_investigate_topics_references_sub_recipe():
    """investigate-topics step must reference the discovery-investigate-topic sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "discovery-investigate-topic" in recipe_ref, (
        f"investigate-topics must reference discovery-investigate-topic sub-recipe, got: {recipe_ref!r}"
    )


def test_investigate_topics_is_recipe_type():
    """investigate-topics step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"investigate-topics step must have type='recipe', got: {step.get('type')!r}"
    )


# ---------------------------------------------------------------------------
# Synthesize stage: steps
# ---------------------------------------------------------------------------


def test_synthesize_stage_has_reconcile_modules_step():
    """Synthesize stage must have a step with id='reconcile-modules'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None, (
        f"No step with id='reconcile-modules' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_stage_has_assemble_step():
    """Synthesize stage must have a step with id='assemble'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "assemble")
    assert step is not None, (
        f"No step with id='assemble' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_stage_has_final_validate_step():
    """Synthesize stage must have a step with id='final-validate'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "final-validate")
    assert step is not None, (
        f"No step with id='final-validate' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_synthesize_stage_has_update_metadata_step():
    """Synthesize stage must have a step with id='update-metadata'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "update-metadata")
    assert step is not None, (
        f"No step with id='update-metadata' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_reconcile_modules_references_sub_recipe():
    """reconcile-modules step must reference the discovery-synthesize-module sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "discovery-synthesize-module" in recipe_ref, (
        f"reconcile-modules must reference discovery-synthesize-module sub-recipe, got: {recipe_ref!r}"
    )


def test_reconcile_modules_has_foreach():
    """reconcile-modules step must have foreach iteration over topics."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    assert "foreach" in step, (
        "reconcile-modules step must have 'foreach' for iteration over topics"
    )
    foreach_val = step["foreach"]
    assert "topics" in str(foreach_val), (
        f"reconcile-modules foreach must iterate over topics: {foreach_val!r}"
    )


def test_assemble_is_bash_type():
    """assemble step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "assemble")
    assert step is not None
    assert step.get("type") == "bash", (
        f"assemble step must have type='bash', got: {step.get('type')!r}"
    )


def test_assemble_output_variable():
    """assemble step must have output='assemble_result'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "assemble")
    assert step is not None
    assert step.get("output") == "assemble_result", (
        f"assemble output must be 'assemble_result', got: {step.get('output')!r}"
    )


def test_final_validate_is_bash_type():
    """final-validate step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "final-validate")
    assert step is not None
    assert step.get("type") == "bash", (
        f"final-validate step must have type='bash', got: {step.get('type')!r}"
    )


def test_final_validate_output_variable():
    """final-validate step must have output='final_validation'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "final-validate")
    assert step is not None
    assert step.get("output") == "final_validation", (
        f"final-validate output must be 'final_validation', got: {step.get('output')!r}"
    )


def test_update_metadata_is_bash_type():
    """update-metadata step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "update-metadata")
    assert step is not None
    assert step.get("type") == "bash", (
        f"update-metadata step must have type='bash', got: {step.get('type')!r}"
    )


def test_update_metadata_output_variable():
    """update-metadata step must have output='metadata_result'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "update-metadata")
    assert step is not None
    assert step.get("output") == "metadata_result", (
        f"update-metadata output must be 'metadata_result', got: {step.get('output')!r}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe file existence
# ---------------------------------------------------------------------------


def test_investigate_topic_sub_recipe_exists():
    """Sub-recipe file discovery-investigate-topic.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-investigate-topic.yaml not found at {sub_recipe}"
    )


def test_synthesize_module_sub_recipe_exists():
    """Sub-recipe file discovery-synthesize-module.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-synthesize-module.yaml not found at {sub_recipe}"
    )


# ---------------------------------------------------------------------------
# Final output
# ---------------------------------------------------------------------------


def test_recipe_has_final_output():
    """Recipe must declare final_output pointing to metadata_result."""
    data = _load_recipe()
    final_output = data.get("final_output", "")
    assert final_output == "metadata_result", (
        f"final_output must be 'metadata_result', got: {final_output!r}"
    )


# ---------------------------------------------------------------------------
# render_png context variable (Improvement 3)
# ---------------------------------------------------------------------------


def test_recipe_context_has_render_png():
    """Context must declare 'render_png' variable with default 'true'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "render_png" in ctx, (
        f"Context must declare 'render_png' variable. Found keys: {list(ctx.keys())}"
    )
    assert ctx["render_png"] == "true", (
        f"render_png default must be 'true', got: {ctx['render_png']!r}"
    )


def test_synthesize_stage_has_render_graphs_step():
    """Synthesize stage must have a step with id='render-graphs'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "render-graphs")
    assert step is not None, (
        f"No step with id='render-graphs' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_render_graphs_is_bash_type():
    """render-graphs step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "render-graphs")
    assert step is not None
    assert step.get("type") == "bash", (
        f"render-graphs step must have type='bash', got: {step.get('type')!r}"
    )


def test_render_graphs_has_condition_on_render_png():
    """render-graphs step must have a condition referencing render_png."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "render-graphs")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "render-graphs step must have a condition"
    assert "render_png" in condition, (
        f"render-graphs condition must reference 'render_png': {condition!r}"
    )


def test_render_graphs_output_variable():
    """render-graphs step must have output='render_result'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "render-graphs")
    assert step is not None
    assert step.get("output") == "render_result", (
        f"render-graphs output must be 'render_result', got: {step.get('output')!r}"
    )

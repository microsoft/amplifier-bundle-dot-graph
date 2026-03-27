"""
Tests for the C1 Lens/Framing System.

Validates:
- All 5 lens content files exist in context/lenses/
- Each lens file has non-empty content (3+ sentences)
- The complete set of built-in lens names is exactly the 5 expected names
- discovery-investigate-topic.yaml declares `lens` in context
- discovery-investigate-topic.yaml has a `lens-resolver` bash step before agent steps
- All 3 agent prompts reference {{lens_result.guidance}}
- quick pipeline context declares `lens` with default `architecture`
- quick pipeline investigate-topics step passes `lens` to the sub-recipe
- deep pipeline context (discovery-pipeline.yaml) declares `lens` with default `architecture`
- strategy-topdown.yaml context declares `lens` with default `architecture`
- strategy-topdown.yaml investigate-topics step passes `lens` to the sub-recipe
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUILT_IN_LENSES = {"architecture", "security", "quality", "onboarding", "debugging"}

LENSES_DIR = REPO_ROOT / "context" / "lenses"
INVESTIGATE_RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"
QUICK_PIPELINE_PATH = REPO_ROOT / "recipes" / "quick" / "discovery-pipeline.yaml"
DEEP_PIPELINE_PATH = REPO_ROOT / "recipes" / "deep" / "discovery-pipeline.yaml"
TOPDOWN_STRATEGY_PATH = REPO_ROOT / "recipes" / "deep" / "strategy-topdown.yaml"
DISCOVER_RECIPE_PATH = REPO_ROOT / "recipes" / "discover.yaml"

AGENT_STEP_IDS = ["code-tracer", "behavior-observer", "integration-mapper"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


def _get_stage_step_by_id(data: dict, stage_name: str, step_id: str) -> dict | None:
    for stage in data.get("stages", []):
        if stage.get("name") == stage_name:
            for step in stage.get("steps", []):
                if step.get("id") == step_id:
                    return step
    return None


# ---------------------------------------------------------------------------
# Lens file existence and content (10 tests)
# ---------------------------------------------------------------------------


def test_lenses_directory_exists():
    """context/lenses/ directory must exist."""
    assert LENSES_DIR.is_dir(), f"context/lenses/ directory not found at {LENSES_DIR}"


def test_architecture_lens_file_exists():
    """context/lenses/architecture.md must exist."""
    path = LENSES_DIR / "architecture.md"
    assert path.exists(), f"architecture.md not found at {path}"


def test_security_lens_file_exists():
    """context/lenses/security.md must exist."""
    path = LENSES_DIR / "security.md"
    assert path.exists(), f"security.md not found at {path}"


def test_quality_lens_file_exists():
    """context/lenses/quality.md must exist."""
    path = LENSES_DIR / "quality.md"
    assert path.exists(), f"quality.md not found at {path}"


def test_onboarding_lens_file_exists():
    """context/lenses/onboarding.md must exist."""
    path = LENSES_DIR / "onboarding.md"
    assert path.exists(), f"onboarding.md not found at {path}"


def test_debugging_lens_file_exists():
    """context/lenses/debugging.md must exist."""
    path = LENSES_DIR / "debugging.md"
    assert path.exists(), f"debugging.md not found at {path}"


def test_each_lens_file_has_non_empty_content():
    """Every lens file must have non-empty trimmed content."""
    for name in BUILT_IN_LENSES:
        path = LENSES_DIR / f"{name}.md"
        if path.exists():
            content = path.read_text().strip()
            assert content, f"Lens file {name}.md exists but is empty"
            assert len(content) > 50, (
                f"Lens file {name}.md content is too short ({len(content)} chars). "
                "Expected at least 3 sentences of guidance."
            )


def test_complete_set_of_built_in_lenses():
    """The directory must contain exactly the 5 expected built-in lens files (no extras)."""
    if not LENSES_DIR.is_dir():
        return  # existence tested separately
    found = {p.stem for p in LENSES_DIR.glob("*.md")}
    assert found == BUILT_IN_LENSES, (
        f"Expected lens files: {BUILT_IN_LENSES}\n"
        f"Found lens files:    {found}\n"
        f"Missing: {BUILT_IN_LENSES - found}\n"
        f"Unexpected: {found - BUILT_IN_LENSES}"
    )


def test_architecture_lens_contains_architecture_guidance():
    """architecture.md must reference component organization or patterns."""
    path = LENSES_DIR / "architecture.md"
    if not path.exists():
        return
    content = path.read_text().lower()
    assert any(
        kw in content
        for kw in ["component", "architecture", "pattern", "abstraction", "boundary"]
    ), "architecture.md must contain architecture-focused investigation guidance"


def test_security_lens_contains_security_guidance():
    """security.md must reference trust boundaries or attack surfaces."""
    path = LENSES_DIR / "security.md"
    if not path.exists():
        return
    content = path.read_text().lower()
    assert any(
        kw in content
        for kw in [
            "trust",
            "security",
            "boundary",
            "validation",
            "attack",
            "credential",
        ]
    ), "security.md must contain security-focused investigation guidance"


# ---------------------------------------------------------------------------
# investigation recipe: lens context variable and lens-resolver step (5 tests)
# ---------------------------------------------------------------------------


def test_investigate_recipe_context_has_lens():
    """discovery-investigate-topic.yaml context must declare 'lens' variable."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    ctx = data.get("context", {})
    assert "lens" in ctx, (
        f"discovery-investigate-topic.yaml context must declare 'lens'. "
        f"Found keys: {list(ctx.keys())}"
    )


def test_investigate_recipe_lens_default_is_architecture():
    """discovery-investigate-topic.yaml 'lens' context default must be 'architecture'."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    ctx = data.get("context", {})
    assert ctx.get("lens") == "architecture", (
        f"lens default must be 'architecture', got: {ctx.get('lens')!r}"
    )


def test_investigate_recipe_has_lens_resolver_step():
    """discovery-investigate-topic.yaml must have a step with id='lens-resolver'."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    step = _get_step_by_id(data, "lens-resolver")
    assert step is not None, (
        f"No step with id='lens-resolver' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(data)]}"
    )


def test_lens_resolver_step_is_bash_type():
    """lens-resolver step must be type='bash'."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    step = _get_step_by_id(data, "lens-resolver")
    if step is None:
        return  # existence tested separately
    assert step.get("type") == "bash", (
        f"lens-resolver step must be type='bash', got: {step.get('type')!r}"
    )


def test_lens_resolver_step_comes_before_agent_steps():
    """lens-resolver step must appear before all 3 agent steps in the steps list."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    steps = _get_steps(data)
    step_ids = [s.get("id") for s in steps]

    if "lens-resolver" not in step_ids:
        return  # existence tested separately

    resolver_idx = step_ids.index("lens-resolver")
    for agent_id in AGENT_STEP_IDS:
        if agent_id in step_ids:
            agent_idx = step_ids.index(agent_id)
            assert resolver_idx < agent_idx, (
                f"lens-resolver (index {resolver_idx}) must come before "
                f"{agent_id} (index {agent_idx})"
            )


# ---------------------------------------------------------------------------
# investigation recipe: agent prompts reference lens_result.guidance (3 tests)
# ---------------------------------------------------------------------------


def test_code_tracer_prompt_references_lens_guidance():
    """code-tracer prompt must reference lens_result.guidance."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    step = _get_step_by_id(data, "code-tracer")
    if step is None:
        return
    prompt = step.get("prompt", "")
    assert "lens_result.guidance" in prompt, (
        "code-tracer prompt must reference {{lens_result.guidance}} for lens injection"
    )


def test_behavior_observer_prompt_references_lens_guidance():
    """behavior-observer prompt must reference lens_result.guidance."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    step = _get_step_by_id(data, "behavior-observer")
    if step is None:
        return
    prompt = step.get("prompt", "")
    assert "lens_result.guidance" in prompt, (
        "behavior-observer prompt must reference {{lens_result.guidance}} for lens injection"
    )


def test_integration_mapper_prompt_references_lens_guidance():
    """integration-mapper prompt must reference lens_result.guidance."""
    data = _load_yaml(INVESTIGATE_RECIPE_PATH)
    step = _get_step_by_id(data, "integration-mapper")
    if step is None:
        return
    prompt = step.get("prompt", "")
    assert "lens_result.guidance" in prompt, (
        "integration-mapper prompt must reference {{lens_result.guidance}} for lens injection"
    )


# ---------------------------------------------------------------------------
# quick pipeline: lens context variable and propagation (2 tests)
# ---------------------------------------------------------------------------


def test_quick_pipeline_context_has_lens_default_architecture():
    """quick pipeline context must declare 'lens' with default 'architecture'."""
    data = _load_yaml(QUICK_PIPELINE_PATH)
    ctx = data.get("context", {})
    assert "lens" in ctx, (
        f"quick pipeline context must declare 'lens'. Found keys: {list(ctx.keys())}"
    )
    assert ctx.get("lens") == "architecture", (
        f"quick pipeline 'lens' default must be 'architecture', got: {ctx.get('lens')!r}"
    )


def test_quick_pipeline_investigate_topics_passes_lens():
    """quick pipeline investigate-topics step must pass 'lens' to the sub-recipe context."""
    data = _load_yaml(QUICK_PIPELINE_PATH)
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None, "investigate-topics step not found in investigate stage"
    ctx = step.get("context", {})
    assert "lens" in ctx, (
        f"investigate-topics step must pass 'lens' in context to sub-recipe. "
        f"Found context keys: {list(ctx.keys())}"
    )


# ---------------------------------------------------------------------------
# deep pipeline: lens context variable and propagation (3 tests)
# ---------------------------------------------------------------------------


def test_deep_pipeline_context_has_lens_default_architecture():
    """deep pipeline (discovery-pipeline.yaml) context must declare 'lens' with default 'architecture'."""
    data = _load_yaml(DEEP_PIPELINE_PATH)
    ctx = data.get("context", {})
    assert "lens" in ctx, (
        f"deep pipeline context must declare 'lens'. Found keys: {list(ctx.keys())}"
    )
    assert ctx.get("lens") == "architecture", (
        f"deep pipeline 'lens' default must be 'architecture', got: {ctx.get('lens')!r}"
    )


def test_topdown_strategy_context_has_lens_default_architecture():
    """strategy-topdown.yaml context must declare 'lens' with default 'architecture'."""
    data = _load_yaml(TOPDOWN_STRATEGY_PATH)
    ctx = data.get("context", {})
    assert "lens" in ctx, (
        f"strategy-topdown.yaml context must declare 'lens'. Found keys: {list(ctx.keys())}"
    )
    assert ctx.get("lens") == "architecture", (
        f"strategy-topdown 'lens' default must be 'architecture', got: {ctx.get('lens')!r}"
    )


def test_topdown_strategy_investigate_topics_passes_lens():
    """strategy-topdown.yaml investigate-topics step must pass 'lens' to the sub-recipe context."""
    data = _load_yaml(TOPDOWN_STRATEGY_PATH)
    # strategy-topdown uses flat stages, find investigate stage
    investigate_step = None
    for stage in data.get("stages", []):
        for step in stage.get("steps", []):
            if step.get("id") == "investigate-topics":
                investigate_step = step
                break
    assert investigate_step is not None, (
        "investigate-topics step not found in strategy-topdown.yaml"
    )
    ctx = investigate_step.get("context", {})
    assert "lens" in ctx, (
        f"strategy-topdown investigate-topics must pass 'lens' in context. "
        f"Found context keys: {list(ctx.keys())}"
    )

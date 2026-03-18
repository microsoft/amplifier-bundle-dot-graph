# Phase C: Two Strategy Recipes Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Create two standalone strategy recipes (`strategy-topdown.yaml` and `strategy-bottomup.yaml`) that extract the top-down conceptual investigation into a reusable recipe and introduce a new bottom-up post-order tree traversal strategy.

**Architecture:** Strategy recipes are independently runnable — users can execute either alone without the full pipeline. The top-down strategy extracts and reorganizes the existing `discovery-pipeline.yaml` logic (scan → investigate → synthesize) into a standalone recipe. The bottom-up strategy introduces a novel post-order directory traversal that synthesizes leaf directories first and builds upward, using `traversal-plan.json` as mutable state. Both strategies reuse the Phase B building block sub-recipes (`synthesize-level.yaml`, `synthesize-subsystem.yaml`, `synthesize-overview.yaml`).

**Tech Stack:** YAML recipes (Amplifier recipe engine), Python (bash steps), pytest (structural tests)

---

## Reference Files

**Recipes to read for patterns:**
- `recipes/discovery-pipeline.yaml` — source to extract top-down logic from
- `recipes/discovery-investigate-topic.yaml` — sub-recipe called by top-down
- `recipes/discovery-synthesize-module.yaml` — sub-recipe called by top-down
- `recipes/synthesize-level.yaml` — building block for bottom-up
- `recipes/synthesize-subsystem.yaml` — building block for both strategies
- `recipes/synthesize-overview.yaml` — building block for both strategies

**Tests to read for patterns:**
- `tests/test_discovery_pipeline_recipe.py` — staged recipe test pattern
- `tests/test_synthesize_level_recipe.py` — flat recipe test pattern
- `tests/test_synthesize_subsystem_recipe.py` — flat recipe test pattern
- `tests/test_final_verification.py` — file count registry

**Agents declared in `behaviors/dot-discovery.yaml`:**
- `dot-graph:discovery-prescan`
- `dot-graph:discovery-code-tracer`
- `dot-graph:discovery-behavior-observer`
- `dot-graph:discovery-integration-mapper`
- `dot-graph:discovery-synthesizer`
- `dot-graph:discovery-level-synthesizer`
- `dot-graph:discovery-subsystem-synthesizer`
- `dot-graph:discovery-overview-synthesizer`
- `dot-graph:discovery-combiner`

**Run all tests:**
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ modules/tool-dot-graph/tests/ --tb=short
```

---

## Task 1: Write failing tests for `strategy-topdown.yaml`

**Files:**
- Create: `tests/test_strategy_topdown_recipe.py`

**Step 1: Write the test file**

Create `tests/test_strategy_topdown_recipe.py` with the following content:

```python
"""
Tests for recipes/strategy-topdown.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, output_dir default, fidelity default 'standard' (4 tests)
- Staged structure with exactly 3 stages (2 tests)
- Stage names: scan, investigate, synthesize (3 tests)
- Scan stage steps: structural-scan, topic-select (4 tests)
- Scan stage has NO approval gate (standalone mode) (1 test)
- topic-select uses agent 'dot-graph:discovery-prescan' (1 test)
- Investigate stage: foreach over topics, references discovery-investigate-topic sub-recipe (3 tests)
- Synthesize stage steps: reconcile-modules, subsystem-synthesis, overview-synthesis (5 tests)
- reconcile-modules references discovery-synthesize-module sub-recipe (1 test)
- subsystem-synthesis references synthesize-subsystem sub-recipe (1 test)
- overview-synthesis references synthesize-overview sub-recipe (1 test)
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
    for expected_tag in [
        "discovery",
        "strategy",
        "top-down",
        "dot-graph",
    ]:
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
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
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


def test_recipe_context_output_dir_default_references_topdown():
    """Context output_dir default must reference 'topdown' path."""
    data = _load_recipe()
    ctx = data.get("context", {})
    output_dir = str(ctx.get("output_dir", ""))
    # The default should be empty (resolved at runtime) or reference topdown
    # An empty string is acceptable — the recipe resolves it in the scan step
    assert output_dir == "" or "topdown" in output_dir, (
        f"output_dir default must be empty or reference 'topdown', got: {output_dir!r}"
    )


# ---------------------------------------------------------------------------
# Staged structure (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_staged_structure():
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
# Scan stage (5 tests)
# ---------------------------------------------------------------------------


def test_scan_stage_has_no_approval_gate():
    """Scan stage must NOT have an approval gate (standalone mode)."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    assert "approval_gate" not in stage, (
        "Scan stage must NOT have an approval_gate in standalone strategy mode"
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


def test_topic_select_uses_prescan_agent():
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


# ---------------------------------------------------------------------------
# Investigate stage (3 tests)
# ---------------------------------------------------------------------------


def test_investigate_stage_has_foreach_over_topics():
    """Investigate stage must have a step with foreach iteration over topics."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    has_foreach = any("foreach" in step and "topics" in str(step["foreach"]) for step in steps)
    assert has_foreach, (
        "Investigate stage must have a step with foreach iteration over topics"
    )


def test_investigate_references_investigate_topic_sub_recipe():
    """Investigate stage must reference discovery-investigate-topic sub-recipe."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    has_ref = any(
        "discovery-investigate-topic" in str(step.get("recipe", ""))
        for step in steps
    )
    assert has_ref, (
        "Investigate stage must reference discovery-investigate-topic sub-recipe"
    )


def test_investigate_sub_recipe_step_is_recipe_type():
    """The sub-recipe dispatch step in investigate must have type='recipe'."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "investigate")
    recipe_steps = [s for s in steps if "discovery-investigate-topic" in str(s.get("recipe", ""))]
    assert len(recipe_steps) >= 1, "Must have at least one step referencing investigate-topic"
    assert recipe_steps[0].get("type") == "recipe", (
        f"investigate-topics step must have type='recipe', got: {recipe_steps[0].get('type')!r}"
    )


# ---------------------------------------------------------------------------
# Synthesize stage (5 tests)
# ---------------------------------------------------------------------------


def test_synthesize_stage_has_reconcile_modules_step():
    """Synthesize stage must have a step with id='reconcile-modules'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None, (
        f"No step with id='reconcile-modules' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_reconcile_modules_references_synthesize_module_sub_recipe():
    """reconcile-modules step must reference discovery-synthesize-module sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "discovery-synthesize-module" in recipe_ref, (
        f"reconcile-modules must reference discovery-synthesize-module, got: {recipe_ref!r}"
    )


def test_synthesize_stage_has_subsystem_synthesis_step():
    """Synthesize stage must have a step with id='subsystem-synthesis'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "subsystem-synthesis")
    assert step is not None, (
        f"No step with id='subsystem-synthesis' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


def test_subsystem_synthesis_references_synthesize_subsystem_sub_recipe():
    """subsystem-synthesis step must reference synthesize-subsystem sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "subsystem-synthesis")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "synthesize-subsystem" in recipe_ref, (
        f"subsystem-synthesis must reference synthesize-subsystem, got: {recipe_ref!r}"
    )


def test_synthesize_stage_has_overview_synthesis_step():
    """Synthesize stage must have a step with id='overview-synthesis'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "overview-synthesis")
    assert step is not None, (
        f"No step with id='overview-synthesis' found in synthesize stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'synthesize')]}"
    )


# ---------------------------------------------------------------------------
# overview-synthesis references (1 test)
# ---------------------------------------------------------------------------


def test_overview_synthesis_references_synthesize_overview_sub_recipe():
    """overview-synthesis step must reference synthesize-overview sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "overview-synthesis")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "synthesize-overview" in recipe_ref, (
        f"overview-synthesis must reference synthesize-overview, got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe files exist on disk (5 tests)
# ---------------------------------------------------------------------------


def test_sub_recipe_investigate_topic_exists():
    """Sub-recipe discovery-investigate-topic.yaml must exist."""
    path = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


def test_sub_recipe_synthesize_module_exists():
    """Sub-recipe discovery-synthesize-module.yaml must exist."""
    path = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


def test_sub_recipe_synthesize_subsystem_exists():
    """Sub-recipe synthesize-subsystem.yaml must exist."""
    path = REPO_ROOT / "recipes" / "synthesize-subsystem.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


def test_sub_recipe_synthesize_overview_exists():
    """Sub-recipe synthesize-overview.yaml must exist."""
    path = REPO_ROOT / "recipes" / "synthesize-overview.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


def test_sub_recipe_synthesize_level_exists():
    """Sub-recipe synthesize-level.yaml must exist (used by bottom-up, validates ecosystem)."""
    path = REPO_ROOT / "recipes" / "synthesize-level.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"
```

**Step 2: Run tests to verify they fail**

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_strategy_topdown_recipe.py -v --tb=short 2>&1 | head -60
```
Expected: FAIL — `test_recipe_file_exists` fails with "recipes/strategy-topdown.yaml not found"

**Step 3: Commit**

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add tests/test_strategy_topdown_recipe.py && git commit -m "test: add failing tests for strategy-topdown.yaml recipe"
```

---

## Task 2: Create `strategy-topdown.yaml`

**Files:**
- Create: `recipes/strategy-topdown.yaml`

**Step 1: Write the recipe**

Create `recipes/strategy-topdown.yaml` with the following content:

```yaml
name: "strategy-topdown"
description: >
  Standalone top-down (conceptual) discovery strategy recipe. Runs a 3-stage
  pipeline: scan the codebase and select investigation topics, investigate
  each topic with parallel agent teams, then synthesize findings into
  consensus diagrams at module, subsystem, and overview levels. Extracted
  from the original discovery-pipeline.yaml to be independently runnable.
  Users can execute this alone for conceptual codebase understanding without
  the full orchestrator pipeline.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "strategy", "top-down", "dot-graph", "multi-agent"]

recursion:
  max_depth: 3
  max_total_steps: 100

context:
  repo_path: ""             # Required: path to target repository
  output_dir: ""            # Optional: defaults to {{repo_path}}/.discovery/investigation/topdown
  fidelity: "standard"      # Optional: quick | standard | deep (default: standard)

stages:
  # ---------------------------------------------------------------------------
  # Stage 1: Scan — discover codebase structure and select investigation topics
  # No approval gate in standalone mode — runs straight through.
  # ---------------------------------------------------------------------------
  - name: "scan"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Structural scan — prescan the repository and resolve output_dir
      # Runs dot_graph prescan with fallback to basic directory listing.
      # Resolves default output_dir to {{repo_path}}/.discovery/investigation/topdown
      # -----------------------------------------------------------------------
      - id: "structural-scan"
        type: "bash"
        output: "scan_result"
        parse_json: true
        timeout: 60
        command: |
          python3 - <<'EOF'
          import json
          import os
          from pathlib import Path

          repo_path = "{{repo_path}}"
          output_dir = "{{output_dir}}"

          # Resolve default output_dir
          if not output_dir:
              output_dir = str(Path(repo_path) / ".discovery" / "investigation" / "topdown")

          Path(output_dir).mkdir(parents=True, exist_ok=True)

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "structure": {},
              "error": None,
          }

          # Try amplifier_module_tool_dot_graph.prescan
          try:
              from amplifier_module_tool_dot_graph import prescan
              structure = prescan.prescan_repo(repo_path)
              result["structure"] = structure
          except Exception as e:
              # Fallback: basic directory listing
              try:
                  top_level = []
                  for entry in sorted(Path(repo_path).iterdir()):
                      if entry.name.startswith("."):
                          continue
                      top_level.append({
                          "name": entry.name,
                          "type": "dir" if entry.is_dir() else "file",
                      })
                  result["structure"] = {"top_level": top_level, "source": "fallback"}
                  result["error"] = f"prescan unavailable ({e}), used fallback listing"
              except Exception as e2:
                  result["error"] = f"structural scan failed: {e2}"

          # Write prescan result to output_dir
          prescan_path = Path(output_dir) / "prescan-result.json"
          prescan_path.write_text(json.dumps(result, indent=2))

          print(json.dumps(result))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Topic selection — choose 3–7 investigation topics
      # Dispatches the discovery-prescan agent to select topics based on the
      # structural scan. Standard: 3-5 topics; deep: 5-7 topics.
      # -----------------------------------------------------------------------
      - id: "topic-select"
        agent: "dot-graph:discovery-prescan"
        output: "topics"
        parse_json: true
        timeout: 600
        prompt: |
          You are the discovery-prescan agent for a top-down strategy run.

          Your task: analyze the structural scan results and select 3-7 investigation
          topics that would best illuminate the architecture of this repository.

          Repository: {{scan_result.repo_path}}
          Fidelity tier: {{fidelity}}
          Output directory: {{scan_result.output_dir}}

          Structural scan results:
          {{scan_result}}

          Topic count guidelines:
          - standard fidelity: select 3-5 topics
          - deep fidelity: select 5-7 topics

          For each topic, identify a meaningful architectural concern, mechanism, or
          subsystem — something that, if well-understood, would clarify how the
          repository works as a whole.

          Return your response as a JSON array only (no markdown, no explanation):
          [
            {
              "name": "Human-readable topic name",
              "slug": "kebab-case-slug",
              "description": "One sentence describing what this topic covers and why it matters"
            },
            ...
          ]

      # -----------------------------------------------------------------------
      # Step 3: Save topics — write topics.json to output_dir
      # -----------------------------------------------------------------------
      - id: "save-topics"
        type: "bash"
        output: "save_topics_result"
        parse_json: true
        timeout: 15
        command: |
          python3 - <<'EOF'
          import json
          from pathlib import Path

          output_dir = "{{scan_result.output_dir}}"
          topics = {{topics}}

          topics_path = Path(output_dir) / "topics.json"
          topics_path.write_text(json.dumps(topics, indent=2))

          print(json.dumps({"topics_path": str(topics_path), "topic_count": len(topics)}))
          EOF

  # ---------------------------------------------------------------------------
  # Stage 2: Investigate — dispatch agent teams per topic
  # ---------------------------------------------------------------------------
  - name: "investigate"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Prepare topic directories
      # Creates per-topic directory structure under output_dir/modules/{slug}/
      # -----------------------------------------------------------------------
      - id: "prepare-topics"
        type: "bash"
        output: "prep_result"
        parse_json: true
        timeout: 15
        command: |
          python3 - <<'EOF'
          import json
          from pathlib import Path

          output_dir = "{{scan_result.output_dir}}"
          topics = {{topics}}

          agent_names = ["code-tracer", "behavior-observer", "integration-mapper"]
          created = []

          for topic in topics:
              slug = topic.get("slug", "")
              if not slug:
                  continue
              module_dir = Path(output_dir) / "modules" / slug
              for agent_name in agent_names:
                  agent_dir = module_dir / "agents" / agent_name
                  agent_dir.mkdir(parents=True, exist_ok=True)
              created.append(str(module_dir))

          print(json.dumps({"created_dirs": created, "topic_count": len(created)}))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Investigate topics — dispatch sub-recipe per topic
      # Runs discovery-investigate-topic.yaml for each selected topic.
      # -----------------------------------------------------------------------
      - id: "investigate-topics"
        type: "recipe"
        foreach: "{{topics}}"
        as: "topic"
        recipe: "@dot-graph:recipes/discovery-investigate-topic.yaml"
        context:
          topic: "{{topic}}"
          fidelity: "{{fidelity}}"
          repo_path: "{{scan_result.repo_path}}"
          output_dir: "{{scan_result.output_dir}}"
        output: "investigation_results"
        timeout: 7200

  # ---------------------------------------------------------------------------
  # Stage 3: Synthesize — produce consensus diagrams at all levels
  # ---------------------------------------------------------------------------
  - name: "synthesize"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Reconcile modules — synthesize per-topic agent findings
      # Runs discovery-synthesize-module.yaml per topic to produce consensus
      # diagram.dot and findings.md in each module directory.
      # -----------------------------------------------------------------------
      - id: "reconcile-modules"
        type: "recipe"
        foreach: "{{topics}}"
        as: "topic"
        recipe: "@dot-graph:recipes/discovery-synthesize-module.yaml"
        context:
          module_name: "{{topic.name}}"
          module_dir: "{{scan_result.output_dir}}/modules/{{topic.slug}}"
          investigation_dir: "{{scan_result.output_dir}}/modules/{{topic.slug}}"
          fidelity: "{{fidelity}}"
          output_dir: "{{scan_result.output_dir}}"
        output: "reconciliation_results"
        timeout: 7200

      # -----------------------------------------------------------------------
      # Step 2: Group modules into subsystems and synthesize
      # Groups topics by prefix/category, then calls synthesize-subsystem.yaml
      # for each group. Single-subsystem fallback when grouping is ambiguous.
      # -----------------------------------------------------------------------
      - id: "subsystem-synthesis"
        type: "recipe"
        recipe: "@dot-graph:recipes/synthesize-subsystem.yaml"
        context:
          subsystem_name: "topdown-discovery"
          module_dot_files: "{{reconciliation_results}}"
          source_dirs: "[]"
          output_dir: "{{scan_result.output_dir}}/subsystems"
        output: "subsystem_results"
        timeout: 3600

      # -----------------------------------------------------------------------
      # Step 3: Overview synthesis — produce top-level overview
      # Calls synthesize-overview.yaml with subsystem DOTs to produce
      # overview.dot at the output root.
      # -----------------------------------------------------------------------
      - id: "overview-synthesis"
        type: "recipe"
        recipe: "@dot-graph:recipes/synthesize-overview.yaml"
        context:
          subsystem_dot_files: "{{subsystem_results}}"
          repo_root: "{{scan_result.repo_path}}"
          output_dir: "{{scan_result.output_dir}}"
        output: "overview_results"
        timeout: 3600

      # -----------------------------------------------------------------------
      # Step 4: Update metadata — write last-run.json
      # Records timestamp, fidelity, and repo_path for future incremental runs.
      # -----------------------------------------------------------------------
      - id: "update-metadata"
        type: "bash"
        output: "metadata_result"
        parse_json: true
        timeout: 10
        command: |
          python3 - <<'EOF'
          import json
          import subprocess
          from datetime import datetime, timezone
          from pathlib import Path

          output_dir = "{{scan_result.output_dir}}"
          repo_path = "{{scan_result.repo_path}}"
          fidelity = "{{fidelity}}"

          # Get current git commit
          commit_hash = ""
          try:
              commit_hash = subprocess.check_output(
                  ["git", "-C", repo_path, "rev-parse", "HEAD"],
                  text=True,
                  stderr=subprocess.DEVNULL,
              ).strip()
          except Exception:
              pass

          metadata = {
              "strategy": "topdown",
              "commit_hash": commit_hash,
              "timestamp": datetime.now(timezone.utc).isoformat(),
              "fidelity": fidelity,
              "repo_path": repo_path,
          }

          last_run_path = Path(output_dir) / "last-run.json"
          last_run_path.write_text(json.dumps(metadata, indent=2))

          print(json.dumps({"written": str(last_run_path), **metadata}))
          EOF

final_output: "metadata_result"
```

**Step 2: Run tests to verify they pass**

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_strategy_topdown_recipe.py -v --tb=short
```
Expected: All 38 tests PASS

**Step 3: Commit**

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add recipes/strategy-topdown.yaml && git commit -m "feat: add strategy-topdown.yaml standalone top-down discovery recipe"
```

---

## Task 3: Write failing tests for `strategy-bottomup.yaml`

**Files:**
- Create: `tests/test_strategy_bottomup_recipe.py`

**Step 1: Write the test file**

Create `tests/test_strategy_bottomup_recipe.py` with the following content:

```python
"""
Tests for recipes/strategy-bottomup.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, output_dir, fidelity default 'standard' (4 tests)
- Staged structure with exactly 3 stages (2 tests)
- Stage names: scan-and-plan, traverse, assemble (3 tests)
- scan-and-plan stage: has a bash step that computes post-order traversal,
  references traversal-plan.json (3 tests)
- traverse stage: has foreach over post_order list, references synthesize-level
  sub-recipe (3 tests)
- assemble stage: has subsystem synthesis step referencing synthesize-subsystem,
  has overview synthesis step referencing synthesize-overview (4 tests)
- Sub-recipe files exist on disk (3 tests)
- traversal-plan.json documentation: recipe description or step comments
  mention traversal-plan.json as mutable state (1 test)

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
    """Return the raw YAML text of the recipe."""
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
    for expected_tag in [
        "discovery",
        "strategy",
        "bottom-up",
        "dot-graph",
    ]:
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
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir' variable. Found keys: {list(ctx.keys())}"
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


def test_recipe_context_output_dir_default_references_bottomup():
    """Context output_dir default must reference 'bottomup' path or be empty."""
    data = _load_recipe()
    ctx = data.get("context", {})
    output_dir = str(ctx.get("output_dir", ""))
    # Empty string is acceptable — the recipe resolves it at runtime
    assert output_dir == "" or "bottomup" in output_dir, (
        f"output_dir default must be empty or reference 'bottomup', got: {output_dir!r}"
    )


# ---------------------------------------------------------------------------
# Staged structure (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_staged_structure():
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
        f"No stage named 'scan-and-plan' found. Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_traverse_exists():
    """Must have a stage named 'traverse'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "traverse")
    assert stage is not None, (
        f"No stage named 'traverse' found. Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_assemble_exists():
    """Must have a stage named 'assemble'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "assemble")
    assert stage is not None, (
        f"No stage named 'assemble' found. Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


# ---------------------------------------------------------------------------
# scan-and-plan stage (3 tests)
# ---------------------------------------------------------------------------


def test_scan_and_plan_has_prescan_step():
    """scan-and-plan stage must have a bash step that runs prescan."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "scan-and-plan")
    bash_steps = [s for s in steps if s.get("type") == "bash"]
    assert len(bash_steps) >= 1, (
        "scan-and-plan stage must have at least one bash step for prescan"
    )


def test_scan_and_plan_computes_post_order():
    """scan-and-plan stage must have a step whose command references 'post_order'."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "scan-and-plan")
    has_post_order = any(
        "post_order" in str(step.get("command", ""))
        for step in steps
    )
    assert has_post_order, (
        "scan-and-plan stage must contain a step that computes 'post_order' traversal"
    )


def test_scan_and_plan_references_traversal_plan_json():
    """scan-and-plan stage must reference traversal-plan.json."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "scan-and-plan")
    has_ref = any(
        "traversal-plan.json" in str(step.get("command", ""))
        for step in steps
    )
    assert has_ref, (
        "scan-and-plan stage must reference 'traversal-plan.json' in a step command"
    )


# ---------------------------------------------------------------------------
# traverse stage (3 tests)
# ---------------------------------------------------------------------------


def test_traverse_stage_has_foreach():
    """traverse stage must have a step with foreach iteration."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "traverse")
    has_foreach = any("foreach" in step for step in steps)
    assert has_foreach, (
        "traverse stage must have a step with 'foreach' iteration over directory levels"
    )


def test_traverse_stage_references_synthesize_level():
    """traverse stage must reference synthesize-level sub-recipe."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "traverse")
    has_ref = any(
        "synthesize-level" in str(step.get("recipe", ""))
        for step in steps
    )
    assert has_ref, (
        "traverse stage must reference synthesize-level sub-recipe"
    )


def test_traverse_stage_synthesize_level_is_recipe_type():
    """The synthesize-level step in traverse must have type='recipe'."""
    data = _load_recipe()
    steps = _get_stage_steps(data, "traverse")
    recipe_steps = [s for s in steps if "synthesize-level" in str(s.get("recipe", ""))]
    assert len(recipe_steps) >= 1, "Must have at least one step referencing synthesize-level"
    assert recipe_steps[0].get("type") == "recipe", (
        f"synthesize-level step must have type='recipe', got: {recipe_steps[0].get('type')!r}"
    )


# ---------------------------------------------------------------------------
# assemble stage (4 tests)
# ---------------------------------------------------------------------------


def test_assemble_stage_has_subsystem_synthesis_step():
    """assemble stage must have a step with id='subsystem-synthesis'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "subsystem-synthesis")
    assert step is not None, (
        f"No step with id='subsystem-synthesis' found in assemble stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'assemble')]}"
    )


def test_assemble_subsystem_synthesis_references_synthesize_subsystem():
    """subsystem-synthesis step in assemble must reference synthesize-subsystem."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "subsystem-synthesis")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "synthesize-subsystem" in recipe_ref, (
        f"subsystem-synthesis must reference synthesize-subsystem, got: {recipe_ref!r}"
    )


def test_assemble_stage_has_overview_synthesis_step():
    """assemble stage must have a step with id='overview-synthesis'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "overview-synthesis")
    assert step is not None, (
        f"No step with id='overview-synthesis' found in assemble stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'assemble')]}"
    )


def test_assemble_overview_synthesis_references_synthesize_overview():
    """overview-synthesis step in assemble must reference synthesize-overview."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "assemble", "overview-synthesis")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "synthesize-overview" in recipe_ref, (
        f"overview-synthesis must reference synthesize-overview, got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe files exist on disk (3 tests)
# ---------------------------------------------------------------------------


def test_sub_recipe_synthesize_level_exists():
    """Sub-recipe synthesize-level.yaml must exist."""
    path = REPO_ROOT / "recipes" / "synthesize-level.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


def test_sub_recipe_synthesize_subsystem_exists():
    """Sub-recipe synthesize-subsystem.yaml must exist."""
    path = REPO_ROOT / "recipes" / "synthesize-subsystem.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


def test_sub_recipe_synthesize_overview_exists():
    """Sub-recipe synthesize-overview.yaml must exist."""
    path = REPO_ROOT / "recipes" / "synthesize-overview.yaml"
    assert path.exists(), f"Sub-recipe not found at {path}"


# ---------------------------------------------------------------------------
# traversal-plan.json documentation (1 test)
# ---------------------------------------------------------------------------


def test_recipe_documents_traversal_plan_json_as_mutable_state():
    """Recipe YAML must mention traversal-plan.json as mutable state file."""
    raw_text = _get_full_yaml_text()
    assert "traversal-plan.json" in raw_text, (
        "Recipe must mention 'traversal-plan.json' — it is the mutable state file "
        "that accumulates child DOT paths during post-order traversal"
    )
```

**Step 2: Run tests to verify they fail**

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_strategy_bottomup_recipe.py -v --tb=short 2>&1 | head -60
```
Expected: FAIL — `test_recipe_file_exists` fails with "recipes/strategy-bottomup.yaml not found"

**Step 3: Commit**

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add tests/test_strategy_bottomup_recipe.py && git commit -m "test: add failing tests for strategy-bottomup.yaml recipe"
```

---

## Task 4: Create `strategy-bottomup.yaml`

**Files:**
- Create: `recipes/strategy-bottomup.yaml`

**Step 1: Write the recipe**

Create `recipes/strategy-bottomup.yaml` with the following content:

```yaml
name: "strategy-bottomup"
description: >
  Standalone bottom-up (empirical) discovery strategy recipe. Runs a 3-stage
  pipeline: scan the codebase and compute a post-order directory traversal plan,
  traverse directories from leaves to root calling synthesize-level.yaml at each
  level, then assemble subsystem and overview diagrams from the traversal results.
  Uses traversal-plan.json as a mutable state file that accumulates child DOT
  paths as the traversal progresses — each foreach iteration reads current state
  and updates it. Designed to be independently runnable for empirical codebase
  understanding without the full orchestrator pipeline.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "strategy", "bottom-up", "dot-graph", "post-order"]

recursion:
  max_depth: 3
  max_total_steps: 200

context:
  repo_path: ""             # Required: path to target repository
  output_dir: ""            # Optional: defaults to {{repo_path}}/.discovery/investigation/bottomup
  fidelity: "standard"      # Optional: quick | standard | deep (default: standard)

stages:
  # ---------------------------------------------------------------------------
  # Stage 1: Scan and Plan — prescan the repository, compute post-order
  # traversal of directories from leaves (deepest) to root (shallowest).
  # Writes traversal-plan.json as the mutable state file for the traverse stage.
  # ---------------------------------------------------------------------------
  - name: "scan-and-plan"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Prescan — run structural scan and resolve output_dir
      # -----------------------------------------------------------------------
      - id: "prescan"
        type: "bash"
        output: "prescan_result"
        parse_json: true
        timeout: 60
        command: |
          python3 - <<'EOF'
          import json
          import os
          from pathlib import Path

          repo_path = "{{repo_path}}"
          output_dir = "{{output_dir}}"

          # Resolve default output_dir
          if not output_dir:
              output_dir = str(Path(repo_path) / ".discovery" / "investigation" / "bottomup")

          Path(output_dir).mkdir(parents=True, exist_ok=True)

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "structure": {},
              "error": None,
          }

          # Try amplifier_module_tool_dot_graph.prescan
          try:
              from amplifier_module_tool_dot_graph import prescan
              structure = prescan.prescan_repo(repo_path)
              result["structure"] = structure
          except Exception as e:
              # Fallback: basic directory listing
              try:
                  top_level = []
                  for entry in sorted(Path(repo_path).iterdir()):
                      if entry.name.startswith("."):
                          continue
                      top_level.append({
                          "name": entry.name,
                          "type": "dir" if entry.is_dir() else "file",
                      })
                  result["structure"] = {"top_level": top_level, "source": "fallback"}
                  result["error"] = f"prescan unavailable ({e}), used fallback listing"
              except Exception as e2:
                  result["error"] = f"structural scan failed: {e2}"

          # Write prescan result
          prescan_path = Path(output_dir) / "prescan-result.json"
          prescan_path.write_text(json.dumps(result, indent=2))

          print(json.dumps(result))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Compute post-order traversal plan
      # Walks the directory tree, skips hidden/build dirs, sorts deepest-first.
      # Writes traversal-plan.json — the mutable state file that accumulates
      # child DOT paths as the traverse stage progresses.
      # -----------------------------------------------------------------------
      - id: "compute-traversal"
        type: "bash"
        output: "traversal_plan"
        parse_json: true
        timeout: 30
        command: |
          python3 - <<'EOF'
          import json
          import os
          import re
          from pathlib import Path

          repo_path = "{{prescan_result.repo_path}}"
          output_dir = "{{prescan_result.output_dir}}"

          SKIP_DIRS = {
              ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv",
              "venv", ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
              ".eggs", ".discovery", ".amplifier",
          }

          def slug_from_path(rel_path):
              """Convert relative path to slug: src/auth -> src-auth."""
              return re.sub(r"[/\\]+", "-", str(rel_path)).strip("-")

          def walk_dirs(base):
              """Recursively walk directories, returning (rel_path, depth) pairs."""
              entries = []
              for item in sorted(Path(base).iterdir()):
                  if not item.is_dir():
                      continue
                  if item.name.startswith(".") or item.name in SKIP_DIRS:
                      continue
                  rel = item.relative_to(repo_path)
                  depth = len(rel.parts)
                  entries.append({
                      "slug": slug_from_path(rel),
                      "path": str(rel),
                      "abs_path": str(item),
                      "parent": slug_from_path(rel.parent) if depth > 1 else None,
                      "depth": depth,
                  })
                  # Recurse into subdirectories
                  entries.extend(walk_dirs(item))
              return entries

          all_dirs = walk_dirs(repo_path)

          # Sort post-order: deepest first, then alphabetically within same depth
          post_order = sorted(all_dirs, key=lambda d: (-d["depth"], d["path"]))

          plan = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "post_order": post_order,
              "child_dots": {},
              "completed": [],
          }

          # Write traversal-plan.json
          plan_path = Path(output_dir) / "traversal-plan.json"
          plan_path.write_text(json.dumps(plan, indent=2))

          print(json.dumps({
              "plan_path": str(plan_path),
              "directory_count": len(post_order),
              "max_depth": max((d["depth"] for d in post_order), default=0),
              "post_order": post_order,
          }))
          EOF

  # ---------------------------------------------------------------------------
  # Stage 2: Traverse — post-order directory traversal
  # Iterates over directories from leaves to root. For each directory:
  # 1. Reads child_dots from traversal-plan.json for this directory's children
  # 2. Calls synthesize-level.yaml to produce diagram.dot + findings.md
  # 3. Updates traversal-plan.json with the new diagram.dot path under parent
  # ---------------------------------------------------------------------------
  - name: "traverse"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Synthesize each directory level (post-order: leaves first)
      # For each entry in post_order, calls synthesize-level.yaml then updates
      # traversal-plan.json with the produced diagram.dot path.
      # -----------------------------------------------------------------------
      - id: "synthesize-levels"
        type: "recipe"
        foreach: "{{traversal_plan.post_order}}"
        as: "level"
        recipe: "@dot-graph:recipes/synthesize-level.yaml"
        context:
          level_path: "{{level.abs_path}}"
          child_dot_files: "[]"
          output_dir: "{{prescan_result.output_dir}}"
          level_slug: "{{level.slug}}"
          fidelity: "{{fidelity}}"
        output: "level_results"
        timeout: 7200

      # -----------------------------------------------------------------------
      # Step 2: Update traversal plan with completed levels
      # After all levels are synthesized, updates traversal-plan.json with
      # the list of all produced diagram.dot paths.
      # -----------------------------------------------------------------------
      - id: "update-traversal-plan"
        type: "bash"
        output: "traversal_update"
        parse_json: true
        timeout: 30
        command: |
          python3 - <<'EOF'
          import json
          from pathlib import Path

          output_dir = "{{prescan_result.output_dir}}"
          plan_path = Path(output_dir) / "traversal-plan.json"

          plan = json.loads(plan_path.read_text())

          # Scan for all produced diagram.dot files
          completed = []
          for entry in plan["post_order"]:
              dot_path = Path(output_dir) / entry["slug"] / "diagram.dot"
              if dot_path.exists():
                  completed.append({
                      "slug": entry["slug"],
                      "dot_path": str(dot_path),
                  })
                  # Update child_dots for parent
                  parent = entry.get("parent")
                  if parent:
                      if parent not in plan["child_dots"]:
                          plan["child_dots"][parent] = []
                      plan["child_dots"][parent].append(str(dot_path))

          plan["completed"] = completed
          plan_path.write_text(json.dumps(plan, indent=2))

          print(json.dumps({
              "completed_count": len(completed),
              "child_dots_groups": len(plan["child_dots"]),
          }))
          EOF

  # ---------------------------------------------------------------------------
  # Stage 3: Assemble — build subsystem and overview diagrams
  # Groups synthesized directories into subsystems by depth (top-level dirs =
  # subsystems), then produces overview from subsystem DOTs.
  # ---------------------------------------------------------------------------
  - name: "assemble"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Identify subsystems — group top-level directories
      # Scans traversal results to find depth-1 directories as subsystems,
      # collecting their diagram.dot files as module DOTs.
      # -----------------------------------------------------------------------
      - id: "identify-subsystems"
        type: "bash"
        output: "subsystem_info"
        parse_json: true
        timeout: 15
        command: |
          python3 - <<'EOF'
          import json
          from pathlib import Path

          output_dir = "{{prescan_result.output_dir}}"
          plan_path = Path(output_dir) / "traversal-plan.json"
          plan = json.loads(plan_path.read_text())

          # Depth-1 directories are subsystems
          subsystems = []
          module_dot_files = []
          for entry in plan["post_order"]:
              dot_path = Path(output_dir) / entry["slug"] / "diagram.dot"
              if dot_path.exists():
                  module_dot_files.append(str(dot_path))
              if entry["depth"] == 1 and dot_path.exists():
                  subsystems.append({
                      "name": entry["slug"],
                      "dot_path": str(dot_path),
                  })

          # Create subsystems output directory
          subsystems_dir = Path(output_dir) / "subsystems"
          subsystems_dir.mkdir(parents=True, exist_ok=True)

          print(json.dumps({
              "subsystems": subsystems,
              "module_dot_files": module_dot_files,
              "subsystems_dir": str(subsystems_dir),
          }))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Subsystem synthesis — synthesize across grouped modules
      # -----------------------------------------------------------------------
      - id: "subsystem-synthesis"
        type: "recipe"
        recipe: "@dot-graph:recipes/synthesize-subsystem.yaml"
        context:
          subsystem_name: "bottomup-discovery"
          module_dot_files: "{{subsystem_info.module_dot_files}}"
          source_dirs: "[]"
          output_dir: "{{subsystem_info.subsystems_dir}}"
        output: "subsystem_results"
        timeout: 3600

      # -----------------------------------------------------------------------
      # Step 3: Overview synthesis — produce top-level overview
      # -----------------------------------------------------------------------
      - id: "overview-synthesis"
        type: "recipe"
        recipe: "@dot-graph:recipes/synthesize-overview.yaml"
        context:
          subsystem_dot_files: "{{subsystem_results}}"
          repo_root: "{{prescan_result.repo_path}}"
          output_dir: "{{prescan_result.output_dir}}"
        output: "overview_results"
        timeout: 3600

      # -----------------------------------------------------------------------
      # Step 4: Update metadata — write last-run.json
      # -----------------------------------------------------------------------
      - id: "update-metadata"
        type: "bash"
        output: "metadata_result"
        parse_json: true
        timeout: 10
        command: |
          python3 - <<'EOF'
          import json
          import subprocess
          from datetime import datetime, timezone
          from pathlib import Path

          output_dir = "{{prescan_result.output_dir}}"
          repo_path = "{{prescan_result.repo_path}}"
          fidelity = "{{fidelity}}"

          # Get current git commit
          commit_hash = ""
          try:
              commit_hash = subprocess.check_output(
                  ["git", "-C", repo_path, "rev-parse", "HEAD"],
                  text=True,
                  stderr=subprocess.DEVNULL,
              ).strip()
          except Exception:
              pass

          metadata = {
              "strategy": "bottomup",
              "commit_hash": commit_hash,
              "timestamp": datetime.now(timezone.utc).isoformat(),
              "fidelity": fidelity,
              "repo_path": repo_path,
          }

          last_run_path = Path(output_dir) / "last-run.json"
          last_run_path.write_text(json.dumps(metadata, indent=2))

          print(json.dumps({"written": str(last_run_path), **metadata}))
          EOF

final_output: "metadata_result"
```

**Step 2: Run tests to verify they pass**

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_strategy_bottomup_recipe.py -v --tb=short
```
Expected: All 30 tests PASS

**Step 3: Commit**

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add recipes/strategy-bottomup.yaml && git commit -m "feat: add strategy-bottomup.yaml standalone bottom-up discovery recipe"
```

---

## Task 5: Update `test_final_verification.py` and run full test suite

**Files:**
- Modify: `tests/test_final_verification.py`

**Step 1: Update the expected files list and count**

In `tests/test_final_verification.py`, add the 2 new recipe files to the `EXPECTED_FILES` list. Find the comment block ending with `# Phase B v2: synthesizer sub-recipes` and the last entry `"recipes/synthesize-overview.yaml"`. Add the following lines immediately after it:

```python
    # Phase C v2: strategy recipes
    "recipes/strategy-topdown.yaml",
    "recipes/strategy-bottomup.yaml",
```

Then update the docstring at the top of the file. Change:
```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 38 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files.
Phase B v2: Updated to include 3 new synthesizer sub-recipes (total 38).
"""
```
to:
```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 38 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files.
Phase B v2: Updated to include 3 new synthesizer sub-recipes (total 38).
Phase C v2: Updated to include 2 new strategy recipes (total 40).
"""
```

Update the comment above `EXPECTED_FILES`:
```python
# The 40 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes + 8 Phase A v2 + 3 Phase B v2 + 2 Phase C v2)
```

Update `test_total_file_count` — change both the count and the message:
```python
def test_total_file_count():
    """Step 6: Total bundle file count is exactly 40 (38 prior + 2 Phase C v2)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 40, (
        f"Expected 40 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )
```

**Step 2: Run the full test suite**

Run:
```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ modules/tool-dot-graph/tests/ --tb=short
```
Expected: ALL tests PASS including the updated file count (40)

**Step 3: Commit**

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add tests/test_final_verification.py && git commit -m "test: update test_final_verification.py to 40 files with 2 Phase C v2 recipes"
```

---

## Summary

| Task | Files | Tests | Description |
|------|-------|-------|-------------|
| 1 | `tests/test_strategy_topdown_recipe.py` | 38 | Write failing tests for strategy-topdown |
| 2 | `recipes/strategy-topdown.yaml` | — | Create the top-down strategy recipe |
| 3 | `tests/test_strategy_bottomup_recipe.py` | 30 | Write failing tests for strategy-bottomup |
| 4 | `recipes/strategy-bottomup.yaml` | — | Create the bottom-up strategy recipe |
| 5 | `tests/test_final_verification.py` | — | Update file count to 40, run full suite |

**Total new tests:** 68 (38 top-down + 30 bottom-up)
**Total new files:** 4 (2 recipes + 2 test files)
**Modified files:** 1 (`test_final_verification.py`)
**Commits:** 5

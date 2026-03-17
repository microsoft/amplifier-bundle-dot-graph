# Discovery Phase D: Recipe YAML Definitions — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Create the 3 recipe YAML files that orchestrate the discovery pipeline, plus structural tests for each.
**Architecture:** Declarative YAML recipes executed by the `tool-recipes` module. An outer staged recipe (`discovery-pipeline.yaml`) orchestrates two sub-recipes: `discovery-investigate-topic.yaml` (per-topic agent dispatch) and `discovery-synthesize-module.yaml` (per-module synthesis with quality gate loop). The outer recipe has an approval gate between scan and investigation stages.
**Tech Stack:** YAML recipe definitions, pytest for structural validation tests.

---

### Task 1: Create `recipes/discovery-investigate-topic.yaml`

**Files:**
- Create: `recipes/discovery-investigate-topic.yaml`
- Test: `tests/test_discovery_investigate_topic_recipe.py`

**Step 1: Write the failing test**

Create `tests/test_discovery_investigate_topic_recipe.py`:

```python
"""
Tests for recipes/discovery-investigate-topic.yaml structure and content.
Validates the sub-recipe YAML parses correctly and has expected steps,
context variables, and conditional execution logic.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"


@pytest.fixture(scope="module")
def recipe() -> dict:
    """Load the recipe YAML once per test module."""
    return yaml.safe_load(RECIPE_PATH.read_text())


# --- File existence ---


def test_recipe_file_exists():
    """recipes/discovery-investigate-topic.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-investigate-topic.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_is_valid_yaml():
    """Recipe must parse as valid YAML dict."""
    content = RECIPE_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "Recipe must parse to a dict"


# --- Top-level metadata ---


def test_recipe_has_name(recipe):
    """Recipe must have a 'name' key."""
    assert "name" in recipe, "Recipe must have 'name' key"
    assert recipe["name"] == "discovery-investigate-topic", (
        f"name must be 'discovery-investigate-topic', got: {recipe['name']}"
    )


def test_recipe_has_description(recipe):
    """Recipe must have a non-empty description."""
    assert "description" in recipe, "Recipe must have 'description' key"
    assert recipe["description"], "description must not be empty"


def test_recipe_has_version(recipe):
    """Recipe must have a version."""
    assert "version" in recipe, "Recipe must have 'version' key"


# --- Context variables ---


def test_recipe_has_context(recipe):
    """Recipe must declare context variables."""
    assert "context" in recipe, "Recipe must have 'context' key"


def test_recipe_context_has_required_vars(recipe):
    """Context must declare topic, fidelity, repo_path, and output_dir."""
    ctx = recipe["context"]
    for var in ["topic", "fidelity", "repo_path", "output_dir"]:
        assert var in ctx, f"context must declare '{var}'"


# --- Steps structure ---


def test_recipe_has_steps(recipe):
    """Recipe must have a 'steps' key (flat recipe, not staged)."""
    assert "steps" in recipe, "Recipe must have 'steps' key"
    assert "stages" not in recipe, "Sub-recipe must be flat (steps, not stages)"


def test_recipe_has_three_agent_steps(recipe):
    """Recipe must have exactly 3 agent steps for the 3 investigation agents."""
    steps = recipe["steps"]
    agent_steps = [s for s in steps if s.get("agent") or s.get("type") == "agent"]
    assert len(agent_steps) == 3, (
        f"Expected 3 agent steps, found {len(agent_steps)}"
    )


def test_recipe_step_ids(recipe):
    """Steps must have expected IDs for code-tracer, behavior-observer, integration-mapper."""
    step_ids = [s["id"] for s in recipe["steps"]]
    assert "code-tracer" in step_ids, "Must have 'code-tracer' step"
    assert "behavior-observer" in step_ids, "Must have 'behavior-observer' step"
    assert "integration-mapper" in step_ids, "Must have 'integration-mapper' step"


# --- Agent references ---


def test_code_tracer_uses_correct_agent(recipe):
    """code-tracer step must reference dot-graph:discovery-code-tracer agent."""
    step = next(s for s in recipe["steps"] if s["id"] == "code-tracer")
    assert step.get("agent") == "dot-graph:discovery-code-tracer", (
        f"code-tracer must use agent 'dot-graph:discovery-code-tracer', got: {step.get('agent')}"
    )


def test_behavior_observer_uses_correct_agent(recipe):
    """behavior-observer step must reference dot-graph:discovery-behavior-observer agent."""
    step = next(s for s in recipe["steps"] if s["id"] == "behavior-observer")
    assert step.get("agent") == "dot-graph:discovery-behavior-observer", (
        f"behavior-observer must use agent 'dot-graph:discovery-behavior-observer', got: {step.get('agent')}"
    )


def test_integration_mapper_uses_correct_agent(recipe):
    """integration-mapper step must reference dot-graph:discovery-integration-mapper agent."""
    step = next(s for s in recipe["steps"] if s["id"] == "integration-mapper")
    assert step.get("agent") == "dot-graph:discovery-integration-mapper", (
        f"integration-mapper must use agent 'dot-graph:discovery-integration-mapper', got: {step.get('agent')}"
    )


# --- Conditional execution (fidelity gating) ---


def test_code_tracer_has_fidelity_condition(recipe):
    """code-tracer runs at standard and deep fidelity (not quick)."""
    step = next(s for s in recipe["steps"] if s["id"] == "code-tracer")
    condition = step.get("condition", "")
    assert "quick" in condition or "fidelity" in condition, (
        f"code-tracer must have a fidelity-based condition, got: {condition!r}"
    )


def test_behavior_observer_has_deep_only_condition(recipe):
    """behavior-observer runs only at deep fidelity."""
    step = next(s for s in recipe["steps"] if s["id"] == "behavior-observer")
    condition = step.get("condition", "")
    assert "deep" in condition, (
        f"behavior-observer must have a deep-only condition, got: {condition!r}"
    )


def test_integration_mapper_has_fidelity_condition(recipe):
    """integration-mapper runs at standard and deep fidelity (not quick)."""
    step = next(s for s in recipe["steps"] if s["id"] == "integration-mapper")
    condition = step.get("condition", "")
    assert "quick" in condition or "fidelity" in condition, (
        f"integration-mapper must have a fidelity-based condition, got: {condition!r}"
    )


# --- Prompts reference topic and output paths ---


def test_agent_prompts_reference_topic(recipe):
    """All agent step prompts must reference the topic context variable."""
    for step in recipe["steps"]:
        if step.get("agent"):
            prompt = step.get("prompt", "")
            assert "topic" in prompt, (
                f"Step '{step['id']}' prompt must reference topic"
            )


def test_agent_prompts_reference_output_dir(recipe):
    """All agent step prompts must reference the output_dir context variable."""
    for step in recipe["steps"]:
        if step.get("agent"):
            prompt = step.get("prompt", "")
            assert "output_dir" in prompt, (
                f"Step '{step['id']}' prompt must reference output_dir"
            )
```

**Step 2: Run test to verify it fails**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_discovery_investigate_topic_recipe.py -v --no-header 2>&1 | head -5`
Expected: FAIL with "not found" (recipe file doesn't exist yet)

**Step 3: Write the recipe YAML**

Create `recipes/discovery-investigate-topic.yaml`:

```yaml
# discovery-investigate-topic.yaml
# Per-Topic Investigation Sub-Recipe
# Dispatches 1-3 agents per topic depending on fidelity tier.
# Each agent writes to its own isolated subdirectory under the topic's module dir.
#
# Called by: recipes/discovery-pipeline.yaml (foreach over topics)
# Can also run standalone for re-investigating a single topic.
#
# Agent dispatch by fidelity:
#   quick:    no agents (this recipe is not invoked at quick tier)
#   standard: code-tracer + integration-mapper (2 agents)
#   deep:     code-tracer + behavior-observer + integration-mapper (3 agents)
#
# Usage:
#   amplifier tool invoke recipes operation=execute \
#     recipe_path=dot-graph:recipes/discovery-investigate-topic.yaml \
#     context='{"topic": {"name": "auth", "slug": "auth"}, "fidelity": "standard", "repo_path": "/path/to/repo", "output_dir": "/path/to/repo/.discovery"}'

name: discovery-investigate-topic
description: |
  Per-topic investigation sub-recipe for the discovery pipeline.
  Dispatches investigation agents (code-tracer, behavior-observer,
  integration-mapper) based on fidelity tier. Each agent writes findings
  and DOT diagrams to isolated subdirectories under the topic's module
  directory, ensuring genuine independence between perspectives.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "investigation", "sub-recipe", "dot-graph"]

context:
  topic: {}           # Required: topic object with 'name' and 'slug' keys
  fidelity: "standard"  # Required: "quick", "standard", or "deep"
  repo_path: ""       # Required: path to the target repository
  output_dir: ""      # Required: path to .discovery output directory

steps:
  # ---------------------------------------------------------------------------
  # Agent 1: Code Tracer (HOW) — traces execution paths, call chains, data flow
  # Runs at: standard, deep
  # ---------------------------------------------------------------------------
  - id: "code-tracer"
    agent: "dot-graph:discovery-code-tracer"
    condition: "{{fidelity}} != 'quick'"
    prompt: |
      ## Investigation Assignment: Code Tracing

      **Topic:** {{topic.name}}
      **Repository:** {{repo_path}}
      **Your artifact directory:** {{output_dir}}/modules/{{topic.slug}}/agents/code-tracer/

      Investigate HOW "{{topic.name}}" works at the code level in the repository at {{repo_path}}.

      ### Your Focus
      - Trace actual execution paths through the codebase using LSP
      - Use goToDefinition, findReferences, incomingCalls, outgoingCalls
      - Cite exact file:line evidence for every claim
      - Follow function calls, conditionals, and error paths

      ### Required Artifacts
      Write ALL of these to {{output_dir}}/modules/{{topic.slug}}/agents/code-tracer/:
      - **findings.md** — Main analysis with code-level narrative
      - **diagram.dot** — Valid GraphViz DOT diagram of execution flow or architecture

      ### Rules
      - Write to YOUR directory only. Never read other agents' output.
      - Every claim needs a file:line citation.
      - Use LSP first, grep second.
    output: "code_tracer_result"
    timeout: 1800

  # ---------------------------------------------------------------------------
  # Agent 2: Behavior Observer (WHAT) — catalogs real instances, quantifies
  # Runs at: deep only
  # ---------------------------------------------------------------------------
  - id: "behavior-observer"
    agent: "dot-graph:discovery-behavior-observer"
    condition: "{{fidelity}} == 'deep'"
    prompt: |
      ## Investigation Assignment: Behavior Observation

      **Topic:** {{topic.name}}
      **Repository:** {{repo_path}}
      **Your artifact directory:** {{output_dir}}/modules/{{topic.slug}}/agents/behavior-observer/

      Investigate WHAT "{{topic.name}}" actually looks like in practice in the repository at {{repo_path}}.

      ### Your Focus
      - Examine 10+ real instances of the mechanism in practice
      - Catalog structure, patterns, and anti-patterns from actual usage
      - Quantify — count instances, measure sizes, categorize types
      - Distinguish what actually exists from what documentation claims

      ### Required Artifacts
      Write ALL of these to {{output_dir}}/modules/{{topic.slug}}/agents/behavior-observer/:
      - **findings.md** — Main analysis with behavioral observations
      - **diagram.dot** — Valid GraphViz DOT diagram of relationships or taxonomy

      ### Rules
      - Write to YOUR directory only. Never read other agents' output.
      - Examine MANY real instances (10+ minimum).
      - Quantify your observations. "Most" is not evidence. "7 out of 12 (58%)" is evidence.
    output: "behavior_observer_result"
    timeout: 1800

  # ---------------------------------------------------------------------------
  # Agent 3: Integration Mapper (WHERE/WHY) — maps cross-boundary connections
  # Runs at: standard, deep
  # ---------------------------------------------------------------------------
  - id: "integration-mapper"
    agent: "dot-graph:discovery-integration-mapper"
    condition: "{{fidelity}} != 'quick'"
    prompt: |
      ## Investigation Assignment: Integration Mapping

      **Topic:** {{topic.name}}
      **Repository:** {{repo_path}}
      **Your artifact directory:** {{output_dir}}/modules/{{topic.slug}}/agents/integration-mapper/

      Investigate WHERE "{{topic.name}}" connects to other parts of the system and WHY those connections matter, in the repository at {{repo_path}}.

      ### Your Focus
      - Map how this component integrates across module boundaries
      - Find cross-cutting concerns, composition effects, and emergent behavior
      - Look at the spaces BETWEEN modules, not just within them
      - For every touchpoint: what crosses, which direction, what gets transformed

      ### Required Artifacts
      Write ALL of these to {{output_dir}}/modules/{{topic.slug}}/agents/integration-mapper/:
      - **integration-map.md** — Comprehensive cross-boundary analysis
      - **diagram.dot** — Valid GraphViz DOT diagram of integration points and data flow

      ### Rules
      - Write to YOUR directory only. Never read other agents' output.
      - Focus on BOUNDARIES, not internals. Other agents handle internals.
      - Every integration point should note: what crosses, which direction, what gets transformed.
    output: "integration_mapper_result"
    timeout: 1800
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_discovery_investigate_topic_recipe.py -v --no-header 2>&1 | tail -5`
Expected: All tests PASS

**Step 5: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add recipes/discovery-investigate-topic.yaml tests/test_discovery_investigate_topic_recipe.py && git commit -m "feat: add discovery-investigate-topic sub-recipe with tests"
```

---

### Task 2: Create `recipes/discovery-synthesize-module.yaml`

**Files:**
- Create: `recipes/discovery-synthesize-module.yaml`
- Test: `tests/test_discovery_synthesize_module_recipe.py`

**Step 1: Write the failing test**

Create `tests/test_discovery_synthesize_module_recipe.py`:

```python
"""
Tests for recipes/discovery-synthesize-module.yaml structure and content.
Validates the sub-recipe YAML parses correctly and has expected steps,
context variables, and quality gate loop logic.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"


@pytest.fixture(scope="module")
def recipe() -> dict:
    """Load the recipe YAML once per test module."""
    return yaml.safe_load(RECIPE_PATH.read_text())


# --- File existence ---


def test_recipe_file_exists():
    """recipes/discovery-synthesize-module.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-synthesize-module.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_is_valid_yaml():
    """Recipe must parse as valid YAML dict."""
    content = RECIPE_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "Recipe must parse to a dict"


# --- Top-level metadata ---


def test_recipe_has_name(recipe):
    """Recipe must have a 'name' key."""
    assert "name" in recipe, "Recipe must have 'name' key"
    assert recipe["name"] == "discovery-synthesize-module", (
        f"name must be 'discovery-synthesize-module', got: {recipe['name']}"
    )


def test_recipe_has_description(recipe):
    """Recipe must have a non-empty description."""
    assert "description" in recipe, "Recipe must have 'description' key"
    assert recipe["description"], "description must not be empty"


def test_recipe_has_version(recipe):
    """Recipe must have a version."""
    assert "version" in recipe, "Recipe must have 'version' key"


# --- Context variables ---


def test_recipe_has_context(recipe):
    """Recipe must declare context variables."""
    assert "context" in recipe, "Recipe must have 'context' key"


def test_recipe_context_has_required_vars(recipe):
    """Context must declare module_name, module_dir, fidelity, and output_dir."""
    ctx = recipe["context"]
    for var in ["module_name", "module_dir", "fidelity", "output_dir"]:
        assert var in ctx, f"context must declare '{var}'"


# --- Steps structure ---


def test_recipe_has_steps(recipe):
    """Recipe must have a 'steps' key (flat recipe, not staged)."""
    assert "steps" in recipe, "Recipe must have 'steps' key"
    assert "stages" not in recipe, "Sub-recipe must be flat (steps, not stages)"


def test_recipe_has_synthesize_step(recipe):
    """Recipe must have a 'synthesize' step with agent type."""
    step_ids = [s["id"] for s in recipe["steps"]]
    assert "synthesize" in step_ids, "Must have 'synthesize' step"
    step = next(s for s in recipe["steps"] if s["id"] == "synthesize")
    assert step.get("agent") == "dot-graph:discovery-synthesizer", (
        f"synthesize step must use agent 'dot-graph:discovery-synthesizer', got: {step.get('agent')}"
    )


def test_recipe_has_validate_step(recipe):
    """Recipe must have a 'validate' step."""
    step_ids = [s["id"] for s in recipe["steps"]]
    assert "validate" in step_ids, "Must have 'validate' step"


def test_recipe_has_check_quality_step(recipe):
    """Recipe must have a 'check-quality' step."""
    step_ids = [s["id"] for s in recipe["steps"]]
    assert "check-quality" in step_ids, "Must have 'check-quality' step"


# --- Quality gate loop ---


def test_recipe_has_quality_gate_loop(recipe):
    """Recipe must have while/loop logic for the quality gate (max 3 retries)."""
    # The quality gate can be implemented via:
    # 1. A while_condition on a step
    # 2. A loop wrapper around the synthesize/validate steps
    # 3. A max_iterations field
    # Check for any loop-related field in steps
    recipe_text = yaml.dump(recipe)
    has_loop = any(
        keyword in recipe_text
        for keyword in ["while", "max_iterations", "loop", "retry", "break_when"]
    )
    assert has_loop, (
        "Recipe must have quality gate loop logic (while_condition, max_iterations, "
        "retry, or break_when)"
    )


def test_quality_gate_has_max_retries(recipe):
    """Quality gate must limit retries (max 3 iterations)."""
    recipe_text = yaml.dump(recipe)
    # Must contain a reference to max iterations of 3
    assert "3" in recipe_text, (
        "Recipe must contain max retry count of 3 somewhere in the quality gate"
    )


# --- Synthesizer prompt references module dir ---


def test_synthesize_prompt_references_module(recipe):
    """Synthesize step prompt must reference the module_dir and module_name."""
    step = next(s for s in recipe["steps"] if s["id"] == "synthesize")
    prompt = step.get("prompt", "")
    assert "module_dir" in prompt, "synthesize prompt must reference module_dir"
    assert "module_name" in prompt, "synthesize prompt must reference module_name"


# --- Validate step invokes dot_graph ---


def test_validate_step_is_bash(recipe):
    """validate step must be a bash step invoking dot_graph validate."""
    step = next(s for s in recipe["steps"] if s["id"] == "validate")
    assert step.get("type") == "bash", "validate step must be type 'bash'"
    command = step.get("command", "")
    assert "validate" in command or "pydot" in command, (
        "validate step command must invoke validation"
    )
```

**Step 2: Run test to verify it fails**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_discovery_synthesize_module_recipe.py -v --no-header 2>&1 | head -5`
Expected: FAIL with "not found"

**Step 3: Write the recipe YAML**

Create `recipes/discovery-synthesize-module.yaml`:

```yaml
# discovery-synthesize-module.yaml
# Per-Module Synthesis Sub-Recipe with Quality Gate Loop
# Reads all agent investigation outputs for a module and produces a consensus
# DOT diagram + findings document. Validates the output and retries up to 3 times
# if validation fails.
#
# Called by: recipes/discovery-pipeline.yaml (foreach over discovered modules)
# Can also run standalone for re-synthesizing a single module.
#
# Quality gate: synthesize -> validate -> check -> retry if invalid (max 3)
#
# Usage:
#   amplifier tool invoke recipes operation=execute \
#     recipe_path=dot-graph:recipes/discovery-synthesize-module.yaml \
#     context='{"module_name": "auth", "module_dir": "/path/.discovery/modules/auth", "fidelity": "standard", "output_dir": "/path/.discovery"}'

name: discovery-synthesize-module
description: |
  Per-module synthesis sub-recipe for the discovery pipeline.
  Reads all agent investigation outputs for a given module, produces a
  consensus DOT diagram and findings document via the discovery-synthesizer
  agent, then validates the output. If validation fails, retries up to 3 times
  with the validation errors as feedback (quality gate loop).
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "synthesis", "quality-gate", "sub-recipe", "dot-graph"]

context:
  module_name: ""     # Required: name of the module being synthesized
  module_dir: ""      # Required: path to the module directory containing agent outputs
  fidelity: "standard"  # Required: fidelity tier (affects synthesis depth)
  output_dir: ""      # Required: path to .discovery output directory
  _retry_count: "0"   # Internal: current retry iteration
  _validation_errors: ""  # Internal: errors from previous validation attempt

steps:
  # ---------------------------------------------------------------------------
  # Step 1: Synthesize — agent reads all investigation outputs, produces consensus
  # ---------------------------------------------------------------------------
  - id: "synthesize"
    agent: "dot-graph:discovery-synthesizer"
    prompt: |
      ## Synthesis Assignment: {{module_name}}

      **Module directory:** {{module_dir}}
      **Fidelity tier:** {{fidelity}}
      **Output directory:** {{module_dir}}

      Read all agent investigation artifacts from {{module_dir}}/agents/ and produce
      a consensus synthesis for module "{{module_name}}".

      ### Agent Artifacts to Read
      List and read all files under {{module_dir}}/agents/ — each subdirectory
      (code-tracer/, behavior-observer/, integration-mapper/) contains an agent's
      independent findings and DOT diagrams.

      ### Required Output
      Write to {{module_dir}}/:
      - **diagram.dot** — Consensus DOT diagram synthesized from all agent perspectives.
        Must be valid GraphViz DOT. Use subgraphs for logical groupings.
      - **findings.md** — Consolidated findings with consensus, discrepancies, and
        open questions. Track discrepancies with IDs (D-01, D-02, ...).

      ### Validation Feedback
      {{_validation_errors}}

      If validation feedback is present above, fix the issues in your diagram.dot output.
      Focus on the specific errors reported and regenerate a corrected version.

      ### Cardinal Rule
      Never reconcile discrepancies by fiat. When agents disagree, the disagreement
      is information — track it, don't suppress it.
    output: "synthesis_result"
    timeout: 1200

  # ---------------------------------------------------------------------------
  # Step 2: Validate — run dot_graph validate on the synthesized diagram
  # ---------------------------------------------------------------------------
  - id: "validate"
    type: "bash"
    command: |
      python3 << 'EOF'
      import json
      from pathlib import Path

      module_dir = "{{module_dir}}"
      diagram_path = Path(module_dir) / "diagram.dot"

      result = {"valid": False, "errors": [], "diagram_exists": False}

      if not diagram_path.exists():
          result["errors"].append("diagram.dot not found in module directory")
          print(json.dumps(result))
          exit(0)

      result["diagram_exists"] = True
      dot_content = diagram_path.read_text()

      # Basic syntax validation via pydot
      try:
          import pydot
          graphs = pydot.graph_from_dot_data(dot_content)
          if not graphs or not graphs[0]:
              result["errors"].append("pydot failed to parse diagram.dot")
          else:
              result["valid"] = True
              result["node_count"] = len(graphs[0].get_nodes())
              result["edge_count"] = len(graphs[0].get_edges())
      except Exception as e:
          result["errors"].append(f"Validation error: {str(e)}")

      print(json.dumps(result))
      EOF
    output: "validation_result"
    parse_json: true
    timeout: 30

  # ---------------------------------------------------------------------------
  # Step 3: Check quality — determine if synthesis passed or needs retry
  # ---------------------------------------------------------------------------
  - id: "check-quality"
    type: "bash"
    command: |
      python3 << 'EOF'
      import json

      validation_raw = r"""{{validation_result}}"""
      validation = json.loads(validation_raw)

      retry_count = int("{{_retry_count}}" or "0")
      max_retries = 3

      if validation.get("valid", False):
          result = {
              "quality_passed": True,
              "retry_count": retry_count,
              "message": "Synthesis validated successfully"
          }
      elif retry_count >= max_retries:
          result = {
              "quality_passed": True,
              "retry_count": retry_count,
              "message": f"Max retries ({max_retries}) reached — keeping best attempt",
              "warning": "Synthesis has validation errors but max retries exhausted"
          }
      else:
          errors = validation.get("errors", [])
          result = {
              "quality_passed": False,
              "retry_count": retry_count + 1,
              "_retry_count": str(retry_count + 1),
              "_validation_errors": f"Previous validation failed (attempt {retry_count + 1}/{max_retries}). Errors: {json.dumps(errors)}. Fix these issues.",
              "message": f"Validation failed (attempt {retry_count + 1}/{max_retries}), retrying"
          }

      print(json.dumps(result))
      EOF
    output: "quality_check"
    parse_json: true
    timeout: 10
    while_condition: "{{quality_check.quality_passed}} == false"
    break_when: "{{quality_check.quality_passed}} == true"
    max_iterations: 3
    loop_back_to: "synthesize"
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_discovery_synthesize_module_recipe.py -v --no-header 2>&1 | tail -5`
Expected: All tests PASS

**Step 5: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add recipes/discovery-synthesize-module.yaml tests/test_discovery_synthesize_module_recipe.py && git commit -m "feat: add discovery-synthesize-module sub-recipe with quality gate loop and tests"
```

---

### Task 3: Create `recipes/discovery-pipeline.yaml`

**Files:**
- Create: `recipes/discovery-pipeline.yaml`
- Test: `tests/test_discovery_pipeline_recipe.py`

**Step 1: Write the failing test**

Create `tests/test_discovery_pipeline_recipe.py`:

```python
"""
Tests for recipes/discovery-pipeline.yaml structure and content.
Validates the outer orchestrator recipe has expected stages, approval gates,
context variables, sub-recipe references, and step structure.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-pipeline.yaml"


@pytest.fixture(scope="module")
def recipe() -> dict:
    """Load the recipe YAML once per test module."""
    return yaml.safe_load(RECIPE_PATH.read_text())


# --- File existence ---


def test_recipe_file_exists():
    """recipes/discovery-pipeline.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-pipeline.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_is_valid_yaml():
    """Recipe must parse as valid YAML dict."""
    content = RECIPE_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "Recipe must parse to a dict"


# --- Top-level metadata ---


def test_recipe_has_name(recipe):
    """Recipe must have a 'name' key."""
    assert "name" in recipe, "Recipe must have 'name' key"
    assert recipe["name"] == "discovery-pipeline", (
        f"name must be 'discovery-pipeline', got: {recipe['name']}"
    )


def test_recipe_has_description(recipe):
    """Recipe must have a non-empty description."""
    assert "description" in recipe, "Recipe must have 'description' key"
    assert recipe["description"], "description must not be empty"


def test_recipe_has_version(recipe):
    """Recipe must have a version."""
    assert "version" in recipe, "Recipe must have 'version' key"


# --- Context variables ---


def test_recipe_has_context(recipe):
    """Recipe must declare context variables."""
    assert "context" in recipe, "Recipe must have 'context' key"


def test_recipe_context_has_required_vars(recipe):
    """Context must declare repo_path, fidelity, and output_dir."""
    ctx = recipe["context"]
    for var in ["repo_path", "fidelity", "output_dir"]:
        assert var in ctx, f"context must declare '{var}'"


def test_recipe_context_fidelity_default(recipe):
    """fidelity must default to 'standard'."""
    assert recipe["context"]["fidelity"] == "standard", (
        f"fidelity default must be 'standard', got: {recipe['context']['fidelity']}"
    )


# --- Staged structure ---


def test_recipe_has_stages(recipe):
    """Recipe must use stages (staged recipe with approval gates)."""
    assert "stages" in recipe, "Recipe must have 'stages' key (staged recipe)"


def test_recipe_has_three_stages(recipe):
    """Recipe must have exactly 3 stages: scan, investigate, synthesize."""
    stages = recipe["stages"]
    assert len(stages) == 3, f"Expected 3 stages, found {len(stages)}"


def test_recipe_stage_names(recipe):
    """Stages must be named 'scan', 'investigate', 'synthesize'."""
    stage_names = [s["name"] for s in recipe["stages"]]
    assert stage_names == ["scan", "investigate", "synthesize"], (
        f"Stage names must be ['scan', 'investigate', 'synthesize'], got: {stage_names}"
    )


# --- Approval gates ---


def test_scan_stage_has_approval_gate(recipe):
    """scan stage must have an approval gate (user reviews topics before investigation)."""
    scan = next(s for s in recipe["stages"] if s["name"] == "scan")
    assert "approval" in scan, "scan stage must have 'approval' key"
    assert scan["approval"].get("required") is True, (
        "scan stage approval must be required"
    )


# --- Scan stage steps ---


def test_scan_stage_has_expected_steps(recipe):
    """scan stage must have change-detect, structural-scan, and topic-select steps."""
    scan = next(s for s in recipe["stages"] if s["name"] == "scan")
    step_ids = [s["id"] for s in scan["steps"]]
    assert "change-detect" in step_ids, "scan must have 'change-detect' step"
    assert "structural-scan" in step_ids, "scan must have 'structural-scan' step"
    assert "topic-select" in step_ids, "scan must have 'topic-select' step"


def test_topic_select_uses_prescan_agent(recipe):
    """topic-select step must reference discovery-prescan agent."""
    scan = next(s for s in recipe["stages"] if s["name"] == "scan")
    step = next(s for s in scan["steps"] if s["id"] == "topic-select")
    assert step.get("agent") == "dot-graph:discovery-prescan", (
        f"topic-select must use 'dot-graph:discovery-prescan', got: {step.get('agent')}"
    )


# --- Investigate stage steps ---


def test_investigate_stage_has_foreach(recipe):
    """investigate stage must have a step that iterates over topics."""
    investigate = next(s for s in recipe["stages"] if s["name"] == "investigate")
    steps = investigate["steps"]
    has_foreach = any("foreach" in s for s in steps)
    has_recipe_type = any(s.get("type") == "recipe" for s in steps)
    assert has_foreach or has_recipe_type, (
        "investigate stage must have a foreach or recipe step for per-topic investigation"
    )


def test_investigate_references_sub_recipe(recipe):
    """investigate stage must reference discovery-investigate-topic sub-recipe."""
    investigate = next(s for s in recipe["stages"] if s["name"] == "investigate")
    recipe_text = yaml.dump(investigate)
    assert "discovery-investigate-topic" in recipe_text, (
        "investigate stage must reference discovery-investigate-topic sub-recipe"
    )


# --- Synthesize stage steps ---


def test_synthesize_stage_has_expected_steps(recipe):
    """synthesize stage must have reconcile-modules, assemble, and final-validate steps."""
    synth = next(s for s in recipe["stages"] if s["name"] == "synthesize")
    step_ids = [s["id"] for s in synth["steps"]]
    assert "reconcile-modules" in step_ids, "synthesize must have 'reconcile-modules' step"
    assert "assemble" in step_ids, "synthesize must have 'assemble' step"
    assert "final-validate" in step_ids, "synthesize must have 'final-validate' step"


def test_synthesize_references_sub_recipe(recipe):
    """synthesize stage must reference discovery-synthesize-module sub-recipe."""
    synth = next(s for s in recipe["stages"] if s["name"] == "synthesize")
    recipe_text = yaml.dump(synth)
    assert "discovery-synthesize-module" in recipe_text, (
        "synthesize stage must reference discovery-synthesize-module sub-recipe"
    )


def test_synthesize_has_update_metadata_step(recipe):
    """synthesize stage must have an update-metadata step for last-run.json."""
    synth = next(s for s in recipe["stages"] if s["name"] == "synthesize")
    step_ids = [s["id"] for s in synth["steps"]]
    assert "update-metadata" in step_ids, "synthesize must have 'update-metadata' step"


# --- Sub-recipe files exist ---


def test_investigate_sub_recipe_exists():
    """The investigation sub-recipe file must exist."""
    path = REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"
    assert path.exists(), f"Sub-recipe not found: {path}"


def test_synthesize_sub_recipe_exists():
    """The synthesis sub-recipe file must exist."""
    path = REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"
    assert path.exists(), f"Sub-recipe not found: {path}"
```

**Step 2: Run test to verify it fails**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_discovery_pipeline_recipe.py -v --no-header 2>&1 | head -5`
Expected: FAIL with "not found" (pipeline recipe doesn't exist yet)

**Step 3: Write the recipe YAML**

Create `recipes/discovery-pipeline.yaml`:

```yaml
# discovery-pipeline.yaml
# Discovery Pipeline — Outer Orchestrator Recipe
# Main entry point for the codebase discovery pipeline.
# Staged recipe with an approval gate between scan and investigation.
#
# Stages:
#   1. scan       — change detection, structural prescan, topic selection
#   2. investigate — per-topic agent dispatch (approval required before this stage)
#   3. synthesize  — per-module reconciliation, DOT assembly, final validation
#
# Usage:
#   amplifier tool invoke recipes operation=execute \
#     recipe_path=dot-graph:recipes/discovery-pipeline.yaml \
#     context='{"repo_path": "/path/to/repo"}'
#
#   With options:
#   amplifier tool invoke recipes operation=execute \
#     recipe_path=dot-graph:recipes/discovery-pipeline.yaml \
#     context='{"repo_path": "/path/to/repo", "fidelity": "deep", "output_dir": "/custom/output"}'

name: discovery-pipeline
description: |
  Codebase discovery pipeline for the DOT graph bundle.
  Systematically walks a repository and generates DOT graph representations
  of its architecture. Builds bottom-up (file -> module -> subsystem -> overview)
  using multi-agent investigation with tiered fidelity (quick/standard/deep).

  Three stages:
  1. **Scan** — detect changes, run structural prescan, select investigation topics
  2. **Investigate** — dispatch investigation agents per topic (approval gate)
  3. **Synthesize** — reconcile agent outputs, assemble DOT hierarchy, validate

  Produces a persistent `.discovery/` directory with per-module DOT files,
  subsystem graphs, and a bounded overview diagram.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "pipeline", "architecture", "dot-graph", "multi-agent"]

recursion:
  max_depth: 3
  max_total_steps: 100

context:
  repo_path: ""              # Required: path to the target repository
  fidelity: "standard"       # Optional: "quick", "standard", or "deep"
  output_dir: ""             # Optional: defaults to {{repo_path}}/.discovery
  _approval_message: ""      # Populated by engine on approval

stages:
  # ==========================================================================
  # STAGE 1: Scan
  # Change detection, structural prescan, and topic selection.
  # No approval needed — this is cheap and fast.
  # ==========================================================================
  - name: "scan"
    steps:
      # Resolve default output_dir and detect changes
      - id: "change-detect"
        type: "bash"
        command: |
          python3 << 'EOF'
          import json
          import subprocess
          from pathlib import Path

          repo_path = "{{repo_path}}"
          output_dir = "{{output_dir}}" or f"{repo_path}/.discovery"
          fidelity = "{{fidelity}}" or "standard"

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "fidelity": fidelity,
              "is_fresh_run": True,
              "changed_files": [],
              "last_commit": None,
              "current_commit": None,
              "tier": fidelity
          }

          # Check for last-run.json
          last_run_path = Path(output_dir) / "last-run.json"
          if last_run_path.exists():
              try:
                  last_run = json.loads(last_run_path.read_text())
                  result["last_commit"] = last_run.get("commit_hash")
                  result["is_fresh_run"] = False
              except (json.JSONDecodeError, KeyError):
                  pass  # Corrupted — treat as fresh run

          # Get current commit hash
          try:
              cp = subprocess.run(
                  ["git", "rev-parse", "HEAD"],
                  capture_output=True, text=True, cwd=repo_path
              )
              if cp.returncode == 0:
                  result["current_commit"] = cp.stdout.strip()
          except FileNotFoundError:
              pass

          # If we have a previous commit, compute changed files
          if result["last_commit"] and result["current_commit"]:
              if result["last_commit"] == result["current_commit"]:
                  result["tier"] = "skip"
                  result["message"] = "No changes since last run"
              else:
                  try:
                      cp = subprocess.run(
                          ["git", "diff", "--name-only",
                           result["last_commit"], result["current_commit"]],
                          capture_output=True, text=True, cwd=repo_path
                      )
                      if cp.returncode == 0:
                          result["changed_files"] = [
                              f for f in cp.stdout.strip().split("\n") if f
                          ]
                  except FileNotFoundError:
                      pass

          # Create output directory
          Path(output_dir).mkdir(parents=True, exist_ok=True)

          print(json.dumps(result))
          EOF
        output: "change_result"
        parse_json: true
        timeout: 30

      # Run structural prescan on the repository
      - id: "structural-scan"
        type: "bash"
        condition: "{{change_result.tier}} != 'skip'"
        command: |
          python3 << 'EOF'
          import json, sys

          # Invoke prescan via the tool module
          try:
              sys.path.insert(0, ".")
              from amplifier_module_tool_dot_graph import prescan
              result = prescan.run_prescan("{{change_result.repo_path}}")
              print(json.dumps(result))
          except ImportError:
              # Fallback: basic directory listing
              from pathlib import Path
              repo = Path("{{change_result.repo_path}}")
              result = {
                  "repo_path": str(repo),
                  "fallback": True,
                  "files": [str(f.relative_to(repo)) for f in repo.rglob("*") if f.is_file()][:200]
              }
              print(json.dumps(result))
          EOF
        output: "scan_result"
        parse_json: true
        timeout: 60

      # Agent selects investigation topics from the structural scan
      - id: "topic-select"
        agent: "dot-graph:discovery-prescan"
        condition: "{{change_result.tier}} != 'skip'"
        prompt: |
          ## Topic Selection for Discovery Pipeline

          **Repository:** {{change_result.repo_path}}
          **Fidelity tier:** {{change_result.fidelity}}
          **Structural scan result:**
          ```json
          {{scan_result}}
          ```

          Based on the structural scan results, select 3-7 investigation topics
          for the discovery pipeline. Each topic should map to a module or
          cross-cutting concern that warrants architectural investigation.

          Adjust topic count by fidelity:
          - standard: 3-5 topics
          - deep: 5-7 topics

          Output a JSON array of topic objects. Each object must have:
          - "name": human-readable topic name
          - "slug": filesystem-safe slug (lowercase, hyphens)
          - "description": brief description of what to investigate

          Output ONLY the JSON array. No prose, no markdown wrapping.
        output: "topics"
        parse_json: true
        timeout: 600

    # APPROVAL GATE — user reviews topics before expensive investigation
    approval:
      required: true
      prompt: |
        ## Discovery Pipeline: Scan Complete

        **Repository:** {{change_result.repo_path}}
        **Fidelity:** {{change_result.fidelity}}
        **Topics selected:** {{topics}}

        ### What to Review
        - Are the selected topics the right focus areas?
        - Should any topics be added or removed?
        - Is the fidelity tier appropriate for the scope of changes?

        ### Estimated Agent Dispatch
        At **{{change_result.fidelity}}** fidelity, this will dispatch agents per topic:
        - standard: 2 agents per topic (code-tracer + integration-mapper)
        - deep: 3 agents per topic (+ behavior-observer)

        **APPROVE** to proceed with investigation.
        **DENY** to stop the pipeline.

  # ==========================================================================
  # STAGE 2: Investigate
  # Per-topic agent dispatch via sub-recipe.
  # ==========================================================================
  - name: "investigate"
    steps:
      # Create per-topic directory structure
      - id: "prepare-topics"
        type: "bash"
        command: |
          python3 << 'EOF'
          import json, os

          topics_raw = r"""{{topics}}"""
          topics = json.loads(topics_raw) if isinstance(topics_raw, str) else topics_raw
          output_dir = "{{change_result.output_dir}}"

          for topic in topics:
              slug = topic.get("slug", topic.get("name", "unknown"))
              agents_dir = os.path.join(output_dir, "modules", slug, "agents")
              for agent in ["code-tracer", "behavior-observer", "integration-mapper"]:
                  os.makedirs(os.path.join(agents_dir, agent), exist_ok=True)

          print(json.dumps({"prepared": True, "topic_count": len(topics)}))
          EOF
        output: "prep_result"
        parse_json: true
        timeout: 15

      # Dispatch investigation sub-recipe for each topic
      - id: "investigate-topics"
        type: "recipe"
        foreach: "{{topics}}"
        as: "topic"
        recipe: "@dot-graph:recipes/discovery-investigate-topic.yaml"
        context:
          topic: "{{topic}}"
          fidelity: "{{change_result.fidelity}}"
          repo_path: "{{change_result.repo_path}}"
          output_dir: "{{change_result.output_dir}}"
        output: "investigation_results"
        timeout: 7200

  # ==========================================================================
  # STAGE 3: Synthesize
  # Per-module reconciliation, DOT assembly, final validation.
  # ==========================================================================
  - name: "synthesize"
    steps:
      # Reconcile each module via the synthesis sub-recipe
      - id: "reconcile-modules"
        type: "recipe"
        foreach: "{{topics}}"
        as: "topic"
        recipe: "@dot-graph:recipes/discovery-synthesize-module.yaml"
        context:
          module_name: "{{topic.slug}}"
          module_dir: "{{change_result.output_dir}}/modules/{{topic.slug}}"
          fidelity: "{{change_result.fidelity}}"
          output_dir: "{{change_result.output_dir}}"
        output: "reconciliation_results"
        timeout: 7200

      # Assemble module DOTs into subsystem + overview hierarchy
      - id: "assemble"
        type: "bash"
        command: |
          python3 << 'EOF'
          import json, os
          from pathlib import Path

          output_dir = "{{change_result.output_dir}}"
          modules_dir = Path(output_dir) / "modules"

          # Build manifest from discovered modules
          manifest = {"modules": {}, "subsystems": {}, "output_dir": output_dir}

          if modules_dir.exists():
              for module_path in sorted(modules_dir.iterdir()):
                  if module_path.is_dir():
                      dot_file = module_path / "diagram.dot"
                      if dot_file.exists():
                          manifest["modules"][module_path.name] = {
                              "dot_path": str(dot_file),
                              "subsystem": "default"
                          }

          # Invoke assemble via the tool module
          try:
              from amplifier_module_tool_dot_graph import assemble
              result = assemble.run_assemble(manifest, output_dir)
              print(json.dumps(result))
          except ImportError:
              print(json.dumps({
                  "fallback": True,
                  "manifest": manifest,
                  "message": "assemble module not available"
              }))
          EOF
        output: "assemble_result"
        parse_json: true
        timeout: 120

      # Validate all output DOT files
      - id: "final-validate"
        type: "bash"
        command: |
          python3 << 'EOF'
          import json
          from pathlib import Path

          output_dir = "{{change_result.output_dir}}"
          results = {"validated": [], "errors": [], "overview_stats": None}

          # Find all .dot files in output
          dot_files = list(Path(output_dir).rglob("*.dot"))
          results["total_dot_files"] = len(dot_files)

          try:
              import pydot
              for dot_file in dot_files:
                  try:
                      content = dot_file.read_text()
                      graphs = pydot.graph_from_dot_data(content)
                      if graphs and graphs[0]:
                          results["validated"].append({
                              "path": str(dot_file.relative_to(output_dir)),
                              "valid": True,
                              "nodes": len(graphs[0].get_nodes()),
                              "edges": len(graphs[0].get_edges())
                          })
                      else:
                          results["errors"].append({
                              "path": str(dot_file.relative_to(output_dir)),
                              "error": "Failed to parse"
                          })
                  except Exception as e:
                      results["errors"].append({
                          "path": str(dot_file.relative_to(output_dir)),
                          "error": str(e)
                      })
          except ImportError:
              results["errors"].append({"error": "pydot not available"})

          results["valid_count"] = len(results["validated"])
          results["error_count"] = len(results["errors"])
          results["all_valid"] = len(results["errors"]) == 0
          print(json.dumps(results))
          EOF
        output: "final_validation"
        parse_json: true
        timeout: 60

      # Write last-run.json metadata
      - id: "update-metadata"
        type: "bash"
        command: |
          python3 << 'EOF'
          import json
          from datetime import datetime, timezone
          from pathlib import Path

          output_dir = "{{change_result.output_dir}}"
          metadata = {
              "commit_hash": "{{change_result.current_commit}}",
              "timestamp": datetime.now(timezone.utc).isoformat(),
              "fidelity": "{{change_result.fidelity}}",
              "repo_path": "{{change_result.repo_path}}",
              "valid_files": {{final_validation.valid_count}},
              "error_files": {{final_validation.error_count}}
          }

          last_run_path = Path(output_dir) / "last-run.json"
          last_run_path.write_text(json.dumps(metadata, indent=2))
          print(json.dumps({"written": str(last_run_path), "metadata": metadata}))
          EOF
        output: "metadata_result"
        parse_json: true
        timeout: 10

final_output: "metadata_result"
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_discovery_pipeline_recipe.py -v --no-header 2>&1 | tail -5`
Expected: All tests PASS

**Step 5: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add recipes/discovery-pipeline.yaml tests/test_discovery_pipeline_recipe.py && git commit -m "feat: add discovery-pipeline outer orchestrator recipe with tests"
```

---

### Task 4: Update `tests/test_final_verification.py`

**Files:**
- Modify: `tests/test_final_verification.py`

**Step 1: Read the current file**

The file is at `tests/test_final_verification.py`. It currently tracks 24 expected bundle files and has a `test_total_file_count()` that asserts exactly 24.

**Step 2: Add recipe directory to expected files list and update count**

Add the 3 recipe files to `EXPECTED_FILES`. After the last entry `"context/discovery-awareness.md",` add:

```python
    # Phase D: discovery pipeline recipes
    "recipes/discovery-pipeline.yaml",
    "recipes/discovery-investigate-topic.yaml",
    "recipes/discovery-synthesize-module.yaml",
```

Update the comment above `test_bundle_file_exists` from:
```python
# --- Step 1: Complete file tree (24 files) ---
```
to:
```python
# --- Step 1: Complete file tree (27 files) ---
```

Update the `EXPECTED_FILES` comment from:
```python
# The 24 expected bundle files (21 original + 3 Phase A additions)
```
to:
```python
# The 27 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes)
```

Update `test_total_file_count()` docstring from:
```python
    """Step 6: Total bundle file count is exactly 24 (21 original + 3 Phase A)."""
```
to:
```python
    """Step 6: Total bundle file count is exactly 27 (21 original + 3 Phase A + 3 Phase D)."""
```

Update the assertion in `test_total_file_count()` from:
```python
    assert len(present) == 24, (
        f"Expected 24 bundle files, found {len(present)}. "
```
to:
```python
    assert len(present) == 27, (
        f"Expected 27 bundle files, found {len(present)}. "
```

**Step 3: Run all verification tests**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/test_final_verification.py -v --no-header 2>&1 | tail -10`
Expected: All tests PASS (including the 3 new parametrized file existence tests)

**Step 4: Run the full test suite**

Run: `cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/ -v --tb=short 2>&1 | tail -15`
Expected: All tests PASS (848 existing + ~55 new recipe tests = ~900+)

**Step 5: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add tests/test_final_verification.py && git commit -m "test: add recipe files to final verification checks"
```

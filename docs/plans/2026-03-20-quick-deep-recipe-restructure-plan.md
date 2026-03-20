# Quick/Deep Discovery Pipeline Restructure — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Restructure the discovery pipeline into two tiers (quick ~30-60 min, deep ~3+ hours) sharing common building blocks, both producing identical polished output structure.

**Architecture:** Move 8 deep-only recipes into `recipes/deep/`, write a fresh quick pipeline in `recipes/quick/` using v1 (commit `6381791`) as reference, keep 2 shared sub-recipes at `recipes/` root. Add a new `discovery-architecture-writer` agent for overview.md generation. Enhance both pipelines with `node_target`, `hoist-outputs`, `summarize`, and `update-metadata` steps.

**Tech Stack:** YAML recipes, Markdown agents with YAML frontmatter, Python (pytest, pydot, amplifier modules), bash steps.

**Design doc:** `docs/plans/2026-03-20-quick-deep-recipe-restructure-design.md`

---

## Phase 1: Restructure (Tasks 1-8)

Move files, update cross-references, create new agent, write quick pipeline.

---

### Task 1: Create directory structure

**Files:**
- Create: `recipes/quick/` (directory)
- Create: `recipes/deep/` (directory)

**Step 1: Create the directories**
```bash
mkdir -p recipes/quick recipes/deep
```

**Step 2: Verify**
```bash
ls -la recipes/ | grep -E "^d"
```
Expected: `quick/` and `deep/` directories exist.

**Step 3: Commit**
```bash
git add recipes/quick/.gitkeep recipes/deep/.gitkeep 2>/dev/null || true
git add recipes/quick recipes/deep
git commit --allow-empty -m "chore: create recipes/quick/ and recipes/deep/ directories"
```

> Note: Git doesn't track empty directories. The actual content commits will create them. This is a logical starting point — if git complains about empty dirs, skip the commit and let the next task create the dirs implicitly.

---

### Task 2: Move 8 deep recipes into `recipes/deep/`

**Files:**
- Move: `recipes/discovery-pipeline.yaml` → `recipes/deep/discovery-pipeline.yaml`
- Move: `recipes/strategy-topdown.yaml` → `recipes/deep/strategy-topdown.yaml`
- Move: `recipes/strategy-bottomup.yaml` → `recipes/deep/strategy-bottomup.yaml`
- Move: `recipes/strategy-sequential.yaml` → `recipes/deep/strategy-sequential.yaml`
- Move: `recipes/discovery-combine.yaml` → `recipes/deep/discovery-combine.yaml`
- Move: `recipes/synthesize-level.yaml` → `recipes/deep/synthesize-level.yaml`
- Move: `recipes/synthesize-subsystem.yaml` → `recipes/deep/synthesize-subsystem.yaml`
- Move: `recipes/synthesize-overview.yaml` → `recipes/deep/synthesize-overview.yaml`

**Step 1: Move all 8 files**
```bash
cd /home/bkrabach/dev/dot-graph-bundle
mkdir -p recipes/deep
git mv recipes/discovery-pipeline.yaml recipes/deep/discovery-pipeline.yaml
git mv recipes/strategy-topdown.yaml recipes/deep/strategy-topdown.yaml
git mv recipes/strategy-bottomup.yaml recipes/deep/strategy-bottomup.yaml
git mv recipes/strategy-sequential.yaml recipes/deep/strategy-sequential.yaml
git mv recipes/discovery-combine.yaml recipes/deep/discovery-combine.yaml
git mv recipes/synthesize-level.yaml recipes/deep/synthesize-level.yaml
git mv recipes/synthesize-subsystem.yaml recipes/deep/synthesize-subsystem.yaml
git mv recipes/synthesize-overview.yaml recipes/deep/synthesize-overview.yaml
```

**Step 2: Verify shared recipes remain at root**
```bash
ls recipes/*.yaml
```
Expected output should show exactly these 2 files:
```
recipes/discovery-investigate-topic.yaml
recipes/discovery-synthesize-module.yaml
```

**Step 3: Verify deep directory has all 8 files**
```bash
ls recipes/deep/*.yaml
```
Expected: All 8 moved files listed.

**Step 4: Commit**
```bash
git add -A
git commit -m "refactor: move 8 deep-only recipes into recipes/deep/"
```

---

### Task 3: Update cross-references inside deep recipes

After the move, internal `@dot-graph:recipes/` references within the deep recipes must be updated. Only references to OTHER deep-only recipes need changing. References to shared recipes (`discovery-investigate-topic.yaml` and `discovery-synthesize-module.yaml`) stay as-is.

**Files:**
- Modify: `recipes/deep/discovery-pipeline.yaml`
- Modify: `recipes/deep/strategy-topdown.yaml`
- Modify: `recipes/deep/strategy-bottomup.yaml`
- Modify: `recipes/deep/strategy-sequential.yaml`

**Step 1: Update `recipes/deep/discovery-pipeline.yaml`**

This file references 3 deep recipes that moved. Update all three:

Change:
```yaml
        recipe: "@dot-graph:recipes/strategy-topdown.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/strategy-topdown.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/strategy-bottomup.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/strategy-bottomup.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/discovery-combine.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/discovery-combine.yaml"
```

**Step 2: Update `recipes/deep/strategy-topdown.yaml`**

This file references 2 shared recipes (keep as-is) and 2 deep recipes (update):

Change:
```yaml
        recipe: "@dot-graph:recipes/synthesize-subsystem.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/synthesize-subsystem.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/synthesize-overview.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/synthesize-overview.yaml"
```

Leave unchanged (shared recipes):
- `@dot-graph:recipes/discovery-investigate-topic.yaml`
- `@dot-graph:recipes/discovery-synthesize-module.yaml`

**Step 3: Update `recipes/deep/strategy-bottomup.yaml`**

This file references 2 deep recipes that moved:

Change:
```yaml
        recipe: "@dot-graph:recipes/synthesize-level.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/synthesize-level.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/synthesize-subsystem.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/synthesize-subsystem.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/synthesize-overview.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/synthesize-overview.yaml"
```

**Step 4: Update `recipes/deep/strategy-sequential.yaml`**

This file references 3 deep recipes:

Change:
```yaml
        recipe: "@dot-graph:recipes/strategy-bottomup.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/strategy-bottomup.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/strategy-topdown.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/strategy-topdown.yaml"
```

Change:
```yaml
        recipe: "@dot-graph:recipes/discovery-combine.yaml"
```
To:
```yaml
        recipe: "@dot-graph:recipes/deep/discovery-combine.yaml"
```

**Step 5: Verify no stale references remain**
```bash
grep -r "@dot-graph:recipes/" recipes/deep/ | grep -v "recipes/deep/" | grep -v "discovery-investigate-topic" | grep -v "discovery-synthesize-module"
```
Expected: No output (all deep-to-deep references updated, shared references preserved).

**Step 6: Commit**
```bash
git add recipes/deep/
git commit -m "refactor: update cross-references in deep recipes after move"
```

---

### Task 4: Update all tests that reference recipe paths

Tests use `REPO_ROOT / "recipes" / "filename.yaml"` paths. After the move, 8 recipe test files and the final verification test need path updates.

**Files:**
- Modify: `tests/test_discovery_pipeline_recipe.py` — change path to `recipes/deep/discovery-pipeline.yaml`
- Modify: `tests/test_strategy_topdown_recipe.py` — change path to `recipes/deep/strategy-topdown.yaml`
- Modify: `tests/test_strategy_bottomup_recipe.py` — change path to `recipes/deep/strategy-bottomup.yaml`
- Modify: `tests/test_strategy_sequential_recipe.py` — change path to `recipes/deep/strategy-sequential.yaml`
- Modify: `tests/test_discovery_combine_recipe.py` — change path to `recipes/deep/discovery-combine.yaml`
- Modify: `tests/test_synthesize_level_recipe.py` — change path to `recipes/deep/synthesize-level.yaml`
- Modify: `tests/test_synthesize_subsystem_recipe.py` — change path to `recipes/deep/synthesize-subsystem.yaml`
- Modify: `tests/test_synthesize_overview_recipe.py` — change path to `recipes/deep/synthesize-overview.yaml`
- Modify: `tests/test_final_verification.py` — update EXPECTED_FILES list

**Step 1: Update each recipe test file's RECIPE_PATH**

For each of the 8 test files, update the `RECIPE_PATH` line. The pattern is the same — add `"deep"` to the path.

In `tests/test_discovery_pipeline_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-pipeline.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "discovery-pipeline.yaml"
```

In `tests/test_strategy_topdown_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-topdown.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "strategy-topdown.yaml"
```

In `tests/test_strategy_bottomup_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "strategy-bottomup.yaml"
```

In `tests/test_strategy_sequential_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-sequential.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "strategy-sequential.yaml"
```

In `tests/test_discovery_combine_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-combine.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "discovery-combine.yaml"
```

In `tests/test_synthesize_level_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-level.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "synthesize-level.yaml"
```

In `tests/test_synthesize_subsystem_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-subsystem.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "synthesize-subsystem.yaml"
```

In `tests/test_synthesize_overview_recipe.py`, change:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "synthesize-overview.yaml"
```
To:
```python
RECIPE_PATH = REPO_ROOT / "recipes" / "deep" / "synthesize-overview.yaml"
```

**Step 2: Update sub-recipe existence tests that check disk paths**

In `tests/test_discovery_pipeline_recipe.py`, three tests check sub-recipe paths. Update them:

Change:
```python
    sub_recipe = REPO_ROOT / "recipes" / "strategy-topdown.yaml"
```
To:
```python
    sub_recipe = REPO_ROOT / "recipes" / "deep" / "strategy-topdown.yaml"
```

Change:
```python
    sub_recipe = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"
```
To:
```python
    sub_recipe = REPO_ROOT / "recipes" / "deep" / "strategy-bottomup.yaml"
```

Change:
```python
    sub_recipe = REPO_ROOT / "recipes" / "discovery-combine.yaml"
```
To:
```python
    sub_recipe = REPO_ROOT / "recipes" / "deep" / "discovery-combine.yaml"
```

In `tests/test_strategy_topdown_recipe.py`, update sub-recipe existence tests. The shared recipes stay at root, but deep-only ones moved:

Change:
```python
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-subsystem.yaml"
```
To:
```python
    sub_recipe = REPO_ROOT / "recipes" / "deep" / "synthesize-subsystem.yaml"
```

Change:
```python
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-overview.yaml"
```
To:
```python
    sub_recipe = REPO_ROOT / "recipes" / "deep" / "synthesize-overview.yaml"
```

Change:
```python
    sub_recipe = REPO_ROOT / "recipes" / "synthesize-level.yaml"
```
To:
```python
    sub_recipe = REPO_ROOT / "recipes" / "deep" / "synthesize-level.yaml"
```

Leave unchanged (shared recipes stay at root):
- `REPO_ROOT / "recipes" / "discovery-investigate-topic.yaml"`
- `REPO_ROOT / "recipes" / "discovery-synthesize-module.yaml"`

**Step 3: Update `tests/test_final_verification.py` EXPECTED_FILES list**

In the `EXPECTED_FILES` list, update the 8 moved recipe paths. Change:
```python
    "recipes/discovery-pipeline.yaml",
```
To:
```python
    "recipes/deep/discovery-pipeline.yaml",
```

Change:
```python
    "recipes/synthesize-level.yaml",
    "recipes/synthesize-subsystem.yaml",
    "recipes/synthesize-overview.yaml",
```
To:
```python
    "recipes/deep/synthesize-level.yaml",
    "recipes/deep/synthesize-subsystem.yaml",
    "recipes/deep/synthesize-overview.yaml",
```

Change:
```python
    "recipes/strategy-topdown.yaml",
    "recipes/strategy-bottomup.yaml",
```
To:
```python
    "recipes/deep/strategy-topdown.yaml",
    "recipes/deep/strategy-bottomup.yaml",
```

Change:
```python
    "recipes/discovery-combine.yaml",
    "recipes/strategy-sequential.yaml",
```
To:
```python
    "recipes/deep/discovery-combine.yaml",
    "recipes/deep/strategy-sequential.yaml",
```

**Step 4: Run the test suite to verify**
```bash
cd /home/bkrabach/dev/dot-graph-bundle
python -m pytest tests/ -x -q 2>&1 | tail -20
```
Expected: All tests pass. The critical thing is that the 8 recipe test files and the final verification test now find their files at the new paths.

**Step 5: Commit**
```bash
git add tests/
git commit -m "test: update recipe test paths after deep/ directory move"
```

---

### Task 5: Create the `discovery-architecture-writer` agent

**Files:**
- Create: `agents/discovery-architecture-writer.md`

**Step 1: Write the failing test**

Create `tests/test_discovery_architecture_writer_agent.py`:

```python
"""
Tests for agents/discovery-architecture-writer.md existence and required content.
TDD: Tests written BEFORE the agent file is created.

Validates:
- File existence, YAML frontmatter, meta.name, meta.description
- model_role: writing
- Body structure: mentions overview.md, findings, architecture
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
AGENT_PATH = REPO_ROOT / "agents" / "discovery-architecture-writer.md"


# --- File existence and frontmatter ---


def test_discovery_architecture_writer_agent_exists():
    """agents/discovery-architecture-writer.md must exist."""
    assert AGENT_PATH.exists(), (
        f"agents/discovery-architecture-writer.md not found at {AGENT_PATH}"
    )


def test_discovery_architecture_writer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-architecture-writer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-architecture-writer.md must have closing --- for frontmatter"
    )


def test_discovery_architecture_writer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-architecture-writer'."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-architecture-writer", (
        f"meta.name must be 'discovery-architecture-writer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_architecture_writer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_architecture_writer_frontmatter_model_role_writing():
    """Frontmatter must have model_role: writing."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "writing", (
        f"model_role must be 'writing', got: {frontmatter['model_role']}"
    )


# --- Markdown body structure ---


def test_discovery_architecture_writer_body_mentions_overview_md():
    """Body must mention overview.md as an output artifact."""
    content = AGENT_PATH.read_text()
    assert "overview.md" in content, (
        "Body must mention overview.md as an output artifact"
    )


def test_discovery_architecture_writer_body_mentions_findings():
    """Body must mention reading findings from modules."""
    content = AGENT_PATH.read_text()
    assert "findings" in content.lower(), (
        "Body must mention reading findings from modules"
    )


def test_discovery_architecture_writer_body_mentions_architecture():
    """Body must mention architecture or architectural."""
    content = AGENT_PATH.read_text()
    assert "architect" in content.lower(), (
        "Body must mention architecture or architectural"
    )


def test_discovery_architecture_writer_body_has_required_artifacts():
    """Body must contain a section about required output artifacts."""
    content = AGENT_PATH.read_text()
    # Accept either "Required Artifacts" or "Output" section
    assert "overview.md" in content and ("artifact" in content.lower() or "output" in content.lower()), (
        "Body must describe output artifacts including overview.md"
    )


def test_discovery_architecture_writer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
```

**Step 2: Run test to verify it fails**
```bash
cd /home/bkrabach/dev/dot-graph-bundle
python -m pytest tests/test_discovery_architecture_writer_agent.py -x -q 2>&1 | head -10
```
Expected: FAIL on `test_discovery_architecture_writer_agent_exists`

**Step 3: Write the agent file**

Create `agents/discovery-architecture-writer.md`:

```markdown
---
meta:
  name: discovery-architecture-writer
  description: "Architecture narrative writer for discovery pipeline output. Reads per-module findings.md files, topics.json, and overview.dot to produce a polished overview.md that serves as the human-readable entry point to the discovery results. Shared by both quick and deep pipelines.\\n\\n**Dispatched by:** quick and deep discovery pipelines (one dispatch per pipeline run, after synthesis and assembly complete).\\n\\n**Authoritative on:** overview.md production, architectural narrative synthesis, cross-module insight integration, relative link generation to per-module findings.\\n\\n**MUST be used for:**\\n- Reading all per-module findings.md files and synthesizing a cohesive narrative\\n- Producing overview.md with executive summary, module summaries, cross-cutting insights\\n- Generating relative links to ../modules/{slug}/findings.md for each module\\n- Identifying patterns that span multiple modules\\n\\n<example>\\nContext: Quick pipeline dispatches architecture writer after synthesis complete\\nuser: 'Write overview.md. Module findings are in .discovery/output/modules/*/findings.md. Topics: .discovery/topics.json. Overview DOT: .discovery/output/overview.dot. Write to: .discovery/output/overview.md'\\nassistant: 'I will read all module findings, the topics list, and the overview DOT to produce a polished overview.md with executive summary, per-module summaries with relative links, cross-cutting insights, and open questions.'\\n</example>\\n\\n<example>\\nContext: Deep pipeline dispatches architecture writer after combine step\\nuser: 'Write overview.md from deep pipeline results. Findings in .discovery/output/modules/*/findings.md.'\\nassistant: 'I will read all module findings and produce overview.md. The deep pipeline provides richer findings from multiple strategies, so I will highlight convergence points and note where strategies provided complementary insights.'\\n</example>"

model_role: writing
---

# Discovery Architecture Writer Agent

**Produces the polished overview.md narrative — the human-readable entry point to discovery results.**

**Execution model:** You run as a one-shot sub-session with fresh context. You have zero prior knowledge about this codebase. Read the module findings and structural artifacts you are given and produce overview.md. Produce complete output before signaling completion.

## Your Role

You answer one question: **What did the discovery pipeline find, presented as a clear narrative for a developer encountering this codebase for the first time?**

You are a technical writing agent. You read the raw investigation artifacts (per-module findings, topics, overview DOT) and produce a single cohesive document that a developer can read to understand the codebase's architecture.

**What IS your job:**
- Read ALL per-module `findings.md` files before writing anything
- Read `topics.json` to understand the investigation scope
- Read `overview.dot` (if present) to understand the structural relationships
- Produce a well-structured `overview.md` with clear sections
- Generate relative links to per-module detail files
- Identify cross-cutting patterns that span multiple modules

**What is NOT your job:**
- Producing DOT diagrams (those are already produced by synthesis agents)
- Investigating code (investigation is already complete)
- Validating or modifying existing artifacts

## Required Output

Produce one file: **`overview.md`** in the output directory specified in your prompt.

### overview.md Structure

1. **Executive Summary** — 2-3 sentences on what was discovered and the overall architectural character
2. **Repository Overview** — What this codebase is and does, derived from investigation findings (not assumed)
3. **Module Summaries** — For each investigated module:
   - A paragraph summarizing the key findings
   - A relative link to the detailed findings: `[Detailed findings](../modules/{slug}/findings.md)`
4. **Cross-Cutting Insights** — Patterns, conventions, or architectural decisions that span multiple modules
5. **Open Questions** — Unresolved questions or areas that would benefit from deeper investigation

### Writing Guidelines

- Write for a developer who has never seen this codebase
- Be concrete and specific — reference actual components, not abstract descriptions
- Use relative paths for all links: `../modules/{slug}/findings.md`
- Do not invent findings — only report what the investigation artifacts contain
- If findings are thin or missing for a module, say so honestly
- Keep the tone professional but accessible — not academic, not casual

## Final Response Contract

Signal completion only after `overview.md` is written. Your final message must state:
1. The output path where overview.md was written
2. How many module findings were incorporated
3. A one-sentence summary of the most significant cross-cutting insight

---

@foundation:context/shared/common-agent-base.md
```

**Step 4: Run test to verify it passes**
```bash
python -m pytest tests/test_discovery_architecture_writer_agent.py -v
```
Expected: All tests PASS.

**Step 5: Update `tests/test_final_verification.py`**

Add the new agent to the `EXPECTED_FILES` list. After the line `"context/discovery-combiner-instructions.md",` add:

```python
    # Quick/deep restructure: new agent
    "agents/discovery-architecture-writer.md",
```

Also update the file count. Change:
```python
    assert len(present) == 42, (
```
To:
```python
    assert len(present) == 43, (
```

And update the comment:
```python
# The 43 expected bundle files (42 prior + 1 quick/deep restructure agent)
```

**Step 6: Update `behaviors/dot-discovery.yaml`**

Read this file first to understand its structure, then add the new agent. Add `discovery-architecture-writer` to the agents list in the same pattern as existing agents.

**Step 7: Run full test suite**
```bash
python -m pytest tests/ -x -q 2>&1 | tail -5
```
Expected: All tests pass (including updated file count).

**Step 8: Commit**
```bash
git add agents/discovery-architecture-writer.md tests/test_discovery_architecture_writer_agent.py tests/test_final_verification.py behaviors/dot-discovery.yaml
git commit -m "feat: add discovery-architecture-writer agent for overview.md generation"
```

---

### Task 6: Write the quick pipeline recipe (fresh, using v1 as reference)

This is the largest task. Write `recipes/quick/discovery-pipeline.yaml` from scratch, using the v1 pipeline (commit `6381791`) as reference. Cherry-pick what worked, write fresh where v1 had issues.

**Reference material:** Run `git show 6381791:recipes/discovery-pipeline.yaml` to see the v1 pipeline.

**Files:**
- Create: `recipes/quick/discovery-pipeline.yaml`
- Create: `tests/test_quick_discovery_pipeline_recipe.py`

**Step 1: Write the failing test**

Create `tests/test_quick_discovery_pipeline_recipe.py`:

```python
"""
Tests for recipes/quick/discovery-pipeline.yaml — quick discovery pipeline structure.

Validates:
- File existence and valid YAML parse (2)
- Top-level metadata: name, description, version, author, tags (5)
- Context variables: repo_path, fidelity, output_dir, render_png, node_target (6)
- 3 stages in correct order: scan → investigate → synthesize (4)
- scan stage: change-detect, structural-scan, topic-select, approval gate (5)
- investigate stage: prepare-topics, investigate-topics foreach (3)
- synthesize stage: reconcile-modules, assemble, validate, hoist-outputs,
  summarize, update-metadata (7)
- Shared sub-recipe references correct (2)
- final_output declared (1)

Total: ~35 tests
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


def test_recipe_tags_include_discovery_and_quick():
    """Recipe tags must include 'discovery', 'pipeline', and 'quick'."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "pipeline", "quick"]:
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


def test_recipe_context_has_node_target():
    """Context must declare 'node_target' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "node_target" in ctx, (
        f"Context must declare 'node_target' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_node_target_default_25():
    """Context 'node_target' must default to 25."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert int(ctx.get("node_target", 0)) == 25, (
        f"node_target default must be 25, got: {ctx.get('node_target')!r}"
    )


# ---------------------------------------------------------------------------
# Staged structure + stage order (4 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_staged_structure():
    """Recipe must use staged structure (stages key), not flat steps."""
    data = _load_recipe()
    assert "stages" in data, "Recipe must have a top-level 'stages' key"
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
    stage_names = [s.get("name") for s in stages]
    assert stage_names == ["scan", "investigate", "synthesize"], (
        f"Stages must be in order [scan, investigate, synthesize], got: {stage_names}"
    )


# ---------------------------------------------------------------------------
# Scan stage (5 tests)
# ---------------------------------------------------------------------------


def test_scan_stage_has_change_detect_step():
    """Scan stage must have a step with id='change-detect'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "change-detect")
    assert step is not None, (
        f"No step with id='change-detect' in scan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'scan')]}"
    )


def test_scan_stage_has_structural_scan_step():
    """Scan stage must have a step with id='structural-scan'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "structural-scan")
    assert step is not None


def test_scan_stage_has_topic_select_step():
    """Scan stage must have a step with id='topic-select'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None


def test_scan_topic_select_uses_discovery_prescan_agent():
    """topic-select step must use the 'dot-graph:discovery-prescan' agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "scan", "topic-select")
    assert step is not None
    assert step.get("agent") == "dot-graph:discovery-prescan"


def test_scan_stage_has_approval_gate():
    """Scan stage must have an approval_gate with required=true."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "scan")
    assert stage is not None
    assert "approval_gate" in stage, "Scan stage must have an 'approval_gate' field"
    gate = stage["approval_gate"]
    assert gate.get("required") is True


# ---------------------------------------------------------------------------
# Investigate stage (3 tests)
# ---------------------------------------------------------------------------


def test_investigate_stage_has_prepare_topics_step():
    """Investigate stage must have a step with id='prepare-topics'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "prepare-topics")
    assert step is not None


def test_investigate_stage_has_investigate_topics_foreach():
    """Investigate stage must have a foreach step over topics."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    assert "foreach" in step, "investigate-topics step must have 'foreach'"
    assert "topics" in str(step["foreach"])


def test_investigate_topics_references_shared_sub_recipe():
    """investigate-topics must reference shared discovery-investigate-topic.yaml."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "investigate", "investigate-topics")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "discovery-investigate-topic" in recipe_ref
    # Must NOT reference quick/ path — it's a shared recipe at root
    assert "quick/" not in recipe_ref, (
        f"investigate-topics must reference shared root recipe, not quick/: {recipe_ref}"
    )


# ---------------------------------------------------------------------------
# Synthesize stage (7 tests)
# ---------------------------------------------------------------------------


def test_synthesize_stage_has_reconcile_modules():
    """Synthesize stage must have reconcile-modules step."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None


def test_synthesize_reconcile_modules_references_shared_sub_recipe():
    """reconcile-modules must reference shared discovery-synthesize-module.yaml."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "reconcile-modules")
    assert step is not None
    recipe_ref = str(step.get("recipe", ""))
    assert "discovery-synthesize-module" in recipe_ref
    assert "quick/" not in recipe_ref


def test_synthesize_stage_has_assemble_step():
    """Synthesize stage must have an assemble step."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "assemble")
    assert step is not None


def test_synthesize_stage_has_hoist_outputs_step():
    """Synthesize stage must have a hoist-outputs step."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "hoist-outputs")
    assert step is not None


def test_synthesize_stage_has_summarize_step():
    """Synthesize stage must have a summarize step using architecture-writer agent."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "summarize")
    assert step is not None
    assert "architecture-writer" in str(step.get("agent", ""))


def test_synthesize_stage_has_update_metadata_step():
    """Synthesize stage must have an update-metadata step."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "update-metadata")
    assert step is not None


def test_synthesize_stage_has_validate_step():
    """Synthesize stage must have a validate step."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "synthesize", "validate")
    assert step is not None


# ---------------------------------------------------------------------------
# final_output declared (1 test)
# ---------------------------------------------------------------------------


def test_recipe_has_final_output():
    """Recipe must declare final_output."""
    data = _load_recipe()
    assert data.get("final_output"), (
        f"final_output must be declared, got: {data.get('final_output')!r}"
    )
```

**Step 2: Run test to verify it fails**
```bash
python -m pytest tests/test_quick_discovery_pipeline_recipe.py::test_recipe_file_exists -v
```
Expected: FAIL — file doesn't exist yet.

**Step 3: Write the quick pipeline recipe**

Create `recipes/quick/discovery-pipeline.yaml`. This is a fresh recipe blending v1 structure with v2 improvements.

**CRITICAL DESIGN DECISIONS (from v1 learnings):**
- Use `os.path.join()` in Python to resolve `output_dir` from `repo_path` — never rely on `{{output_dir}}` when its default contains `{{repo_path}}` (nested template gotcha).
- Never put `{{variable}}` inside Python comments in `command: |` blocks.
- Use `change_result.output_dir` and `change_result.repo_path` from the change-detect step for all downstream references (this was v1's elegant solution).
- Write topics.json to the output directory so downstream steps can read from file instead of template-serialized `{{topics}}`.

```yaml
name: "quick-discovery-pipeline"
description: >
  Quick discovery pipeline for lightweight architectural scanning (~30-60 min).
  Runs a single top-down investigation pass: scan (prescan + topic selection with
  approval gate), investigate (dispatch code-tracer + integration-mapper per topic),
  synthesize (consensus DOTs, assembly, validation, overview.md). Produces the same
  polished output structure as the deep pipeline but at lower depth. Uses shared
  building blocks (discovery-investigate-topic, discovery-synthesize-module) for
  consistency with the deep pipeline.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "pipeline", "quick", "architecture", "dot-graph"]

context:
  repo_path: ""                         # Required: path to target repository
  fidelity: "standard"                  # Optional: quick | standard | deep (default: standard)
  output_dir: "{{repo_path}}/.discovery" # Optional: defaults to {{repo_path}}/.discovery
  render_png: "true"                    # Optional: render assembled DOTs to PNG (default: true)
  node_target: "25"                     # Optional: soft target for overview DOT node count (default: 25)
  _approval_message: ""                 # Populated by engine on approval

stages:
  # ---------------------------------------------------------------------------
  # Stage 1: Scan — discover codebase structure and select investigation topics
  # ---------------------------------------------------------------------------
  - name: "scan"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Change detection — check if a full scan is needed
      # Resolves default output_dir, checks last-run.json, computes git diff.
      # -----------------------------------------------------------------------
      - id: "change-detect"
        type: "bash"
        output: "change_result"
        parse_json: true
        timeout: 30
        command: |
          python3 - <<'EOF'
          import json
          import os
          import subprocess
          from pathlib import Path

          repo_path = "{{repo_path}}"
          output_dir = "{{output_dir}}"

          if not output_dir or "{{" in output_dir:
              output_dir = os.path.join(repo_path, ".discovery")

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "tier": "full",
              "current_commit": "",
              "last_commit": "",
              "changed_files": [],
          }

          try:
              current_commit = subprocess.check_output(
                  ["git", "-C", repo_path, "rev-parse", "HEAD"],
                  text=True,
                  stderr=subprocess.DEVNULL,
              ).strip()
              result["current_commit"] = current_commit
          except Exception:
              current_commit = ""

          last_run_path = Path(output_dir) / "last-run.json"
          if last_run_path.exists():
              try:
                  last_run = json.loads(last_run_path.read_text())
                  last_commit = last_run.get("commit_hash", "")
                  result["last_commit"] = last_commit
                  if last_commit and last_commit == current_commit:
                      result["tier"] = "skip"
                  elif last_commit and current_commit:
                      try:
                          changed = subprocess.check_output(
                              ["git", "-C", repo_path, "diff", "--name-only", last_commit, current_commit],
                              text=True,
                              stderr=subprocess.DEVNULL,
                          ).strip().splitlines()
                          result["changed_files"] = changed
                          result["tier"] = "incremental" if changed else "skip"
                      except Exception:
                          result["tier"] = "full"
              except Exception:
                  pass

          Path(output_dir).mkdir(parents=True, exist_ok=True)

          print(json.dumps(result))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Structural scan — map the repository layout
      # -----------------------------------------------------------------------
      - id: "structural-scan"
        type: "bash"
        condition: "{{change_result.tier}} != 'skip'"
        output: "scan_result"
        parse_json: true
        timeout: 60
        command: |
          python3 - <<'EOF'
          import json
          import os
          import sys
          from pathlib import Path

          repo_path = "{{change_result.repo_path}}"
          output_dir = "{{change_result.output_dir}}"

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "structure": {},
              "error": None,
          }

          sys.path.insert(0, 'modules/tool-dot-graph')
          try:
              from amplifier_module_tool_dot_graph import prescan
              structure = prescan.prescan_repo(repo_path)
              result["structure"] = structure
          except Exception as e:
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

          os.makedirs(output_dir, exist_ok=True)
          with open(os.path.join(output_dir, "prescan-result.json"), "w") as f:
              json.dump(result, f, indent=2)

          print(json.dumps(result))
          EOF

      # -----------------------------------------------------------------------
      # Step 3: Topic selection — choose 3-5 investigation topics
      # -----------------------------------------------------------------------
      - id: "topic-select"
        agent: "dot-graph:discovery-prescan"
        condition: "{{change_result.tier}} != 'skip'"
        output: "topics"
        parse_json: true
        timeout: 600
        prompt: |
          You are the discovery-prescan agent for a quick discovery pipeline run.

          Your task: analyze the structural scan results and select 3-5 investigation
          topics that would best illuminate the architecture of this repository.

          Repository: {{change_result.repo_path}}
          Fidelity tier: {{fidelity}}
          Output directory: {{change_result.output_dir}}

          Structural scan results:
          {{scan_result}}

          Select 3-5 topics. Each should be a meaningful architectural concern,
          mechanism, or subsystem.

          Write the topics to {{change_result.output_dir}}/topics.json as a JSON array.
          Return your response as a JSON array only (no markdown, no explanation):
          [
            {
              "name": "Human-readable topic name",
              "slug": "kebab-case-slug",
              "description": "One sentence describing what this topic covers and why it matters"
            },
            ...
          ]

    approval_gate:
      required: true
      prompt: |
        Quick Discovery Pipeline — Scan Complete

        Repository:  {{change_result.repo_path}}
        Fidelity:    {{fidelity}}
        Output dir:  {{change_result.output_dir}}

        Selected investigation topics:
        {{topics}}

        Estimated: 2 agents × {{topics | length}} topics = {{topics | length * 2}} agent calls

        Type APPROVE to proceed with investigation, or DENY to cancel.

  # ---------------------------------------------------------------------------
  # Stage 2: Investigate — dispatch agent teams per topic
  # ---------------------------------------------------------------------------
  - name: "investigate"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Prepare topic directories
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

          output_dir = "{{change_result.output_dir}}"
          topics = {{topics}}

          agent_names = ["code-tracer", "behavior-observer", "integration-mapper"]
          created = []

          for topic in topics:
              slug = topic.get("slug", "")
              if not slug:
                  continue
              for agent_name in agent_names:
                  agent_dir = Path(output_dir) / "modules" / slug / "agents" / agent_name
                  agent_dir.mkdir(parents=True, exist_ok=True)
              created.append(str(Path(output_dir) / "modules" / slug))

          print(json.dumps({"created_dirs": created, "topic_count": len(created)}))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Investigate topics — dispatch shared sub-recipe per topic
      # -----------------------------------------------------------------------
      - id: "investigate-topics"
        type: "recipe"
        foreach: "{{topics}}"
        as: "topic"
        recipe: "@dot-graph:recipes/discovery-investigate-topic.yaml"
        context:
          topic_name: "{{topic.name}}"
          topic_slug: "{{topic.slug}}"
          topic_description: "{{topic.description}}"
          fidelity: "{{fidelity}}"
          repo_path: "{{change_result.repo_path}}"
          output_dir: "{{change_result.output_dir}}"
        output: "investigation_results"
        timeout: 7200

  # ---------------------------------------------------------------------------
  # Stage 3: Synthesize — produce consensus diagrams, overview, and output
  # ---------------------------------------------------------------------------
  - name: "synthesize"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Reconcile modules — synthesize per-topic findings
      # -----------------------------------------------------------------------
      - id: "reconcile-modules"
        type: "recipe"
        foreach: "{{topics}}"
        as: "topic"
        recipe: "@dot-graph:recipes/discovery-synthesize-module.yaml"
        context:
          module_name: "{{topic.name}}"
          module_dir: "{{change_result.output_dir}}/modules/{{topic.slug}}"
          investigation_dir: "{{change_result.output_dir}}/modules/{{topic.slug}}"
          fidelity: "{{fidelity}}"
          output_dir: "{{change_result.output_dir}}"
        output: "reconciliation_results"
        timeout: 7200

      # -----------------------------------------------------------------------
      # Step 2: Assemble — merge per-module DOTs into overview
      # -----------------------------------------------------------------------
      - id: "assemble"
        type: "bash"
        output: "assemble_result"
        parse_json: true
        timeout: 120
        command: |
          python3 - <<'EOF'
          import json
          import sys
          from pathlib import Path

          output_dir = "{{change_result.output_dir}}"
          topics_path = Path(output_dir) / "topics.json"
          if topics_path.exists():
              topics = json.loads(topics_path.read_text())
          else:
              topics = {{topics}}

          manifest = {
              "output_dir": output_dir,
              "topics": [],
              "error": None,
          }

          sys.path.insert(0, 'modules/tool-dot-graph')
          try:
              from amplifier_module_tool_dot_graph import assemble
              modules_dir = Path(output_dir) / "modules"
              modules_def = {
                  topic.get("slug", ""): {
                      "dot_path": str(modules_dir / topic.get("slug", "") / "diagram.dot"),
                      "subsystem": "discovery",
                  }
                  for topic in topics if topic.get("slug")
              }
              assemble_manifest = {
                  "modules": modules_def,
                  "subsystems": {"discovery": {"modules": list(modules_def.keys())}},
              }
              output_path = str(Path(output_dir) / "output")
              Path(output_path).mkdir(parents=True, exist_ok=True)
              hierarchy = assemble.assemble_hierarchy(assemble_manifest, output_path)
              manifest["assembly"] = hierarchy
              for topic in topics:
                  slug = topic.get("slug", "")
                  module_dir = modules_dir / slug
                  manifest["topics"].append({
                      "name": topic.get("name", ""),
                      "slug": slug,
                      "diagram": str(module_dir / "diagram.dot") if (module_dir / "diagram.dot").exists() else None,
                      "findings": str(module_dir / "findings.md") if (module_dir / "findings.md").exists() else None,
                  })
          except Exception as e:
              modules_dir = Path(output_dir) / "modules"
              for topic in topics:
                  slug = topic.get("slug", "")
                  module_dir = modules_dir / slug
                  manifest["topics"].append({
                      "name": topic.get("name", ""),
                      "slug": slug,
                      "diagram": str(module_dir / "diagram.dot") if (module_dir / "diagram.dot").exists() else None,
                      "findings": str(module_dir / "findings.md") if (module_dir / "findings.md").exists() else None,
                  })
              manifest["error"] = f"assemble module unavailable ({e}), used fallback"

          print(json.dumps(manifest))
          EOF

      # -----------------------------------------------------------------------
      # Step 3: Validate — validate all produced .dot files
      # -----------------------------------------------------------------------
      - id: "validate"
        type: "bash"
        output: "final_validation"
        parse_json: true
        timeout: 60
        command: |
          python3 - <<'EOF'
          import json
          from pathlib import Path

          output_dir = "{{change_result.output_dir}}"

          result = {
              "valid_count": 0,
              "error_count": 0,
              "errors": [],
              "dot_files": [],
          }

          dot_files = list(Path(output_dir).rglob("*.dot"))
          result["dot_files"] = [str(f) for f in dot_files]

          try:
              import pydot

              for dot_file in dot_files:
                  try:
                      graphs = pydot.graph_from_dot_file(str(dot_file))
                      if graphs:
                          result["valid_count"] += 1
                      else:
                          result["error_count"] += 1
                          result["errors"].append(f"{dot_file}: empty parse result")
                  except Exception as e:
                      result["error_count"] += 1
                      result["errors"].append(f"{dot_file}: {e}")
          except ImportError:
              result["errors"].append("pydot not available — validation skipped")

          print(json.dumps(result))
          EOF

      # -----------------------------------------------------------------------
      # Step 4: Hoist outputs — create flat output/ directory
      # Copies per-module diagram.dot and findings.md to output/ root,
      # plus overview.dot. Creates the output structure described in design.
      # -----------------------------------------------------------------------
      - id: "hoist-outputs"
        type: "bash"
        output: "hoist_result"
        parse_json: true
        timeout: 30
        command: |
          python3 - <<'EOF'
          import json
          import shutil
          from pathlib import Path

          output_dir = "{{change_result.output_dir}}"
          output_root = Path(output_dir) / "output"
          output_root.mkdir(parents=True, exist_ok=True)

          hoisted = []
          modules_dir = Path(output_dir) / "modules"

          if modules_dir.exists():
              for module_dir in sorted(modules_dir.iterdir()):
                  if not module_dir.is_dir():
                      continue
                  slug = module_dir.name
                  dot_src = module_dir / "diagram.dot"
                  if dot_src.exists():
                      dot_dest = output_root / f"{slug}.dot"
                      shutil.copy2(str(dot_src), str(dot_dest))
                      hoisted.append(str(dot_dest))
                  findings_src = module_dir / "findings.md"
                  if findings_src.exists():
                      findings_dest = output_root / f"{slug}-findings.md"
                      shutil.copy2(str(findings_src), str(findings_dest))
                      hoisted.append(str(findings_dest))

          overview_dot = output_root / "overview.dot"
          if not overview_dot.exists():
              for candidate in [
                  Path(output_dir) / "output" / "overview.dot",
                  Path(output_dir) / "overview.dot",
              ]:
                  if candidate.exists() and candidate != overview_dot:
                      shutil.copy2(str(candidate), str(overview_dot))
                      hoisted.append(str(overview_dot))
                      break

          print(json.dumps({"hoisted": hoisted, "count": len(hoisted)}))
          EOF

      # -----------------------------------------------------------------------
      # Step 5: Summarize — produce overview.md using architecture-writer agent
      # -----------------------------------------------------------------------
      - id: "summarize"
        agent: "dot-graph:discovery-architecture-writer"
        output: "summary_result"
        timeout: 1200
        prompt: |
          You are the architecture writer for a quick discovery pipeline run.

          Your task: read all per-module findings and produce a polished overview.md
          that serves as the human-readable entry point to the discovery results.

          Repository: {{change_result.repo_path}}
          Output directory: {{change_result.output_dir}}
          Node target for overview: {{node_target}}

          Read per-module findings from:
            {{change_result.output_dir}}/modules/*/findings.md

          Read the topics list from:
            {{change_result.output_dir}}/topics.json

          Read the overview DOT (if present) from:
            {{change_result.output_dir}}/output/overview.dot

          Write overview.md to:
            {{change_result.output_dir}}/output/overview.md

          Structure overview.md with:
          1. Executive summary (2-3 sentences)
          2. Repository overview (what this codebase is)
          3. Per-module summaries with links to ../modules/{slug}/findings.md
          4. Cross-cutting insights
          5. Open questions

      # -----------------------------------------------------------------------
      # Step 6: Update metadata — write last-run.json
      # -----------------------------------------------------------------------
      - id: "update-metadata"
        type: "bash"
        output: "metadata_result"
        parse_json: true
        timeout: 10
        command: |
          python3 - <<'EOF'
          import json
          import os
          from datetime import datetime, timezone
          from pathlib import Path

          repo_path = "{{change_result.repo_path}}"
          output_dir = os.path.join(repo_path, ".discovery")
          fidelity = "{{fidelity}}"
          commit_hash = "{{change_result.current_commit}}"

          metadata = {
              "pipeline": "quick",
              "commit_hash": commit_hash,
              "timestamp": datetime.now(timezone.utc).isoformat(),
              "fidelity": fidelity,
              "repo_path": repo_path,
          }

          last_run_path = Path(output_dir) / "last-run.json"
          last_run_path.parent.mkdir(parents=True, exist_ok=True)
          last_run_path.write_text(json.dumps(metadata, indent=2))

          print(json.dumps({"written": str(last_run_path), **metadata}))
          EOF

final_output: "metadata_result"
```

**Step 4: Run test to verify it passes**
```bash
python -m pytest tests/test_quick_discovery_pipeline_recipe.py -v
```
Expected: All tests PASS.

**Step 5: Update `tests/test_final_verification.py`**

Add the quick pipeline to the `EXPECTED_FILES` list. After the line for `discovery-architecture-writer.md`, add:

```python
    "recipes/quick/discovery-pipeline.yaml",
```

Update the file count from 43 to 44. Update the comment to match.

**Step 6: Run full test suite**
```bash
python -m pytest tests/ -x -q 2>&1 | tail -5
```
Expected: All tests pass.

**Step 7: Commit**
```bash
git add recipes/quick/discovery-pipeline.yaml tests/test_quick_discovery_pipeline_recipe.py tests/test_final_verification.py
git commit -m "feat: add quick discovery pipeline recipe with tests"
```

---

## Phase 2: Enhance Quick Pipeline (Tasks 7-10)

Add node_target to overview synthesizer, render SVGs, and ensure output parity.

---

### Task 7: Update overview synthesizer agent prompt with node_target instructions

The `discovery-overview-synthesizer` agent needs updated instructions about the `node_target` concept. This applies to both pipelines.

**Files:**
- Modify: `agents/discovery-overview-synthesizer.md`

**Step 1: Read the current file**
```bash
cat agents/discovery-overview-synthesizer.md
```

**Step 2: Update the Quality Gate section**

In `agents/discovery-overview-synthesizer.md`, find the section:
```markdown
## Quality Gate

**Hard limit: ≤80 nodes.**
```

Replace the entire Quality Gate section with:

```markdown
## Quality Gate — Node Target

The pipeline provides a `node_target` (default: 25) that you should use as a soft goal for your overview diagram:

- **Strive to reach** the target — don't produce a 5-node overview when 25 would be richer
- **Strive to stay near** the target — don't produce 60 nodes when 25 was asked for
- **Not a hard limit** — a simple repo might naturally be 12 nodes and that's fine; a complex one might justify 30

### Value-Driven Allocation

Decide how to spend your node budget based on architectural significance, not even distribution. A concept that's most complex or most interesting gets more depth. A concept that's genuinely simple stays simple.

### Adaptive Graph Structure

- **Focused repo** (single main idea): One graph with more internal depth. Most nodes go toward depth of that single idea.
- **Medium repo** (3-5 main ideas): Subgraph clusters per idea with internal structure proportional to significance — not size.
- **Broad repo** (many ideas): More clusters, less depth per cluster, but still mini-graphs not single boxes.

### Key Rule

Every top-level concept should be represented by enough structure to understand what it does when scanning across many repos. A single unlabeled box is never enough. But "enough" varies — for a trivial utility it might be 2 nodes, for a complex subsystem it might be 8.

**Fallback hard limit: ≤80 nodes.** If you somehow exceed 80 nodes despite the node target, apply collapse strategies before writing any artifact:

1. **Merge related subsystems** — combine subsystems that share a single owner or purpose
2. **Group utilities** — collapse support subsystems into a single `utilities` node
3. **Remove disconnected subsystems** — document them in `findings.md` instead
```

**Step 3: Run existing overview synthesizer tests**
```bash
python -m pytest tests/test_discovery_overview_synthesizer_agent.py -v
```
Expected: All existing tests still pass (we preserved the ≤80 mention and all other required content).

**Step 4: Commit**
```bash
git add agents/discovery-overview-synthesizer.md
git commit -m "feat: add node_target with value-driven allocation to overview synthesizer"
```

---

### Task 8: Add node_target to deep pipeline overview synthesis

The deep pipeline's `synthesize-overview.yaml` needs to pass `node_target` in its synthesize step prompt.

**Files:**
- Modify: `recipes/deep/synthesize-overview.yaml`

**Step 1: Read the current file**
```bash
cat recipes/deep/synthesize-overview.yaml
```

**Step 2: Update the synthesize step prompt**

In `recipes/deep/synthesize-overview.yaml`, find the synthesize step prompt. After the line:
```yaml
      Output directory: {{output_dir}}
```

Add:
```yaml

      Node target: {{node_target}} (soft goal for node count — see agent instructions)
```

**Step 3: Add `node_target` to the context section**

In the `context:` block at the top of the file, add:
```yaml
  node_target: "25"            # soft target for overview DOT node count (default: 25)
```

**Step 4: Run synthesize-overview tests**
```bash
python -m pytest tests/test_synthesize_overview_recipe.py -v
```
Expected: All tests pass.

**Step 5: Commit**
```bash
git add recipes/deep/synthesize-overview.yaml
git commit -m "feat: add node_target context variable to deep pipeline overview synthesis"
```

---

### Task 9: Add node_target to deep pipeline entry point

The deep pipeline's `discovery-pipeline.yaml` needs `node_target` in its context so it flows down to overview synthesis.

**Files:**
- Modify: `recipes/deep/discovery-pipeline.yaml`

**Step 1: Read the current file**
```bash
cat recipes/deep/discovery-pipeline.yaml
```

**Step 2: Add `node_target` to the context section**

In the `context:` block, after the `strategies` line, add:
```yaml
  node_target: "25"                     # Optional: soft target for overview DOT node count (default: 25)
```

**Step 3: Run deep pipeline tests**
```bash
python -m pytest tests/test_discovery_pipeline_recipe.py -v
```
Expected: All tests pass.

**Step 4: Commit**
```bash
git add recipes/deep/discovery-pipeline.yaml
git commit -m "feat: add node_target context variable to deep pipeline entry point"
```

---

### Task 10: Add hoist-outputs and summarize steps to deep pipeline

The deep pipeline needs the same output polish steps as the quick pipeline. These go into the `discovery-combine.yaml` recipe (which is the final stage of the deep pipeline).

**Files:**
- Modify: `recipes/deep/discovery-combine.yaml`

**Step 1: Read the current file**
```bash
cat recipes/deep/discovery-combine.yaml
```

**Step 2: Add `node_target` to context**

In the `context:` block, add:
```yaml
  node_target: "25"            # soft target for overview DOT node count
```

**Step 3: Add hoist-outputs step after the render step**

After the existing `render` step (the last step currently), add:

```yaml
  # ---------------------------------------------------------------------------
  # Step 5: hoist-outputs — create flat output/ directory
  # Copies per-module diagram.dot files and combined.dot to output root.
  # ---------------------------------------------------------------------------
  - id: "hoist-outputs"
    type: "bash"
    output: "hoist_result"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      import shutil
      from pathlib import Path

      output_dir = "{{output_dir}}"
      output_root = Path(output_dir)
      output_root.mkdir(parents=True, exist_ok=True)

      hoisted = []

      combined_dot = output_root / "combined.dot"
      overview_dot = output_root / "overview.dot"
      if combined_dot.exists() and not overview_dot.exists():
          shutil.copy2(str(combined_dot), str(overview_dot))
          hoisted.append(str(overview_dot))

      print(json.dumps({"hoisted": hoisted, "count": len(hoisted)}))
      EOF

  # ---------------------------------------------------------------------------
  # Step 6: summarize — produce overview.md using architecture-writer agent
  # ---------------------------------------------------------------------------
  - id: "summarize"
    agent: "dot-graph:discovery-architecture-writer"
    output: "summary_result"
    timeout: 1200
    prompt: |
      You are the architecture writer for a deep discovery pipeline run.

      Your task: read all findings and produce a polished overview.md
      that serves as the human-readable entry point to the discovery results.

      Repository: {{repo_path}}
      Output directory: {{output_dir}}
      Node target for overview: {{node_target}}

      Read the combined output from:
        {{output_dir}}/

      Look for per-module findings, combined.dot, discrepancies.md, and any
      per-strategy investigation artifacts.

      Write overview.md to:
        {{output_dir}}/overview.md

      Structure overview.md with:
      1. Executive summary (2-3 sentences)
      2. Repository overview
      3. Per-module summaries with links to detail files
      4. Cross-cutting insights (highlight convergence/divergence from strategies)
      5. Open questions
```

**Step 4: Update the test to reflect new step count**

In `tests/test_discovery_combine_recipe.py`, the test `test_recipe_has_exactly_4_steps` checks for exactly 4 steps. Update it:

Change:
```python
    assert len(steps) == 4, f"Expected exactly 4 steps, got {len(steps)}"
```
To:
```python
    assert len(steps) == 6, f"Expected exactly 6 steps, got {len(steps)}"
```

Also update `test_recipe_steps_correct_order`:

Change:
```python
    assert step_ids == ["check-inputs", "combine", "validate", "render"], (
        f"Steps must be in order [check-inputs, combine, validate, render], got: {step_ids}"
    )
```
To:
```python
    assert step_ids == ["check-inputs", "combine", "validate", "render", "hoist-outputs", "summarize"], (
        f"Steps must be in order [check-inputs, combine, validate, render, hoist-outputs, summarize], got: {step_ids}"
    )
```

**Step 5: Also wire node_target through the deep pipeline's combine call**

In `recipes/deep/discovery-pipeline.yaml`, find the `run-combine` step's context block and add `node_target`:

```yaml
          node_target: "{{node_target}}"
```

**Step 6: Run tests**
```bash
python -m pytest tests/test_discovery_combine_recipe.py -v
python -m pytest tests/test_discovery_pipeline_recipe.py -v
```
Expected: All tests pass.

**Step 7: Commit**
```bash
git add recipes/deep/discovery-combine.yaml recipes/deep/discovery-pipeline.yaml tests/test_discovery_combine_recipe.py
git commit -m "feat: add hoist-outputs and summarize steps to deep pipeline"
```

---

## Phase 3: Final Integration & Verification (Tasks 11-14)

---

### Task 11: Add update-metadata step to deep pipeline combine recipe

The deep pipeline's combine recipe should also write `last-run.json` after completion, matching the quick pipeline.

**Files:**
- Modify: `recipes/deep/discovery-combine.yaml`

**Step 1: Add update-metadata step after the summarize step**

After the `summarize` step, add:

```yaml
  # ---------------------------------------------------------------------------
  # Step 7: update-metadata — write last-run.json
  # -----------------------------------------------------------------------
  - id: "update-metadata"
    type: "bash"
    output: "metadata_result"
    parse_json: true
    timeout: 10
    command: |
      python3 - <<'EOF'
      import json
      import os
      import subprocess
      from datetime import datetime, timezone
      from pathlib import Path

      repo_path = "{{repo_path}}"
      output_dir = os.path.join(repo_path, ".discovery")
      fidelity = "standard"

      try:
          commit_hash = subprocess.check_output(
              ["git", "-C", repo_path, "rev-parse", "HEAD"],
              text=True,
              stderr=subprocess.DEVNULL,
          ).strip()
      except Exception:
          commit_hash = ""

      metadata = {
          "pipeline": "deep",
          "commit_hash": commit_hash,
          "timestamp": datetime.now(timezone.utc).isoformat(),
          "repo_path": repo_path,
      }

      last_run_path = Path(output_dir) / "last-run.json"
      last_run_path.parent.mkdir(parents=True, exist_ok=True)
      last_run_path.write_text(json.dumps(metadata, indent=2))

      print(json.dumps({"written": str(last_run_path), **metadata}))
      EOF
```

**Step 2: Update the test step count again**

In `tests/test_discovery_combine_recipe.py`, update:

Change:
```python
    assert len(steps) == 6, f"Expected exactly 6 steps, got {len(steps)}"
```
To:
```python
    assert len(steps) == 7, f"Expected exactly 7 steps, got {len(steps)}"
```

Update `test_recipe_steps_correct_order`:
```python
    assert step_ids == ["check-inputs", "combine", "validate", "render", "hoist-outputs", "summarize", "update-metadata"], (
        f"Steps must be in order [check-inputs, combine, validate, render, hoist-outputs, summarize, update-metadata], got: {step_ids}"
    )
```

**Step 3: Run tests**
```bash
python -m pytest tests/test_discovery_combine_recipe.py -v
```
Expected: All tests pass.

**Step 4: Commit**
```bash
git add recipes/deep/discovery-combine.yaml tests/test_discovery_combine_recipe.py
git commit -m "feat: add update-metadata step to deep pipeline combine recipe"
```

---

### Task 12: Run full test suite to verify nothing broke

**Step 1: Run all tests**
```bash
cd /home/bkrabach/dev/dot-graph-bundle
python -m pytest tests/ -v 2>&1 | tail -30
```
Expected: All tests pass. Pay attention to:
- Recipe path tests (should find files in `recipes/deep/`)
- Sub-recipe existence tests (should find shared recipes at `recipes/` root)
- Final verification file count (should match updated count)
- New quick pipeline tests (should all pass)
- New architecture-writer agent tests (should all pass)

**Step 2: Check for any remaining stale references**
```bash
grep -rn "recipes/strategy-topdown.yaml" tests/ recipes/ --include="*.py" --include="*.yaml" | grep -v "recipes/deep/"
grep -rn "recipes/synthesize-overview.yaml" tests/ recipes/ --include="*.py" --include="*.yaml" | grep -v "recipes/deep/"
grep -rn "recipes/discovery-combine.yaml" tests/ recipes/ --include="*.py" --include="*.yaml" | grep -v "recipes/deep/"
grep -rn "recipes/discovery-pipeline.yaml" tests/ recipes/ --include="*.py" --include="*.yaml" | grep -v "recipes/deep/" | grep -v "recipes/quick/"
```
Expected: No stale references to old paths (only references should be in `recipes/deep/` or `recipes/quick/`). Exception: the shared recipes `discovery-investigate-topic.yaml` and `discovery-synthesize-module.yaml` should still be referenced at root.

**Step 3: Fix any remaining issues**

If any tests fail or stale references are found, fix them.

**Step 4: Commit if any fixes were needed**
```bash
git add -A
git commit -m "fix: resolve any remaining stale references from restructure"
```

---

### Task 13: Verify cross-reference integrity

Verify that all `@dot-graph:recipes/` references inside recipe files point to files that actually exist.

**Step 1: Run cross-reference check**
```bash
cd /home/bkrabach/dev/dot-graph-bundle
grep -roh "@dot-graph:recipes/[^ \"']*" recipes/ | sort -u | while read ref; do
  path=$(echo "$ref" | sed 's|@dot-graph:||')
  if [ ! -f "$path" ]; then
    echo "BROKEN: $ref -> $path"
  else
    echo "OK: $ref"
  fi
done
```
Expected: All references resolve to existing files. No "BROKEN" lines.

**Step 2: Commit (no changes expected)**

This is a verification step only.

---

### Task 14: Final commit and summary

**Step 1: Run the complete test suite one final time**
```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -40
```
Expected: All tests pass.

**Step 2: Review the final directory structure**
```bash
find recipes/ -name "*.yaml" | sort
```
Expected:
```
recipes/deep/discovery-combine.yaml
recipes/deep/discovery-pipeline.yaml
recipes/deep/strategy-bottomup.yaml
recipes/deep/strategy-sequential.yaml
recipes/deep/strategy-topdown.yaml
recipes/deep/synthesize-level.yaml
recipes/deep/synthesize-overview.yaml
recipes/deep/synthesize-subsystem.yaml
recipes/discovery-investigate-topic.yaml
recipes/discovery-synthesize-module.yaml
recipes/quick/discovery-pipeline.yaml
```

**Step 3: Review the final agent list**
```bash
ls agents/
```
Expected: 12 agent files (11 original + 1 new `discovery-architecture-writer.md`).

**Step 4: Create a summary commit if needed**

If there are any uncommitted changes:
```bash
git add -A
git commit -m "chore: finalize quick/deep pipeline restructure"
```

---

## Smoke Test Instructions (Post-Implementation)

These are manual verification instructions, not automated tasks.

### Quick Pipeline Smoke Test

To verify the quick pipeline works end-to-end against a small repo:

```bash
# Using the amplifier CLI (or recipe runner):
# Execute: @dot-graph:recipes/quick/discovery-pipeline.yaml
# Context: repo_path=/path/to/small/test/repo

# After completion, verify output structure:
find /path/to/small/test/repo/.discovery/output/ -type f | sort
```

Expected output files:
```
.discovery/output/overview.md
.discovery/output/overview.dot
.discovery/output/{slug}.dot           (one per topic)
.discovery/output/{slug}-findings.md   (one per topic)
.discovery/last-run.json
.discovery/topics.json
```

### Deep Pipeline Regression Test

To verify the deep pipeline still works after the restructure:

```bash
# Execute: @dot-graph:recipes/deep/discovery-pipeline.yaml
# Context: repo_path=/path/to/test/repo, strategies=topdown

# After completion, verify output structure:
find /path/to/test/repo/.discovery/ -name "*.dot" -o -name "*.md" -o -name "*.json" | sort
```

Expected: Same artifacts as before the restructure, plus `overview.md` in the output directory.

---

## Summary of All New/Modified Files

### New Files (3)
| File | Description |
|------|-------------|
| `agents/discovery-architecture-writer.md` | New agent for overview.md generation |
| `recipes/quick/discovery-pipeline.yaml` | Quick discovery pipeline |
| `tests/test_quick_discovery_pipeline_recipe.py` | Tests for quick pipeline |
| `tests/test_discovery_architecture_writer_agent.py` | Tests for new agent |

### Moved Files (8)
| From | To |
|------|-----|
| `recipes/discovery-pipeline.yaml` | `recipes/deep/discovery-pipeline.yaml` |
| `recipes/strategy-topdown.yaml` | `recipes/deep/strategy-topdown.yaml` |
| `recipes/strategy-bottomup.yaml` | `recipes/deep/strategy-bottomup.yaml` |
| `recipes/strategy-sequential.yaml` | `recipes/deep/strategy-sequential.yaml` |
| `recipes/discovery-combine.yaml` | `recipes/deep/discovery-combine.yaml` |
| `recipes/synthesize-level.yaml` | `recipes/deep/synthesize-level.yaml` |
| `recipes/synthesize-subsystem.yaml` | `recipes/deep/synthesize-subsystem.yaml` |
| `recipes/synthesize-overview.yaml` | `recipes/deep/synthesize-overview.yaml` |

### Modified Files (12)
| File | Change |
|------|--------|
| `recipes/deep/discovery-pipeline.yaml` | Updated cross-refs, added node_target |
| `recipes/deep/strategy-topdown.yaml` | Updated cross-refs |
| `recipes/deep/strategy-bottomup.yaml` | Updated cross-refs |
| `recipes/deep/strategy-sequential.yaml` | Updated cross-refs |
| `recipes/deep/discovery-combine.yaml` | Updated cross-refs, added hoist/summarize/metadata steps |
| `recipes/deep/synthesize-overview.yaml` | Added node_target |
| `agents/discovery-overview-synthesizer.md` | Added node_target instructions |
| `behaviors/dot-discovery.yaml` | Added architecture-writer agent |
| `tests/test_discovery_pipeline_recipe.py` | Updated paths |
| `tests/test_strategy_topdown_recipe.py` | Updated paths |
| `tests/test_strategy_bottomup_recipe.py` | Updated paths |
| `tests/test_strategy_sequential_recipe.py` | Updated paths |
| `tests/test_discovery_combine_recipe.py` | Updated paths + step counts |
| `tests/test_synthesize_level_recipe.py` | Updated paths |
| `tests/test_synthesize_subsystem_recipe.py` | Updated paths |
| `tests/test_synthesize_overview_recipe.py` | Updated paths |
| `tests/test_final_verification.py` | Updated EXPECTED_FILES + count |

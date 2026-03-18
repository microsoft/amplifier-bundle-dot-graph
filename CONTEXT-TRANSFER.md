# Context Transfer — `amplifier-bundle-dot-graph`

**Transfer date:** 2026-03-18
**Session duration:** 5 days, 114+ turns, 178 session:resume cycles
**Termination reason:** 780MB events.jsonl caused I/O starvation during context compaction, crashing tmux repeatedly. Fresh session is the correct mitigation.

This document contains EVERYTHING a fresh session needs to continue this work seamlessly.

---

## Table of Contents

1. [What This Project Is](#what-this-project-is)
2. [The Key Insight That Drives Everything](#the-key-insight-that-drives-everything)
3. [What We Built — The Full History](#what-we-built--the-full-history)
4. [Current State — Where We Are Right Now](#current-state--where-we-are-right-now)
5. [Known Recipe Framework Gotchas](#known-recipe-framework-gotchas)
6. [Immediate Next Steps](#immediate-next-steps)
7. [Architecture — The Complete Bundle Structure](#architecture--the-complete-bundle-structure)
8. [Design Philosophy](#design-philosophy)
9. [Key Files to Read](#key-files-to-read)
10. [Workspace Layout](#workspace-layout)
11. [Bundle Stats at Transfer Time](#bundle-stats-at-transfer-time)

---

## What This Project Is

`amplifier-bundle-dot-graph` is a first-class DOT/Graphviz infrastructure bundle for the Amplifier ecosystem. GitHub: `microsoft/amplifier-bundle-dot-graph`. Any bundle can gain DOT capabilities with one include line.

**Install:**
```
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=behaviors/dot-graph.yaml --app
```

**What it provides:**
- Knowledge layer (agents, skills, docs) — works with zero dependencies
- Validation & rendering (3-layer validation, Graphviz CLI wrapper) — needs `pydot`, optionally Graphviz
- Graph intelligence (NetworkX-backed analysis) — needs `pydot` + `networkx`
- Discovery pipeline (automated codebase mapping via multi-agent investigation) — needs all of the above

**7 primary use cases discovered:**

| # | Use Case | What It Means |
|---|----------|---------------|
| 1 | Reconciliation forcing function | Surfaces bugs no other tool catches |
| 2 | Dense context representation | Token-efficient system understanding |
| 3 | Multi-scale navigation | Google Maps-style zoom via subgraphs |
| 4 | Analysis substrate | Cheap code-based graph algorithms, zero LLM cost |
| 5 | Multi-modal bridge | Render to SVG/PNG for users, apps, vision models |
| 6 | Workflow/recipe visualization | Complex workflows become comprehensible as visual flow graphs |
| 7 | Investigation artifacts | Forces structural commitment over vague analysis |

---

## The Key Insight That Drives Everything

Building a valid DOT graph of a system forces structural reconciliation. Agents can't produce a valid graph without resolving contradictions — and that reconciliation surfaces bugs, dead code, duplicate paths, and gaps that LSP, compilers, and prose-based analysis routinely miss.

**The diagram doesn't document the bug. Drawing the diagram finds the bug.**

This insight is why DOT is more than a visualization format — it's an analysis tool. When agents are forced to commit to specific nodes, edges, and relationships in a formal graph structure, they cannot paper over contradictions. The graph won't validate. This is the core value proposition that makes this bundle worth building.

---

## What We Built — The Full History

### Phase 1: Knowledge Layer (original bundle)

- 2 core agents: `dot-author` (creates/refines DOT) + `diagram-reviewer` (PASS/WARN/FAIL quality verdicts)
- 5 skills: `dot-syntax`, `dot-patterns`, `dot-as-analysis`, `dot-quality`, `dot-graph-intelligence`
- 5 docs: full syntax reference, patterns, quality standards, graphviz setup, analysis guide
- Shell scripts for validation and rendering
- Tool module `tool-dot-graph` with operations: validate, render, setup

### Phase 2: Tool Operations

- Real validate (3-layer: syntax + structural + render quality)
- Real render (SVG/PNG/PDF via graphviz CLI)
- Setup helper (environment detection)

### Phase 3: Graph Intelligence

- NetworkX-backed analysis: stats, reachability, unreachable nodes, cycles, paths, critical_path, subgraph_extract, diff
- Prescan tool operation (structural codebase scan — walks a repo, produces language/module/file inventory)
- Assemble tool operation (hierarchical DOT assembly — merges per-module DOTs into subsystem + overview graphs)

### Discovery Pipeline v1 (Phases A-E)

- **Phase A:** Discovery pipeline design
- **Phase B:** Prescan and assemble tool operations
- **Phase C:** 5 discovery investigation agents (code-tracer, behavior-observer, integration-mapper, prescan, synthesizer)
- **Phase D:** 3 recipe files (discovery-pipeline.yaml, discovery-investigate-topic.yaml, discovery-synthesize-module.yaml)
- **Phase E:** Integration testing

### Three Improvements (pre-v2)

1. Split `.discovery/` into `output/` and `investigation/` directories
2. Fix subgraph recursion in `analyze.py` (pydot→NetworkX now recurses into clusters)
3. Make PNG rendering optional (`render_png` parameter)

### Discovery Pipeline v2 (Phases A-D) — THE MAJOR REDESIGN

**The core insight:** The v1 pipeline was a monolith. `assemble.py` carried semantic responsibility (graph manipulation) that belonged to agents. The pipeline only did top-down (conceptual) investigation, missing the empirical (bottom-up) perspective. The output graphs were structurally correct but semantically dead compared to the rich agent-authored investigation graphs.

**Design philosophy — B+C hybrid:**
- Level-specific agents for each zoom level (B's specialization)
- Synthesis is recursive — the same act (reconcile → discover → synthesize) applies at every zoom level, not just a separate "assembly" step (C's concept)
- `assemble.py` becomes pure plumbing (directory creation, manifest tracking, zero semantic content)
- A small collection of composable strategy recipes — each works standalone, composes into larger orchestrations

#### Phase A v2 — 4 new agents

| Agent | Model Role | Purpose |
|-------|-----------|---------|
| `discovery-level-synthesizer` | coding | Recursive bottom-up agent, invoked per directory level during post-order traversal |
| `discovery-subsystem-synthesizer` | reasoning | Seam-finder between modules — cross-module data flows, shared interfaces |
| `discovery-overview-synthesizer` | reasoning | System-level pattern finder, produces overview with ≤80 nodes |
| `discovery-combiner` | reasoning | Convergence/divergence analyst (Convergence=green, Top-down-only=amber, Bottom-up-only=blue, Divergence=red with D-01, D-02... tracking) |

#### Phase B v2 — assemble.py reduction + 3 building block sub-recipes

- `assemble.py` stripped from 521 lines to ~153 lines (pure plumbing — directory creation, manifest tracking, file management, render triggering)
- `synthesize-level.yaml` — per-directory synthesis (used by bottom-up traversal)
- `synthesize-subsystem.yaml` — cross-module seam synthesis
- `synthesize-overview.yaml` — system-level overview synthesis

#### Phase C v2 — 2 strategy recipes

- `strategy-topdown.yaml` — standalone conceptual investigation (extracted from the monolithic pipeline)
- `strategy-bottomup.yaml` — standalone empirical post-order tree traversal (entirely new concept)

#### Phase D v2 — orchestrators + combination

- `discovery-combine.yaml` — reads both strategy outputs, classifies as Convergence/Top-down-only/Bottom-up-only/Divergence
- `strategy-sequential.yaml` — bottom-up first, approval gate, top-down with `bottomup_context`, then combine
- `discovery-pipeline.yaml` — rewritten from 521-line monolith to ~175-line thin orchestrator (prescan + both strategies + combine)

### The Complete Recipe Library (10 recipes)

| Recipe | Type | Purpose |
|--------|------|---------|
| `synthesize-level.yaml` | Building block | Per-directory synthesis |
| `synthesize-subsystem.yaml` | Building block | Cross-module seam synthesis |
| `synthesize-overview.yaml` | Building block | System-level overview synthesis |
| `discovery-investigate-topic.yaml` | Building block | Per-topic agent dispatch |
| `discovery-synthesize-module.yaml` | Building block | Per-module consensus with quality gate |
| `discovery-combine.yaml` | Building block | Convergence/divergence analysis |
| `strategy-topdown.yaml` | Strategy | Standalone conceptual investigation |
| `strategy-bottomup.yaml` | Strategy | Standalone empirical traversal |
| `strategy-sequential.yaml` | Composition | Bottom-up informs top-down |
| `discovery-pipeline.yaml` | Orchestrator | Parallel + combine (default entry point) |

---

## Current State — Where We Are Right Now

### Git State

**Workspace** (`/home/bkrabach/dev/dot-graph-bundle`):
- HEAD: `2d34677` (fix: batch fix recipe runtime issues found during validation audit)
- 1287 tests passing (verified at transfer time)
- Cache at `~/.amplifier/cache/amplifier-bundle-dot-graph-43d42df775a679a7/` is in sync with workspace

**Clean push repo** (`/home/bkrabach/dev/amplifier-bundle-dot-graph`):
- HEAD: `e26b55e` (feat: Phase D v2 — discovery-combine, strategy-sequential, and pipeline refactor to thin orchestrator)
- This is what's on GitHub remote `microsoft/amplifier-bundle-dot-graph` main branch
- The Phase A-D v2 implementation IS pushed and working
- The 9 recipe bug-fix commits ARE NOT pushed yet

### The 9 Unpushed Recipe Bug-Fix Commits

These commits exist in the workspace only (`e26b55e..2d34677`). They fix bugs discovered during e2e testing:

| Commit | What It Fixes |
|--------|---------------|
| `22e0262` | `when` → `condition` (recipe framework uses `condition:` not `when:` for conditional steps) |
| `dd8681a` | foreach data-flow: flatten topic objects (`topic_name: "{{topic.name}}"` instead of `topic: "{{topic}}"`) |
| `0da941b` | JSON booleans in Python: `json.loads(r"""{{var}}""")` instead of `x = {{var}}` |
| `2e0b73b` | Skip double-scan: `parent_topics_available` flag when strategy-topdown called as sub-recipe |
| `b09ffc0` | save-topics outputs to context, prepare-topics reads from file |
| `46b43a2` | Split save-topics into conditional steps to avoid undefined variable when topic-select skipped |
| `a9efc1f` | `parent_topics_available` flag replaces `topics_file` path (avoids nested template resolution) |
| (intermediate) | Fix commits absorbed into above |
| `2d34677` | Batch fix: path mismatches in investigate-topic prompts, missing `repo_root` in overview calls, wrong context keys for subsystem synthesis |

### What's On Remote (Working But With Known Bugs)

The GitHub remote has the complete v2 pipeline (all 10 recipes, all 11 agents, 3 behaviors) but WITHOUT the 9 bug fixes above. **The recipes will fail at runtime with the bugs listed above.** The bugs were discovered during e2e testing attempts.

### What's Been Tested

**Schema validation:** All 10 recipes pass `amplifier tool invoke recipes operation=validate`

**Tier 1 runtime test (PASSED):** `synthesize-level.yaml` executed successfully on `amplifier/agents/` directory. Produced a valid DOT file (9 nodes, 13 edges) with findings.md. The `discovery-level-synthesizer` agent correctly analyzed the agents directory.

```python
# How the test was run:
recipes(
    operation="execute",
    recipe_path="/home/bkrabach/dev/dot-graph-bundle/recipes/synthesize-level.yaml",
    context={
        "level_path": "/home/bkrabach/dev/dot-graph-bundle/amplifier/agents",
        "level_slug": "agents",
        "output_dir": "/tmp/test-synth-level",
        "fidelity": "standard"
    }
)
```

**Tier 2-4 runtime tests (NOT DONE).** The following recipes have NOT been individually tested at runtime:
- `synthesize-subsystem.yaml`
- `synthesize-overview.yaml`
- `discovery-investigate-topic.yaml`
- `discovery-synthesize-module.yaml`
- `discovery-combine.yaml`
- `strategy-topdown.yaml` (partially tested — got through scan + topic-select before bugs)
- `strategy-bottomup.yaml`
- `strategy-sequential.yaml`
- `discovery-pipeline.yaml` (attempted 5+ times, each found a new bug)

**Recipe validation audit:** A comprehensive code review of all 10 recipes was done (see `docs/RECIPE-VALIDATION-REPORT.md`). All 5 known bug patterns were checked. 4 additional bugs were found and fixed in commit `2d34677`. See the report for full details.

### Discovery Pipeline v1 Test Runs (Preserved)

Before the v2 redesign, we ran the v1 pipeline successfully on 4 repos. The results are preserved in `.discovery-prior/` directories:
- `amplifier/.discovery-prior/` — 8 DOT files, 8 PNGs
- `amplifier-core/.discovery-prior/` — 19 DOT files, 9 PNGs
- `amplifier-foundation/.discovery-prior/` — 11 DOT files, 11 PNGs
- `amplifier-bundle-dev-machine/.discovery-prior/` — 19 DOT files, 9 PNGs

---

## Known Recipe Framework Gotchas

These were learned the hard way during e2e testing. **CRITICAL knowledge for anyone working on these recipes:**

### 1. `condition:` not `when:`

The recipe framework's `Step` class uses `condition:` for conditional execution. Using `when:` causes `Step.__init__() got an unexpected keyword argument 'when'`.

```yaml
# WRONG
- id: my-step
  when: "{{some_var}} == 'true'"

# CORRECT
- id: my-step
  condition: "{{some_var}} == 'true'"
```

### 2. JSON booleans in Python

When `{{variable}}` is template-substituted into a bash heredoc containing Python code, JSON booleans (`true`/`false`) are substituted verbatim. These are invalid Python (`True`/`False`).

```bash
# WRONG — produces: render_png = true (Python NameError)
render_png = {{render_png}}

# CORRECT — works with both JSON and Python booleans
import json
render_png = json.loads(r"""{{render_png}}""")
```

### 3. foreach stringifies dicts

When `foreach: "{{topics}}"` iterates and passes `context: {topic: "{{topic}}"}` to a sub-recipe, the template engine stringifies the dict. The sub-recipe receives a string like `"{'name': 'foo', 'slug': 'bar'}"` instead of an object.

```yaml
# WRONG — sub-recipe receives stringified dict
foreach: "{{topics}}"
context:
  topic: "{{topic}}"

# CORRECT — flatten fields in the parent
foreach: "{{topics}}"
context:
  topic_name: "{{topic.name}}"
  topic_slug: "{{topic.slug}}"
  topic_description: "{{topic.description}}"
```

### 4. Eager template substitution (undefined variables)

The template engine substitutes ALL `{{variable}}` references in a step's command text BEFORE executing, even in Python if/else branches that won't be reached. If a variable might be undefined (because a prior step was skipped via `condition:`), it WILL fail with `Undefined variable`.

```yaml
# WRONG — if topic-select was skipped, {{topics}} is undefined and this fails
# even if the condition evaluates to false
- id: save-topics
  condition: "{{parent_topics_available}} != 'true'"
  command: |
    cat << 'EOF'
    {{topics}}
    EOF

# CORRECT — split into separate conditional steps where each only references
# variables guaranteed to exist when its condition is true
- id: save-topics-from-scan
  condition: "{{parent_topics_available}} != 'true'"
  command: |
    echo '{{topics}}' > {{output_dir}}/topics.json

- id: save-topics-from-file
  condition: "{{parent_topics_available}} == 'true'"
  command: |
    # Only references {{repo_path}} which always exists
    cat {{repo_path}}/.discovery/investigation/topdown/topics.json
```

### 5. Nested templates don't resolve

`{{output_dir}}` where `output_dir`'s default is `{{repo_path}}/.discovery` results in the literal string `{{repo_path}}/.discovery` in sub-recipe context (no recursive resolution).

```yaml
# WRONG — sub-recipe receives the literal string "{{repo_path}}/.discovery"
context:
  output_dir: "{{repo_path}}/.discovery"
  # Then in sub-recipe:
  sub_output_dir: "{{output_dir}}/modules"  # becomes "{{repo_path}}/.discovery/modules" (unresolved!)

# CORRECT — use simple values and construct paths from {{repo_path}} directly
context:
  repo_path: "{{repo_path}}"
  # Construct paths in the sub-recipe from repo_path
```

### 6. `output:` + `parse_json: true` needed for context propagation

A bash step must have `output: "variable_name"` and `parse_json: true` to populate a recipe context variable. Without these, stdout is discarded — the next step can't read what the previous step produced.

```yaml
# WRONG — stdout goes nowhere
- id: compute-plan
  command: |
    python3 -c "import json; print(json.dumps({'items': [1,2,3]}))"

# CORRECT — stdout captured into recipe context as structured data
- id: compute-plan
  command: |
    python3 -c "import json; print(json.dumps({'items': [1,2,3]}))"
  output: "plan"
  parse_json: true

# Now {{plan.items}} is available in subsequent steps
```

---

## Immediate Next Steps

### Priority 1: Sync bug fixes and push

Copy the 9 bug-fix commits from workspace to clean repo and push to GitHub. The remote currently has recipes that fail at runtime.

```bash
# In the clean repo:
cd /home/bkrabach/dev/amplifier-bundle-dot-graph

# Copy fixed recipes from workspace
cp /home/bkrabach/dev/dot-graph-bundle/recipes/*.yaml recipes/

# Copy updated tests
cp /home/bkrabach/dev/dot-graph-bundle/tests/test_discovery_pipeline_recipe.py tests/
cp /home/bkrabach/dev/dot-graph-bundle/tests/test_discovery_combine_recipe.py tests/
cp /home/bkrabach/dev/dot-graph-bundle/tests/test_strategy_sequential_recipe.py tests/
cp /home/bkrabach/dev/dot-graph-bundle/tests/test_discovery_investigate_topic_recipe.py tests/
cp /home/bkrabach/dev/dot-graph-bundle/tests/test_final_verification.py tests/

# Also copy the validation report
cp /home/bkrabach/dev/dot-graph-bundle/docs/RECIPE-VALIDATION-REPORT.md docs/

# Run tests, commit, push
python -m pytest tests/ modules/tool-dot-graph/tests/ --tb=short
git add -A && git commit -m "fix: batch recipe runtime fixes (9 bug fixes from e2e testing)"
git push origin main
```

### Priority 2: Test each recipe individually (Tier 2-4)

Follow the tiered approach from `docs/RECIPE-VALIDATION-REPORT.md`. Test bottom-up, each tier building on the previous:

**Tier 2 — Investigation sub-recipes:**
- `discovery-investigate-topic.yaml` — dispatch investigation agents for a single topic
- `discovery-synthesize-module.yaml` — synthesize per-module consensus with quality gate
- `discovery-combine.yaml` — convergence/divergence analysis (needs mock inputs from both strategies)

**Tier 3 — Strategy recipes:**
- `strategy-topdown.yaml` — full conceptual investigation pipeline
- `strategy-bottomup.yaml` — full empirical traversal pipeline

**Tier 4 — Orchestrators:**
- `strategy-sequential.yaml` — bottom-up then top-down
- `discovery-pipeline.yaml` — both in parallel then combine

For each: execute with minimal context against the `amplifier` repo, observe what works and what fails. Follow integration-testing-discipline: **observe ALL failures first, fix as a batch, then retest.** Do NOT fix bugs during observation runs.

### Priority 3: Full e2e pipeline run

Once all individual recipes pass, run the full pipeline:

```python
recipes(
    operation="execute",
    recipe_path="@dot-graph:recipes/discovery-pipeline.yaml",
    context={
        "repo_path": "/home/bkrabach/dev/dot-graph-bundle/amplifier",
        "fidelity": "standard",
        "strategies": "both",
        "render_png": "true"
    }
)
```

### Priority 4: Run on remaining repos

After amplifier passes, run on amplifier-core, amplifier-foundation, and amplifier-bundle-dev-machine.

---

## Architecture — The Complete Bundle Structure

```
amplifier-bundle-dot-graph/
├── bundle.md                              # Root bundle
├── behaviors/
│   ├── dot-graph.yaml                     # Full bundle = dot-core + dot-discovery
│   ├── dot-core.yaml                      # Core: dot-author + diagram-reviewer + tool
│   └── dot-discovery.yaml                 # Discovery: 9 investigation agents + recipes
├── agents/                                # 11 agents total
│   ├── dot-author.md                      # Creates/refines DOT diagrams (model_role: coding)
│   ├── diagram-reviewer.md                # PASS/WARN/FAIL quality verdicts (model_role: critique)
│   ├── discovery-prescan.md               # Topic selection from prescan data
│   ├── discovery-code-tracer.md           # HOW: traces execution paths
│   ├── discovery-behavior-observer.md     # WHAT: catalogs real instances
│   ├── discovery-integration-mapper.md    # WHERE/WHY: maps boundaries
│   ├── discovery-synthesizer.md           # Per-module consensus
│   ├── discovery-level-synthesizer.md     # v2: recursive bottom-up (model_role: coding)
│   ├── discovery-subsystem-synthesizer.md # v2: cross-module seams (model_role: reasoning)
│   ├── discovery-overview-synthesizer.md  # v2: system-level overview (model_role: reasoning)
│   └── discovery-combiner.md              # v2: convergence/divergence (model_role: reasoning)
├── context/                               # 12 context files
│   ├── dot-awareness.md                   # Bundle awareness (~30 lines, ~150 tokens)
│   ├── dot-instructions.md                # Core DOT instructions (~150 lines)
│   ├── discovery-awareness.md             # Discovery awareness
│   └── discovery-*-instructions.md        # Per-agent instructions (9 files)
├── recipes/                               # 10 recipes
│   ├── discovery-pipeline.yaml            # Thin orchestrator (parallel + combine)
│   ├── strategy-topdown.yaml              # Standalone conceptual investigation
│   ├── strategy-bottomup.yaml             # Standalone empirical traversal
│   ├── strategy-sequential.yaml           # Bottom-up then top-down
│   ├── discovery-combine.yaml             # Convergence/divergence analysis
│   ├── discovery-investigate-topic.yaml   # Per-topic agent dispatch
│   ├── discovery-synthesize-module.yaml   # Per-module consensus w/ quality gate
│   ├── synthesize-level.yaml              # Per-directory synthesis
│   ├── synthesize-subsystem.yaml          # Cross-module synthesis
│   └── synthesize-overview.yaml           # System-level synthesis
├── modules/tool-dot-graph/                # Tool module
│   └── amplifier_module_tool_dot_graph/
│       ├── __init__.py                    # DotGraphTool class (async mount(coordinator, config))
│       ├── validate.py                    # 3-layer validation (syntax + structural + render)
│       ├── render.py                      # Graphviz CLI rendering (SVG/PNG/PDF)
│       ├── setup_helper.py                # Environment detection + install guidance
│       ├── analyze.py                     # NetworkX-backed analysis (8 operations)
│       ├── prescan.py                     # Structural codebase scan
│       └── assemble.py                    # Plumbing only (v2: stripped to ~153 lines)
├── skills/                                # 5 skills
│   ├── dot-syntax/SKILL.md               # Quick syntax reference
│   ├── dot-patterns/SKILL.md             # Pattern catalog with templates
│   ├── dot-as-analysis/SKILL.md          # Reconciliation approach
│   ├── dot-quality/SKILL.md              # Quality standards (Iron Law style)
│   └── dot-graph-intelligence/SKILL.md   # Graph analysis tools
├── scripts/
│   ├── dot-validate.sh                    # Standalone validation
│   └── dot-render.sh                      # Standalone rendering
├── docs/
│   ├── DOT-SYNTAX-REFERENCE.md            # Full DOT language reference
│   ├── DOT-PATTERNS.md                    # Pattern catalog
│   ├── DOT-QUALITY-STANDARDS.md           # Quality gates, shape vocabularies
│   ├── GRAPHVIZ-SETUP.md                  # Installation guide
│   ├── GRAPH-ANALYSIS-GUIDE.md            # How to use analysis tools
│   ├── RECIPE-VALIDATION-REPORT.md        # Comprehensive audit of all 10 recipes
│   └── plans/                             # Design specs + implementation plans
│       ├── 2026-03-13-dot-graph-bundle-design.md        # Original bundle design
│       ├── 2026-03-16-discovery-pipeline-design.md      # v1 discovery design
│       ├── 2026-03-17-discovery-pipeline-v2-design.md   # v2 discovery design
│       └── 2026-03-17-discovery-phase-*-v2-implementation.md  # Phase A-D v2 plans
└── tests/                                 # 1287 tests
    ├── test_final_verification.py         # Master file count + structure verification
    ├── test_discovery_pipeline_recipe.py   # Pipeline recipe tests
    ├── test_discovery_combine_recipe.py    # Combine recipe tests
    ├── test_strategy_sequential_recipe.py  # Sequential strategy tests
    ├── test_discovery_investigate_topic_recipe.py  # Investigate-topic tests
    └── ... (many more)
```

### Tool Operations (6 total)

| Operation | What It Does | Dependencies |
|-----------|-------------|--------------|
| `validate` | 3-layer validation (syntax → structural → render quality) | pydot; Graphviz optional |
| `render` | Graphviz CLI rendering to SVG/PNG/PDF | pydot + Graphviz |
| `setup` | Environment detection, install guidance | None |
| `analyze` | NetworkX-backed graph analysis (8 sub-operations) | pydot + networkx |
| `prescan` | Structural codebase scan (directory tree, language detection, file inventory) | None |
| `assemble` | Hierarchical DOT assembly (directory creation, manifest tracking, render triggering) | pydot |

### Analysis Sub-Operations (8 total)

| Sub-Operation | What It Does |
|--------------|-------------|
| `stats` | Node count, edge count, density, DAG detection, connected components |
| `reachability` | All nodes reachable from a source node |
| `unreachable` | Nodes with no incoming edges (excluding known entry points) |
| `cycles` | Detect all simple cycles in a directed graph |
| `paths` | All simple paths between two nodes (capped at 100) |
| `critical_path` | Longest path in a DAG |
| `subgraph_extract` | Extract a named cluster subgraph into standalone DOT |
| `diff` | Structural differences between two DOT graphs |

---

## Design Philosophy

### Reconciliation as Analysis

The diagram doesn't document the bug. Drawing the diagram finds the bug. When agents are forced to reconcile all discovered information into a valid graph, they cannot paper over contradictions — the graph won't validate. This surfaces issues that prose-based analysis, LSP tools, and even compilers routinely miss.

### Composable Recipe Library

Each recipe is independently useful. They compose into larger strategies. You can run `strategy-topdown.yaml` alone, `strategy-bottomup.yaml` alone, `strategy-sequential.yaml` for enriched investigation, or `discovery-pipeline.yaml` for both in parallel. New strategies can be added without touching existing recipes.

### Top-Down vs Bottom-Up (Complementary Perspectives)

- **Top-down:** "What do we think matters about this system?" — conceptual, hypothesis-driven. Pick topics via prescan, investigate how things work, synthesize per-topic.
- **Bottom-up:** "What does this system actually contain?" — empirical, discovery-driven. Post-order tree traversal from leaf directories upward, synthesizing what actually exists at each level.
- **The delta between them is itself valuable data.** Where they diverge is where the architecture's mental model doesn't match its actual implementation.

### Synthesis is Recursive

The same core act (reconcile → discover → synthesize) applies at every zoom level:
- Investigation agents at the bottom
- `discovery-level-synthesizer` working up through directories
- `discovery-subsystem-synthesizer` at module boundaries
- `discovery-overview-synthesizer` at the top
- `discovery-combiner` comparing the two perspectives

`assemble.py` is just plumbing — agents do ALL the semantic work.

### Agent-Produced Output at Every Level

The v1 pipeline used agents for investigation but `assemble.py` (Python tool) for the final output — producing structurally correct but semantically dead graphs. The v2 redesign makes every level agent-produced: richly styled, color-coded clusters, semantic shapes, meaningful edge labels that explain WHY not just WHAT.

### Data Flow

```
prescan
  │
  ├──────────────────────────────┐
  ▼                              ▼
strategy-topdown               strategy-bottomup
  │                              │
  │  topics → investigate →      │  leaf dirs → post-order traversal
  │  per-module synthesis →      │  level-synthesizer at each dir →
  │  subsystem synthesis →       │  subsystem synthesis →
  │  overview synthesis          │  overview synthesis
  │                              │
  ▼                              ▼
.discovery/investigation/      .discovery/investigation/
  topdown/                       bottomup/
  │                              │
  └──────────┬───────────────────┘
             ▼
      discovery-combine
             │
             ▼
      .discovery/output/
        overview.dot/png
        subsystems/
```

### Convergence/Divergence Classification

The `discovery-combiner` agent classifies findings into 4 categories:

| Category | Color | Meaning |
|----------|-------|---------|
| Convergence | Green | Both strategies found the same thing. High-confidence understanding. |
| Top-down only | Amber | Conceptual investigation saw it but bottom-up didn't. Aspirational structure not reflected in code. |
| Bottom-up only | Blue | Empirical traversal found it but conceptual investigation missed it. Hidden complexity or undocumented design. |
| Divergence | Red | Same thing characterized differently by both strategies. Highest-value findings. Tracked as D-01, D-02... |

---

## Key Files to Read

| Need | File |
|------|------|
| v2 design spec | `docs/plans/2026-03-17-discovery-pipeline-v2-design.md` |
| Original bundle design | `docs/plans/2026-03-13-dot-graph-bundle-design.md` |
| Recipe validation audit | `docs/RECIPE-VALIDATION-REPORT.md` |
| Phase A v2 implementation | `docs/plans/2026-03-17-discovery-phase-a-v2-implementation.md` |
| Phase B v2 implementation | `docs/plans/2026-03-17-discovery-phase-b-v2-implementation.md` |
| Phase C v2 implementation | `docs/plans/2026-03-17-discovery-phase-c-v2-implementation.md` |
| Phase D v2 implementation | `docs/plans/2026-03-17-discovery-phase-d-v2-implementation.md` |
| v1 discovery design | `docs/plans/2026-03-16-discovery-pipeline-design.md` |
| This document | `CONTEXT-TRANSFER.md` |

---

## Workspace Layout

```
/home/bkrabach/dev/dot-graph-bundle/           # Main workspace (development)
├── amplifier/                                  # Submodule: microsoft/amplifier
│   └── .discovery-prior/                       # v1 pipeline results (preserved)
├── amplifier-core/                             # Submodule: microsoft/amplifier-core
│   └── .discovery-prior/                       # v1 pipeline results (preserved)
├── amplifier-foundation/                       # Submodule: microsoft/amplifier-foundation
│   └── .discovery-prior/                       # v1 pipeline results (preserved)
├── amplifier-bundle-dev-machine/               # Submodule: ramparte/amplifier-bundle-dev-machine
│   └── .discovery-prior/                       # v1 pipeline results (preserved)
├── [all bundle source files]                   # The actual bundle code
├── CONTEXT-TRANSFER.md                         # THIS FILE
└── AGENTS.md                                   # Workspace instructions

/home/bkrabach/dev/amplifier-bundle-dot-graph/  # Clean push repo (for GitHub pushes)
```

**Why two repos?** The workspace has submodules (amplifier, amplifier-core, etc.) that the bundle itself doesn't ship — they're targets for discovery pipeline testing. The clean push repo has only the bundle files. Changes are developed in the workspace, then copied to the clean repo for pushing.

---

## Bundle Stats at Transfer Time

| Metric | Count |
|--------|:-----:|
| Tests passing | 1287 |
| Agents | 11 (2 core + 9 discovery) |
| Skills | 5 |
| Docs | 5 |
| Recipes | 10 |
| Behaviors | 3 (dot-core, dot-discovery, dot-graph) |
| Tool operations | 6 (validate, render, setup, analyze, prescan, assemble) |
| Analysis sub-operations | 8 (stats, reachability, unreachable, cycles, paths, critical_path, subgraph_extract, diff) |
| Commits in workspace | ~105 |
| Commits on GitHub | 89 (missing 9 recipe bug fixes + validation report) |
| Session turns | 114+ |
| Session duration | 5 days |
| events.jsonl size at termination | 780MB (6,619 events, 178 resume cycles) |

---

## Session Termination Details

This session accumulated a **780MB events.jsonl** (6,619 events, 178 session:resume cycles) over 5 days and 114+ turns. The file caused I/O starvation during context compaction, repeatedly crashing the tmux window. The session-analyst confirmed this as the root cause. Starting a fresh session is the correct mitigation — all state is preserved in git commits and this context transfer document.

The `events.jsonl` file is located at:
```
~/.amplifier/events/<session-id>/events.jsonl
```

If the session ID needs to be found, check recent `.amplifier/` state or `amplifier session list`.

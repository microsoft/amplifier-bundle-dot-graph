# `amplifier-bundle-dot-graph` Design

## Goal

Create a general-purpose DOT/Graphviz infrastructure bundle for the Amplifier ecosystem that provides core plumbing — knowledge, tools, and graph intelligence — enabling any bundle to gain DOT capabilities through behavior composition.

## Background

DOT is used extensively across the Amplifier ecosystem — Attractor pipelines are defined in DOT, dot-docs generates architecture diagrams, recipes can be visualized as flow graphs, and Parallax uses DOT for investigation artifacts. Despite this widespread usage, every project re-invents DOT infrastructure: validation logic, rendering wrappers, quality standards, and authoring guidance.

An extensive multi-agent discovery effort (12+ agent dispatches across 3 waves, scanning 6,240 sessions, cataloging 70+ existing DOT artifacts across 6 projects) confirmed this fragmentation and revealed significant untapped potential — DOT as a reconciliation forcing function, as an analysis substrate for cheap code-based graph intelligence, and as a dense context representation format.

This bundle consolidates the general-purpose DOT infrastructure into one composable package, so domain bundles can focus on their domain semantics while getting world-class DOT plumbing for free.

## Approach

**Infrastructure Toolkit with Three Tiers**, designed as one coherent thing:

| Tier | What | Dependencies |
|------|------|-------------|
| Tier 1 — Knowledge Layer | Agents + context + skills | None. Works with no tool module and no Graphviz installed |
| Tier 2 — Validation & Rendering | Python tool module with syntax/structural/render validation, Graphviz CLI wrapper, setup helper | `pydot` (pure Python). Graphviz optional — graceful degradation |
| Tier 3 — Graph Intelligence | NetworkX-backed analysis: parse DOT into graph objects for cheap code-based intelligence | `pydot` + `networkx` (both pure Python) |

This approach was chosen over alternatives (knowledge-only bundle, tool-only module, monolithic DOT engine) because it provides immediate value at Tier 1 with zero dependencies, while the tool tiers add progressively more powerful capabilities. Domain bundles get exactly what they need through composition.

## Architecture

### Bundle Identity

- **Name:** `amplifier-bundle-dot-graph`
- **Namespace:** `dot-graph`
- **What it is:** General-purpose DOT/Graphviz infrastructure. Knowledge, tools, graph intelligence.
- **What it is NOT:** Not domain-specific. Does not know about Attractor pipelines, recipe structures, Parallax investigations, or codebase architecture. Domain bundles compose the behavior and add their own semantics.

### Directory Structure

```
amplifier-bundle-dot-graph/
├── bundle.md                          # Thin root bundle (~15 lines YAML)
├── behaviors/
│   └── dot-graph.md                   # The composable behavior (agents + context + tools)
├── agents/
│   ├── dot-author.md                  # DOT authoring expert (context sink)
│   └── diagram-reviewer.md            # DOT quality reviewer (PASS/WARN/FAIL)
├── context/
│   ├── dot-awareness.md               # Thin pointer (~30 lines) — loaded by composing bundles
│   └── dot-instructions.md            # Mid-weight reference (~150 lines) — @mentioned by agents
├── docs/
│   ├── DOT-SYNTAX-REFERENCE.md        # Full DOT language reference (heavy, agent-only)
│   ├── DOT-PATTERNS.md                # Pattern catalog with copy-paste templates
│   ├── DOT-QUALITY-STANDARDS.md       # Quality gates, shape vocabularies, anti-patterns
│   ├── GRAPHVIZ-SETUP.md              # Installation guide for all platforms
│   └── GRAPH-ANALYSIS-GUIDE.md        # How to use the analysis tools
├── skills/
│   ├── dot-syntax/                    # Quick syntax reference skill
│   ├── dot-patterns/                  # Common pattern templates skill
│   ├── dot-as-analysis/               # DOT for code/system analysis (reconciliation approach)
│   ├── dot-quality/                   # Quality standards discipline
│   └── dot-graph-intelligence/        # Graph analysis tools process
├── modules/
│   └── tool-dot-graph/
│       ├── pyproject.toml             # name = "amplifier-module-tool-dot-graph", hatchling
│       └── amplifier_module_tool_dot_graph/
│           ├── __init__.py            # async mount(coordinator, config)
│           ├── validate.py            # Syntax + structural + quality validation
│           ├── render.py              # Graphviz CLI wrapper (PNG/SVG/PDF)
│           ├── analyze.py             # NetworkX-backed graph intelligence
│           └── setup_helper.py        # Graphviz detection and install guidance
└── scripts/
    ├── dot-validate.sh                # Standalone validation script
    └── dot-render.sh                  # Standalone rendering script
```

### Key Structural Decisions

- **`behaviors/dot-graph.md`** is the primary integration point — one line in any bundle's includes.
- **`context/dot-awareness.md`** is the only thing that loads in composing sessions (~30 lines, ~150 tokens).
- **`docs/`** carries the heavy knowledge — only loaded via `@mention` inside agent sessions.
- **`skills/`** provides on-demand reference without requiring the full behavior.
- **`scripts/`** gives standalone CLI utility even outside Amplifier sessions.
- **`modules/tool-dot-graph/`** follows the co-located module convention (same as recipes, python-dev, rust-dev). Referenced in behavior YAML via `source: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=modules/tool-dot-graph`. Build backend: `hatchling`. Dependencies: `pydot`, `networkx`. No PyPI publishing — installs from git.

## Components

### Tier 1 — Knowledge Layer

#### dot-author Agent

DOT authoring expert operating as a context sink:

- Carries: full DOT syntax reference, shape vocabularies (general-purpose AND pipeline), quality standards, anti-patterns catalog, pattern templates
- Can generate DOT from scratch, review/refine existing DOT, explain DOT structures
- Knows about progressive disclosure (overview → detail files), line count targets, legend conventions
- Model role: `coding` (primary output is DOT code)

#### diagram-reviewer Agent

DOT quality reviewer producing structured verdicts:

- Reads a DOT file and produces a structured verdict: **PASS** / **WARN** / **FAIL**
- Checks against quality standards: line count ranges, legend presence, node ID conventions, shape vocabulary compliance, anti-patterns
- Knows about the reconciliation value — flags structural issues that may indicate real code/system problems
- Model role: `critique`

#### Context — Two Tiers

| File | Size | Loaded When | Purpose |
|------|------|-------------|---------|
| `dot-awareness.md` | ~30 lines | Always (in composing bundles) | Thin pointer with capability awareness (tools, agents, skills) PLUS value proposition seeds — one line each for: dense representation, reconciliation forcing function, multi-scale navigation, analysis substrate, multi-modal bridge, workflow visualization, investigation artifact |
| `dot-instructions.md` | ~150 lines | `@mentioned` by agents | Mid-weight reference with syntax quick-ref, common patterns, quality gates |

The awareness context seeds ALL value propositions into every composing session, priming the reconciliation mindset and the full range of DOT value at minimal token cost.

#### Skills — Five Packages

| Skill | Type | Size Target | Purpose |
|-------|------|-------------|---------|
| `dot-syntax` | Reference | ~150 lines | Quick-reference card: nodes, edges, attributes, subgraphs, HTML labels, copy-paste snippets |
| `dot-patterns` | Reference | ~200 lines | Pattern catalog: DAGs, state machines, layered architectures, fan-out/fan-in, legends. Companion files with `.dot` templates |
| `dot-as-analysis` | Process | ~200 lines | How to use DOT for code/system analysis — the reconciliation approach. Step-by-step: introspect → represent → reconcile → surface issues. Anti-rationalization table for when agents try to skip reconciliation |
| `dot-quality` | Discipline | ~150 lines | Quality rules: line count targets, legend requirements, shape vocabulary, node ID conventions, anti-patterns. "Iron Law" style enforcement |
| `dot-graph-intelligence` | Process | ~150 lines | How to use graph analysis tools: parse DOT → run algorithms → interpret results. When to use code-based analysis vs LLM-based review |

Skills design principles:
- Descriptions start with "Use when..." for proper discovery
- Heavy reference goes to companion files
- `dot-as-analysis` gets anti-rationalization tables
- `dot-quality` gets "Iron Law" treatment
- Shipped via `tools:` config in behavior YAML

### Tier 2 — Validation & Rendering Tools

#### dot_validate — Three-Layer Validation

| Layer | What It Checks | How | Requires Graphviz? |
|-------|---------------|-----|-------------------|
| Syntax | Valid DOT that parses | `pydot` parser (pure Python) | No |
| Structural | Connectivity, unreachable nodes, orphan clusters, missing legends | `pydot` parse → inspect graph object | No |
| Render quality | Actually renders without warnings, output size reasonable | `dot -Tcanon` or `dot -Tsvg` | Yes (graceful skip if absent) |

Returns structured output:
```json
{
  "valid": true,
  "issues": [{"layer": "structural", "severity": "warn", "line": 12, "message": "..."}],
  "stats": {"nodes": 15, "edges": 22, "clusters": 3, "lines": 87}
}
```

Layers 1 and 2 work without Graphviz. Layer 3 gracefully degrades with clear setup guidance.

**Existing code to adapt:** `dot_validation.py` (216 lines) from the dot-docs project.

#### dot_render — Graphviz CLI Wrapper

- **Input:** DOT file path or DOT string content
- **Output formats:** SVG (default), PNG, PDF, JSON
- **Layout engines:** `dot` (default), `neato`, `fdp`, `circo`, etc.
- **Returns:** Rendered file path, or error with installation guidance if Graphviz not found

#### dot_setup — Environment Helper

- Detects Graphviz installation, version, available layout engines
- Platform-specific installation instructions (`apt`, `brew`, `choco`, `conda`)
- Detects Python deps (`pydot`, `networkx`)
- Returns structured status report

### Tier 3 — Graph Intelligence Tools

#### dot_analyze — Graph Intelligence Operations

NetworkX-backed, pure Python, zero LLM cost:

| Operation | What It Does | Use Case |
|-----------|-------------|----------|
| `reachability` | From node X, what nodes can be reached? | Impact analysis |
| `unreachable` | Nodes with no incoming edges (excluding start/entry) | Dead code detection |
| `cycles` | Detect cycles in what should be a DAG | Circular dependency detection |
| `paths` | All paths between node A and node B | Connection understanding |
| `critical_path` | Longest path through the graph | Bottleneck identification |
| `subgraph_extract` | Pull out a cluster as standalone DOT | Zoom-in navigation |
| `diff` | Structural diff between two DOT files | Architecture change tracking |
| `stats` | Node count, edge count, density, components, diameter | Health metrics |

**Input:** DOT file path, DOT string, or previously-parsed graph reference.

**Output:** Structured JSON AND optionally annotated DOT (unreachable nodes in red, cycles in bold, etc.).

**Dependencies:** `pydot` (parsing) + `networkx` (analysis). Both pure Python.

#### The Analysis-to-Artifact Loop

```
Agent produces DOT
  → dot_analyze finds issues
    → annotated DOT highlights problems
      → dot_render makes it visible
        → agent or human acts
          → updated DOT
            → loop
```

## Data Flow

### Behavior Composition Flow

Any bundle includes the behavior with one line:

```yaml
includes:
  - dot-graph:behaviors/dot-graph
```

What that gives them (token cost in their session):

| Component | Token Cost | When |
|-----------|-----------|------|
| `dot-awareness.md` context | ~150 tokens | Always loaded |
| `dot-author` agent | 0 | Until spawned |
| `diagram-reviewer` agent | 0 | Until spawned |
| DOT tools | 0 | Tool registration only |
| DOT skills | 0 | Until loaded on demand |

The context sink pattern ensures heavy knowledge (full syntax reference, quality standards, pattern catalog) loads only in agent sub-sessions, never in the composing bundle's root session.

### Composing Bundle Relationships

```
amplifier-bundle-dot-graph (infrastructure)
  │
  ├── amplifier-bundle-attractor
  │     Composes: dot-graph:behaviors/dot-graph
  │     Keeps: shape-to-handler mapping, pipeline execution, model stylesheet, fidelity modes
  │     Gains: general validation, rendering, graph analysis (cycle detection for free)
  │
  ├── amplifier-bundle-recipes
  │     Composes: dot-graph:behaviors/dot-graph
  │     Adds: recipe-to-DOT mapping (domain knowledge)
  │     Gains: validation, rendering, recipe flow visualization
  │
  ├── amplifier-bundle-parallax-discovery
  │     Composes: dot-graph:behaviors/dot-graph
  │     Uses DOT for: investigation artifacts, multi-scale navigation
  │     Gains: graph analysis for comparing findings, structural diffing between waves
  │
  └── amplifier-foundation (generate_event_dot.py)
        Stays in foundation. Can optionally use dot-graph tools if behavior composed.
```

## Error Handling

### Graphviz Not Installed

Tier 1 (knowledge layer) works fully. Tier 2 validation layers 1-2 (syntax, structural) work fully. Tier 2 layer 3 (render quality) and `dot_render` gracefully skip with clear error message and platform-specific installation instructions via `dot_setup`.

### Invalid DOT Input

`dot_validate` returns structured issues with layer, severity, line number, and message. Never crashes — always returns a verdict. Parsing errors from `pydot` are caught and reported as syntax-layer issues.

### Tool Module Not Installed

Skills and agents work without the tool module. Agent guidance includes manual validation approaches (visual inspection, mental model checking) when tools are unavailable.

### Analysis on Disconnected Graphs

`dot_analyze` operations handle disconnected graphs gracefully. `stats` reports component count. `reachability` scopes to the connected component. `cycles` checks each component independently.

## Testing Strategy

### Tool Module Tests

- **Unit tests** for each validation layer (syntax, structural, render quality) with known-good and known-bad DOT inputs
- **Unit tests** for each analysis operation against hand-crafted graph fixtures
- **Integration tests** for the render pipeline (requires Graphviz — marked as optional, skipped in CI if unavailable)
- **Fixture library** of DOT files: valid, invalid syntax, structurally flawed, complex real-world examples adapted from ecosystem artifacts

### Knowledge Layer Validation

- **Skill loading tests** — verify each skill loads, has proper metadata, descriptions start with "Use when..."
- **Agent smoke tests** — verify agents can be spawned and produce DOT output
- **Context size tests** — verify `dot-awareness.md` stays under token budget (~30 lines)

### Composition Tests

- **Behavior composition test** — verify a minimal bundle can compose `dot-graph:behaviors/dot-graph` and access all components
- **Cross-bundle tests** — verify Attractor and recipes can compose the behavior alongside their own

## Use Cases & Value Propositions

### Primary Use Cases

The bundle actively teaches and supports these through skills, agents, and awareness context:

1. **DOT as reconciliation forcing function** — Force graph construction to surface bugs, dead code, gaps, contradictions that LSP, compilers, and prose miss. Graph's formal structure demands structural commitment.

2. **DOT as dense context representation** — Compress complex system understanding into navigable, token-efficient graph structures.

3. **DOT as multi-scale navigation** — Subgraphs as zoom levels. Context window is the fixed "screen size." Google Maps metaphor for system understanding.

4. **DOT as analysis substrate** — Parse into graph objects for cheap code-based intelligence: impact analysis, path finding, cycle detection, dead node detection, structural diffing. Zero LLM tokens.

5. **DOT as multi-modal bridge** — Rendered to SVG/PNG for users, dashboards, docs, vision-capable models.

6. **DOT as workflow/recipe visualization** — Complex workflows become comprehensible as visual flow graphs.

7. **DOT as investigation artifact** — Forces agents to commit to specific nodes/edges, preventing vague analysis.

### Enabling Use Cases

Infrastructure for domain bundles to build on:

8. **Pipeline definition** — Attractor's domain. dot-graph provides syntax/validation/rendering.

9. **Architecture documentation** — General quality standards and review from dot-graph. Domain-specific standards with domain bundles.

10. **Systematic codebase mapping** — Future recipe-driven workflow: walk codebase file-by-file, build DOT per module, assemble into full system graph, plug into graph intelligence.

## Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Bundle name:** `amplifier-bundle-dot-graph`, namespace `dot-graph` | About DOT the language, not specifically the Graphviz tool |
| 2 | **Tool module location:** co-located at `modules/tool-dot-graph/` | Follows recipes/python-dev/rust-dev convention. Referenced via `#subdirectory=` in behavior YAML |
| 3 | **Graphviz:** optional dependency | Tier 1 and Tier 2 Layers 1-2 work without it. Graceful degradation with setup guidance |
| 4 | **Python parsing:** `pydot` for parsing, `networkx` for analysis | `pydot` reads DOT into manipulable objects (unlike `graphviz` package which only generates). Both pure Python |
| 5 | **Quality standards location:** general standards in dot-graph | Shape vocabulary, line counts, legends, anti-patterns here. Domain-specific standards stay with domain bundles |
| 6 | **No PyPI publishing** | Tool installs from git via behavior `source:` field, same as every other ecosystem module |
| 7 | **Dialect handling:** bundle teaches general DOT | Documents both Attractor shape-based and `node_type` attribute-based dialects as ecosystem context. Validation tools accept both |
| 8 | **dot-author scope:** general DOT only | Domain bundles create domain-specific DOT agents or add mappings themselves |
| 9 | **dot-docs assets:** migrated here | dot-docs as a separate project is not assumed to continue. General-purpose assets (validation logic, quality standards, shape vocabulary, rendering wrappers) come into this bundle |

## Open Questions

These are noted for the implementation phase:

- **Shape vocabulary for general-purpose DOT** — Exact shape vocabulary for non-pipeline DOT needs to be adapted from dot-docs quality standards during implementation.
- **Discovery pipeline scope** — How much of the dot-docs discovery pipeline (prescan/synthesis recipes) to bring into this bundle vs. treat as future roadmap.
- **Format conversion** — Whether to include a `dot_convert` tool for DOT-to-other-format conversions beyond Graphviz rendering (e.g., DOT to Mermaid, DOT to JSON graph format).
- **Graph database integration** — Noted as future vision. NetworkX in-memory first, with potential future graph DB for persistent cross-session graph intelligence.

## Discovery Context

This design was informed by an extensive multi-agent discovery effort:

- 12+ agent dispatches across 3 waves, scanning 6,240 sessions
- 70+ existing DOT artifacts cataloged across the ecosystem
- 10 research documents produced:
  - `SESSION-INDEX.md` — Session catalog
  - `DOT-CONCEPTS-DEEP-DIVE.md` — Conceptual analysis
  - `BUNDLE-GUIDANCE.md` — Bundle architecture guidance
  - `DOT-ARTIFACTS-CATALOG.md` — Artifact inventory
  - `DOT-ECOSYSTEM-RESEARCH.md` — Ecosystem-wide research
  - `DOT-DIALECT-COMPARISON.md` — Dialect analysis
  - `ATTRACTOR-DOT-EXPERTISE.md` — Attractor-specific DOT expertise
  - `BOOTSTRAP-SYNTHESIS.md` — Bootstrap synthesis
  - `DOT-DOCS-SESSION-MINING.md` — dot-docs session mining
  - `RECIPE-DOT-ANALYSIS.md` — Recipe DOT analysis
- `DISCOVERY-INDEX.md` serves as the master navigation for all discovery work

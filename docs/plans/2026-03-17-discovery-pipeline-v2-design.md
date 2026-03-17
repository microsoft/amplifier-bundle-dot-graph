# Discovery Pipeline v2 Design

## Goal

Redesign the discovery pipeline around three principles: every level of the hierarchy is agent-produced (`assemble.py` loses all semantic responsibility), a small collection of composable strategy recipes each works standalone and composes into larger orchestrations, and both top-down (conceptual) and bottom-up (empirical) passes run in parallel to surface what only becomes visible by comparing them.

## Background

The current `discovery-pipeline.yaml` is a monolith. It handles prescan, topic selection, investigation dispatch, per-module synthesis, subsystem assembly, and overview generation in a single recipe. `assemble.py` carries semantic responsibility it shouldn't — manipulating graph content, merging DOTs, making architectural decisions that belong to agents. There is no empirical (bottom-up) pass; the pipeline only investigates what it conceptually decides to look for, missing structure that exists in the code but wasn't predicted by topic selection.

After this redesign, `discovery-pipeline.yaml` becomes a thin orchestrator calling composable strategy recipes. `assemble.py` becomes pure file plumbing. A new bottom-up strategy provides empirical ground truth, and a combination step explicitly surfaces where conceptual and empirical understanding converge or diverge.

## Approach

Decompose the pipeline into a two-tier recipe architecture (strategy recipes + building block sub-recipes) with four new agents that replace `assemble.py`'s semantic work. Strategy recipes are independently runnable and compose into larger orchestrations. The parallel pipeline runs both strategies simultaneously and combines their output through a dedicated agent that classifies findings as convergence, divergence, top-down-only, or bottom-up-only.

## Architecture

### Recipe Collection — Two Tiers

**Strategy recipes** (standalone, run independently):

| Recipe | Purpose |
|---|---|
| `strategy-topdown.yaml` | The current conceptual investigation, extracted and made independent. Pick topics, investigate how things work, synthesize per-topic. |
| `strategy-bottomup.yaml` | NEW. Post-order tree traversal from leaf directories upward, building a picture of what actually exists. |
| `strategy-sequential.yaml` | NEW. Composes the two strategies sequentially: bottom-up first, top-down uses its output as context. |

**Building block sub-recipes** (used by strategies, also callable directly):

| Recipe | Purpose |
|---|---|
| `investigate-topic.yaml` | Exists now, unchanged. Per-topic agent dispatch. |
| `synthesize-level.yaml` | NEW. Synthesize one directory level (used recursively by bottom-up). |
| `synthesize-subsystem.yaml` | NEW. Agent-driven subsystem synthesis (replaces `assemble.py`'s semantic content). |
| `synthesize-overview.yaml` | NEW. Agent-driven overview synthesis. |

**Orchestrator recipes** (compose strategies):

| Recipe | Purpose |
|---|---|
| `discovery-pipeline.yaml` | Updated to lightweight orchestrator. Default: runs both strategies in parallel then combines. Accepts a `strategies` context variable for configurability. |
| `discovery-combine.yaml` | NEW. Reads top-down + bottom-up outputs, produces unified output with convergence/divergence analysis. |

A user can run `strategy-topdown.yaml` alone for quick conceptual understanding, `strategy-bottomup.yaml` alone for empirical discovery, `strategy-sequential.yaml` for enriched investigation (bottom-up informs top-down), or `discovery-pipeline.yaml` to get both with comparison. New strategies can be added without touching anything existing.

## Components

### The Bottom-Up Traversal (`strategy-bottomup.yaml`)

Uses the prescan tool to get the directory tree, then recursively traverses it **post-order** — children before parents. Each level:

1. Investigates all files **directly at that level** (not recursively — just immediate files)
2. Reads the synthesis DOT from **each immediate child directory** as additional context
3. Produces a synthesis DOT for that level: what lives here, how it connects to what the children synthesized, what's only visible at this boundary

The recursion bottoms out when the agent (guided by language-specific heuristics from prescan) determines a directory is a "leaf" — typically a directory with fewer than ~20 source files and no meaningful subdirectories, or a recognized module boundary (Python package with `__init__.py`, Rust module, Go package). The agent has judgment here — it can override the heuristic if the codebase's natural structure suggests a different boundary.

Each level writes to `.discovery/investigation/bottomup/{path}/` maintaining the output/investigation split. The recipe drives this using a `foreach` loop over the directory tree processed in post-order — leaves first, roots last.

The key agent: `discovery-level-synthesizer`, whose job is "read what's in this directory + what the children already found, produce a graph of this level."

### Agent-Driven Synthesis

Three new agents replace `assemble.py`'s semantic responsibility:

**`discovery-level-synthesizer`** — the core agent for the bottom-up strategy. Invoked once per directory level during post-order traversal. Input: actual source files at this level + synthesis DOTs from each immediate child directory. Job: produce a DOT that represents this level — what lives here directly, how it connects to what children synthesized, what only becomes visible at this boundary (cross-child connections, interfaces that span children, emergent patterns). Richly styled, semantically colored, level-appropriate shape vocabulary.

**`discovery-subsystem-synthesizer`** — used by the top-down strategy after per-module synthesis. Input: all per-module consensus DOTs within a subsystem + source files at subsystem boundaries. Job: produce a subsystem DOT showing how modules within the subsystem interoperate — cross-module data flows, shared interfaces, emergent subsystem-level patterns. Investigation at the seams between modules, not inside them.

**`discovery-overview-synthesizer`** — used by both strategies. Input: all subsystem DOTs + source at the repo root. Job: produce an overview showing how subsystems relate — cross-subsystem dependencies, the governing architecture, what you'd explain to a newcomer in 5 minutes.

**`assemble.py` reduced to plumbing**: directory creation, manifest tracking, file copying, triggering render. Zero semantic content. If you removed it you'd lose filesystem convenience, nothing else.

### The Sequential Strategy (`strategy-sequential.yaml`)

Three stages — proves composability by literally calling the other strategy recipes:

**Stage 1:** Run `strategy-bottomup.yaml` fully to completion. Writes to `.discovery/investigation/bottomup/`. Produces ground-truth DOTs at every directory level.

**[Approval gate]** — user reviews what bottom-up actually found before conceptual investigation begins. Valuable: may identify specific areas to focus top-down investigation on.

**Stage 2:** Run `strategy-topdown.yaml` with extra context variable: `bottomup_context` pointing to the bottom-up output directory. Prescan and topic selection agents see what bottom-up produced — they pick topics informed by actual structure. Investigation agents reference specific bottom-up DOTs as starting points and are primed to notice divergences: "the architecture suggests X but the bottom-up DOT of this directory shows Y."

**Stage 3:** Run `discovery-combine.yaml` — a combination agent reads both passes and produces unified output explicitly surfacing divergences.

Key design principle: `strategy-sequential.yaml` has no novel agents or logic of its own. It orchestrates three other recipes. Improvements to component recipes propagate automatically.

### The Parallel Pipeline & Combination

**`discovery-pipeline.yaml` (updated)** — lightweight orchestrator. Stage 1 runs prescan (shared, both strategies need it). Stage 2 dispatches `strategy-topdown.yaml` and `strategy-bottomup.yaml` as parallel sub-recipe invocations — each writes to its own output directory, neither waits for the other. Stage 3 runs `discovery-combine.yaml`. Optional approval gate between stages 2 and 3.

**`discovery-combine.yaml`** — invokes a new `discovery-combiner` agent. Reads both the top-down and bottom-up investigation directories and produces combined output explicitly distinguishing:

- **Convergence** — things both strategies found. High-confidence understanding.
- **Top-down only** — things the conceptual investigation saw but bottom-up didn't surface. Suggests architecture has aspirational structure not reflected in actual code.
- **Bottom-up only** — things the empirical traversal found that conceptual investigation missed. Suggests hidden complexity or undocumented design.
- **Divergence** — same thing characterized differently by both strategies. Highest-value findings. Explicitly tracked as discrepancies with IDs (D-01, D-02...).

Each category is visually distinct in the combined DOT output. Combined output writes to `.discovery/output/`. Individual strategy outputs live in `.discovery/investigation/topdown/` and `.discovery/investigation/bottomup/`.

## Data Flow

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

## Output Structure

```
.discovery/
├── investigation/
│   ├── topdown/           ← strategy-topdown outputs (per-topic)
│   └── bottomup/          ← strategy-bottomup outputs (directory hierarchy, post-order)
└── output/                ← discovery-combine final output
    ├── overview.dot/png
    └── subsystems/
```

## Error Handling

Each strategy recipe runs independently. If one strategy fails, the other's output is still available in its investigation directory. `discovery-combine.yaml` can operate in degraded mode with only one strategy's output (producing that output directly without convergence/divergence analysis). The approval gate in `strategy-sequential.yaml` provides a checkpoint where failures in the bottom-up pass can be reviewed before committing to the top-down pass.

## Testing Strategy

Each recipe is independently testable since strategies are standalone. Testing levels:

1. **Agent unit tests** — each of the 4 new agents tested in isolation with known inputs
2. **Sub-recipe tests** — `synthesize-level.yaml`, `synthesize-subsystem.yaml`, `synthesize-overview.yaml` tested with fixture directories
3. **Strategy integration tests** — `strategy-topdown.yaml` and `strategy-bottomup.yaml` run against a known codebase, outputs validated
4. **Combination tests** — `discovery-combine.yaml` tested with known convergent/divergent inputs to verify classification accuracy
5. **End-to-end tests** — `discovery-pipeline.yaml` run against the bundle's own codebase

## What Changes

### New Recipes (7)

| Recipe | Purpose |
|---|---|
| `strategy-topdown.yaml` | Extracts conceptual investigation from current pipeline |
| `strategy-bottomup.yaml` | New post-order traversal |
| `strategy-sequential.yaml` | Composes both sequentially |
| `discovery-combine.yaml` | Reads both strategy outputs, produces unified output |
| `synthesize-level.yaml` | Building block for bottomup recursion (per-directory level) |
| `synthesize-subsystem.yaml` | Building block for subsystem-level agent synthesis |
| `synthesize-overview.yaml` | Building block for overview-level agent synthesis |

### Updated Files

| File | Change |
|---|---|
| `discovery-pipeline.yaml` | Shrinks to thin orchestrator calling strategies + combine |
| `discovery-synthesize-module.yaml` | Called by `strategy-topdown` rather than pipeline directly |
| `behaviors/dot-discovery.yaml` | Declares 4 new agents alongside existing 5 |
| `assemble.py` | Keeps directory creation, manifest tracking, file management, render triggering. Loses all graph manipulation and semantic content. |

### Unchanged Files

| File | Note |
|---|---|
| `discovery-investigate-topic.yaml` | Still used by `strategy-topdown` |

### New Agents (4)

Declared in `behaviors/dot-discovery.yaml`:

| Agent | Role |
|---|---|
| `discovery-level-synthesizer` | Recursive bottom-up agent — per-directory-level synthesis |
| `discovery-subsystem-synthesizer` | Seam-finder between modules |
| `discovery-overview-synthesizer` | System-level pattern finder |
| `discovery-combiner` | Convergence/divergence analyst |

## Open Questions

1. **Leaf-level calibration** — How deep does the prescan-based leaf-level detection go for typical monorepos? The ~20-file heuristic needs calibration against real codebases.
2. **Context passing in sequential mode** — Should `strategy-sequential.yaml` pass the full bottom-up directory tree or just the top-level synthesis DOTs to the top-down investigation agents?
3. **Divergence taxonomy** — The `discovery-combiner` agent needs a clear taxonomy for what "divergence" means vs "top-down only." Worth refining before implementation.
4. **Sub-recipe granularity** — Does `synthesize-level.yaml` need its own recipe or can it be a parameterized step within `strategy-bottomup.yaml`?
